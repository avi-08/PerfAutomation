# This file contains the main utility that is used to run the framework
# based on user inputs from the command line.

from __future__ import print_function

import sys
import logging
import os
import argparse
import json

from src.util import HostSession, LogUtil
from src.env_conf import settings
from src.tests import host_config


_CURR_DIR = os.path.dirname(os.path.realpath(__file__))

LOGGING_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

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
                        help='list effective settings configuration and exit')
    args = vars(parser.parse_args())

    return args


def handle_list_options(args):
    """ Process --list cli arguments if needed

    :param args: A dictionary with all CLI arguments
    """
    if args['list_settings']:
        print(str(settings))
        sys.exit(0)

    if args['list_default_settings']:
        print(str(settings))
        sys.exit(0)


def configure_logging(level):
    """Configure logging.
    """
    log_file_default = os.path.join(settings.getValue('LOG_DIR'), settings.getValue('LOG_FILE_DEFAULT'))

    global _LOGGER
    _LOGGER.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s [%(levelname)-8s]: (%(name)s) - %(message)s', datefmt='%Y-%m-%dT%H:%M:%SZ')

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(LOGGING_LEVELS[level])
    stream_handler.setFormatter(formatter)
    _LOGGER.addHandler(stream_handler)

    file_handler = logging.FileHandler(filename=log_file_default)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    _LOGGER.addHandler(file_handler)


def main():
    """
    Main Script
    """
    args = parse_args()

    # configure settings

    settings.load_from_dir(os.path.join(_CURR_DIR, 'env_conf'))

    # load command line parameters first in case there are settings files
    # to be used
    settings.load_from_dict(args)

    # reload command line parameters since these should take higher priority
    # than both a settings file and environment variables
    settings.load_from_dict(args)

    # if required, handle list-* operations
    handle_list_options(args)

    if(args['verbose']):
        configure_logging('debug')
    else:
        configure_logging(settings.getValue('VERBOSITY'))

    host_config.host_config(settings)
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

#if __name__ == 'main':
main()