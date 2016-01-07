# -*- coding: utf-8 -

try:
    import gevent
except ImportError:
    raise RuntimeError("You need install gevent")

from gevent.monkey import patch_all
patch_all(subprocess=False, aggressive=False)
from gevent.server import StreamServer
from maria.worker.base import WorkerClass


class GeventServer(WorkerClass):

    def run(self):
        server = StreamServer(self.addr, self.app)
        try:
            self.logger.info('Maria System Start at %s:%s' % self.addr)
            server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info('Maria System Stopped')
