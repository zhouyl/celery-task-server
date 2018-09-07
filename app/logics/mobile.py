# -*- coding: utf-8 -*-

import json
from helpers import *
from providers import di

REDIS_KEY = 'PYSC_MOBILE_LOCATIONS'


def _load_from_redis(prefix):
    '''从 redis 中查询归属地信息'''
    return json.loads(di['redis'].hget(REDIS_KEY, prefix).decode('utf8'))


def _load_from_database(prefix):
    '''从数据库查询归属地信息'''
    data = di['db'].fetch_row(
        'select * from mobile_location where phone_prefix=%s', prefix)

    if not data:
        return None

    di['redis'].hset(REDIS_KEY, prefix, json.dumps(data))

    return dict(data)


def location(mobile):
    '''查询手机号码归属地信息'''
    if is_encrypted(mobile):
        mobile = decrypt(mobile)

    if not isinstance(mobile, str):
        return None

    mobile = re.sub(r'(^\s*86\s*)|(\s+)', '', re.sub(r'[^\d]', ' ', mobile))

    if not bool(re.match(r'^(1[3456789][0-9]{9})$', mobile)):
        return None

    prefix = mobile[:7]

    if di['redis'].hexists(REDIS_KEY, prefix):
        return _load_from_redis(prefix)

    return _load_from_database(prefix)
