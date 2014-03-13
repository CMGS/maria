#coding:utf-8

from base64 import b64decode, b64encode
from urllib import quote, unquote


class DecodeError(Exception):
        pass


def encode(username, password):
    return 'Basic ' + b64encode('%s:%s' % (quote(username), quote(password)))


def decode(basic_auth):
    split = basic_auth.strip().split(' ')

    if len(split) == 1:
        try:
            username, password = b64decode(split[0]).split(':')
        except:
            raise DecodeError
    elif len(split) == 2:
        if split[0].strip().lower() == 'basic':
            try:
                username, password = b64decode(split[1]).split(':')
            except:
                raise DecodeError
        else:
            raise DecodeError
    else:
        raise DecodeError
    return unquote(username), unquote(password)

