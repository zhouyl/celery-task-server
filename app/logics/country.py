# -*- coding: utf-8 -*-

import os
import json

'''国家区域信息数据接口
'''

CHINA = 37

JSON_FILE = os.path.dirname(__file__) + '/countries.json'

countries = {}


def all():
    '''获取所有的国家域名数据'''
    global countries

    if not countries:
        with open(JSON_FILE) as f:
            countries = json.load(f)

    return countries


def get(id, default=None):
    '''根据 id 查询国家信息'''
    return all().get(str(id), default)


def name(id, default='-', name_key='cname'):
    '''根据 id 获取国家名称'''
    return get(id).get(name_key) if id in all() else default


def from_country(country, name_key='ename'):
    '''根据国家名称，获取国家信息'''
    for v in all().values():
        if v[name_key] == country:
            return v
    return None


def from_copyid(copyid):
    '''根据 copymaster 社区的国家 id，获取国家信息'''
    for v in all().values():
        if v['copyid'] == int(copyid):
            return v
    return None
