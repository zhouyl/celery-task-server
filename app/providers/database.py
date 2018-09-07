# -*- coding: utf-8 -*-

from utils import logger
from utils.container import Provider
from helpers.common import config

logger.apply_config()


class DatabaseProvider(Provider):
    '''数据库服务'''

    def register(self):
        self.di['db'] = self.create_db_manager

    def create_db_manager(self):
        from utils.mysql import ConnectionManager

        return ConnectionManager(**config('database'))
