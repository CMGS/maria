# -*- coding: utf-8 -*-

import logging


class WorkerClass(object):

    def __init__(self, addr, app):
        self.addr = addr
        self.app = app
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self):
        raise NotImplementedError()
