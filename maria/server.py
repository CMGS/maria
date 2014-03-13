#!/usr/bin/python
#coding:utf-8

try:
    from gevent.monkey import patch_all
    patch_all(subprocess=False, aggressive=False)
    from gevent.server import StreamServer
    from gevent.pywsgi import WSGIServer
except ImportError:
    print 'You need install gevent manually! System shutdown.'

import logging
import paramiko
from maria.config import config
from maria.utils import hex_key
from maria.handler import handle
from maria.ghttp import GHTTPServer
from maria.libs.loader import load_class
logger = logging.getLogger()


def run(host="0.0.0.0",
        port=2200,
        worker="maria.gssh.GSSHServer",
        interface=""):
    config.host = host
    config.port = port
    config.worker = worker
    config.worker = load_class(worker)

    if worker == "maria.gssh.GSSHServer":
        if interface:
            config.gssh_interface = interface
        config.gssh_interface = load_class(config.gssh_interface)
        config.host_key = paramiko.RSAKey(filename=config.host_key)
        logger.info('Host Key %s' % hex_key(config.host_key))
        server = StreamServer((config.host, config.port), handle)
    else:
        if interface:
            config.ghttp_interface = interface
        config.ghttp_interface = load_class(config.ghttp_interface)
        server = WSGIServer((config.host, config.port), GHTTPServer())

    try:
        logger.info('Maria System Start at %s:%d' % (config.host, config.port))
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info('Maria System Stopped')
