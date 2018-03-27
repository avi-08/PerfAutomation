import os
import sys
import logging

from src.env_conf import settings

_LOGGER = logging.getLogger(__name__)


def deploy_vm():
    vm_name = settings.getValue('VM_NAME')
    datastore = settings.getValue('DATASTORE')
    networks = settings.getValue('NETWORKS').split(',')
    ostype = sys.platform
    if ostype.startswith('win32'):
        folder_name = 'win32'
        dir_name = 'C:\\Users\\savi\\Desktop\\ovftool'
        tool_path = os.path.join(dir_name, folder_name, 'ovftool.exe')
        for hosts in settings.getValue('HOST_DETAILS'):
            host = hosts['HOST']
            uname = hosts['USER']
            password = hosts['PASSWORD']
            cmd = [tool_path, '--acceptAllEulas', '--powerOn', '--machineOutput', f'--datastore="{datastore}"', f'--name="{vm_name}"', f'"--net:PG1={networks[0]}"', f'"--net:PG2={networks[1]}"', '"C:\\Users\\savi\\Desktop\\dpdk.ova"', f'"vi://{uname}:{password}@{host}"']
            _LOGGER.debug(f'Running command: {" ".join(cmd)}')
            os.system(" ".join(cmd))
