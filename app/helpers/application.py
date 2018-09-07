# -*- coding: utf-8 -*-

'''这里用来写一些与项目强相关的全局变量、常量、或者函数
'''

from .common import *
from .valid import *


def encrypt(*args, **kwargs):
    '''对输入的字符进行加密处理'''
    from providers import di

    with di['security'].item() as client:
        return client.encrypt(*args, **kwargs)


def decrypt(*args, **kwargs):
    '''对输入的字符进行解密处理'''
    from providers import di

    with di['security'].item() as client:
        return client.decrypt(*args, **kwargs)


def identity_birthday(id_number):
    '''提取身份证生日'''
    if not isinstance(id_number, (str)) or not is_cn_identity(id_number):
        return '0000-00-00'

    return '%s-%s-%s' % (id_number[6:10], id_number[10:12], id_number[12:14])


def identity_gender(id_number):
    '''提取身份证性别(0:未知/1:男/2:女)'''
    if not is_cn_identity(id_number) or not isinstance(id_number, (str)):
        return 0

    return 1 if int(id_number[16:17]) % 2 else 2
