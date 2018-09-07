# -*- coding: utf-8 -*-

import os
import sys
import pytz

VERSION = '1.0'

# 项目运行环境
if os.path.isfile('/etc/py.env.production'):
    ENVIRONMENT = 'PRODUCTION'
elif os.path.isfile('/etc/py.env.testing'):
    ENVIRONMENT = 'TESTING'
else:
    ENVIRONMENT = 'DEVELOPMENT'

PRODUCTION = ENVIRONMENT is 'PRODUCTION'
TESTING = ENVIRONMENT is 'TESTING'
DEVELOPMENT = ENVIRONMENT is 'DEVELOPMENT'

# 时区
TIMEZONE = 'Asia/Shanghai'

# 用于 datetime 的默认时区设置
TZINFO = pytz.timezone(TIMEZONE)

# 日期时间格式
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# 项目路径配置
ROOT_PATH = os.path.dirname(sys.path[0] or '/'.join(__file__.split('/')[:-2]))
