# -*- coding: utf-8 -*-

from datetime import timedelta
from celery.schedules import crontab

'''Celery配置参数

@link http://docs.celeryproject.org/en/latest/userguide/configuration.html#new-lowercase-settings
'''

# Broker and Backend
BROKER_URL = 'redis://127.0.0.1:6379/8'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/9'

# 指定时区，不指定默认为 'UTC'
CELERY_TIMEZONE = 'Asia/Shanghai'

# task 结果过期时间
CELERY_TASK_RESULT_EXPIRES = 3600

# import
CELERY_IMPORTS = (
    # 'tasks.hello',
    'tasks.users'
)

# schedules
CELERYBEAT_SCHEDULE = {
}

'''以下这段代码用于测试服务器性能

for i in range(100):
    CELERYBEAT_SCHEDULE['say-hello-timedelta%d' % i] = {
        'task': 'tasks.hello.say_hello',
        'schedule': timedelta(seconds=0.1),
        'args': ['n-%d' % i],
    }
'''
