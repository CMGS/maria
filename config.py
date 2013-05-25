#!/usr/local/bin/python2.7
#coding:utf-8

import paramiko

DEBUG = True

SSH_LOG_FILE_PATH = '/tmp/maria.log'
paramiko.util.log_to_file(SSH_LOG_FILE_PATH)

_HOST_KEY = 'host.key'
HOST_KEY = paramiko.RSAKey(filename=_HOST_KEY)

AUTH_TIMEOUT = 20
CHECK_TIMEOUT = 10
SELECT_TIMEOUT = 10
