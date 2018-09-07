# -*- coding: utf-8 -*-

from utils.container import Provider
from helpers.common import config


class OApiProvider(Provider):

    '''数据加解密服务'''

    def register(self):
        self.di['oapi'] = self.create_oapi_client

    def create_oapi_client(self):
        from utils.oapi import OApiClient
        return OApiClient(**config('oapi'))
