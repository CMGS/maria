#!/usr/local/bin/python2.7
#coding:utf-8


class Config(object):

    def __init__(self):
        self.debug = False
        self.log_file = '/tmp/maria.log'
        self.host_key = 'host.key'
        self.auth_timeout = 20
        self.check_timeout = 10
        self.select_timeout = 10
        self.host = "0.0.0.0"
        self.port = 2200
        self.hook = ""
        # TODO:
        # maria.gssh.GSSHServer
        # maria.ghttp.GHTTPServer
        self.worker = "maria.gssh.GSSHServer"
        self.git_path = "git"
        self.repo_root_path = "./"

    def parser(self, args):
        for key in dir(args):
            if key.startswith('_'):
                continue
            new_conf = getattr(args, key)
            orig_conf = getattr(self, key, None)
            if orig_conf == new_conf:
                continue
            setattr(self, key, new_conf)

config = Config()
