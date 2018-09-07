# -*- coding: utf-8 -*-

from utils.container import Provider
from helpers.common import config


class CacheProvider(Provider):

    '''注册一些缓存服务 memcache/redis'''

    def register(self):
        self.di['memcache'] = self.create_memcache
        self.di['redis'] = self.create_redis

    def create_memcache(self):
        '''创建一个 memcache 连接'''
        import memcache
        return memcache.Client(config('cache.memcache'))

    def create_redis(self):
        '''创建一个 redis 连接'''
        from redis import Redis, BlockingConnectionPool

        # 构建一个连接池
        pool = BlockingConnectionPool(max_connections=10)

        return Redis(connection_pool=pool, **config('cache.redis'))
