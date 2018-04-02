# This file contains the  that is used to run the framework
# based on user inputs from the command line.

from __future__ import print_function

import sys
import logging
import os

from src.core.traffic_generator import Trex
from src.env_conf import settings
from src.util import LogUtil, ParserUtil
from src.usecases import host_config
from src.usecases import vm_deploy
from src.usecases import vm_config


def main():
    """
    Main Script that controls the framework execution; This is the starting point of the framework.
    """
    args = ParserUtil.Parser().parse_cmd_args()
    logger = logging.getLogger()


    print(host_config.__doc__)
    # configure settings
    print("Loading configuration file values in current session...")
    settings.load_from_dir(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'env_conf'))
    print("Done.")

    # load command line parameters first in case there are settings files
    # to be used
    settings.load_from_dict(args)

    # reload command line parameters since these should take higher priority
    # than both a settings file and environment variables
    settings.load_from_dict(args)

    # if required, handle list-* operations
    print("Scanning for command line arguments...")
    ParserUtil.Parser().process_cmd_switches(args)
    print("Done.")

    if(args['verbose']):
        LogUtil.LogUtil().configure_logging(logger, 'debug')
    else:
        LogUtil.LogUtil().configure_logging(logger, settings.getValue('VERBOSITY'))

    # Check if there are any specific operations to perform, otherwise continue the normal framework execution.
    if args['perform']:
        # Apply host optimizations
        if args['perform'] == 'host_config':
            logger.info('Initiating host optimizations.')
            if host_config.host_config() == False:
                logger.error('Unable to configure host optimizations.')
                sys.exit(0)
            else:
                logger.info('Host optimizations successful.')

        # Deploy vnfs based on the vnf.json file
        if args['perform'] == 'vm_deploy':
            logger.info('Initiating VM deployment on host')
            if vm_deploy.VMDeploy().deploy_vm() == False:
                logger.error('Unable to deploy VM.')
                sys.exit(0)
            else:
                logger.info('VM Deployment complete')

        # Apply VM optimizations
        if args['perform'] == 'vm_config':
            logger.info('Initiating VM optimization')
            vm_config.vm_config()
            logger.info('VM optimization complete')

        # Run traffic from traffic generator
        if args['perform'] == 'run_traffic':
            trex = Trex.Trex()
            trex.trafficGen()
    else:
        logger.info('Initiating host optimizations.')
        if host_config.host_config() == False:
            logger.error('Unable to configure host optimizations.')
            sys.exit(0)
        else:
            logger.info('Host optimizations successful.')
        logger.info('Initiating VM deployment on host')
        if vm_deploy.VMDeploy().deploy_vm() == False:
            logger.error('Unable to deploy VM.')
            sys.exit(0)
        else:
            logger.info('VM Deployment complete')
        logger.info('Initiating VM optimization')
        vm_config.vm_config()
        logger.info('VM optimization complete')
        trex = Trex.Trex()
        trex.trafficGen()


main()
