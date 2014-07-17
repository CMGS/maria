# -*- coding: utf-8 -*-
from SocketServer import TCPServer
from maria import Maria
from maria.config import config

__all__ = ['main']

def main():
    config.host_key_path = 'host.key'
    app = Maria(config=config)
    server = TCPServer(('0.0.0.0', 2022), app)
    server.serve_forever()


if __name__ == '__main__':
    main()
