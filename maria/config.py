# -*- coding: utf-8 -*-

import os
import sys
import argparse


def populate_argument_parser(parser):
    parser.add_argument("-b", "--bind", default="127.0.0.1:2200", dest="bind",
                        help="bind host:port")
    parser.add_argument("-k", "--key", default="host.key", dest="host_key_path",
                        help="key file path")
    parser.add_argument("-w", "--worker", default="sync", dest="worker",
                        help="worker async(gevent), sync(socketserver)")
    parser.add_argument("--git-path", default="/usr/bin", dest="git_path",
                        help="git command path")
    parser.add_argument("--repo-path",  default="", dest="project_root",
                        help="git repository root path")
    parser.add_argument("--debug", default=False, dest="debug",
                        action="store_true",
                        help="debug")
    parser.add_argument("--log-file", default="./maria.log", dest="log_file",
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


class Config(object):

    def __init__(self, usage=None, prog=None):
        self.usage = usage
        self.prog = prog or os.path.basename(sys.argv[0])
        self.host_key = None

        self.bind = '0.0.0.0:2200'
        self.host_key_path = 'host.key'
        self.worker = 'sync'
        self.git_path = '/usr/bin'
        self.project_root = ''
        self.debug = False
        self.log_file = './maria.log'
        self.auth_timeout = 20
        self.check_timeout = 10
        self.select_timeout = 10

    # set the config options by args
    def load_options(self, args):
        for key in dir(args):
            if key.startswith('_') or key == 'apps':
                continue
            new_conf = getattr(args, key)
            orig_conf = getattr(self, key, None)
            if orig_conf is None or orig_conf == new_conf:
                continue
            setattr(self, key, new_conf)

    # construct a ArgumentParser
    def parse(self):
        parser = argparse.ArgumentParser(
                 prog = self.prog,
                 usage = self.usage,
                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        populate_argument_parser(parser)
        parser.add_argument("apps", nargs="*", help=argparse.SUPPRESS)
        return parser

    # return (host, port)
    def get_addr(self):
        addr = self.bind.split(':')
        if len(addr) is not 2:
            raise ValueError('Unrecognized argument value: "%s"' % self.bind)
        return (addr[0], int(addr[1]))

    def get(self, key):
        value = getattr(self, key, None)
        if not value:
            raise AttributeError("No configuration setting for: %s" % key)
        return value


config = Config()
