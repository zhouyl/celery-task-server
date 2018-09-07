# -*- coding: utf-8 -*-

from cleo import Application
from helpers.constants import *
from .make_command import MakeCommand
from .import_users_command import ImportUsersCommand
from .import_qrcodes_command import ImportQrcodesCommand

application = Application('celery-task-server', VERSION, complete=True)

# 在非生产环境下，不捕获异常以便进行调试
application.set_catch_exceptions(PRODUCTION or TESTING)

# 将需要添加的 command 全部添加到项目中
application.add(MakeCommand())
application.add(ImportUsersCommand())
application.add(ImportQrcodesCommand())
