########################################################################################################################
# Functions to handle generation of tech support files.
#
#
########################################################################################################################
import os
import re
import sys
import shutil
from src.env_conf import settings
from src.util import LogUtil, HostSession, HostUtil


class TechSupport:

    def __init__(self):
        pass

    def generate_tech_support(self, client, extra_commands=None):
        logger = LogUtil.LogUtil()
        timestamp = re.sub(":", "", LogUtil.LogUtil().get_host_time())
        dirpath = os.path.join(settings.getValue('TECH_SUPPORT_DIR'), f'tech_support_{timestamp}')
        os.makedirs(dirpath)
        filename = os.path.join(dirpath, f'Command_Line_support.txt')
        logger.info('Creating command line support file...')
        try:
            with open(filename, 'w') as f:
                if client.lower() == 'host':
                    target_list = settings.getValue('HOST_DETAILS')
                    for target in target_list:
                        target_client = HostSession.HostSession().connect(target['HOST'], target['USER'], target['PASSWORD'])
                        f.write(f'Host: {target["HOST"]}\n')
                        command_list = settings.getValue('ESXI_COMMANDS')
                        if extra_commands:
                            for x in extra_commands[0].split(','):
                                command_list.append(x)
                        for command in command_list:
                            stdin, stdout, stderr = target_client.exec_command(command)
                            f.write(f'Executed Command: {command}\n')
                            f.write(f'Output: \n{stdout.read().decode()}')
                            errors = stderr.read().decode()
                            if len(errors):
                                f.write(f'Error: \n{errors}')
                        HostSession.HostSession().disconnect(target_client)
            logger.info(f'Command Line support file created: {filename}')


            logger.info('Collecting Net stats....')
            filename = os.path.join(dirpath, f'netstats.log')
            with open(filename, 'w') as f:
                if client.lower() == 'host':
                    target_list = settings.getValue('HOST_DETAILS')
                    for target in target_list:
                        target_client = HostSession.HostSession().connect(target['HOST'], target['USER'], target['PASSWORD'])
                        f.write(f'Host: {target["HOST"]}\n')
                        command = f'net-stats -i 20 -t WicQv -A'
                        stdin, stdout, stderr = target_client.exec_command(command)
                        f.write(stdout.read().decode())
                        errors = stderr.read().decode()
                        if len(errors):
                            f.write(f'Error: \n{errors}')
                        HostSession.HostSession().disconnect(target_client)
            logger.info('Collecting Sched stats...')
            filename = os.path.join(dirpath, f'schedstats.log')
            with open(filename, 'w') as f:
                if client.lower() == 'host':
                    target_list = settings.getValue('HOST_DETAILS')
                    for target in target_list:
                        target_client = HostSession.HostSession().connect(target['HOST'], target['USER'], target['PASSWORD'])
                        f.write(f'Host: {target["HOST"]}\n')
                        command = f'sched-stats -t pcpu-stats'
                        stdin, stdout, stderr = target_client.exec_command(command)
                        f.write(stdout.read().decode())
                        errors = stderr.read().decode()
                        if len(errors):
                            f.write(f'Error: \n{errors}')
                        logger.info('Collecting environment details...')
                        filename = os.path.join(dirpath, f'env_details.log')
                        HostUtil.HostUtil().list_env_details(target_client)
                        HostSession.HostSession().disconnect(target_client)


            if sys.platform.startswith('win'):
                filename = shutil.make_archive(dirpath, 'zip', settings.getValue('TECH_SUPPORT_DIR'))
                logger.info(f'Compressed Tech support file created {filename}')
                #shutil.rmtree(dirpath)
            elif sys.platform.startswith('lin'):
                filename = shutil.make_archive(dirpath, 'tar', settings.getValue('TECH_SUPPORT_DIR'))
                logger.info(f'Compressed Tech support file created {filename}')
                shutil.rmtree(dirpath)
        except FileNotFoundError as fex:
            print(f'FileNotFoundError: {fex.filename} {fex.args}\nCheck TECH_SUPPORT_DIR value in common.json')
        except NotImplementedError as ex:
            print(f'NotImplementedError: {ex.args}')
        except Exception as ex:
            print(f'Exception: {ex.args}')