########################################################################################################################
# Functions to handle generation of tech support files.
#
#
########################################################################################################################
import os
import re
import time
from src.env_conf import settings
from src.util import LogUtil, HostSession


class TechSupport:

    def __init__(self):
        pass

    def generate_tech_support(self, target):
        logger = LogUtil.LogUtil()
        timestamp = re.sub(":", "", LogUtil.LogUtil().get_host_time())
        filename = os.path.join(settings.getValue('TECH_SUPPORT_DIR'), f'Command_Line_support_{timestamp}.txt')
        logger.info('Creating command line support file...')
        try:
            with open(filename, 'w') as f:
                if target.lower() == 'host':
                    target_list = settings.getValue('HOST_DETAILS')
                    for target in target_list:
                        target_client = HostSession.HostSession().connect(target['HOST'], target['USER'], target['PASSWORD'])
                        command_list = settings.getValue('ESXI_COMMANDS')
                        for command in command_list:
                            stdin, stdout, stderr = target_client.exec_command(command)
                            f.write(f'Executed Command: {command}')
                            f.write(f'Output: \n{stdout.read().decode()}')
                            errors = stderr.read().decode()
                            if len(errors):
                                f.write(f'Error: \n{errors}')
                        HostSession.HostSession().disconnect(target_client)
            logger.info(f'Command Line support file created: {filename}')
        except FileNotFoundError as fex:
            print(f'FileNotFoundError: {fex.filename} {fex.args}\nCheck TECH_SUPPORT_DIR value in common.json')
        except Exception as ex:
            print(f'Exception: {ex.args}')