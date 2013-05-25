#!/usr/local/bin/python2.7
#coding:utf-8

import select
import logging
import threading
import subprocess

import utils
import config
import paramiko

logger = logging.getLogger(__name__)

class Gerver(paramiko.ServerInterface):

    def __init__(self):
        self.command = None
        self.hex_fingerprint = None
        self.event = threading.Event()

    def get_allowed_auths(self, username):
        return 'publickey'

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_publickey(self, username, key):
        hex_fingerprint = utils.hex_key(key)
        logger.info('Auth attempt with key: %s' % hex_fingerprint)
        if (username == 'git') and utils.check_store_key(hex_fingerprint):
            self.hex_fingerprint = hex_fingerprint
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_exec_request(self, channel, command):
        logger.info('Command %s received' % command)
        command, repo = utils.parser_command(command)
        if not utils.check_command(command[0]) or not utils.check_permits(self.hex_fingerprint, repo):
            self.event.set()
            return False
        self.command = command
        self.event.set()
        return True

    def main_loop(self, channel):
        p = subprocess.Popen(self.command, \
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)

        while True:
            import time
            time.sleep(10)
            r_ready, w_ready, x_ready = select.select(
                    [channel, p.stdout, ], [channel, p.stdin, ], [], \
                    config.SELECT_TIMEOUT)

            if channel in r_ready and p.stdin in w_ready:
                data = channel.recv(8)
                if data:
                    p.stdin.write(data)

            if channel in w_ready and p.stdout in r_ready:
                data = p.stdout.read(1)
                if not data:
                    break
                channel.sendall(data)

        logger.info('Command execute finished')
        retcode = p.wait()
        channel.send_exit_status(retcode)
        channel.close()

