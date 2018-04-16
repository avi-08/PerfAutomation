"""
    There are a few configurations on the VM also that impact the overall networking throughput delivered.
    1.Verify that exclusive affinity of all vCPU are enable.
    2.Verify CPU reservation and share are reserved and made available to VM.
    3.Verify Memory(RAM) reservation and share are reserved and made available to VM.
    4.Verify Latency sensitivity is taking effect.
    5.Verify the vNIC adapter type.
    6.Verify the vNIC TX thread allocation is set.
    7.Verify the SysContext is set to the no. of thread to be pinned.
    8.Verify the vm NUMA is aligned to the NUMA of the physical NIC.

    The above verification are done to ensure that it will not impact the overall networking throughput delivered.
    Configuration are done if the verification fails.

"""

from src.core.vm import VmTuning, VmUtil
from src.util import HostSession
from src.core.host import Host
from src.env_conf import settings
from  src.util import ParserUtil, LogUtil
import json
import logging

_LOGGER = LogUtil.LogUtil()


def vm_config(keep_defaults=False):
    hosts = settings.getValue('HOST_DETAILS')
    #print(hosts)
    vm_conf = json.load(open(r'env_conf\vm.json'))
    vmTune = VmTuning.VmTunning()
    vmUtil = VmUtil.VmUtility()
    conf_host = Host.HostConfig()
    parser = ParserUtil.Parser()
    for host in hosts:
        # print(host['HOST'], host['USER'], host['PASSWORD'])
        client = HostSession.HostSession().connect(host['HOST'], host['USER'], host['PASSWORD'], False)
        # print(client)
        # vms = vmUtil.get_vm_list(client)
        temp_vms = vm_conf['ESXI_65']['VM_NAMES']
        #print(temp_vms)
        ver = conf_host.get_host_version(client)
        _NICS = host['NICS'].split(',')
        _LOGGER.info('Verifying optimization on virtual machine')
        for vm in temp_vms:
        # for vm in vms:
            """
                ESXI VERSION 6.5
            """
            print(parser.dict_to_table(get_env_data(client, vm), 'Current VM Status', False))
            if ver.find('6.5') > -1:
                param = vm_conf['ESXI_65']
                _LOGGER.info(f'HOST VERSION : ESXI 6.5 ')
                _LOGGER.info(f'virtual machine : {vm}')
                vmUtil.power_off_vm(client, vm)
                _LOGGER.info(f'checking Latency sensitivity is set to "high":{vmTune.verify_latency_sensitivity(client,vm)}')
                status = vmTune.config_latency_sensitivity(client, vm)
                if status:
                    _LOGGER.info(f'Setting latency sensitivity to high : {status}')
                else:
                    _LOGGER.error(f'Setting latency sensitivity to high :{status}')

                _LOGGER.info(f'checking CPU reservation : {vmTune.verify_cpu_reservation(client,vm)}')
                status = vmTune.config_cpu_reservation(client, vm)
                if status:
                    _LOGGER.info(f'changing CPU reservation :{status}')
                else:
                    _LOGGER.error(f'changing CPU reservation :{status}')

                _LOGGER.info(f'checking CPU share :{vmTune.verify_cpu_share(client, vm)}')
                status = vmTune.config_cpu_share(client, vm)
                if status:
                    _LOGGER.info(f'changing CPU share : {status}')
                else:
                    _LOGGER.error(f'chaging CPU share : {status}')

                _LOGGER.info(f'checking Memory reservation : {vmTune.verify_mem_reservation(client,vm)}')
                status = vmTune.config_mem_reservation(client, vm)
                if status:
                    _LOGGER.info(f'changing Memory reservation :{status}')
                else:
                    _LOGGER.error(f'changing Memory reservation :{status}')

                _LOGGER.info(f'checking Memory share :{vmTune.verify_mem_share(client, vm)}')
                status = vmTune.config_mem_share(client, vm)
                if status:
                    _LOGGER.info(f'changing Memory share : {status}')
                else:
                    _LOGGER.error(f'chaging Memory share : {status}')

                for vnic in set(vmUtil.get_vnic_no(client, vm)):
                    _LOGGER.info(f'checking the vNIC adapter type : {vmTune.verify_nic_adapter_type(client, vm, param["ADAPTER_TYPE"],vnic)}')
                    status = vmTune.config_nic_adapter_type(client, vm, param["ADAPTER_TYPE"],vnic)
                    if status:
                        _LOGGER.info(f'changing the vNIC adapter type  to {param["ADAPTER_TYPE"]}:{status}')
                    else:
                        _LOGGER.error(f'changing the vNIC adapter type  to {param["ADAPTER_TYPE"]}:{status}')

                    _LOGGER.info(f'checking the TX thread Allocation for vnic{vnic}: {vmTune.verify_tx_thread_allocation(client, vm, vnic)}')
                    status = vmTune.config_tx_thread_allocation(client, vm, vnic)
                    if status:
                        _LOGGER.info(f'changing the TX thread allocation for vnic{vnic}: {status}')
                    else:
                        _LOGGER.error(f'changing the TX thread allocation  for vnic{vnic}: {status}')

                _LOGGER.info(f'Checking the SysContext : {vmTune.verify_sys_context(client, vm, vmTune.get_syscontext_value(client, vm, True))}')
                status = vmTune.config_sys_context(client, vm, vmTune.get_syscontext_value(client, vm, True))
                if status:
                    _LOGGER.info(f'changing SysContext value to {vmTune.get_syscontext_value(client, vm, True)} : {status}')
                else:
                    _LOGGER.error(f'changing SysContext value to {vmTune.get_syscontext_value(client, vm, True)} : {status}')

                for nic in _NICS:
                    _LOGGER.info(f'Checking the NUMA affinity value for {nic} : {vmTune.verify_numa_affinity(client,vm, nic)}')
                    status = vmTune.config_numa_affinity(client, vm, nic)
                    if status:
                        _LOGGER.info(f'changing NUMA value for {nic}:{status}')
                    else:
                        _LOGGER.error(f'changing NUMA value for {nic}:{status}')
                vmTune.clean_file(client, vm)
                vmUtil.power_on_vm(client, vm)

            else:
                """
                    ESXI VERSION 6.0 U2
                """
                param = vm_conf['ESXI_60U2']
                _LOGGER.info(f'HOST VETSION : ESXI 6.0 U2')
                _LOGGER.info('Verifying optimization on virtual machine')
                vmUtil.power_off_vm(client, vm)
                _LOGGER.info(f'checking Latency sensitivity is set to "high":{vmTune.verify_latency_sensitivity()}')
                status = vmTune.config_latency_sensitivity(client, vm)
                if status:
                    _LOGGER.info(f'Setting latency sensitivity to high : {status}')
                else:
                    _LOGGER.error(f'Setting latency sensitivity to high :{status}')
                    return False

                _LOGGER.info(f'checking CPU reservation : {vmTune.verify_cpu_reservation(client,vm)}')
                status = vmTune.config_cpu_reservation(client, vm)
                if status:
                    _LOGGER.info(f'changing CPU reservation :{status}')
                else:
                    _LOGGER.error(f'changing CPU reservation :{status}')

                _LOGGER.info(f'checking CPU share :{vmTune.verify_cpu_share(client, vm)}')
                status = vmTune.config_cpu_share(client, vm)
                if status:
                    _LOGGER.info(f'changing CPU share : {status}')
                else:
                    _LOGGER.error(f'chaging CPU share : {status}')

                _LOGGER.info(f'checking Memory reservation : {vmTune.verify_mem_reservation(client,vm)}')
                status = vmTune.config_mem_reservation(client, vm)
                if status:
                    _LOGGER.info(f'changing Memory reservation :{status}')
                else:
                    _LOGGER.error(f'changing Memory reservation :{status}')

                _LOGGER.info(f'checking Memory share :{vmTune.verify_mem_share(client, vm)}')
                status = vmTune.config_mem_share(client, vm)
                if status:
                    _LOGGER.info(f'changing Memory share : {status}')
                else:
                    _LOGGER.error(f'chaging Memory share : {status}')

                for vnic in set(vmUtil.get_vnic_no(client, vm)):
                    _LOGGER.info(f'checking the TX thread Allocation for vnic{vnic}: {vmTune.verify_tx_thread_allocation(client, vm,vnic)}')
                    status = vmTune.config_tx_thread_allocation(client, vm, vnic)
                    if status:
                        _LOGGER.info(f'changing the TX thread allocation for vnic{vnic}: {status}')
                    else:
                        _LOGGER.error(f'changing the TX thread allocation  for vnic{vnic}:: {status}')

                    _LOGGER.info(f'checking the vNIC adapter type : {vmTune.verify_nic_adapter_type(client, vm, vmTune.get_syscontext_value(client, vm, False))}')
                    status = vmTune.config_nic_adapter_type(client, vm, vmTune.get_syscontext_value(client, vm, False))
                    if status:
                        _LOGGER.info(f'changing the vNIC adapter type  to {vmTune.get_syscontext_value(client, vm, False)}:{status}')
                    else:
                        _LOGGER.error(f'changing the vNIC adapter type  to {vmTune.get_syscontext_value(client, vm, False)}:{status}')

                _LOGGER.info(f'Checking the SysContext : {vmTune.verify_sys_context(client,vm,param["VM_SYSCONTEXT"])}')
                status = vmTune.config_sys_context(client, vm, param["VM_SYSCONTEXT"])
                if status:
                    _LOGGER.info(f'changing SysContext value to {param["VM_SYSCONTEXT"]} : {status}')
                else:
                    _LOGGER.error(f'changing SysContext value to {param["VM_SYSCONTEXT"]} : {status}')

                """
                for nic in _NICS:
                    _LOGGER.info(
                        f'Checking the NUMA affinity value for {nic} : {vmTune.verify_numa_affinity(client,vm, nic)}')
                    status = vmTune.config_numa_affinity(client, vm, nic)
                    if status:
                        _LOGGER.info(f'changing NUMA value for {nic}:{status}')
                    else:
                        _LOGGER.error(f'changing NUMA value for {nic}:{status}')
                """
                vmTune.clean_file(client, vm)
                vmUtil.power_on_vm(client, vm)
            print(parser.dict_to_table(get_env_data(client, vm), 'Post configuration VM Status', False))
        HostSession.HostSession().disconnect(client)

def get_env_data(client, vm):
    vmTune = VmTuning.VmTunning()
    vmUtil = VmUtil.VmUtility()
    parser = ParserUtil.Parser()
    b = {}
    b['Adapter Type'] = list()
    b['TX thread'] = list()
    a = vmTune.get_latency_sensitivity(client, vm)
    b['latency Sensitivity'] = a['out']
    a =vmTune.get_cpu_reservation(client, vm)
    b['CPU Reservation '] = a['out']
    a = vmTune.get_cpu_share(client, vm)
    b['CPU Share'] = a['out']
    a = vmTune.get_mem_share(client, vm)
    b['Memory Share'] = a['out']
    a = vmTune.get_mem_reservation(client, vm)
    b['Memory Reservation'] = a['out']
    for vnic in set(vmUtil.get_vnic_no(client, vm)):
        a = vmTune.get_nic_adapter_type(client, vm,vnic)
        b['Adapter Type'].append(a['out'].strip("\n").strip())
        a = vmTune.get_tx_thread_allocation(client, vm, vnic)
        b['TX thread'].append(a['out'].strip("\n").strip())

    a = vmTune.get_sys_context(client,vm)
    b['SysContext'] = a['out']
    a = vmTune.get_numa_affinity(client,'vmnic6')
    b['NUMA affinity'] = a['out']
    # print(parser.dict_to_table(b,'VM Status',False))
    return b


"""
def vm_config():
    hosts = json.load(open(r'..\env_conf\host.json'))
    vms = json.load(open(r'..\env_conf\vm.json'))
    for host in hosts['HOST_DETAILS']:
        client = HostSession.HostSession().connect(host['HOST'], host['USER'], host['PASSWORD'], False)
        print(host['HOST'])
        print(f'Latency Sensitivity set to High and Reserved :{VmTuning.verify_latencySensitivity(client)}')
        # if VmTuning.verify_latencySensitivity(client) == False:
        print(f'Vmnic Adapter type (vmxnet):{VmTuning.vnic_adapter_type(client,datastore,vmname)}')
        print(f'vNIC TX thread allocation :{VmTuning.verify_vnic_tx_thread(client,datastore,vmname)}')
        if VmTuning.verify_vnic_tx_thread(client,datastore,vmname) == False: 
        print(f'Numa Affinity :{VmTuning.verify_numa_NodeAffinity(client,datastore,vmname)}')
        print(f'system context : {VmTuning.verify_SysContext(client,datastore,vmname)}')

        print(f'Vm config is Completed')

        print('Latency Sensitivity Verification:{}'.format(VmTuning.verify_latency_sensitivity(client, vmname) == 'high'))
        if VmTuning.verify_latency_sensitivity(client, vmname) != 'high':
            VmTuning.config_latency_sensitivity(client, vmname)
        print('verify_tx_thread_allocation:{}'.format(VmTuning.verify_tx_thread_allocation(client, vmname)))
        if VmTuning.verify_tx_thread_allocation(client, vmname) == False:
            VmTuning.config_tx_thread_allocation(client, vmname, False)
        print('verify_sys_context : {}'.format(VmTuning.verify_sys_context(client, vmname, 3)))
        client.close()
"""