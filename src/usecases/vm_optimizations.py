"""
    There are a few configurations on the VM also that impact the overall networking throughput delivered.
    1.Verify that exclusive affinity of all vCPU are enable.
    2.Verify CPU reservation and share are reserved and made available to VM.
    3.Verify Memory(RAM) reservation and share are reserved and made available to VM.
    4.Verify Latency sensitivity is taking effect.
    5.Verify the vNIC adapter type.
    6.Verify the vNIC TX thread allocation is set.
    7.Verify the SysContext is set to the number of thread to be pinned.
    8.Verify the vm NUMA is aligned to the NUMA of the physical NIC.

    The above verification are done to ensure that it will not impact the overall networking throughput delivered.
    Configuration are done if the verification fails.

"""
import re
from src.core.vm import VmTuning, VmUtil
from src.util import HostSession
from src.core.host import Host
from src.env_conf import settings
from src.util import ParserUtil, LogUtil

_LOGGER = LogUtil.LogUtil()
vm_tune = VmTuning.VmTunning()
vm_util = VmUtil.VmUtility()
conf_host = Host.HostConfig()
parser = ParserUtil.Parser()


def vm_config(keep_defaults=False):
    hosts = settings.getValue('HOST_DETAILS')
    print(f'''\n{'-'*60}\n\t\t\tInitiating VM Optimizations\n{'-'*60}\n''')
    for host in hosts:
        client = HostSession.HostSession().connect(host['HOST'], host['USER'], host['PASSWORD'], False)
        temp_vms = settings.getValue('VM_TOPOLOGY')['VM_DETAILS']
        ver = conf_host.get_host_version(client)
        _NICS = host['NICS'].split(',')
        _LOGGER.info('Verifying optimization on virtual machine')
        print('- Verifying optimization on virtual machine')
        for vm in temp_vms:
        # for vm in vms:
            if ver.find('6.5') > -1:
                # ESXI 6.5
                param = settings.getValue('ESXI_65')
                _LOGGER.info(f'HOST VERSION : ESXI 6.5 ')
                print(f'- Getting the current configuration of virtual machine :{vm["VM_NAME"]}')
                print(parser.dict_to_table(get_env_data(client, vm["VM_NAME"]), f'Current configuration of Virtual Machine - {vm["VM_NAME"]}', False))
                _LOGGER.info(f'virtual machine : {vm["VM_NAME"]}')
                print(f'- Optimization verification has been started.')
                vm_util.power_off_vm(client, vm["VM_NAME"])
                _LOGGER.info(f'checking Latency sensitivity is set to "high":{vm_tune.verify_latency_sensitivity(client,vm["VM_NAME"])}')
                status = vm_tune.config_latency_sensitivity(client, vm["VM_NAME"])
                if status:
                    _LOGGER.info(f'Setting latency sensitivity to high : {status}')
                else:
                    _LOGGER.error(f'Setting latency sensitivity to high :{status}')

                _LOGGER.info(f'checking CPU reservation : {vm_tune.verify_cpu_reservation(client,vm["VM_NAME"])}')
                status = vm_tune.config_cpu_reservation(client, vm["VM_NAME"])
                if status:
                    _LOGGER.info(f'changing CPU reservation :{status}')
                else:
                    _LOGGER.error(f'CPU reservation status :{status}')

                _LOGGER.info(f'checking CPU share :{vm_tune.verify_cpu_share(client, vm["VM_NAME"])}')
                status = vm_tune.config_cpu_share(client, vm["VM_NAME"])
                if status:
                    _LOGGER.info(f'changing CPU share : {status}')
                else:
                    _LOGGER.error(f'changing CPU share : {status}')

                _LOGGER.info(f'checking Memory reservation : {vm_tune.verify_mem_reservation(client,vm["VM_NAME"])}')
                status = vm_tune.config_mem_reservation(client, vm["VM_NAME"])
                if status:
                    _LOGGER.info(f'changing Memory reservation :{status}')
                else:
                    _LOGGER.error(f'changing Memory reservation :{status}')

                _LOGGER.info(f'checking Memory share :{vm_tune.verify_mem_share(client, vm["VM_NAME"])}')
                status = vm_tune.config_mem_share(client, vm["VM_NAME"])
                if status:
                    _LOGGER.info(f'changing Memory share : {status}')
                else:
                    _LOGGER.error(f'chaging Memory share : {status}')

                for vnic in set(vm_util.get_vnic_no(client, vm["VM_NAME"])):
                    _LOGGER.info(f'checking the vNIC adapter type : {vm_tune.verify_nic_adapter_type(client, vm["VM_NAME"], param["ADAPTER_TYPE"],vnic)}')
                    status = vm_tune.config_nic_adapter_type(client, vm["VM_NAME"], param["ADAPTER_TYPE"],vnic)
                    if status:
                        _LOGGER.info(f'changing the vNIC adapter type  to {param["ADAPTER_TYPE"]}:{status}')
                    else:
                        _LOGGER.error(f'changing the vNIC adapter type  to {param["ADAPTER_TYPE"]}:{status}')

                    _LOGGER.info(f'checking the TX thread Allocation for vnic{vnic}: {vm_tune.verify_tx_thread_allocation(client, vm["VM_NAME"], vnic)}')
                    status = vm_tune.config_tx_thread_allocation(client, vm["VM_NAME"], vnic)
                    if status:
                        _LOGGER.info(f'changing the TX thread allocation for vnic{vnic}: {status}')
                    else:
                        _LOGGER.error(f'changing the TX thread allocation  for vnic{vnic}: {status}')

                _LOGGER.info(f'Checking the SysContext : {vm_tune.verify_sys_context(client, vm["VM_NAME"], vm_tune.get_syscontext_value(client, vm["VM_NAME"], True))}')
                status = vm_tune.config_sys_context(client, vm["VM_NAME"], vm_tune.get_syscontext_value(client, vm["VM_NAME"], True))
                if status:
                    _LOGGER.info(f'changing SysContext value to {vm_tune.get_syscontext_value(client, vm["VM_NAME"], True)} : {status}')
                else:
                    _LOGGER.error(f'changing SysContext value to {vm_tune.get_syscontext_value(client, vm["VM_NAME"], True)} : {status}')

                for nic in _NICS:
                    _LOGGER.info(f'Checking the NUMA affinity value for {nic} : {vm_tune.verify_numa_affinity(client,vm["VM_NAME"], nic)}')
                    status = vm_tune.config_numa_affinity(client, vm["VM_NAME"], nic)
                    if status:
                        _LOGGER.info(f'changing NUMA value for {nic}:{status}')
                    else:
                        _LOGGER.error(f'changing NUMA value for {nic}:{status}')
            else:
                """
                    ESXI VERSION 6.0 U2
                """
                param = settings.getValue('ESXI_60U2')
                _LOGGER.info(f'HOST VETSION : ESXI 6.0 U2')
                _LOGGER.info('Verifying optimization on virtual machine')
                vm_util.power_off_vm(client, vm["VM_NAME"])
                print(f' - Getting the current configuration of virtual machine :{vm["VM_NAME"]}')
                print(parser.dict_to_table(get_env_data(client, vm["VM_NAME"]), f'Current configuration of Virtual Machine :{vm["VM_NAME"]}', False))
                _LOGGER.info(f'checking Latency sensitivity is set to "high":{vm_tune.verify_latency_sensitivity()}')
                status = vm_tune.config_latency_sensitivity(client, vm["VM_NAME"])
                if status:
                    _LOGGER.info(f'Setting latency sensitivity to high : {status}')
                else:
                    _LOGGER.error(f'Setting latency sensitivity to high :{status}')
                    return False
                _LOGGER.info(f'checking CPU reservation : {vm_tune.verify_cpu_reservation(client,vm["VM_NAME"])}')
                status = vm_tune.config_cpu_reservation(client, vm["VM_NAME"])
                if status:
                    _LOGGER.info(f'changing CPU reservation :{status}')
                else:
                    _LOGGER.error(f'changing CPU reservation :{status}')

                _LOGGER.info(f'checking CPU share :{vm_tune.verify_cpu_share(client, vm["VM_NAME"])}')
                status = vm_tune.config_cpu_share(client, vm["VM_NAME"])
                if status:
                    _LOGGER.info(f'changing CPU share : {status}')
                else:
                    _LOGGER.error(f'chaging CPU share : {status}')

                _LOGGER.info(f'checking Memory reservation : {vm_tune.verify_mem_reservation(client,vm["VM_NAME"])}')
                status = vm_tune.config_mem_reservation(client, vm["VM_NAME"])
                if status:
                    _LOGGER.info(f'changing Memory reservation :{status}')
                else:
                    _LOGGER.error(f'changing Memory reservation :{status}')

                _LOGGER.info(f'checking Memory share :{vm_tune.verify_mem_share(client, vm["VM_NAME"])}')
                status = vm_tune.config_mem_share(client, vm["VM_NAME"])
                if status:
                    _LOGGER.info(f'changing Memory share : {status}')
                else:
                    _LOGGER.error(f'chaging Memory share : {status}')

                for vnic in set(vm_util.get_vnic_no(client, vm["VM_NAME"])):
                    _LOGGER.info(f'checking the TX thread Allocation for vnic{vnic}: {vm_tune.verify_tx_thread_allocation(client, vm["VM_NAME"],vnic)}')
                    status = vm_tune.config_tx_thread_allocation(client, vm["VM_NAME"], vnic)
                    if status:
                        _LOGGER.info(f'changing the TX thread allocation for vnic{vnic}: {status}')
                    else:
                        _LOGGER.error(f'changing the TX thread allocation  for vnic{vnic}:: {status}')

                    _LOGGER.info(f'checking the vNIC adapter type : {vm_tune.verify_nic_adapter_type(client, vm["VM_NAME"], vm_tune.get_syscontext_value(client, vm["VM_NAME"], False))}')
                    status = vm_tune.config_nic_adapter_type(client, vm["VM_NAME"], vm_tune.get_syscontext_value(client, vm["VM_NAME"], False))
                    if status:
                        _LOGGER.info(f'changing the vNIC adapter type  to {vm_tune.get_syscontext_value(client, vm["VM_NAME"], False)}:{status}')
                    else:
                        _LOGGER.error(f'changing the vNIC adapter type  to {vm_tune.get_syscontext_value(client, vm["VM_NAME"], False)}:{status}')

                _LOGGER.info(f'Checking the SysContext : {vm_tune.verify_sys_context(client,vm["VM_NAME"],param["VM_SYSCONTEXT"])}')
                status = vm_tune.config_sys_context(client, vm["VM_NAME"], param["VM_SYSCONTEXT"])
                if status:
                    _LOGGER.info(f'changing SysContext value to {param["VM_SYSCONTEXT"]} : {status}')
                else:
                    _LOGGER.error(f'changing SysContext value to {param["VM_SYSCONTEXT"]} : {status}')

                for nic in _NICS:
                    _LOGGER.info(f'Checking the NUMA affinity value for {nic} : {vm_tune.verify_numa_affinity(client,vm["VM_NAME"], nic)}')
                    status = vm_tune.config_numa_affinity(client, vm["VM_NAME"], nic)
                    if status:
                        _LOGGER.info(f'changing NUMA value for {nic}:{status}')
                    else:
                        _LOGGER.error(f'changing NUMA value for {nic}:{status}')
            vm_tune.clean_file(client, vm["VM_NAME"])
            vm_util.power_on_vm(client, vm["VM_NAME"])
            print(f'- Virtual machine Verification are done.')
            print(f'- Getting the current configuration of virtual machine(post Optimization) :{vm["VM_NAME"]}')
            print(parser.dict_to_table(get_env_data(client, vm["VM_NAME"]), f'Post configuration VM Status- {vm["VM_NAME"]}', False))
        HostSession.HostSession().disconnect(client)


def get_env_data(client, vm):
    _LOGGER.info(f'Getting Environment Details')
    b = dict()
    b['Adapter Type'] = list()
    b['TX thread'] = list()
    a = vm_tune.get_latency_sensitivity(client, vm)
    b['latency Sensitivity'] = a['out']
    a =vm_tune.get_cpu_reservation(client, vm)
    b['CPU Reservation '] = a['out']
    a = vm_tune.get_cpu_share(client, vm)
    b['CPU Share'] = a['out']
    a = vm_tune.get_mem_share(client, vm)
    b['Memory Share'] = a['out']
    a = vm_tune.get_mem_reservation(client, vm)
    b['Memory Reservation'] = a['out']
    for vnic in set(vm_util.get_vnic_no(client, vm)):
        a = vm_tune.get_nic_adapter_type(client, vm, vnic)
        b['Adapter Type'].append(a['out'].strip("\n").strip())
        a = vm_tune.get_tx_thread_allocation(client, vm, vnic)
        b['TX thread'].append(a['out'].strip("\n").strip())
    a = vm_tune.get_sys_context(client, vm)
    b['SysContext'] = a['out']
    a = vm_tune.get_numa_affinity(client,'vmnic6')
    b['NUMA affinity'] = a['out']
    return b


def get_vm_macs(client):
    """
    Function to get MAC addresses of VMs using a SSH session.
    :param client: paramiko SSH client object to VM.
    :return: list of all MAC addresses of VM.
    """
    stdin, stdout, stderr = client.exec_command('ifconfig | grep HWaddr')
    pattern = '[0-9A-Za-z][0-9A-Za-z]:[0-9A-Za-z][0-9A-Za-z]:[0-9A-Za-z][0-9A-Za-z]:[0-9A-Za-z][0-9A-Za-z]:' \
              '[0-9A-Za-z][0-9A-Za-z]:[0-9A-Za-z][0-9A-Za-z]'
    return re.findall(pattern, stdout.read().decode(), re.MULTILINE)


def dpdk_init():
    """
    Configure appropriate mac addresses in startL3fwd.sh files and initiate the script on each of the dpdk VMs.
    :return:
    """
    deploy_settings = settings.getValue('VM_TOPOLOGY')
    tgen_mac = ''
    if deploy_settings['TOPOLOGY_TYPE'] == 'PVP':
        client = HostSession.HostSession().connect(deploy_settings['VM_DETAILS'][0]['IP'], deploy_settings['VM_USER'],
                                                   deploy_settings['VM_PASSWORD'], False)
        vm_mac = get_vm_macs(client)
        pattern = '[0-9A-Za-z][0-9A-Za-z]:[0-9A-Za-z][0-9A-Za-z]:[0-9A-Za-z][0-9A-Za-z]:[0-9A-Za-z][0-9A-Za-z]:' \
                  '[0-9A-Za-z][0-9A-Za-z]:[0-9A-Za-z][0-9A-Za-z]'
        stdin, stdout, stderr = client.exec_command('cat startL3fwd.sh')
        dpdk_file_data = stdout.read().decode()
        pattern1 = '--eth-dest=0,' + pattern
        pattern2 = '--eth-dest=1,' + pattern
        dpdk_file_data = re.sub(pattern1, f'--eth-dest=0,{vm_mac[1]}', dpdk_file_data)
        dpdk_file_data = re.sub(pattern2, f'--eth-dest=1,{tgen_mac}', dpdk_file_data)
        client.exec_command(f'echo "{dpdk_file_data}" > startL3fwd.sh')
        client.exec_command(r'sudo ./startL3fwd.sh')
        HostSession.HostSession().disconnect(client)
    elif deploy_settings['TOPOLOGY_TYPE'] == 'PVVP':
        client = []
        for vm in deploy_settings['VM_DETAILS']:
            client.append(HostSession.HostSession().connect(vm['IP'], deploy_settings['VM_USER'],
                                                   deploy_settings['VM_PASSWORD'], False))
        pattern = '[0-9A-Za-z][0-9A-Za-z]:[0-9A-Za-z][0-9A-Za-z]:[0-9A-Za-z][0-9A-Za-z]:[0-9A-Za-z][0-9A-Za-z]:' \
                  '[0-9A-Za-z][0-9A-Za-z]:[0-9A-Za-z][0-9A-Za-z]'
        vm_mac = []
        pattern1 = '--eth-dest=0,' + pattern
        pattern2 = '--eth-dest=1,' + pattern
        for i in range(len(client)):
            vm_mac.append(get_vm_macs(client[i]))
        for i in range(len(client)):
            stdin, stdout, stderr = client[i].exec_command('cat startL3fwd.sh')
            dpdk_file_data = stdout.read().decode()
            dpdk_file_data = re.sub(pattern1, f'--eth-dest=0,{vm_mac[i][1]}', dpdk_file_data)
            if i == len(client) - 1:
                dpdk_file_data = re.sub(pattern2, f'--eth-dest=1,{tgen_mac}', dpdk_file_data)
            else:
                dpdk_file_data = re.sub(pattern2, f'--eth-dest=1,{vm_mac[1][i]}', dpdk_file_data)
            client[i].exec_command(f'echo "{dpdk_file_data}" > startL3fwd.sh')
            client[i].exec_command(r'sudo ./startL3fwd.sh')
        for i in range(len(client)):
            HostSession.HostSession().disconnect(client[i])
