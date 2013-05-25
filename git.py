#!/usr/local/bin/python2.7
#coding:utf-8

import logging
from binascii import hexlify

import config
import paramiko

from gerver import Gerver

logger = logging.getLogger(__name__)

logger.info('Host Key %s' % hexlify(config.HOST_KEY.get_fingerprint()))

def handle(socket, address):
    client = None
    try:
        client = paramiko.Transport(socket)
        try:
            client.load_server_moduli()
        except Exception:
            logger.exception('Failed to load moduli -- gex will be unsupported.')
            raise

        client.add_server_key(config.HOST_KEY)
        server = Gerver()
        try:
            client.start_server(server=server)
        except paramiko.SSHException:
            logger.exception('SSH negotiation failed.')
            return

        channel = auth(client, address)
        if not channel:
            return

        if not check_command(server, address):
            return

        server.main_loop(channel)
    except Exception:
        logger.exception('Caught Exception')
    finally:
        if client:
            client.close()
        return

def auth(client, address):
    channel = client.accept(config.AUTH_TIMEOUT)
    if channel is None:
        logger.info('Auth timeout %s' % address)
        return None
    return channel

def check_command(server, address):
    if not server.event.wait(config.CHECK_TIMEOUT):
        logger.info('Check timeout %s' % address)
        return False
    return True

