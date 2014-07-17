# -*- coding: utf-8 -*-

import os
import shlex
import select
import subprocess
from contextlib import contextmanager


@contextmanager
def chdir(dir):
    cwd = os.getcwd()
    os.chdir(dir)
    yield
    os.chdir(cwd)


def callback(p):
    ofd = p.stdout.fileno()
    efd = p.stderr.fileno()
    while True:
        r_ready, w_ready, x_ready = select.select([ofd, efd], [], [], 30)

        if ofd in r_ready:
            data = os.read(ofd, 8192)
            if not data:
                break
            yield data

        if efd in r_ready:
            data = os.read(efd, 8192)
            yield data
            break

    output, err = p.communicate()
    if output:
        yield output
        if err:
            yield err


class Git(object):

    def __init__(self, dir=''):
        self.git_path = os.path.join(dir, 'git')

    @property
    def command_options(self):
        return {"advertise_refs": "--advertise-refs"}

    def command(self, cmd, opts={}, env=None):
        cmd = "%s %s %s" % (self.git_path, cmd, " ".join(opts.get("args")))
        cmd = shlex.split(cmd)
        p = subprocess.Popen(cmd,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             close_fds=True,
                             env=env)
        data = opts.get("msg")
        if data:
            p.stdin.write(data)
        return callback(p)

    def upload_pack(self, repository_path, opts=None, env=None):
        cmd = "upload-pack"
        args = []
        if not opts:
            opts = {}
        for k, v in opts.iteritems():
            if k in self.command_options:
                args.append(self.command_options.get(k))
        args.append("--stateless-rpc")
        args.append(repository_path)
        opts["args"] = args
        return self.command(cmd, opts, env=env)

    def receive_pack(self, repository_path, opts=None, env=None):
        cmd = "receive-pack"
        args = []
        if not opts:
            opts = {}
        for k, v in opts.iteritems():
            if k in self.command_options:
                args.append(self.command_options.get(k))
        args.append("--stateless-rpc")
        args.append(repository_path)
        opts["args"] = args
        return self.command(cmd, opts, env=env)

    def update_server_info(self, repository_path, opts=None, env=None):
        cmd = "update-server-info"
        args = []
        if not opts:
            opts = {}
        for k, v in opts.iteritems():
            if k in self.command_options:
                args.append(self.command_options.get(k))
        opts["args"] = args
        with chdir(repository_path):
            self.command(cmd, opts, env=env)

    def get_config_setting(self, repository_path, key):
        # TODO: user pygit2 or ellen
        path = self.get_config_location(repository_path)
        result = self.command("config", {"args": ["-f %s" % path, key]})
        if result:
            return result.strip('\n').strip('\r')
        return result

    def get_config_location(self, repository_path):
        non_bare = os.path.join(repository_path, ".git")
        if os.path.exists(non_bare):
            non_bare_config = os.path.join(non_bare, "config")
            return non_bare_config if os.path.exists(non_bare_config) else None
        else:
            bare_config = os.path.join(repository_path, "config")
            return bare_config if os.path.exists(bare_config) else None
