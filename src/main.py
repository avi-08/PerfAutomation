# This file contains the main utility that is used to run the framework
# based on user inputs from the command line.

from __future__ import print_function

import sys
import argparse
import json

#from src.util import HostSession, Logger
#from src.core import Host


def parse_args():
    parser = argparse.ArgumentParser()
    parser.parse_args()
    pass

def main():
    """
    Main Script
    """
    args = parse_args()
    """
    file = open('env_conf\host.json','r')
    jsonData = file.read()
    data = json.loads(jsonData)
    print('Host: {}\nUserName: {}\nPassword: {}'.format(data['host_credentials'][0]['host'],data['host_credentials'][0]['user'], data['host_credentials'][0]['password']))
    """

    sess = HostSession.HostSession().connect('10.107.182.18', 'root', 'ca$hc0w', False)
    #sess = HostSession.HostSession().connect(data['host_credentials'][0]['host'], data['host_credentials'][0]['user'], data['host_credentials'][0]['password'] , False)
    if sess:
        stdin, stdout, stderr = sess.exec_command('esxcli system version get')
        for line in stdout:
            print(line.strip('\n'))
        HostSession.HostSession().disconnect(sess)
    else:
        print("Unable to connect.")


# if __name__ == 'main':
main()
