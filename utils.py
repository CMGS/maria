#!/usr/local/bin/python2.7
#coding:utf-8

import base64
import paramiko
from binascii import hexlify

def parser_command(command):
    if not command:
        return None
    #TODO get repo path
    repo = 'test.git'
    command = command.split(' ')
    command[-1] = command[-1].strip("'")
    return command, repo

def check_command(command):
    if not command or not command in ('git-receive-pack', 'git-upload-pack'):
        return False
    return True

# TODO get from mysql
def check_store_key(hex_fingerprint):
    data = 'AAAAB3NzaC1yc2EAAAADAQABAAABAQDJOtsej4dNSKTdMBnD8v6L0lZ1Tk+WTMlxsFf2+pvkdoAu3EB3RZ/frpyV6//bJNTDysyvwgOvANT/K8u5fzrOI2qDZqVU7dtDSwUedM3YSWcSjjuUiec7uNZeimqhEwzYGDcUSSXe7GNH9YsVZuoWEf1du6OLtuXi7iJY4HabU0N49zorXtxmlXcPeGPuJwCiEu8DG/uKQeruI2eQS9zMhy73Jx2O3ii3PMikZt3g/RvxzqIlst7a4fEotcYENtsJF1ZrEm7B3qOBZ+k5N8D3CkDiHPmHwXyMRYIQJnyZp2y03+1nXT16h75cer/7MZMm+AfWSATdp09/meBt6swD'
    key = paramiko.RSAKey(data=base64.decodestring(data))
    if hex_key(key)  == hex_fingerprint:
        return True
    return False

# TODO check repo and user permits
def check_permits(hex_fingerprint, repo):
    if not hex_fingerprint or not repo:
        return False
    return True

def hex_key(key):
    return hexlify(key.get_fingerprint())

