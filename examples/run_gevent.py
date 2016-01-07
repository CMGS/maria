# -*- coding: utf-8 -*-

try:
    from gevent.monkey import patch_all
    patch_all()
    from gevent.server import StreamServer
except ImportError:
    print 'You need install gevent manually! System shutdown.'

from maria import Maria
from maria.config import config

app = Maria(config=config)

if __name__ == '__main__':
    server = StreamServer(('0.0.0.0', 2022), app)
    server.serve_forever()
