#!/usr/local/bin/python2.7
#coding:utf-8

from maria.gssh import GSSHInterface

DATA = 'AAAAB3NzaC1yc2EAAAADAQABAAABAQDJOtsej4dNSKTdMBnD8v6L0lZ1Tk+WTMlx' \
    'sFf2+pvkdoAu3EB3RZ/frpyV6//bJNTDysyvwgOvANT/K8u5fzrOI2qDZqVU7dtDSwU' \
    'edM3YSWcSjjuUiec7uNZeimqhEwzYGDcUSSXe7GNH9YsVZuoWEf1du6OLtuXi7iJY4H' \
    'abU0N49zorXtxmlXcPeGPuJwCiEu8DG/uKQeruI2eQS9zMhy73Jx2O3ii3PMikZt3g/' \
    'RvxzqIlst7a4fEotcYENtsJF1ZrEm7B3qOBZ+k5N8D3CkDiHPmHwXyMRYIQJnyZp2y0' \
    '3+1nXT16h75cer/7MZMm+AfWSATdp09/meBt6swD'


class NGSSHInterface(GSSHInterface):

    def check_key(self, key):
        self.key = key
        key_b = key.get_base64()
        return DATA == key_b

