# -*- coding: utf-8 -*-

from utils.container import Provider
from helpers.common import config


class SecurityProvider(Provider):
    '''数据加解密服务'''

    def register(self):
        self.di['security'] = self.create_security_pool

    def create_security_pool(self):
        from utils.pools import ConnectionPool

        return ConnectionPool(self.create_security, max_size=10, name='security')

    def create_security(self):
        from thrifts.security import SecurityClient

        return SecurityClient(**config('thrift.security'), redis=self.di['redis'])
