# -*- coding: utf-8 -*-

from contextlib import contextmanager
from .base_command import BaseCommand, StopError
from helpers import *
from providers import di
from utils import logger
from tasks import users


class ImportQrcodesCommand(BaseCommand):

    '''
    导入二维码用户数据

    import:qrcodes
        {--i|id= : 从这个 id 开始导入，默认值为自动查询数据库}
    '''

    # 日志记录器
    log = logger.get(__name__)

    # 从这个 uid 开始导入
    last_id = None

    # 每次处理的记录数大小
    limit = 10000

    # 每次循环处理事物的间隔时间
    interval = 60

    def handle(self):
        '''脚本从这里开始执行'''
        self.last_id = force_int(self.option('id') or self.max_id())

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
                    self.sleep(self.interval)

    def max_id(self):
        return di['db'].fetch_first('select max(id) from user_qrcodes')

    @contextmanager
    def fetch_items(self):
        sql = '''select
                id, platform, uid, fromid, add_time
            from t_line_extension
            where id > %s
            limit %s''' % (self.last_id, self.limit)

        yield di['db'].connection('bar').fetch_all(sql)

    def do_import(self, item):
        self.put_tasks([users.add_qrcode], item)
        self.last_id = item['id']

    def put_tasks(self, tasks, *args):
        '''将任务投递到 celery tasks'''
        if isinstance(tasks, str):
            tasks = [tasks]

        for task in tasks:
            # 允许重试3次，每次间隔3秒
            task.apply_async(args, max_retries=3, interval_start=3, retry=True)
            self.log.info('Add celery task [%s], args: %s', task.__name__, str(args))
