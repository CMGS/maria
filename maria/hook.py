#!/usr/local/bin/python2.7
#coding:utf-8

import sys
import logging
from maria.config import config

logger = logging.getLogger(__name__)


# TODO get repo path
def parser_command(command):
    if not command:
        return None
    repo = 'test.git'
    command = command.split(' ')
    command[-1] = command[-1].strip("'")
    return command, repo


# TODO define by yourself
def check_command(command):
    if not command or not command in ('git-receive-pack', 'git-upload-pack'):
        return False
    return True


# TODO get from mysql
def check_store_key(key):
    data = 'AAAAB3NzaC1yc2EAAAADAQABAAABAQDJOtsej4dNSKTdMBnD8v6L0lZ1Tk+WTMlx' \
        'sFf2+pvkdoAu3EB3RZ/frpyV6//bJNTDysyvwgOvANT/K8u5fzrOI2qDZqVU7dtDSwU' \
        'edM3YSWcSjjuUiec7uNZeimqhEwzYGDcUSSXe7GNH9YsVZuoWEf1du6OLtuXi7iJY4H' \
        'abU0N49zorXtxmlXcPeGPuJwCiEu8DG/uKQeruI2eQS9zMhy73Jx2O3ii3PMikZt3g/' \
        'RvxzqIlst7a4fEotcYENtsJF1ZrEm7B3qOBZ+k5N8D3CkDiHPmHwXyMRYIQJnyZp2y0' \
        '3+1nXT16h75cer/7MZMm+AfWSATdp09/meBt6swD'
    key_b = key.get_base64()
    if data == key_b:
        return True
    return False


# TODO get from mysql
def check_username(username):
    if username == 'git':
        return True
    return False


# TODO check repo and user permits
def check_permits(key, repo):
    if not key or not repo:
        return False
    return True


if config.hook:
    try:
        execfile(config.hook)
    except Exception:
        logger.exception('Load hook file failed')
        sys.exit(1)
