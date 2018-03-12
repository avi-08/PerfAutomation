# This file contains the main utility that is used to run the framework
# based on user inputs from the command line.

from __future__ import print_function

import sys
import argparse
import json

from src.util import HostSession


def parse_args():
    """
    Function to parse command line arguments
    :return: Dictionary containing command line args
    """
    pass

def main():
    """
    Main Script
    """
    parse_args()
    hosts = json.load(open(r'env_conf\host.json'))
    for host in hosts['HOST_DETAILS']:
        sess = HostSession.HostSession().connect(host['HOST'], host['USER'], host['PASSWORD'], False)
        if sess:
            stdin, stdout, stderr = sess.exec_command('vsish -ep get /net/pNics/vmnic0/properties | grep "module"')
            print(stdout.readline()[:-2].split(':')[1][1:].strip('"'))
            print("{0}".format(True if [x.strip().strip('"') for x in stdout.readline().strip()[:-1].split(':')].__contains__('ixgben') else False))
            #for line in stdout:
             #   print(line.strip('\n'))
            HostSession.HostSession().disconnect(sess)
        else:
            print("Unable to connect.")


# if __name__ == 'main':
main()