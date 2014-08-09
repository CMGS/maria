# -*- coding: utf-8 -*-

import os
import sys
import argparse 


def populate_argument_parser(parser):
    parser.add_argument("-b", "--bind", default="127.0.0.1:2200", dest="bind",
                        help="bind host:port")
    parser.add_argument("-k", "--key", default="host.key", dest="host_key_path",
                        help="key file path")
    parser.add_argument("-w", "--worker", default="maria.worker.socket.SocketServer", dest="worker_class",
                        help="worker async(gevent), sync(socketserver)")
    parser.add_argument("--git-path", default="/usr/bin", dest="git_path",
                        help="git command path")
    parser.add_argument("--repo-path",  default="", dest="project_root",
                        help="git repository root path")
    parser.add_argument("--debug", default=False, dest="debug",
                        action="store_true",
                        help="debug")
    parser.add_argument("--log-file", default="/tmp/maria.log", dest="log_file",
                        help="log file path")
    parser.add_argument("--auth-timeout", default=20, dest="auth_timeout",
                        type=int,
                        help="auth timeout")
    parser.add_argument("--check-timeout", default=10, dest="check_timeout",
                        type=int,
                        help="check timeout")
    parser.add_argument("--select-timeout", default=10, dest="select_timeout",
                        type=int,
                        help="select timeout")


class Settings(object):
    """
    contain the setting values
    """
    def __init__(self):
        self.bind = '127.0.0.1:2200'
        self.host_key_path = 'host.key'
        self.worker_class = "maria.worker.socket.SocketServer"
        self.git_path = "git"
        self.project_root = ""
        self.debug = False
        self.log_file = '/tmp/maria.log'
        self.auth_timeout = 20
        self.check_timeout = 10
        self.select_timeout = 10
    
    def load_settings(self, args):

        for key in dir(args):
            if key.startswith('_'):
                continue
            new_conf = getattr(args, key)
            orig_conf = getattr(self, key, None)
            if orig_conf is None or orig_conf == new_conf:
                continue
            setattr(self, key, new_conf)


class Config(object):

    def __init__(self, usage, prog):
        self.usage = usage
        self.prog = prog or os.path.basename(sys.argv[0])
        self.host_key = None
        self.settings = Settings()

    def parse(self):

        parser = argparse.ArgumentParser(
                 prog = self.prog,
                 usage = self.usage,
                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        populate_argument_parser(parser)
        # argparse.SUPPRESS silence the help entry for certain options
        parser.add_argument("args", nargs="*", help=argparse.SUPPRESS)
        return parser

    @property
    def bind(self):
        addr = self.settings.bind.split(':')
        if len(addr) is not 2:
            raise ValueError('Unrecognized argument value: "%s"' % args.bind)
        return (addr[0], int(addr[1]))

    @property
    def host_key_path(self):
        return self.settings.host_key_path

    @property
    def worker_class(self):
        return self.settings.worker_class

    @property
    def git_path(self):
        return self.settings.git_path

    @property
    def project_root(self):
        return self.settings.project_root

    @property
    def debug(self):
        return self.settings.debug

    @property
    def log_file(self):
        return self.settings.log_file

    @property
    def auth_timeout(self):
        return self.settings.auth_timeout

    @property
    def check_timeout(self):
        return self.settings.check_timeout
    
    @property
    def select_timeout(self):
        return self.settings.select_timeout

    def get(self, key):
        if key not in self:
            raise AttributeError("No configuration setting for: %s" % key)
        return settings.__getattribute__(self, key)

