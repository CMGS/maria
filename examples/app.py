#!/usr/bin/python
#coding:utf-8

try:
    from gevent.monkey import patch_all
    patch_all()
except ImportError:
    raise RuntimeError("You need install gevent")

from maria import Maria
from maria.config import config

app = Maria(config=config)

