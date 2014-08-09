# -*- coding: utf-8 -

try:
    import gevent
except ImportError:
    raise RuntimeError("You need install gevent")

from gevent.monkey import patch_all
patch_all(subprocess=False, aggressive=False)
from gevent.server import StreamServer

from maria.worker.base import WorkerClass
import logging


from importlib import import_module

class GeventServer(object):

    def run(self):
        self.logger = logging.getLogger(__name__)
        server = StreamServer(self.addr, self.app)
        try:
            self.logger.info('Maria System Start at %s:%s' % self.addr)
            server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info('Maria System Stopped')
