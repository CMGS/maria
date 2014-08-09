# -*- coding: utf-8 -*-

import logging
import paramiko
from maria.config import Config
from maria.loader import load_class, import_app
from maria.colorlog import ColorizingStreamHandler

__all__ = ['main']


class Application(object):

    def __init__(self, usage=None, prog=None): 
        self.usage = usage
        self.prog = prog
        self.config = None
        self.logger = logging.getLogger(__name__) 
        self.load_config()

    def init_log(self):
        logging.StreamHandler = ColorizingStreamHandler
        level = logging.DEBUG
        if not self.config.debug:
            level = logging.INFO
        logging.BASIC_FORMAT = "%(asctime)s [%(name)s] %(message)s"
        logging.basicConfig(level=level)
        if self.config.log_file:
            paramiko.util.log_to_file(self.config.log_file, level=level)

    def load_config(self):
        self.config = Config(self.usage, prog=self.prog)
        parser = self.config.parse()
        args = parser.parse_args()
        self.config.settings.load_settings(args)
        self.init_log()

        if len(args.args) < 1:
            self.logger.info("No application module specified, using default maria.gssh:GSSHServer")
            self.config.app_uri = 'maria.gssh:GSSHServer'
        else:
            self.config.app_uri = args.args[0]
    
    def load_app(self):
        return import_app(self.config.app_uri)

    def load_worker(self):
        return load_class(self.config.worker_class)

    def run(self):
        server = self.load_worker()
        app = self.load_app()
        return server(self.config.bind, app(config=self.config)).run()


def main():
    Application("%(prog)s [OPTIONAL_ARGUMENTS] [APP_MODULE]").run()


if __name__ == '__main__':
    main()
