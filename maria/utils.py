# -*- coding: utf-8 -*-

from paramiko.util import hexify


def hex_key(key):
    return hexify(key.get_fingerprint())
