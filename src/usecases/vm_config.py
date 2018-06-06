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
        temp_vms = settings.getValue('ESXI_65')['VM_NAMES']
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
                print(f'- Getting the current configuration of virtual machine :{vm}')
                print(parser.dict_to_table(get_env_data(client, vm), f'Current configuration of Virtual Machine - {vm}', False))
                _LOGGER.info(f'virtual machine : {vm}')
                print(f'- Optimization verification has been started.')
                vm_util.power_off_vm(client, vm)
                _LOGGER.info(f'checking Latency sensitivity is set to "high":{vm_tune.verify_latency_sensitivity(client,vm)}')
                status = vm_tune.config_latency_sensitivity(client, vm)
                if status:
                    _LOGGER.info(f'Setting latency sensitivity to high : {status}')
                else:
                    _LOGGER.error(f'Setting latency sensitivity to high :{status}')

                _LOGGER.info(f'checking CPU reservation : {vm_tune.verify_cpu_reservation(client,vm)}')
                status = vm_tune.config_cpu_reservation(client, vm)
                if status:
                    _LOGGER.info(f'changing CPU reservation :{status}')
                else:
                    _LOGGER.error(f'CPU reservation status :{status}')

                _LOGGER.info(f'checking CPU share :{vm_tune.verify_cpu_share(client, vm)}')
                status = vm_tune.config_cpu_share(client, vm)
                if status:
                    _LOGGER.info(f'changing CPU share : {status}')
                else:
                    _LOGGER.error(f'changing CPU share : {status}')

                _LOGGER.info(f'checking Memory reservation : {vm_tune.verify_mem_reservation(client,vm)}')
                status = vm_tune.config_mem_reservation(client, vm)
                if status:
                    _LOGGER.info(f'changing Memory reservation :{status}')
                else:
                    _LOGGER.error(f'changing Memory reservation :{status}')

                _LOGGER.info(f'checking Memory share :{vm_tune.verify_mem_share(client, vm)}')
                status = vm_tune.config_mem_share(client, vm)
                if status:
                    _LOGGER.info(f'changing Memory share : {status}')
                else:
                    _LOGGER.error(f'chaging Memory share : {status}')

                for vnic in set(vm_util.get_vnic_no(client, vm)):
                    _LOGGER.info(f'checking the vNIC adapter type : {vm_tune.verify_nic_adapter_type(client, vm, param["ADAPTER_TYPE"],vnic)}')
                    status = vm_tune.config_nic_adapter_type(client, vm, param["ADAPTER_TYPE"],vnic)
                    if status:
                        _LOGGER.info(f'changing the vNIC adapter type  to {param["ADAPTER_TYPE"]}:{status}')
                    else:
                        _LOGGER.error(f'changing the vNIC adapter type  to {param["ADAPTER_TYPE"]}:{status}')

                    _LOGGER.info(f'checking the TX thread Allocation for vnic{vnic}: {vm_tune.verify_tx_thread_allocation(client, vm, vnic)}')
                    status = vm_tune.config_tx_thread_allocation(client, vm, vnic)
                    if status:
                        _LOGGER.info(f'changing the TX thread allocation for vnic{vnic}: {status}')
                    else:
                        _LOGGER.error(f'changing the TX thread allocation  for vnic{vnic}: {status}')

                _LOGGER.info(f'Checking the SysContext : {vm_tune.verify_sys_context(client, vm, vm_tune.get_syscontext_value(client, vm, True))}')
                status = vm_tune.config_sys_context(client, vm, vm_tune.get_syscontext_value(client, vm, True))
                if status:
                    _LOGGER.info(f'changing SysContext value to {vm_tune.get_syscontext_value(client, vm, True)} : {status}')
                else:
                    _LOGGER.error(f'changing SysContext value to {vm_tune.get_syscontext_value(client, vm, True)} : {status}')

                for nic in _NICS:
                    _LOGGER.info(f'Checking the NUMA affinity value for {nic} : {vm_tune.verify_numa_affinity(client,vm, nic)}')
                    status = vm_tune.config_numa_affinity(client, vm, nic)
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
                vm_util.power_off_vm(client, vm)
                print(f' - Getting the current configuration of virtual machine :{vm}')
                print(parser.dict_to_table(get_env_data(client, vm), f'Current configuration of Virtual Machine :{vm}', False))
                _LOGGER.info(f'checking Latency sensitivity is set to "high":{vm_tune.verify_latency_sensitivity()}')
                status = vm_tune.config_latency_sensitivity(client, vm)
                if status:
                    _LOGGER.info(f'Setting latency sensitivity to high : {status}')
                else:
                    _LOGGER.error(f'Setting latency sensitivity to high :{status}')
                    return False
                _LOGGER.info(f'checking CPU reservation : {vm_tune.verify_cpu_reservation(client,vm)}')
                status = vm_tune.config_cpu_reservation(client, vm)
                if status:
                    _LOGGER.info(f'changing CPU reservation :{status}')
                else:
                    _LOGGER.error(f'changing CPU reservation :{status}')

                _LOGGER.info(f'checking CPU share :{vm_tune.verify_cpu_share(client, vm)}')
                status = vm_tune.config_cpu_share(client, vm)
                if status:
                    _LOGGER.info(f'changing CPU share : {status}')
                else:
                    _LOGGER.error(f'chaging CPU share : {status}')

                _LOGGER.info(f'checking Memory reservation : {vm_tune.verify_mem_reservation(client,vm)}')
                status = vm_tune.config_mem_reservation(client, vm)
                if status:
                    _LOGGER.info(f'changing Memory reservation :{status}')
                else:
                    _LOGGER.error(f'changing Memory reservation :{status}')

                _LOGGER.info(f'checking Memory share :{vm_tune.verify_mem_share(client, vm)}')
                status = vm_tune.config_mem_share(client, vm)
                if status:
                    _LOGGER.info(f'changing Memory share : {status}')
                else:
                    _LOGGER.error(f'chaging Memory share : {status}')

                for vnic in set(vm_util.get_vnic_no(client, vm)):
                    _LOGGER.info(f'checking the TX thread Allocation for vnic{vnic}: {vm_tune.verify_tx_thread_allocation(client, vm,vnic)}')
                    status = vm_tune.config_tx_thread_allocation(client, vm, vnic)
                    if status:
                        _LOGGER.info(f'changing the TX thread allocation for vnic{vnic}: {status}')
                    else:
                        _LOGGER.error(f'changing the TX thread allocation  for vnic{vnic}:: {status}')

                    _LOGGER.info(f'checking the vNIC adapter type : {vm_tune.verify_nic_adapter_type(client, vm, vm_tune.get_syscontext_value(client, vm, False))}')
                    status = vm_tune.config_nic_adapter_type(client, vm, vm_tune.get_syscontext_value(client, vm, False))
                    if status:
                        _LOGGER.info(f'changing the vNIC adapter type  to {vm_tune.get_syscontext_value(client, vm, False)}:{status}')
                    else:
                        _LOGGER.error(f'changing the vNIC adapter type  to {vm_tune.get_syscontext_value(client, vm, False)}:{status}')

                _LOGGER.info(f'Checking the SysContext : {vm_tune.verify_sys_context(client,vm,param["VM_SYSCONTEXT"])}')
                status = vm_tune.config_sys_context(client, vm, param["VM_SYSCONTEXT"])
                if status:
                    _LOGGER.info(f'changing SysContext value to {param["VM_SYSCONTEXT"]} : {status}')
                else:
                    _LOGGER.error(f'changing SysContext value to {param["VM_SYSCONTEXT"]} : {status}')

                for nic in _NICS:
                    _LOGGER.info(f'Checking the NUMA affinity value for {nic} : {vm_tune.verify_numa_affinity(client,vm, nic)}')
                    status = vm_tune.config_numa_affinity(client, vm, nic)
                    if status:
                        _LOGGER.info(f'changing NUMA value for {nic}:{status}')
                    else:
                        _LOGGER.error(f'changing NUMA value for {nic}:{status}')
            vm_tune.clean_file(client, vm)
            vm_util.power_on_vm(client, vm)
            print(f'- Virtual machine Verification are done.')
            print(f'- Getting the current configuration of virtual machine(post Optimization) :{vm}')
            print(parser.dict_to_table(get_env_data(client, vm), f'Post configuration VM Status- {vm}', False))
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
    a = vm_tune.get_sys_context(client,vm)
    b['SysContext'] = a['out']
    a = vm_tune.get_numa_affinity(client,'vmnic6')
    b['NUMA affinity'] = a['out']
    return b
