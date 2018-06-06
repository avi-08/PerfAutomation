import os
import sys
import logging

from src.env_conf import settings

_LOGGER = logging.getLogger(__name__)


class VMDeploy:
    def __init__(self):
        pass

    def deploy_vm(self, vmname='TEST'):
        print(f'''\n{'-'*60}\n\t\t\tInitiating VM Deployment\n{'-'*60}\n''')
        vms = settings.getValue('VM_DETAILS')
        for vm in vms:
            vm_name = vm['VM_NAME']
            datastore = vm['DATASTORE']
            networks = vm['NETWORKS'].split(',')
            ostype = sys.platform
            if ostype.startswith('win32'):
                folder_name = 'win32'
                dir_name = settings.getValue('OVF_TOOL_DIR')
                tool_path = os.path.join(dir_name, folder_name, 'ovftool.exe')
                _LOGGER.debug(f'opening {tool_path} ')
                for hosts in settings.getValue('HOST_DETAILS'):
                    host = hosts['HOST']
                    uname = hosts['USER']
                    password = hosts['PASSWORD']
                    # cmd = [tool_path, '--acceptAllEulas', '--powerOn', f'--datastore="{datastore}"', f'--name="{vm_name}"', f'"--net:PG1={networks[0]}"', f'"--net:PG2={networks[1]}"', '"C:\\Users\\somanathr\\Desktop\\dpdk.ova"', f'"vi://{uname}:{password}@{host}"']
                    cmd = [tool_path, '--acceptAllEulas', '--powerOn', f'--datastore="{datastore}"', f'--name="{vm_name}"', f'--network="{networks[0]}"', '"C:\\Users\\somanathr\\Desktop\\dpdk.ova"', f'"vi://{uname}:{password}@{host}"']
                    _LOGGER.debug(f'Executing command: {" ".join(cmd)}')
                    _LOGGER.info('Deploying vm. This might take a few minutes...')
                    os.system(" ".join(cmd))
                return True
            elif ostype.startswith('linux'):
                folder_name = 'lin64'
                dir_name = settings.getValue('OVF_TOOL_DIR')
                tool_path = os.path.join(dir_name, folder_name, 'ovftool.exe')
                _LOGGER.debug(f'opening {tool_path}')
                for hosts in settings.getValue('HOST_DETAILS'):
                    host = hosts['HOST']
                    uname = hosts['USER']
                    password = hosts['PASSWORD']
                    cmd = [tool_path, '--acceptAllEulas', '--powerOn', f'--datastore="{datastore}"', f'--name="{vm_name}"', f'"--net:PG1={networks[0]}"', f'"--net:PG2={networks[1]}"', '"C:\\Users\\somanathr\\Desktop\\dpdk.ova"', f'"vi://{uname}:{password}@{host}"']
                    _LOGGER.debug(f'Executing command: {" ".join(cmd)}')
                    _LOGGER.info('Deploying vm. This might take a few minutes...')
                    os.system(" ".join(cmd))
                return True
            # TODO for mac deployment
            return False
