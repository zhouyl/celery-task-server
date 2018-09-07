# -*- coding: utf-8 -*-

__applied = False


def apply_config():
    '''加载日志配置并使之生效'''
    global __applied

    if not __applied:
        import logging.config
        from helpers.common import config, root_path

        conf = config('logger')

        for (name, options) in conf['handlers'].items():
            filepath = options.get('filename')
            if filepath is not None and filepath.startswith('logs/'):
                # 替换一下日志扩展配置中的路径
                conf['handlers'][name]['filename'] = root_path(filepath)

        # 初始化日志配置
        logging.config.dictConfig(conf)

    __applied = True


def get(*args, **kwargs):
    '''相当于 logging.getLogger()'''
    import logging

    apply_config()  # 自动加载配置

    return logging.getLogger(*args, **kwargs)
