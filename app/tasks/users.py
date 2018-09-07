# -*- coding: utf-8 -*-

from helpers import *
from providers import di
from tasks import app
from logics import mobile
from logics.refer import Refer
from logics.user.bind import *


@app.task
def add_basic(user):
    '''导入一条客户基本信息'''
    data = dict_only(user, 'uid', 'nickname', 'phone', 'email', 'refid',
                     'reg_time', 'country_id')

    data.update({
        'reg_from': Refer.unit(user['refer']),
        'qrcode_id': dict_get(user, 'qrcode.id', 0),
        'create_time': timestamp(),
        'update_time': timestamp(),
    })

    data['city_id'] = (mobile.location(data['phone']) or {}).get('city_id', 0)

    with di['db'].pool() as db:
        return db.insert('insert ignore into user_basic_info', **data)


@app.task
def add_refer(user):
    '''导入一条客户 refer 数据'''
    data = dict_only(user, 'uid', 'refid', 'reg_time', 'source_type',
                     'market_channel', 'sub_platform')

    data.update(dict_only(user['refer'], 'channel_id', 'business_v', 'platform_type'))

    data['update_time'] = timestamp()

    with di['db'].pool() as db:
        return db.insert('insert ignore into user_refer_info', **data)


@app.task
def add_qrcode(item):
    '''导入一条二维码注册数据'''
    data = {
        'id': item['id'],
        'platform': item['platform'],
        'uid': item['uid'],
        'sales_id': item['fromid'],
        'bind_sales_id': item['fromid'],
        'add_time': arrow.get(item['add_time']).timestamp,
        'create_time': timestamp(),
        'update_time': timestamp(),
    }

    with di['db'].pool() as db:
        rowcount = db.insert('insert ignore into user_qrcodes', **data)

        if rowcount:
            bind_sales.delay(item['uid'], BindType.QRCODE, item['fromid'], '二维码客户导入')
            return True
        return False


@app.task
def bind_sales(uid, bind_type, sales_id, note=''):
    '''首次绑定销售关系'''
    with di['db'].pool() as db:
        return BindUser(uid, db).first_bind(bind_type, sales_id, note)
