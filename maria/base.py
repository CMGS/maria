#!/usr/local/bin/python2.7
#coding:utf-8

import os
from maria.config import config

class BaseInterface(object):
    def check_user(self, name):
        raise NotImplementedError()

    def check_key(self, key):
        raise NotImplementedError()

    def check_password(self, password):
        raise NotImplementedError()

    def check_repo(self, repo):
        self.repo = repo
        return True

    def check_command(self, cmd):
        return True

    def get_env(self):
        return None

    def get_repo_path(self):
        return os.path.join(config.repos_path, self.repo)
