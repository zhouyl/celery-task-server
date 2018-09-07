# -*- coding: utf-8 -*-

'''在 helpers 目录下定义的文件，应当直接 import *

因为这些文件定义的都是项目中需要直接用到的变量，或者方法

例如 database 中的 db 变量，app 中的 config() 函数

import * 的方式可以将这些变量或者函数当作全局变量/函数来应用

虽然这种方法不是很好的设计，但用起来很方便不是么？不用频繁的 import

所以，不要在 helpers 中写大段直接执行的代码，会影响全局性能的！！！
'''

from .constants import *
from .datetime import *
from .dictionary import *
from .valid import *
from .common import *
from .application import *
