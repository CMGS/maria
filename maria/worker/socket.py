# -*- coding: utf-8 -

from SocketServer import TCPServer
from maria.worker.base import WorkerClass


class SocketServer(WorkerClass):

    def run(self):
        server = TCPServer(self.addr, self.app)
        try:
            self.logger.info('Maria System Start at %s:%s' % self.addr)
            server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info('Maria System Stopped')
