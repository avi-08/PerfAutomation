"""
    This module deals with host configurations, verification and other controls
"""

from __future__ import print_function

__author__ = 'Avi Sharma'

import json
import sys

from src.util import HostSession

class HostConfig:

    def __init__(self):
        pass

    def config_nic_driver(self, session, vmnic):
        if not self.verfiy_nic_driver(session, vmnic):
            pass


    def verfiy_nic_driver(self, session, vmnic):
        stdin, stdout, stderr = session.exec_command(f'vsish -ep get /net/pNics/{vmnic}/properties | grep "module"')
        module = stdout.readline()[:-2].split(':')[1][1:].strip('"')
        return True if(module == 'ixgben') else False

    def verify_rss(self, session):
        stdin, stdout, stderr = session.exec_command('esxcli system module parameters list --module ixgben')
        rss = stdout.read().con


    def verify_nic_ring_size(self, session, vmnic):
        stdin, stdout, stderr = session.exec_command(f'vsish -e get /net/pNics/{vmnic}/stats')

    def verify_queue_pairing(self, session):
        stdin, stdout, stderr = session.exec_command('vsish -e get /config/Net/intOpts/NetNetqRxQueueFeatPairEnable')
