#!/usr/local/bin/python2.7
#coding:utf-8

import os
import select
import logging
import threading
import subprocess
import paramiko
from maria import hook
from maria import utils
from maria.config import config

logger = logging.getLogger(__name__)


class GSSHServer(paramiko.ServerInterface):

    def __init__(self):
        self.command = None
        self.key = None
        self.event = threading.Event()
        self.git_env = None
        self.interface = config.gssh_interface()

    def get_allowed_auths(self, username):
        return 'publickey'

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_publickey(self, username, key):
        hex_fingerprint = utils.hex_key(key)
        logger.info('Auth attempt with key: %s' % hex_fingerprint)
        if not self.interface.check_user(username):
            return paramiko.AUTH_SUCCESSFUL
        if not self.interface.check_user_key(key):
            return paramiko.AUTH_SUCCESSFUL
        if hook.check_username(username) and hook.check_store_key(key):
            self.key = key
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_exec_request(self, channel, command):
        logger.info('Command %s received' % command)
        command, repo = hook.parser_command(command)
        if not self.interface.check_repo(repo):
            self.event.set()
            return False
        if not self.interface.check_command(command):
            self.event.set()
            return False
        if not hook.check_command(command[0]) \
                or not hook.check_permits(self.key,
                                          repo):
            self.event.set()
            return False
        if not hook.check_exisit(repo):
            channel.sendall_stderr('Error: Repository not found.\n')
            self.event.set()
            return True
        self.command = command
        self.event.set()
        return True

    def main_loop(self, channel):
        if not self.command:
            return

        self.git_env = self.interface.get_env()
        p = subprocess.Popen(self.command,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             close_fds=True,
                             env=self.git_env)

        ofd = p.stdout.fileno()
        efd = p.stderr.fileno()

        while True:
            r_ready, w_ready, x_ready = select.select([channel, ofd, efd],
                                                      [],
                                                      [],
                                                      config.select_timeout)

            if channel in r_ready:
                data = channel.recv(16384)
                if not data and (channel.closed or channel.eof_received):
                    break
                p.stdin.write(data)

            if ofd in r_ready:
                data = os.read(ofd, 16384)
                if not data:
                    break
                channel.sendall(data)

            if efd in r_ready:
                data = os.read(efd, 16384)
                channel.sendall(data)
                break

        output, err = p.communicate()
        if output:
            channel.sendall(output)
        if err:
            channel.sendall_stderr(err)
        channel.send_exit_status(p.returncode)
        channel.shutdown(2)
        channel.close()
        logger.info('Command execute finished')


class GSSHInterface(object):

    def __init__(self):
        pass

    def check_user(self, name):
        return hook.check_username(name)

    def check_user_key(self, key):
        return hook.check_store_key(key)

    def check_repo(self, repo):
        key = self.key
        return hook.check_permits(key, repo)

    def check_command(self, command):
        return hook.check_command(command)

    def get_env():
        return None

    def get_repo_path():
        return None
