# -*- coding: utf-8 -*-

import os
import time
import arrow

from .constants import *

# 设置时区
os.environ['TZ'] = TIMEZONE
time.tzset()

'''这个 helpers 主要用于定义一些与日期、时间相关的重要函数

在项目中，使用了 date, time, dateutil, pytz, pytzdata, arrow, pendulum 这些包

在使用过程中，优先推荐使用 arrow，因为它已经能完成我们大部分的工作

不推荐使用 pendulum，因为它的时区不太准确，它只适合做一些复杂的日期时间计算工作
如果能够使用 timedelta 解决，不用这个包也是可以的
'''


def timestamp(*args, **kwargs):
    '''快速调用 arrow.get()，并获取一个时间戳'''
    return arrow.get(*args, **kwargs).timestamp
