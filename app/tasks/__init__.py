# -*- coding: utf-8 -*-

from celery import Celery
from helpers.common import config
from utils import logger

# 激活默认日志配置
logger.apply_config()

app = Celery('tasks')

# 加载配置
app.config_from_object('tasks.celeryconfig')
