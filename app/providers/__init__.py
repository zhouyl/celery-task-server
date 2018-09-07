# -*- coding: utf-8 -*-

from utils.container import Container
from .database import DatabaseProvider
from .cache import CacheProvider
from .security import SecurityProvider
from .oapi import OApiProvider

di = Container()

di.add_provider(DatabaseProvider) \
  .add_provider(CacheProvider) \
  .add_provider(SecurityProvider) \
  .add_provider(OApiProvider)
