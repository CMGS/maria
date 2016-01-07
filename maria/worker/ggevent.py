# -*- coding: utf-8 -

try:
    from gevent.monkey import patch_all
    patch_all()
    from gevent.server import StreamServer
except ImportError:
    raise RuntimeError("You need install gevent")

from maria.worker.base import WorkerClass


class GeventServer(WorkerClass):

    def run(self):
        server = StreamServer(self.addr, self.app)
        try:
            self.logger.info('Maria System Start at %s:%s' % self.addr)
            server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info('Maria System Stopped')
