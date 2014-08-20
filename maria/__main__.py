# -*- coding: utf-8 -*-

import logging
import paramiko
from maria import Maria
from maria.config import Config 
from maria.loader import load, load_class
from maria.colorlog import ColorizingStreamHandler

__all__ = ['main']


class Application(object):

    def __init__(self, usage=None, prog=None): 
        self.usage = usage
        self.prog = prog
        self.config = None
        self.app = None
        self.logger = logging.getLogger(self.__class__.__name__) 
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
        self.config = Config(usage=self.usage, prog=self.prog)
        parser = self.config.parse()
        args = parser.parse_args()
        self.config.load_options(args)
        self.init_log()
    
        # load xxx.xxx:app 
        if len(args.apps) < 1:
            self.logger.info('No application module specified, using default setting')
            app = load('maria.gssh.GSSHServer')
            self.app = app(config=self.config)
        else:
            app = load(args.apps[0])
            # command line options has priority over the app's
            for key in dir(args):
                if key.startswith('_') or key == 'apps':
                    continue
                cmd_conf = getattr(args, key)
                app_conf = getattr(app.config, key)
                if cmd_conf == app_conf:
                    continue
                setattr(app.config, key, cmd_conf)
                if key == 'host_key_path':
                    self.logger.info('host key path got changed by command line')
                    app.init_key()
            self.app = app
            self.config.worker = app.config.worker

    # choose worker
    def load_worker(self):
        if self.config.worker == 'sync':
            return load('maria.worker.socket.SocketServer')
        elif self.config.worker == 'async':
            return load('maria.worker.ggevent.GeventServer')
        else:
            raise Exception('Invalid Worker!')

    def run(self):
        server = self.load_worker()
        addr = self.app.config.get_addr()
        return server(addr, self.app).run()


def main():
    Application("%(prog)s [OPTIONAL_ARGUMENTS] [APP_MODULE]").run()


if __name__ == '__main__':
    main()
