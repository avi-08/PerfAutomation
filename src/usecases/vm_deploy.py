import os
import re
import sys
import logging
import subprocess
import xml.etree.ElementTree as et

from src.env_conf import settings

_LOGGER = logging.getLogger(__name__)


class VMDeploy:
    def __init__(self):
        pass

    def get_ova_networks(self, ova_path):
        ostype = sys.platform
        folder_name = str()
        if ostype.startswith('win32'):
            folder_name = 'win32'
        elif ostype.startswith('linux'):
            folder_name = 'lin64'
        dir_name = settings.getValue('OVF_TOOL_DIR')
        ovftool_path = os.path.join(dir_name, folder_name, 'ovftool')
        cmd = [ovftool_path, '--machineOutput', ova_path]
        ova_details = subprocess.run(cmd, stdout = subprocess.PIPE).stdout.decode()
        ova_details = re.sub('\+', '', ova_details)
        xml_data = et.fromstring(
            ova_details[ova_details.index('<probeResult>') : ova_details.index('</probeResult>') + len('</probeResult>')])
        networks = []
        for network in xml_data.find('networks'):
            networks.append(network.find('name').text.strip())
        return networks

    def deploy_vm(self):
        print(f'''\n{'-'*60}\n\t\t\tInitiating VM Deployment\n{'-'*60}\n''')
        deploy_settings = settings.getValue('VM_TOPOLOGY')
        vms = deploy_settings['VM_DETAILS']
        ova_path = deploy_settings["OVA_FILE_PATH"]
        source_networks = self.get_ova_networks(ova_path)
        datastore = deploy_settings['DATASTORE']
        target_switch = str()
        success = True
        if deploy_settings['DEPLOYMENT_TARGET'] == "VCENTER" or deploy_settings['DEPLOYMENT_TARGET'] == "NSX-V":
            target_ip = settings.getValue('VCENTER_DETAILS')['IP']
            target_user = settings.getValue('VCENTER_DETAILS')['USER']
            target_password = settings.getValue('VCENTER_DETAILS')['PASSWORD']
            host_ip = settings.getValue('HOST_DETAILS')[0]['HOST']
            target_user = re.sub('@', '%40', target_user)
            target_password = re.sub('@', '%40', target_password)
            target_switch = f'"vi://{target_user}:{target_password}@{target_ip}?ip={host_ip}"'
        elif deploy_settings['DEPLOYMENT_TARGET'] == "ESXI":
            target_ip = settings.getValue('HOST_DETAILS')[0]['HOST']
            target_user = settings.getValue('HOST_DETAILS')[0]['USER']
            target_password = settings.getValue('HOST_DETAILS')[0]['PASSWORD']
            target_user = re.sub('@', '%40', target_user)
            target_password = re.sub('@', '%40', target_password)
            target_switch = f'"vi://{target_user}:{target_password}@{target_ip}"'
        for vm in vms:
            vm_name = vm['VM_NAME']
            target_networks = vm['NETWORKS']
            ip = vm['IP_ADDRESS']
            netmask = vm['NETMASK']
            gateway = vm['GATEWAY']
            ostype = sys.platform
            if ostype.startswith('win32'):
                folder_name = 'win32'
                dir_name = settings.getValue('OVF_TOOL_DIR')
                tool_path = os.path.join(dir_name, folder_name, 'ovftool.exe')
                _LOGGER.debug(f'opening {tool_path} ')
                command_switches = ['--acceptAllEulas', '--powerOn', '--allowExtraConfig', '--noSSLVerify']
                cmd = [tool_path] + command_switches
                cmd += [f'--datastore="{datastore}"', f'--name="{vm_name}"',
                        f'--net:{source_networks[0]}="{target_networks[0]}"',
                        f'--net:{source_networks[1]}="{target_networks[1]}"',
                        f'--net:{source_networks[2]}="{target_networks[2]}"', f'--prop:"ipAddress"={ip}',
                        f'--prop:"netmask"={netmask}' f'--prop:"gateway"={gateway}', ova_path, target_switch]
                _LOGGER.debug(f'Executing command: {" ".join(cmd)}')
                _LOGGER.info('Deploying vm. This might take a few minutes...')
                result = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode()
                print(result)
            elif ostype.startswith('linux'):
                folder_name = 'lin64'
                dir_name = settings.getValue('OVF_TOOL_DIR')
                tool_path = os.path.join(dir_name, folder_name, 'ovftool.exe')
                _LOGGER.debug(f'opening {tool_path} ')
                command_switches = ['--acceptAllEulas', '--powerOn', 'allowExtraConfig', 'noSSLVerify']
                cmd = [tool_path] + command_switches
                cmd += [f'--datastore="{datastore}"', f'--name="{vm_name}"',
                        f'--net:{source_networks[0]}="{target_networks[0]}"',
                        f'--net:{source_networks[1]}="{target_networks[1]}"',
                        f'--net:{source_networks[2]}="{target_networks[2]}"', f'--prop:"ipAddress"={ip}',
                        f'--prop:"netmask"={netmask}' f'--prop:"gateway"={gateway}', ova_path, target_switch]
                _LOGGER.debug(f'Executing command: {" ".join(cmd)}')
                _LOGGER.info('Deploying vm. This might take a few minutes...')
                result = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode()
                print(result)
            # TODO for mac deployment
        return success
