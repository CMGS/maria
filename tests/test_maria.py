# -*- coding: utf-8 -*-

import time
import subprocess
import maria
import unittest


class TestMaria(unittest.TestCase):
    
    def setUp(self):
        self.git_bare = '~/temp_bare.git'
        self.git_repo = '~/temp_repo.git'

        cmd = './git_init_bare.sh ' + self.git_bare
        status = subprocess.call(cmd, shell=True)
        assert status != 1, 'temp git_bare path existed!'
        assert status == 0, 'temp git_bare init error!'
        
        args = ['maria',
                '-k', '../examples/host.key',
                '-b', '127.0.0.1:2200']
        self.p = subprocess.Popen(args)
        time.sleep(1)

    def tearDown(self):
        self.p.terminate()
        cmd = 'rm %s %s -rf' % (self.git_bare, self.git_repo)
        status = subprocess.call(cmd, shell=True)
        assert status == 0, 'delete temp git repos error!'

    def test_clone(self):
        cmd = 'git clone git@127.0.0.1:%s %s' \
               % (self.git_bare, self.git_repo)
        pclone = subprocess.Popen(cmd, shell=True)
        assert pclone.wait() == 0, 'git clone error!'

    def test_push(self):
        cmd = './git_init_repo.sh ' \
              + self.git_repo + ' ' + self.git_bare
        ppush = subprocess.Popen(cmd, shell=True)
        status = ppush.wait()
        assert status != 1, 'temp git_bare path does not exist!'
        assert status != 2, 'temp git_repo path existed!'
        assert status == 0, 'git push error!'


if __name__ == "__main__":
    unittest.main()
