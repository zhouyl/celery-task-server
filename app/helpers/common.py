# -*- coding: utf-8 -*-

import os
import sys
import re

from .constants import *
from var_dump import var_dump

__config = {}


def env(environment=None):
    '''判断当前项目环境，或获取当前项目环境'''
    return environment.upper() == ENVIRONMENT if environment else ENVIRONMENT.lower()


def config(name, default=None):
    '''快速加载配置文件

    该函数会根据传入的 name 参数，查找 config 目录下的 yaml 配置文件，
    并支持通过路径的方式进行查找，例如：config('db.dbase')
    '''
    global __config

    if name.find('.') == -1:
        parts = []
    else:
        parts = name.split('.')
        name = parts[0]

    def __from_config_dict(data, parts, default):
        '''从 dict 配置中读取数据'''
        for key in parts[1:]:
            if isinstance(data, dict) and key in data:
                data = data.get(key)
            else:
                return default

        return data

    def __load_config_file(name):
        '''将配置加载到会话缓存中'''
        file = config_path("%s.yaml" % name)

        if os.path.isfile(file):
            import yaml
            with open(file, 'r') as f:
                return yaml.load(f.read())

        # 配置文件不存在
        raise IOError('The configuration file "%s" is not found' % file)

    if name not in __config:
        __config[name] = __load_config_file(name)

    return __from_config_dict(__config[name], parts, default)


def dd(*args):
    ''' var_dump 打印 & 结束脚本运行'''
    var_dump(*args)
    sys.exit(0)


def normalize_path(path):
    '''格式化路径
    去掉多余的斜线反斜线，去掉末尾的反斜线'''
    return re.compile(r'[\/\\\\]+').sub('/', path).rstrip('/')


def mask_path(path):
    '''从路径中，移除项目路径'''
    return str(path).replace(ROOT_PATH, '~')


def root_path(path=''):
    '''获取项目根下的路径'''
    return normalize_path(ROOT_PATH + '/' + path)


def app_path(path):
    '''获取 app 目录下的路径 '''
    return root_path('app/' + path)


def log_path(path):
    '''获取 logs 目录下的路径 '''
    return root_path('logs/' + path)


def config_path(path='', environment=ENVIRONMENT):
    '''获取配置文件路径 '''
    filepath = root_path('config/%s/%s' % (environment.lower(), path))

    if os.path.isfile(filepath) or os.path.isdir(filepath):
        return filepath

    return root_path('config/' + path)


def makedirs_ignore_error(path, mode=0o777):
    '''调用 os.makedirs 但忽略 OSError 类型错误'''
    try:
        os.makedirs(path, mode)
    except OSError:
        pass

    return os.path.isdir(path)


def force_type(value, t, default=None):
    '''强制数据类型转换'''
    if not isinstance(default, t):
        if default is None:
            raise ValueError("<default> argument must be instance of %s" % t)
        default = t(default)

    if value is None:
        return default

    if isinstance(value, t):
        return value

    return t(value)


def force_int(value, default=0):
    '''强制转换为 int 类型'''
    return force_type(value, int, default)


def force_float(value, default=float(0)):
    '''强制转换为 float 类型'''
    return force_type(value, float, default)


def force_bool(value, default=False):
    '''强制转换为 bool 类型'''
    return force_type(value, bool, default)


def force_str(value, default=''):
    '''强制转换为 str 类型'''
    return force_type(value, str, default)
