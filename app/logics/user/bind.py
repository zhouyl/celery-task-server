# -*- coding: utf-8 -*-

from helpers import *
from providers import di


class BindType(object):

    AGENT = 'AGENT'
    MARKETING = 'MARKETING'
    POTENTIAL = 'POTENTIAL'
    QRCODE = 'QRCODE'


class BindUser(object):

    def __init__(self, uid, db=None):
        self.uid = uid
        self.db = db or di['db'].connection('foo')

    @property
    def is_bind(self):
        return bool(self.bind_info)

    @property
    def bind_info(self):
        return self.db.fetch_row(
            'select * from user_bind_sales where uid=%s', self.uid)

    def first_bind(self, bind_type, sales_id, note='', operator=0):
        if self.is_bind:
            return False

        data = {
            'uid': self.uid,
            'bind_type': bind_type,
            'bind_sales_id': sales_id,
            'orig_sales_id': sales_id,
            'first_bind_time': int(time.time()),
            'last_bind_time': int(time.time()),
        }
        rowcount = self.db.insert('insert ignore into user_bind_sales', **data)

        if not rowcount:
            return False

        self.add_bind_logs(sales_id, 0, note, operator)

        return True

    def rebind_to(self, sales_id, note='', operator=0):
        info = self.bind_info
        if not info:
            return False

        data = {
            'bind_sales_id': sales_id,
            'last_bind_time': int(time.time()),
        }

        rowcount = self.db.update(
            'update user_bind_sales where uid=%s', self.uid, **data)

        if not rowcount:
            return False

        self.add_bind_logs(sales_id, info['bind_sales_id'], note, operator)

        return True

    def add_bind_logs(self, bind_sales_id, before_sales_id, note='', operator=0):
        self.db.insert('insert into user_bind_sales_logs', **{
            'uid': self.uid,
            'before_sales_id': before_sales_id,
            'bind_sales_id': bind_sales_id,
            'note': note,
            'operator': operator,
            'log_time': int(time.time()),
        })
