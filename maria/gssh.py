# -*- coding: utf-8 -*-

import os
import select
import logging
import threading
import subprocess
import paramiko
from . import utils
from .colorlog import ColorizingStreamHandler


class GSSHServer(object):

    def __init__(self, config=None):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.init_log()
        self.init_key()

    # SocketServer:
    #  self.RequestHandlerClass(request, client_address, self)
    def __call__(self, socket, address, _=None):
        client = None
        try:
            client = paramiko.Transport(socket)
            try:
                client.load_server_moduli()
            except Exception:
                self.logger.exception('Failed to load moduli -- gex will be unsupported.')
                raise

            client.add_server_key(self.config.host_key)
            server = GSSHServerInterface(app=self)
            try:
                client.start_server(server=server)
            except paramiko.SSHException:
                self.logger.exception('SSH negotiation failed.')
                return

            channel = self.check_ssh_auth(client, address)
            if not channel:
                return

            if not self.check_ssh_command(server, address):
                return

            server.main_loop(channel)
        except Exception:
            self.logger.exception('Caught Exception')
        finally:
            if client:
                client.close()
            return

    def init_log(self):
        logging.StreamHandler = ColorizingStreamHandler
        level = logging.DEBUG
        if not self.config.debug:
            level = logging.INFO
        logging.BASIC_FORMAT = "%(asctime)s [%(name)s] %(message)s"
        logging.basicConfig(level=level)
        if self.config.log_file:
            paramiko.util.log_to_file(self.config.log_file, level=level)

    def init_key(self):
        path = os.path.realpath(self.config.host_key_path)
        self.config.host_key = paramiko.RSAKey(filename=path)
        self.logger.info('Host Key %s' % utils.hex_key(self.config.host_key))

    def check_ssh_auth(self, client, address):
        channel = client.accept(self.config.auth_timeout)
        if channel is None:
            self.logger.info('Auth timeout %s:%d' % address)
            return None
        return channel

    def check_ssh_command(self, server, address):
        if not server.event.wait(self.config.check_timeout):
            self.logger.info('Check timeout %s:%d' % address)
            return False
        return True

    def parse_ssh_command(self, command):
        if not command:
            return [], ''
        # command eg: git-upload-pack 'code.git'
        args = command.split(' ')
        cmd = args[:-1]
        repo = args[-1].strip("'")
        return cmd, repo

    def check_ssh_user(self, name):
        if name == 'git':
            return True
        return False

    def check_ssh_key(self, key):
        # key_b = key.get_base64()
        # check key_b
        if not key:
            return False
        return True

    def check_git_repo(self, repo):
        # 'Error: Repository not found.\n'
        if not repo:
            return False
        return True

    def check_git_command(self, command):
        if not command[0]:
            return False
        if not command[0] in ('git-receive-pack',
                              'git-upload-pack'):
            return False
        if self.config.git_path:
            command[0] = os.path.join(self.config.git_path, command[0])
        return True

    def get_permission(self, cmd):
        if cmd == 'git-receive-pack':
            return 'write'
        if cmd == 'git-upload-pack':
            return 'read'

    # args: path
    def get_repo_path(self, f):
        self._get_repo_path_handler = f
        return f

    # args: ssh_username, key
    def get_user(self, f):
        self._get_user_handler = f
        return f

    # args: user, path, perm
    def has_permission(self, f):
        self._has_permission_handler = f
        return f

    # args: user, path
    def get_environ(self, f):
        self._get_environ_handler = f
        return f


class GSSHServerInterface(paramiko.ServerInterface):

    def __init__(self, app=None):
        self.app = app
        self.event = threading.Event()
        self.ssh_key = None
        self.ssh_username = ''
        self.repo_name = ''
        self.username = ''
        self.command = None
        self.message = ''  # TODO: useless
        self.environ = None

    def get_allowed_auths(self, username):
        return 'publickey'

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_publickey(self, username, key):
        hex_fingerprint = utils.hex_key(key)
        self.app.logger.info('Auth attempt with key: %s' % hex_fingerprint)
        self.ssh_username = username
        if not self.app.check_ssh_user(username):
            return paramiko.AUTH_FAILED
        self.ssh_key = key
        if not self.app.check_ssh_key(key):
            return paramiko.AUTH_FAILED
        if hasattr(self.app, '_get_user_handler'):
            self.username = self.app._get_user_handler(self.ssh_username, self.ssh_key)
            if not self.username:
                return paramiko.AUTH_FAILED
        return paramiko.AUTH_SUCCESSFUL

    # not paramiko method
    def check_error_message(self, channel):
        message = self.message
        if message:
            channel.sendall_stderr(message)
            self.event.set()
            return True
        self.event.set()

    def check_channel_exec_request(self, channel, command):
        self.app.logger.info('Command %s received' % command)
        command, repo = self.app.parse_ssh_command(command)
        self.repo_name = repo

        try:
            if not self.app.check_git_repo(repo):
                return False
            if not self.app.check_git_command(command):
                return False

            if hasattr(self.app, '_has_permission_handler'):
                perm = self.app.get_permission(command[0])
                if not self.app._has_permission_handler(self.username, repo, perm):
                    return False

        except Exception as e:
            self.message = str(e)
            if self.check_error_message(channel):
                return True
            return False

        if hasattr(self.app, '_get_environ_handler'):
            self.environ = self.app._get_environ_handler(self.username, repo)

        if hasattr(self.app, '_get_repo_path_handler'):
            repo = self.app._get_repo_path_handler(repo)
        else:
            repo = os.path.join(self.app.config.project_root, repo)

        command.append(repo)
        self.command = command
        self.event.set()
        return True

    def main_loop(self, channel):
        if not self.command:
            return

        p = subprocess.Popen(self.command,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             close_fds=True,
                             env=self.environ)

        ofd = p.stdout.fileno()
        efd = p.stderr.fileno()

        while True:
            r_ready, w_ready, x_ready = select.select([channel, ofd, efd],
                                                      [],
                                                      [],
                                                      self.app.config.select_timeout)

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
        if not channel.recv(4):
            channel.shutdown(2)
            channel.close()
        self.app.logger.info('Command execute finished')
