#!/usr/local/bin/python2.7
#coding:utf-8

try:
    from gevent.monkey import patch_all
    patch_all(subprocess=False, aggressive=False)
    from gevent.server import StreamServer
    from gevent.pywsgi import WSGIServer
except ImportError:
    print 'You need install gevent manually! System shutdown.'

import logging
import argparse
import paramiko

from maria.config import config
from maria.utils import hex_key
from maria.handler import handle
from maria.ghttp import GHTTPServer
from maria.libs.loader import load_class
from maria.libs.colorlog import ColorizingStreamHandler

logger = logging.getLogger()


def populate_argument_parser(parser):
    parser.add_argument("-p", "--port", default=2200, dest="port",
                        type=int,
                        help="port number")
    parser.add_argument("--host", default="0.0.0.0", dest="host",
                        help="host")
    parser.add_argument("-w", "--worker", default="maria.gssh.GSSHServer",
                        dest="worker",
                        help="worker define")
    parser.add_argument("-c", "--hook", default="", dest="hook",
                        help="The path to a maria hook file.")
    parser.add_argument("--debug", default=False, dest="debug",
                        action="store_true",
                        help="debug")
    parser.add_argument("--host-key", default="host.key", dest="host_key",
                        help="host key file path")
    parser.add_argument("--log-file", default="/tmp/maria.log",
                        dest="log_file",
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


def main():
    parser = argparse.ArgumentParser()
    populate_argument_parser(parser)
    args = parser.parse_args()

    config.parser(args)
    init_log()
    # init hook file
    from maria import hook

    if config.worker == "maria.gssh.GSSHServer":
        config.host_key = paramiko.RSAKey(filename=config.host_key)
        logger.info('Host Key %s' % hex_key(config.host_key))
        server = StreamServer((args.host, args.port), handle)
    else:
        server = WSGIServer((args.host, args.port), GHTTPServer())
    config.worker = load_class(config.worker)
    config.gssh_interface = load_class(config.gssh_interface)
    config.ghttp_interface = load_class(config.ghttp_interface)

    try:
        logger.info('Maria System Start at %s:%d' % (config.host, config.port))
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info('Maria System Stopped')


def init_log():
    logging.StreamHandler = ColorizingStreamHandler
    level = logging.DEBUG
    if not config.debug:
        level = logging.INFO
    logging.BASIC_FORMAT = "%(asctime)s [%(name)s] %(message)s"
    logging.basicConfig(level=level)
    paramiko.util.log_to_file(config.log_file, level=level)


if __name__ == '__main__':
    main()
