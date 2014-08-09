# -*- coding: utf-8 -*-



class WorkerClass(object):

    def __init__(self, addr, app):
        self.addr = addr
        self.app = app

    def run(self):
        raise NotImplementedError()
