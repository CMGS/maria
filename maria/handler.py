#!/usr/local/bin/python2.7
#coding:utf-8

import logging

import paramiko

from maria.config import config

logger = logging.getLogger(__name__)

def handle(socket, address):
    client = None
    try:
        client = paramiko.Transport(socket)
        try:
            client.load_server_moduli()
        except Exception:
            logger.exception('Failed to load moduli -- gex will be unsupported.')
            raise

        client.add_server_key(config.host_key)
        server = config.worker()
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
    channel = client.accept(config.auth_timeout)
    if channel is None:
        logger.info('Auth timeout %s:%d' % address)
        return None
    return channel

def check_command(server, address):
    if not server.event.wait(config.check_timeout):
        logger.info('Check timeout %s:%d' % address)
        return False
    return True

