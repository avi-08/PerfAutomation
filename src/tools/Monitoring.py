import json
import yaml
from src.util import HostSession

result_data = {}

"""
    functions to monitoring 
"""

def monitorNetStats(client, duration, filename):
    stdin, stdout, stderr = client.exec_command(f'net-stats -i {duration} -t WicQv -A > {filename}')
    return stdout.read().decode()


def monitorSchedStats(client, filename):
    stdin, stdout, stderr = client.exec_command(f'sched-stats -t pcpu-stats > {filename}')
    return stdout.read().decode()


def startMonitoring(client):
    stdin, stdout, stderr = client.exec_command(f'sudo python ')
    return stdout.read().decode()


def getNetStats(client, filename):
    stdin, stdout, stderr = client.exec_command(f'cat {filename}')
    return stdout.read().decode()


def getSchedStats(client, filename):
    stdin, stdout, stderr = client.exec_command(f'cat {filename}')
    return stdout.read().decode()


def getTraffic(client, filename):
    stdin, stdout, stderr = client.exec_command(f'cat /home/trex/Results/{filename}')
    return stdout.read().decode()
