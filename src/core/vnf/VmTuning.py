"""
    This module deals with VM configurations, verification and other controls
"""
from __future__ import print_function

__author__= 'Somanath'

class VMConfig :

    def __init__(self):
        pass

    def verify_latencySensitivity(self, session):
        """
        Verify the Latency Sensitivity feature

        :param session:
        :return:
        """
        stdin, stdout, stderr = session.exec_command('net-stats -i 60 -t WicQv -A > netstats')
        result = stdout.readline()
        # print(result)

