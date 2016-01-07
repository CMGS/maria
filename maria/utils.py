# -*- coding: utf-8 -*-

from binascii import hexlify


def hex_key(key):
    return hexlify(key.get_fingerprint()).upper()

