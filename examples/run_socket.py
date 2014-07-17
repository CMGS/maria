# -*- coding: utf-8 -*-

from SocketServer import TCPServer
from maria import Maria
from maria.config import config

config.host_key_path = 'host.key'
app = Maria(config=config)

if __name__ == '__main__':
    server = TCPServer(('0.0.0.0', 2022), app)
    server.serve_forever()
