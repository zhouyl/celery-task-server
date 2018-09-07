# -*- coding: utf-8 -*-

from utils import logger

logger.apply_config()

if __name__ == '__main__':
    from commands import application
    application.run()
