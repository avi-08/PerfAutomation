# This file contains the main utility that is used to run the framework
# based on user inputs from the command line.

from __future__ import print_function

import sys
import logging
import os
import argparse
import re

from src.util import HostSession, LogUtil
from src.env_conf import settings
from src.core.traffic_generator import Trex
from src.usecases import host_config
from src.usecases import vm_deploy
from src.usecases import vm_config


_CURR_DIR = os.path.dirname(os.path.realpath(__file__))
_LOGGER = logging.getLogger()


def parse_args():
    """
    Function to parse command line arguments
    :return: Dictionary containing command line args
    """
    parser = argparse.ArgumentParser(prog=__file__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', '--list-settings', action='store_true',
                        help='list effective settings configuration and exit')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Set verbosity level for console output as DEBUG; default is INFO')
    parser.add_argument('-l', '--list-testcases', action='store_true', help='get a list of testcases' )
    parser.add_argument('-g', '--get-testcase', action="store", type=str,
                        help='get details of specified testcase', metavar=('TESTCASE',))
    parser.add_argument('-t', '--testcase', action="store", type=str, metavar=('TESTCASE',),
                        help='Run test for given test case'
                             '; a comma seperated list for running multiple tests')
    parser.add_argument('--list-operations', action='store_true', help='get a list of all available operations')
    parser.add_argument('--perform', action='store', type=str, choices=['host_config', 'vm_deploy', 'vm_config', 'traffic_config', 'run_traffic', 'monitoring', 'reporting', 'cleanup'],
                        help='Perform given operation; provide ', metavar=('OPERATION',))
    args = vars(parser.parse_args())

    return args


def get_usecases():
    pass


def handle_list_options(args):
    """ Process --list cli arguments if needed

    :param args: A dictionary with all CLI arguments
    """
    if args['list_settings']:
        print(str(settings))
        sys.exit(0)
    if args['list_testcases']:
        if len(settings.getValue('TESTCASES')) > 0:
            print(settings.getValue('TESTCASES'))
        else:
            print("No defined testcases found")
        sys.exit(0)
    if args['get_testcase']:
        print(args['get_testcase'])
        if settings.getValue('TESTCASES')[0]['NAME'] == [args['get_testcase']]:
            print(settings.getValue('TESTCASES')[args['get_testcase']])
        else:
            print("No defined testcase found by that name.")
        sys.exit(0)

    if args['list_operations']:
        get_usecases()
        sys.exit(0)


def main():
    """
    Main Script
    """
    args = parse_args()

    # configure settings
    print("Loading configuration file values in current session...")
    settings.load_from_dir(os.path.join(_CURR_DIR, 'env_conf'))
    print("Done.")

    # load command line parameters first in case there are settings files
    # to be used
    settings.load_from_dict(args)

    # reload command line parameters since these should take higher priority
    # than both a settings file and environment variables
    settings.load_from_dict(args)

    # if required, handle list-* operations
    print("Scanning for command line arguments...")
    handle_list_options(args)
    print("Done.")

    if(args['verbose']):
        LogUtil.LogUtil().configure_logging(_LOGGER, 'debug')
    else:
        LogUtil.LogUtil().configure_logging(_LOGGER, settings.getValue('VERBOSITY'))

    if args['perform'] == 'host_config':
        _LOGGER.info('Initiating host optimizations.')
        if host_config.host_config() == False:
            _LOGGER.error('Unable to configure host optimizations.')
            sys.exit(0)
        else:
            _LOGGER.info('Host optimizations successful.')

    # Deploy vnfs based on the vnf.json file
    if args['perform'] == 'vm_deploy':
        _LOGGER.info('Initiating VM deployment on host')
        if vm_deploy.VMDeploy().deploy_vm() == False:
            _LOGGER.error('Unable to deploy VM.')
            sys.exit(0)
        else:
            _LOGGER.info('VM Deployment complete')

    if args['perform'] == 'vm_config':
        _LOGGER.info('Initiating VM optimization')
        vm_config.vm_config()
        _LOGGER.info('VM optimization complete')

    if args['perform'] == 'run_traffic':
        trex = Trex.Trex()
        trex.trafficGen()
    """
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
            _LOGGER.error("Unable to connect.")
    """


main()