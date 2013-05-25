#!/usr/local/bin/python2.7
#coding:utf-8

from gevent.monkey import patch_all
patch_all(subprocess=False)
import logging
import argparse

import config
from git import handle
from gevent.server import StreamServer

logger = logging.getLogger()

def populate_argument_parser(parser):
    parser.add_argument("-p", \
                        "--port", \
                        default=2200, \
                        dest="port", \
                        type=int, \
                        help="port")
    parser.add_argument("--host", \
                        default="0.0.0.0", \
                        dest="host", \
                        help="host")

def main():
    parser = argparse.ArgumentParser()
    populate_argument_parser(parser)
    args = parser.parse_args()

    logging.BASIC_FORMAT = "%(asctime)s [%(name)s] %(message)s"
    logging.basicConfig(level=logging.DEBUG if config.DEBUG else logging.INFO)

    server = StreamServer((args.host, args.port), handle)
    try:
        logger.info('Maria System Start at %s:%d' % (args.host, args.port))
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info('Maria System Stopped')

if __name__ == '__main__':
    main()

