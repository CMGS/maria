#!/usr/bin/python
#coding:utf-8

import os
import select
import logging
import threading
import subprocess
import paramiko
from maria import utils
from maria.config import config

logger = logging.getLogger(__name__)


class GSSHServer(paramiko.ServerInterface):

    def __init__(self):
        self.command = None
        self.event = threading.Event()
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
        if not self.interface.check_key(key):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    # not paramiko method
    def check_error_message(self, channel):
        message = self.interface.message
        if message:
            channel.sendall_stderr(message)
            self.event.set()
            return True
        self.event.set()

    def check_channel_exec_request(self, channel, command):
        logger.info('Command %s received' % command)
        command, repo = self.interface.parse_command(command)
        if not self.interface.check_repo(repo):
            if self.check_error_message(channel):
                return True
            return False
        if not self.interface.check_command(command):
            if self.check_error_message(channel):
                return True
            return False
        command.append(self.interface.get_repo_path())
        self.command = command
        self.event.set()
        return True

    def main_loop(self, channel):
        if not self.command:
            return

        env = self.interface.get_env()
        p = subprocess.Popen(self.command,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             close_fds=True,
                             env=env)

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


DATA = 'AAAAB3NzaC1yc2EAAAADAQABAAABAQDJOtsej4dNSKTdMBnD8v6L0lZ1Tk+WTMlx' \
    'sFf2+pvkdoAu3EB3RZ/frpyV6//bJNTDysyvwgOvANT/K8u5fzrOI2qDZqVU7dtDSwU' \
    'edM3YSWcSjjuUiec7uNZeimqhEwzYGDcUSSXe7GNH9YsVZuoWEf1du6OLtuXi7iJY4H' \
    'abU0N49zorXtxmlXcPeGPuJwCiEu8DG/uKQeruI2eQS9zMhy73Jx2O3ii3PMikZt3g/' \
    'RvxzqIlst7a4fEotcYENtsJF1ZrEm7B3qOBZ+k5N8D3CkDiHPmHwXyMRYIQJnyZp2y0' \
    '3+1nXT16h75cer/7MZMm+AfWSATdp09/meBt6swD'


class GSSHInterface(object):

    def __init__(self):
        self.message = ''
        self.repo = ''
        self.username = ''
        self.key = ''
        self.command = []
        self.ssh_username = ''

    def parse_command(self, command):
        if not command:
            return [], ''
        # command eg: git-upload-pack 'code.git'
        args = command.split(' ')
        cmd = args[:-1]
        repo = args[-1].strip("'")
        return cmd, repo

    def check_user(self, name):
        self.ssh_username = name
        if name == 'git':
            return True
        return False

    def check_key(self, key):
        self.key = key
        key_b = key.get_base64()
        if DATA == key_b:
            return True
        return False

    def check_repo(self, repo):
        self.repo = repo
        # 'Error: Repository not found.\n'
        key = self.key
        if not key or not repo:
            return False
        return True

    def check_command(self, command):
        self.command = command
        if not command[0] or not command[0] in ('git-receive-pack',
                                                'git-upload-pack'):
            return False
        return True

    def get_env(self):
        return None

    def get_repo_path(self):
        return self.repo
