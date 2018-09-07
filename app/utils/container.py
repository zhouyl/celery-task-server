# -*- coding: utf-8 -*-


class Provider(object):

    '''这是一个服务提供者 (Provider) 的抽象类

    所有注册的 provider，都必须实例这个接口的相关方法'''

    di = None

    def __init__(self, container):
        self.di = container

    def register(self):
        '''将当前的 provider 注册到容器 (container) 中'''
        raise NotImplementedError

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return self.__class__.__name__


class Container(object):

    '''这是一个依赖注入容器类

    可以通过注册 provider 的方式，为我们创建/调用实例带来方便
    尤其是注册回调的方式，帮助我们实例按需加载，避免资源的过度消耗

    代码示例：

        # 创建容器
        di = Container()

        # 通过 callback 回调的方式注册，实现按需加载
        def create_cache_connection():
            memcache.Client(['127.0.0.1:11211'])
        di['cache'] = create_cache_connection

        # 获取容器实例，将会自动根据回调创建实例
        di['cache'].set('key', 'value')

        # 直接指定实例
        di['cache'] = memcache.Client(['127.0.0.1:11211'])

        # 通过 Provider 加载
        from providers import CacheProvider
        di.add_provider(CacheProvider)
    '''

    _providers = {}
    _instances = {}

    def __init__(self, **kwargs):
        '''可以在容器初始化的时候，就指定一些实例

            di = Container(db=create_database_manager)
            di['db'].execute(...)
        '''
        self._instances.update(kwargs)

    def add_provider(self, provider):
        '''新增一个 provider'''
        if not isinstance(provider, Provider):
            if not issubclass(provider, Provider):
                raise ValueError("Invalid provider [%s]" % str(provider))
            else:
                # 有可能传进来的只是 Provider 类
                provider = provider(self)

        self._providers[provider.__class__.__name__] = provider

        provider.register()

        return self

    def get_provider(self, provider):
        '''根据指定的 provider 的类型，获取一个已注册的 provider'''
        if isinstance(provider, Provider):
            provider = provider.__class__.__name__
        elif issubclass(provider, Provider):
            provider = provider.__name__

        return self._providers.get(str(provider))

    def providers(self):
        return self._providers.keys()

    def instances(self):
        return self._instances.keys()

    def set(self, name, value):
        '''为依赖注入容器，新增一个实例或实例的创建者回调'''
        self._instances[name] = value

    def get(self, name):
        '''从已注册的服务中，获取一个实例'''
        if name not in self._instances:
            raise AttributeError("[%s] is not registered in the container" % name)

        item = self._instances.get(name)

        if hasattr(item, '__call__'):
            self._instances[name] = item()

        return self._instances[name]

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, name, value):
        self.set(name, value)

    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self.set(name, value)

    def __call__(self, name):
        return self.get(name)
