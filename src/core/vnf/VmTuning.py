"""
    There are a few configurations on the VM also that impact the overall networking throughput delivered.
    1.Verify that exclusive affinity of all vCPU are enable.
    2.Verify CPU reservation and share are reserved and made available to VM.
    3.Verify Memory(RAM) reservation and share are reserved and made available to VM.
    4.Verify Latency sensitivity is taking effect.
    5.Verify the vNIC adapter type.
    6.Verify the vNIC TX thread allocation is set.
    7.Verify the SysContext is set to the no. of thread to be pinned.
    8.Verify the vm NUMA is alligned to the NUMA of the physical NIC.

    The above verification are done to ensure that it will not impact the overall networking throughput delivered.
    Configuration are done if the verification fails.

"""

from __future__ import print_function
from src.util import VmUtil
import re
import logging

__author__ = "Somanath"

vmUtil = VmUtil.VmUtility()
_LOGGER = logging.getLogger(__name__)

class VmTunning :
    
    def __init__(self):
        pass

    """
        configration function for the Virtual machine optimization
    """
    #cleaning the file
    def clean_file (self, session, vmname):
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
        data = stdout.read().decode()
        data = data.split('\n')
        res = ''
        for d in data:
            if d != '':
                res += d.strip() + '\n'
        res = res.replace('"', '\\"')
        # print( data )
        stdin, stdout, stderr = session.exec_command(f'echo "{res}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')

    # configration of the latency sensitivity
    def config_latency_sensitivity(self, session, vmname): 
        if self.verify_latency_sensitivity(session, vmname):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            data = data.replace('sched.cpu.latencySensitivity = "normal"', 'sched.cpu.latencySensitivity = "high"')
            data = data.replace('"', '\\"')
            # print( data )
            stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
            # return False if stderr.read() else True
            return True
 
    # configuring the NIC adapter type
    def config_nic_adapter_type(self, session, vmname, adapter):
        if self.verify_nic_adapter_type(session, vmname, adapter):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep ethernet{vmUtil.get_vnic_no(session,vmname)}.virtualDev -i')
            r = stdout.read().decode()
            st = re.search('"(.*?)"', r)
            if st:
                exist = st.group()
                exist = exist.strip('"')
                data = data.replace(f'ethernet{vmUtil.get_vnic_no(session,vmname)}.virtualDev = "{exist}"',f'ethernet{vmUtil.get_vnic_no(session,vmname)}.virtualDev = "{adapter}"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                return False if stderr.read() else True
            else:
                data += f'ethernet{vmUtil.get_vnic_no(session,vmname)}.virtualDev = "{adapter}"'
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                return False if stderr.read() else True

    # configuring the TX thread allocation
    def config_tx_thread_allocation(self, session, vmname, vnic):
        if self.verify_tx_thread_allocation(session, vmname, vnic):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            #for vnic in set(vmUtil.get_vnic_no(session, vmname)):
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep ethernet{vnic}.ctxPerDev -i')
            r = stdout.read().decode()
            flag = re.search('"(.*?)"', r)
            # print(f'ethernet{vnic}.ctxPerDev : {flag}')
            if flag:
                data = data.replace(f'ethernet{vnic}.ctxPerDev = "0"', f'ethernet{vnic}.ctxPerDev = "1"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                return False if stderr.read() else True
            else:
                # print(f'addding tx thread')
                data += f'ethernet{vnic}.ctxPerDev = "1"'
                # print(f'addding tx thread {data}')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                return False if stderr.read() else True


    # configuration SysContext
    def config_sys_context(self, session, vmname, vcpu):
        if self.verify_sys_context(session, vmname, vcpu):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.cpu.latencySensitivity.sysContexts -i')
            r = stdout.read().decode()
            st = re.search('"(.*?)"', r)
            if st:
                cpu = st.group()
                cpu = cpu.strip('"')
                data = data.replace(f'sched.cpu.latencySensitivity.sysContexts = "{cpu}"', f'sched.cpu.latencySensitivity.sysContexts = "{vcpu}"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                return False if stderr.read() else True
            else:
                data += f'sched.cpu.latencySensitivity.sysContexts = "{vcpu}"'
                data = data.replace('"', '\\"')
                vmUtil.power_off_vm(session, vmname)
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                vmUtil.power_on_vm(session, vmname)
                return False if stderr.read() else True

    # configuration of cpu reservation
    def config_cpu_reservation(self, session, vmname):
        if self.verify_cpu_reservation(session,vmname):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.cpu.min -i')
            r = stdout.read().decode()
            st = re.search('"(.*?)"', r)
            max_size = int(vmUtil.get_vcpu_core(session, vmname)) * int(vmUtil.get_cpu_speed(session))
            # print(f'config cpu reserve : {max_size}')
            if st:
                old = st.group()
                old = old.strip('"')
                data = data.replace(f'sched.cpu.min = "{old}"', f'sched.cpu.min = "{max_size}"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                return False if stderr.read() else True
            else:
                data += f'sched.cpu.min = "{max_size}"'
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                return False if stderr.read() else True

    # configuration cpu share
    def config_cpu_share(self, session, vmname):
        if self.verify_cpu_share(session, vmname):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.cpu.shares -i')
            r = stdout.read().decode()
            st = re.search('"(.*?)"', r)
            if st:
                old = st.group()
                old = old.strip('"')
                data = data.replace(f'sched.cpu.shares = "{old}"','sched.cpu.shares = "high"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                return False if stderr.read() else True
            else:
                data += 'sched.cpu.shares = "high"'
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                return False if stderr.read() else True

    # configuration on Memory share
    def config_mem_share(self, session, vmname):
        if self.verify_mem_share(session, vmname):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.mem.shares -i')
            r = stdout.read().decode()
            st = re.search('"(.*?)"', r)
            if st:
                old = st.group()
                old = old.strip('"')
                data = data.replace(f'sched.mem.shares = "{old}"','sched.mem.shares = "high"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                return False if stderr.read() else True
            else:
                data += 'sched.mem.shares = "high"'
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                return False if stderr.read() else True

    # configuration on Memory reservation
    def config_mem_reservation(self, session, vmname):
        if self.verify_mem_reservation(session,vmname):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.mem.minSize -i')
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.mem.minSize -i')
            r = stdout.read().decode()
            st = re.search('"(.*?)"', r)
            if st:
                size = st.group()
                size = size.strip('"')
                data = data.replace(f'sched.mem.minSize = "{size}"',f'sched.mem.minSize = "{vmUtil.get_vm_memory(session, vmname)}"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                return False if stderr.read() else True




    #configuring Numa Affinity
    def config_numa_affinity(self, session, vmname, vmnic):
        if self.verify_numa_affinity(session, vmname, vmnic):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep numa.nodeAffinity')
            a = stdout.read().decode()
            e = vmUtil.get_numa_node(session, vmname)
            if a:
                data += f'numa.nodeAffinity = "{e}"'
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                return False if stderr.read() else True
                # return True
            else:
                stdin, stdout, stderr = session.exec_command(f'vsish -e get /net/pNics/{vmnic}/properties | grep NUMA')
                r = stdout.read().decode()
                st = re.search('\d', r)
                if st:
                    numa = st.group()
                    old = vmUtil.get_numa_node(session, vmname)
                    data = data.replace(f'numa.nodeAffinity = "{old}"', f'numa.nodeAffinity = "{numa}"')
                    data = data.replace('"', '\\"')
                    stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx')
                    return False if stderr.read() else True
                    # return True
                else:
                    _LOGGER.error(f'unable to configure node affinity for vmnic : {vmnic}')



    """
        verification  function for virtual machine optimization 
    """

    # latency Sensitivity
    def verify_latency_sensitivity(self, session, vmname): 
        vmid = vmUtil.get_vm_id(session, vmname)
        if vmid != '':
            _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep latency')
            # print(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep latency')
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep latency')
            r = stdout.read().decode()
            _LOGGER.debug(f'{r}')
            st = re.search('"(.*?)"', r)
            if st:
                status = st.group()
                return True if status.strip('"') == 'high' else False
            else:
                return False

    # verification of CPU reservation
    def verify_cpu_reservation(self, session, vmname):
        _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.cpu.min -i ')
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.cpu.min -i')
        r = stdout.read().decode()
        _LOGGER.debug(f'{r}')
        st = re.search('"(.*?)"', r)
        max_size = int(vmUtil.get_vcpu_core(session, vmname)) * int(vmUtil.get_cpu_speed(session))
        print(f'max_size cpu reservation: {max_size}')
        if st:
            status = st.group()
            return True if int(status.strip('"')) == max_size else False

    # verification of CPU share
    def verify_cpu_share(self,session,vmname):
        _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.cpu.shares -i ')
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.cpu.shares -i')
        r = stdout.read().decode()
        _LOGGER.debug(f'{r}')
        st = re.search('"(.*?)"', r)
        if st:
            status = st.group()
            return True if status.strip('"') == 'high' else False

    # verification of Memory shares
    def verify_mem_share(self, session, vmname):
        _LOGGER.debug(f'executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.mem.shares -i')
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.mem.shares -i')
        r = stdout.read().decode()
        _LOGGER.debug(f'{r}')
        st = re.search('"(.*?)"', r)
        if st:
            status = st.group()
            return True if status.strip('"') == 'high' else False

    # verification of Memory reservation
    def verify_mem_reservation(self, session, vmname ):
        _LOGGER.debug(f'executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.mem.minSize -i')
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.mem.minSize -i')
        r = stdout.read().decode()
        _LOGGER.debug(f'{r}')
        st = re.search('"(.*?)"', r)
        if st:
            status = st.group()
            return True if status.strip('"') == vmUtil.get_vm_memory(session, vmname) else False

    # verification of the Virtual NIC adapter
    def verify_nic_adapter_type(self, session, vmname, adapter):
        for v_nic in set(vmUtil.get_vnic_no(session, vmname)):
            _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep ethernet{v_nic}.virtualDev -i')
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx |grep ethernet{v_nic}.virtualDev -i')
            r = stdout.read().decode()
            _LOGGER.info(f'networtk adapter : {r}')
            st = re.search('"(.*?)"', r)
            if st:
                adapter_type = st.group()
                # print(f'adapeter in print : {adapter_type}')
                return True if (adapter_type.strip('"')) == adapter else False
            else:
                return False

    # verification of the Tx thread allocation is enable
    def verify_tx_thread_allocation(self, session, vmname, vnic):
        for vnic in set(vmUtil.get_datastore(session, vmname)):
            _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vnic}/{vmname}/test.vmx | grep ethernet{vnic}ctxPerDev -i')
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vnic}/{vmname}/test.vmx | grep ethernet{vnic}.ctxPerDev -i')
            r = stdout.read().decode()
            # print(f'verify tx :{r}')
            _LOGGER.debug(f'{r}')
            st = re.search('"(.*?)"', r)
            if st:
                status = st.group()
                return True if int(status.strip('"')) == 1 else False
            else:
                # print('nope')
                return False

    # verification of sysContext
    def verify_sys_context(self, session, vmname, vcpu):
        _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.cpu.latencySensitivity.sysContexts -i')
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/test.vmx | grep sched.cpu.latencySensitivity.sysContexts -i')
        r = stdout.read().decode()
        _LOGGER.debug(f'{r}')
        st = re.search('"(.*?)"', r)
        if st:
            cpu = st.group()
            return True if int(cpu.strip('"')) == vcpu else False

    # verification of NUMA affinity
    def verify_numa_affinity(self, session, vmname, vmnic):
        _LOGGER.debug(f'Executing command : vsish -e get /net/pNics/{vmnic}/properties | grep NUMA ')
        stdin, stdout, stderr = session.exec_command(f'vsish -e get /net/pNics/{vmnic}/properties | grep NUMA')
        r = stdout.read().decode()
        _LOGGER.debug(f'numa affinity to set : {r}')
        st = re.search('\d', r)
        if st:
            numa = st.group()
            old = vmUtil.get_numa_node(session, vmname)
            # print(f'True value : {numa} \n exist value : {old}')
            return True if old == numa else False
        else:
            return False


# _LOGGER.debug(f'Executing command : ')