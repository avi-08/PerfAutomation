import re
import logging
import json, openpyxl
import sys
from prettytable import PrettyTable
from openpyxl import Workbook

_LOGGER = logging.getLogger(__name__)


class Monitor:
    def __init__(self):
        pass

    def monitor_netstats(self, client, duration=10, filename='server_schedstats.logs'):
        stdin, stdout, stderr = client.exec_command(f'net-stats -i {duration} -t WicQv -A > {filename}')
        logging.debug(f'Executing command : net-stats -i {duration} -t WicQv -A > {filename}')
        return stdout.read().decode()

    def monitor_schedstats(self,client, filename='server_netstats.logs'):
        stdin, stdout, stderr = client.exec_command(f'sched-stats -t pcpu-stats > {filename}')
        logging.debug(f'Executing command : sched-stats -t pcpu-stats > {filename}')
        return stdout.read().decode()

    def start_monitoring(self,client):
        stdin, stdout, stderr = client.exec_command(f'sudo python ')
        return stdout.read().decode()

    def get_netstats(self, client, filename):
        stdin, stdout, stderr = client.exec_command(f'cat {filename}')
        logging.debug(f'Excuting command : cat {filename}')
        return stdout.read().decode()

    def get_schedstats(self,client, filename):
        stdin, stdout, stderr = client.exec_command(f'cat {filename}')
        logging.debug(f'Excuting command : cat {filename}')
        return stdout.read().decode()

    def get_traffic(self,client, filename):
        stdin, stdout, stderr = client.exec_command(f'cat /home/trex/Results/{filename}')
        logging.debug(f'Excuting command : cat /home/trex/Results/{filename}')
        return stdout.read().decode()

    def ping(self, client, dest):
        stdin, stdout, stderr = client.exec_command(f'ping {dest} -c 4')
        logging.info(f'ping to {dest}')
        logging.debug(f'Excuting command : ping {dest} -c 4 ')
        a = stdout.read().decode()
        a = a.split('\n\n')[1].split('\n')[1].split(',')
        packet_loss = re.search('(.*?%)', a[2]).group().strip().strip('%')
        if int(packet_loss) == 0:
            return True
        else:
            return False
    def start_trex(self,client ):
        stdin, stdout, stderr = client.exec_command(f'./home/trex/t-rex-64 -i -c 1')
        a = stdout.read().decode()
        if a:
            return True
        else:
            return False

    def start_dpdk(self, client):
        stdin, stdout, stderr = client.exec_command(f'./startL3fwd.sh')
        a = stdout.read().decode()
        if a:
            return True
        else:
            return False
