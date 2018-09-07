# -*- coding: utf-8 -*-

import time
import re

from contextlib import contextmanager
from .base_command import BaseCommand, StopError
from helpers import *
from providers import di
from utils import logger
from tasks import users
from logics import country
from logics.refer import Refer


class ImportUsersCommand(BaseCommand):

    '''
    客户数据导入服务

    import:users
        {--u|uid= : 从这个 uid 开始导入，默认值为自动查询数据库}
    '''

    # 日志记录器
    log = logger.get(__name__)

    # 从这个 uid 开始导入
    uid = None

    # 每次处理的记录数大小
    limit = 10000

    # 每次循环处理事物的间隔时间
    interval = 60

    # 时间延迟：可能其它的客户数据还没准备好，适当的延迟可以保证准确性
    delay = timestamp() - 600

    def handle(self):
        '''脚本从这里开始执行'''

        self.uid = force_int(self.option('uid') or self.max_uid())

        while not self.stopped:
            with self.fetch_items() as items:
                self.log.info('Total %d records found.', len(items))

                try:
                    for item in items:
                        if self.stopped:
                            raise StopError
                        self.do_import(item)
                except StopError:
                    break

                # 取出的结果集小于限制的记录数，休息一段时间
                if len(items) < self.limit:
                    self.log.debug('Waiting for new records ...')
                    time.sleep(self.interval)

    def max_uid(self):
        '''# 获取导入开始的 uid'''
        return di['db'].fetch_first('select max(uid) from user_basic_info')

    @contextmanager
    def fetch_items(self):
        '''获取一批客户数据'''
        sql = '''select
            a.uid, a.registration_time as reg_time, a.source_type,
            a.sub_platform, a.market_channel, a.refid,
            b.email_safe, b.phone_safe, b.nickname, b.location
        from t_registration_affliated_info as a
        join t_formax_user_info as b on a.uid=b.uid
        where a.uid > %d
            and a.registration_time > 0
            and a.registration_time < %d
        order by a.uid
        limit %d''' % (self.uid, self.delay, self.limit)

        yield di['db'].connection('bar').fetch_all(sql)

    def do_import(self, item):
        '''执行客户导入操作'''
        item['phone'] = decrypt(item['phone_safe']) or ''
        item['email'] = decrypt(item['email_safe']) or ''
        item['qrcode'] = self.qrcode_info(item['uid'])
        item['refer'] = self.refer_info(item)
        item['refid'] = item['refer']['refer_id']
        item['country_id'] = self.country_id(item)

        self.put_tasks([users.add_basic, users.add_refer], item)

        self.uid = item['uid']  # 记下最后一次处理的 uid

    def put_tasks(self, tasks, *args):
        '''将任务投递到 celery tasks'''
        if isinstance(tasks, str):
            tasks = [tasks]

        for task in tasks:
            # 允许重试3次，每次间隔3秒
            task.apply_async(args, max_retries=3, interval_start=3, retry=True)
            self.log.info('Add celery task [%s], args: %s', task.__name__, str(args))

    def refer_info(self, user):
        '''获取 refer 数据'''
        if user['refid'] == '' or user['refid'] == 'no_refid':
            refer = Refer.lookup(**user)
        else:
            refer = Refer.refer(user['refid'][0:8])

        return refer if refer else Refer.refer(Refer.DEFAULT_REFID)

    def qrcode_info(self, uid):
        '''获取二维码数据'''
        return di['db'].connection('bar').fetch_row(
            'select id, fromid from t_line_extension where uid = %s', uid)

    def country_id(self, user):
        '''获取用户城市 id'''
        country_id = self.location_to_country_id(user.get('location'))

        if country_id > 0:
            return country_id

        return country.CHINA if self.is_cn_user(user) else 0

    def location_to_country_id(self, location):
        '''将用户信息中的 location 信息转化为 country_id'''
        if not location:
            return 0

        matches = re.findall(r'^\d+', location)
        if not matches:
            return 0

        info = country.from_copyid(matches[0])

        return info.get('id') if info else 0

    def is_cn_user(self, user):
        '''根据用户信息，判断是否中国用户'''
        return is_cn_mobile(user.get('phone')) \
            or is_cn_email(user.get('email')) \
            or is_chinese(user.get('nickname'))
