# -*- coding: utf-8 -*-

import os
import time
import subprocess
import maria


class TestMaria():
    
    def setUp(self):
        self.git_bare = '~/temp_bare.git'
        self.git_repo = '~/temp_repo.git'

        os.system('mkdir %s; \
                   cd %s; \
                   git init --bare' %
                   (self.git_bare, self.git_bare))

        args = ['maria',
                '-k', '../examples/host.key',
                '-b', '127.0.0.1:2200']
        self.p = subprocess.Popen(args)
        time.sleep(1)

    def tearDown(self):
        self.p.terminate()
        os.system('rm %s %s -rf' % (self.git_bare, self.git_repo))

    def test_clone(self):
        cmd = 'git clone git@127.0.0.1:%s %s' % (self.git_bare, self.git_repo)
        pclone=subprocess.Popen(cmd, shell=True)
        assert pclone.wait() == 0

    def test_push(self):
        cmd = 'mkdir %s; \
               cd %s; \
               git init;\
               touch test.c; \
               git add test.c; \
               git commit -m "Add test.c"; \
               git remote add origin git@127.0.0.1:%s; \
               git push origin master' \
               % (self.git_repo, self.git_repo, self.git_bare)
        ppush=subprocess.Popen(cmd, shell=True)
        assert ppush.wait() == 0

