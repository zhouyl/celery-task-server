# -*- coding: utf-8 -*-

import re

from .common import *

'''这里定义一些 True/False 判断的函数
'''


def is_base64str(text):
    '''判断是否一个通过 base64 加密的字符串'''
    try:
        if not isinstance(text, str):
            return False

        import base64
        convert = base64.b64encode(base64.b64decode(text))
        return convert == text or convert.decode('utf-8') == text
    except BaseException:
        return False


def is_encrypted(text):
    '''判断是否加密字符'''
    return is_base64str(text)


def is_numeric(n):
    '''判断值是否为一个数字，当输入值为 int, float, 数据型 str 时，返回 True'''
    return isinstance(n, (int, float)) \
        or (isinstance(n, str) and bool(re.match(r'^[\+\-]?[\d\.]+$', n)))


def is_chinese(text):
    '''判断是否包含中文字符'''
    return isinstance(text, str) and bool(re.match(r'.*[\u4e00-\u9fff]+', text))


def is_email(email):
    '''判断是否合法的 email 地址'''
    return isinstance(email, str) \
        and bool(re.match(r'^[a-z0-9\.\+_-]+@[a-z0-9\._-]+\.[a-z]*$', email.lower()))


def is_cn_email(email):
    '''判断是否中国邮箱地址'''
    r = r'''(163\.com)|(126\.com)|(yeah\.net)|(188\.com)|(sina\.com)|
        (sohu\.com)|(139\.com)|(21cn\.com)|(qq\.com)|(foxmail\.com)|(\.cn)$'''

    return isinstance(email, str) and bool(re.match(r, email, re.I | re.X))


def is_url(url):
    '''判断是否合法的 url'''
    pattern = r'^https?:\/\/([a-z0-9\-]+\.)+[a-z]{2,3}([a-z0-9_~#%&\/\'\+\=\:\?\.\-])*$'
    return isinstance(url, str) and bool(re.match(pattern, url.lower()))


def is_phone_number(phone):
    '''判断是否合法的电话号码'''
    return isinstance(phone, str) and len(phone) > 8 \
        and bool(re.match(r'^[+]?(\d+[\s-]?)?(\d+[\s-]?)*\d+$', phone))


def is_mobile(mobile):
    '''判断是否合法的手机号码'''
    return is_cn_mobile(mobile) or is_foreign_mobile(mobile)


def is_cn_mobile(mobile):
    '''判断是否合法的中国手机号码'''
    return isinstance(mobile, str) \
        and bool(re.match(r'^(\+?(00)?86[\s\-]*)?1[3456789][0-9]{9}', mobile))


def is_foreign_mobile(mobile):
    '''判断是否合法的海外手机号码'''
    return is_phone_number(mobile) and not is_cn_mobile(mobile) \
        and bool(re.match(r'^\+?\d{1,3}[\s\-]*\d{6,12}$', mobile))  # MSISDN


def is_cn_identity(id_number):
    '''判断是否合法的中国身份证号码'''
    return isinstance(id_number, str) \
        and bool(re.match(r'(^\d{15}$)|(^\d{17}([0-9]|X)$)', id_number))


def is_formax_uid(uid):
    '''是否我司注册客户 uid'''
    return bool(re.match(r'^[\d]{6, 10}$', force_str(uid)))


def is_mt4_login(login):
    '''判断是否外汇 mt4 账号'''
    return bool(re.match(r'^\d{2,}$', str(login)))
