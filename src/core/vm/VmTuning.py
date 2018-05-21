"""
This script contains all the functions to validate and apply the virtual machine optimizations.
This script tunes Virtual Machine for following properties according to best practices for the particular version of host.
1.

"""
from __future__ import print_function
from src.core.vm import VmUtil
import re
from src.util import LogUtil

__author__ = "Somanath"

vmUtil = VmUtil.VmUtility()
_LOGGER = LogUtil.LogUtil()

class VmTunning :
    
    def __init__(self):
        pass

    def clean_file (self, session, vmname):
        """
        Removing any Extra whitespaces and blank lines if any
        :param session:  paramiko SSHClient object
        :param vmname:  Name of the Virtual machine
        :return:
        """
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
        data = stdout.read().decode()
        data = data.split('\n')
        res = ''
        for d in data:
            if d != '':
                res += d.strip() + '\n'
        res = res.replace('"', '\\"')
        stdin, stdout, stderr = session.exec_command(f'echo "{res}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')

    def config_latency_sensitivity(self, session, vmname):
        """
        Configure virtual machine's latency Sensitivity to high
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual machine
        :return:
        """
        if self.verify_latency_sensitivity(session, vmname):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            data = data.replace('sched.cpu.latencySensitivity = "normal"', 'sched.cpu.latencySensitivity = "high"')
            data = data.replace('"', '\\"')
            stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
            # return False if stderr.read() else True
            return True

    def config_nic_adapter_type(self, session, vmname, adapter,vnic):
        """
        configure the adapter type of the Virtual machine
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual machine
        :param adapter: Type of adapter to be configured
        :return:
        """
        if self.verify_nic_adapter_type(session, vmname, adapter, vnic):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep ethernet{vnic}.virtualDev -i')
            r = stdout.read().decode()
            st = re.search('"(.*?)"', r)
            if st:
                exist = st.group()
                exist = exist.strip('"')
                data = data.replace(f'ethernet{vnic}.virtualDev = "{exist}"',f'ethernet{vnic}.virtualDev = "{adapter}"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                return False if stderr.read() else True
            else:
                data += f'ethernet{vnic}.virtualDev = "{adapter}"'
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                return False if stderr.read() else True

    def config_tx_thread_allocation(self, session, vmname, vnic):
        """
        Configuring the virtual machine's Tx-thread is enabled
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual Machine
        :param vnic: vNIC number
        :return:
        """
        if self.verify_tx_thread_allocation(session, vmname, vnic):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            #for vnic in set(vmUtil.get_vnic_no(session, vmname)):
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep ethernet{vnic}.ctxPerDev -i')
            r = stdout.read().decode()
            flag = re.search('"(.*?)"', r)
            # print(f'ethernet{vnic}.ctxPerDev : {flag}')
            if flag:
                data = data.replace(f'ethernet{vnic}.ctxPerDev = "0"', f'ethernet{vnic}.ctxPerDev = "1"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                return False if stderr.read() else True
            else:
                # print(f'addding tx thread')
                data += f'ethernet{vnic}.ctxPerDev = "1"'
                # print(f'addding tx thread {data}')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                return False if stderr.read() else True

    def config_sys_context(self, session, vmname, vcpu):
        """
        Configure the virtual machine's number of threads to be pinned
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual Machine
        :param vcpu: Noumbetr of vCPU to be configured
        :return:
        """
        if self.verify_sys_context(session, vmname, vcpu):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.cpu.latencySensitivity.sysContexts -i')
            r = stdout.read().decode()
            st = re.search('"(.*?)"', r)
            if st:
                cpu = st.group()
                cpu = cpu.strip('"')
                data = data.replace(f'sched.cpu.latencySensitivity.sysContexts = "{cpu}"', f'sched.cpu.latencySensitivity.sysContexts = "{vcpu}"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                return False if stderr.read() else True
            else:
                data += f'sched.cpu.latencySensitivity.sysContexts = "{vcpu}"'
                data = data.replace('"', '\\"')
                vmUtil.power_off_vm(session, vmname)
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                vmUtil.power_on_vm(session, vmname)
                return False if stderr.read() else True

    def config_cpu_reservation(self, session, vmname):
        """
        configuring the virtual machines's CPU reservation to it's maximum capacity
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual machine
        :return:
        """
        if self.verify_cpu_reservation(session,vmname):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.cpu.min -i')
            r = stdout.read().decode()
            st = re.search('"(.*?)"', r)
            max_size = int(vmUtil.get_vcpu_core(session, vmname)) * int(vmUtil.get_cpu_speed(session))
            # print(f'config cpu reserve : {max_size}')
            if st:
                old = st.group()
                old = old.strip('"')
                data = data.replace(f'sched.cpu.min = "{old}"', f'sched.cpu.min = "{max_size}"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                return False if stderr.read() else True
            else:
                data += f'sched.cpu.min = "{max_size}"'
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                return False if stderr.read() else True

    def config_cpu_share(self, session, vmname):
        """
        Configuring the virtual machine's CPU share to it's maximum capacity
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual machine
        :return:
        """
        if self.verify_cpu_share(session, vmname):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.cpu.shares -i')
            r = stdout.read().decode()
            st = re.search('"(.*?)"', r)
            if st:
                old = st.group()
                old = old.strip('"')
                data = data.replace(f'sched.cpu.shares = "{old}"','sched.cpu.shares = "high"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                return False if stderr.read() else True
            else:
                data += 'sched.cpu.shares = "high"'
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                return False if stderr.read() else True

    def config_mem_share(self, session, vmname):
        """
        Configuring the virtual machine's memory share to it's maximum capacity
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual Machine
        :return:<boolean> Return True if the configuration is sucessfully made.
        """
        if self.verify_mem_share(session, vmname):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.mem.shares -i')
            r = stdout.read().decode()
            st = re.search('"(.*?)"', r)
            if st:
                old = st.group()
                old = old.strip('"')
                data = data.replace(f'sched.mem.shares = "{old}"','sched.mem.shares = "high"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                return False if stderr.read() else True
            else:
                data += 'sched.mem.shares = "high"'
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                return False if stderr.read() else True

    def config_mem_reservation(self, session, vmname):
        """
        Configuring the virtual machine's memory reservation to it's maximum capacity
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual Machine
        :return:
        """
        if self.verify_mem_reservation(session,vmname):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.mem.minSize -i')
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.mem.minSize -i')
            r = stdout.read().decode()
            st = re.search('"(.*?)"', r)
            if st:
                size = st.group()
                size = size.strip('"')
                data = data.replace(f'sched.mem.minSize = "{size}"',f'sched.mem.minSize = "{vmUtil.get_vm_memory(session, vmname)}"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                return False if stderr.read() else True

    def config_numa_affinity(self, session, vmname, vmnic):
        """
        Configuring the virtual machine NUMA value to the NUMA value of the physical NIC
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual Machine
        :param vmnic: Name of the vmNIC
        :return:
        """
        if self.verify_numa_affinity(session, vmname, vmnic):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep numa.nodeAffinity')
            a = stdout.read().decode()
            e = vmUtil.get_numa_node(session, vmname)
            if a:
                data += f'numa.nodeAffinity = "{e}"'
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
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
                    stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                    return False if stderr.read() else True
                else:
                    _LOGGER.error(f'unable to configure node affinity for vmnic : {vmnic}')

    def get_syscontext_value(self, session, vmname, flag):
        """
        Calculating the sysContext value for the virtual machine
        :param session: paramiko SSHClient object
        :param vmname: Name of the virtual machine
        :return:
        """
        if flag:
            return 8
        return 2

    def get_latency_sensitivity(self, session, vmname):
        """
        Get latency sensitivity status
        :param session: paramiko SSHClient object
        :param vmname: Name of the virtual machine
        :return:
        """
        vmid = vmUtil.get_vm_id(session, vmname)
        if vmid != '':
            command = f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep "latencySensitivity ="'
            _LOGGER.info(f'Executing command :{command}')
            stdin, stdout, stderr = session.exec_command(command)
            r = stdout.read().decode()
            mod = {}
            if r:
                mod['command'] = command
                mod['out'] = r
            else:
                mod['command'] = command
                mod['out'] = ''
            return mod

    def verify_latency_sensitivity(self, session, vmname):
        """
        Checking the latency sensitivity of the virtual machine is set to high
        :param session: paramiko SSHClient object
        :param vmname: Name of the virtual machine
        :return:
        """
        vmid = vmUtil.get_vm_id(session, vmname)
        if vmid != '':
            _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep "latencySensitivity ="')
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep "latencySensitivity ="')
            r = stdout.read().decode()
            _LOGGER.debug(f'{r}')
            st = re.search('"(.*?)"', r)
            if st:
                status = st.group()
                return True if status.strip('"') == 'high' else False
            else:
                return False

    def get_cpu_reservation(self, session, vmname):
        """
        Get the CPU reservation detailss
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual machine
        :return:
        """
        command = f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.cpu.min -i'
        stdin, stdout, stderr = session.exec_command(command)
        r = stdout.read().decode()
        mod = {}
        if r:
            mod['command'] = command
            mod['out'] = r
        else:
            mod['command'] = command
            mod['out'] = ''
        return mod

    def verify_cpu_reservation(self, session, vmname):
        """
        Checking the virtual machine's CPU reservation is set to it's maximum capacity
        :param session: paramiko SSHClient object
        :param vmname: Name of the virtual Machine
        :return:
        """
        _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.cpu.min -i ')
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.cpu.min -i')
        r = stdout.read().decode()
        _LOGGER.debug(f'output : {r}')
        st = re.search('"(.*?)"', r)
        max_size = int(vmUtil.get_vcpu_core(session, vmname)) * int(vmUtil.get_cpu_speed(session))
        _LOGGER.info(f'max size cpu reservation available : {max_size}')
        if st:
            status = st.group()
            return True if int(status.strip('"')) == max_size else False

    def get_cpu_share(self, session, vmname ):
        """
        Get the virtual machine CPU share detail
        :param session: paramiko SSHClient object
        :param vmname: Name of the virtual machine
        :return:
        """
        command = f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.cpu.shares -i'
        stdin, stdout, stderr = session.exec_command(command)
        r = stdout.read().decode()
        mod = {}
        if r:
            mod['command'] = command
            mod['out'] = r
        else:
            mod['command'] = command
            mod['out'] = ''
        return mod

    def verify_cpu_share(self, session, vmname):
        """
        Checking the virtual machine's CPU share is set to it's maximum capacity
        :param session: paramiko SSHClient object
        :param vmname: Name of the virtual machine
        :return:
        """
        _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.cpu.shares -i ')
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.cpu.shares -i')
        r = stdout.read().decode()
        _LOGGER.debug(f'{r}')
        st = re.search('"(.*?)"', r)
        if st:
            status = st.group()
            return True if status.strip('"') == 'high' else False

    def get_mem_share(self, session, vmname):
        """
        get the virtual machine memory share detail
        :param session: paramiko SSHClient object
        :param vmname: Name of the virtual machine
        :return:
        """
        command = f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.mem.shares -i'
        stdin, stdout, stderr = session.exec_command(command)
        r = stdout.read().decode()
        mod = {}
        if r:
            mod['command'] = command
            mod['out'] = r
        else:
            mod['command'] = command
            mod['out'] = ''
        return mod

    def verify_mem_share(self, session, vmname):
        """
        Checking the memory share is set to it's maximum capacity
        :param session: paramiko SSHClient object
        :param vmname: Name of the virtual machine
        :return:
        """
        _LOGGER.debug(f'executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.mem.shares -i')
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.mem.shares -i')
        r = stdout.read().decode()
        _LOGGER.debug(f'{r}')
        st = re.search('"(.*?)"', r)
        if st:
            status = st.group()
            return True if status.strip('"') == 'high' else False

    def get_mem_reservation(self, session, vmname):
        """
        Get the virtual machine's memory reservation
        :param session:
        :param vmname:
        :return:
        """
        command = f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.mem.minSize -i'
        stdin, stdout, stderr = session.exec_command(command)
        r = stdout.read().decode()
        mod = {}
        if r:
            mod['command'] = command
            mod['out'] = r
        else:
            mod['command'] = command
            mod['out'] = ''
        return mod

    def verify_mem_reservation(self, session, vmname ):
        """
        Checking the memory reservation is set to it's  maximum capacity
        :param session: paramiko SSHClient object
        :param vmname: Name of the virtual machine
        :return:
        """
        _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.mem.minSize -i')
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.mem.minSize -i')
        r = stdout.read().decode()
        _LOGGER.debug(f'{r}')
        st = re.search('"(.*?)"', r)
        if st:
            status = st.group()
            return True if status.strip('"') == vmUtil.get_vm_memory(session, vmname) else False

    def get_nic_adapter_type(self, session,vmname,vnic):
        """
        Get virtual machine NIC adapeter type
        :param session:
        :param vmname:
        :return:
        """
        command = f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx |grep ethernet{vnic}.virtualDev -i'
        stdin, stdout, stderr = session.exec_command(command)
        r = stdout.read().decode()
        mod = {}
        if r:
            mod['command'] = command
            mod['out'] = r
        else:
            mod['command'] = command
            mod['out'] = ''
        return mod

    def verify_nic_adapter_type(self, session, vmname, adapter,vnic):
        """
        Checking the virtual machine adapter type is same as the required adapter type
        :param session: paramiko SSHClient object
        :param vmname: Name of the virtual machine
        :param adapter: Name of the adapter type
        :return:
        """
        #for v_nic in set(vmUtil.get_vnic_no(session, vmname)):
        _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep ethernet{vnic}.virtualDev -i')
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx |grep ethernet{vnic}.virtualDev -i')
        r = stdout.read().decode()
        _LOGGER.info(f'networtk adapter : {r}')
        st = re.search('"(.*?)"', r)
        if st:
            adapter_type = st.group()
            return True if (adapter_type.strip('"')) == adapter else False
        else:
            return False

    def get_tx_thread_allocation(self, session, vmname, vnic):
        """
        Get virtual machine Tx thread detail of a specific vNIC
        :param session: paramiko SSHClient object
        :param vmname: Name of the virtual machine
        :param vnic: vNIC number
        :return:
        """
        command = f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep ethernet{vnic}.ctxPerDev -i'
        stdin, stdout, stderr = session.exec_command(command)
        r = stdout.read().decode()
        mod = {}
        if r:
            mod['command'] = command
            mod['out'] = r
        else:
            mod['command'] = command
            mod['out'] = ''
        return mod

    def verify_tx_thread_allocation(self, session, vmname, vnic):
        """
        Checking the Tx-thread of the vNIC is exist and enabled
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual Machine
        :param vnic: vNIC number
        :return:
        """
        # for vnic in set(vmUtil.get_vnic_no(session, vmname)):
        _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep ethernet{vnic}.ctxPerDev -i')
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep ethernet{vnic}.ctxPerDev -i')
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
    def get_sys_context(self, session, vmname):
        """
        Get virtual machine SysContext Detail
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual machine
        :return:
        """
        command = f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.cpu.latencySensitivity.sysContexts -i'
        _LOGGER.info(f'Executing command : {command}')
        stdin, stdout, stderr = session.exec_command(command)
        r = stdout.read().decode()
        mod = {}
        if r:
            mod['command'] = command
            mod['out'] = r
        else:
            mod['command'] = command
            mod['out'] = ''
        return mod

    def verify_sys_context(self, session, vmname, vcpu):
        """
        Checking the SysContext value is same as the required value
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual Machine
        :param vcpu: Number of vCPU to be pinned
        :return:
        """
        _LOGGER.debug(f'Executing command : cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.cpu.latencySensitivity.sysContexts -i')
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep sched.cpu.latencySensitivity.sysContexts -i')
        r = stdout.read().decode()
        _LOGGER.debug(f'{r}')
        st = re.search('"(.*?)"', r)
        if st:
            cpu = st.group()
            return True if int(cpu.strip('"')) == vcpu else False

    def get_numa_affinity(self, session, vmnic):
        """
        Getting the virtual machine's NUMA affinity details
        :param session: paramiko SSHClient object
        :param vmnic: name of the vmNIC
        :return:
        """
        command = f'vsish -e get /net/pNics/{vmnic}/properties | grep NUMA'
        stdin, stdout, stderr = session.exec_command(command)
        r = stdout.read().decode()
        mod = {}
        if r:
            mod['command'] = command
            mod['out'] = r
        else:
            mod['command'] = command
            mod['out'] = ''
        return mod

    def verify_numa_affinity(self, session, vmname, vmnic):
        """
        Checking the virtual machine NUMA is aligned to the NUMA of the physical NIC
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual Machine
        :param vmnic: Name of the vmNIC
        :return:
        """
        _LOGGER.debug(f'Executing command : vsish -e get /net/pNics/{vmnic}/properties | grep NUMA ')
        stdin, stdout, stderr = session.exec_command(f'vsish -e get /net/pNics/{vmnic}/properties | grep NUMA')
        r = stdout.read().decode()
        _LOGGER.debug(f'numa affinity to set : {r}')
        st = re.search('\d', r)
        if st:
            numa = st.group()
            old = vmUtil.get_numa_node(session, vmname)
            return True if old == numa else False
        else:
            return False

    def config_vm_hw_version(self, session, vmname, version):
        """
        configuring virtual machine hardware version
        :param session: paramiko SSHClient object
        :param vmname: Name of the virtual machine
        :param version: hardware version to be applied
        :return:
        """
        if self.verify_vm_hw_version(session, vmname, version):
            return True
        else:
            data = vmUtil.read_vmx(session, vmname)
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep  virtualHW.version')
            r = stdout.read().decode()
            st = re.search('"(.*?)"', r)
            if st:
                old = st.group()
                old = old.strip('"')
                data = data.replace(f'virtualHW.version = "{old}"', f'virtualHW.version = "{version}"')
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                return False if stderr.read() else True
            else:
                data += f'virtualHW.version = "{version}"'
                data = data.replace('"', '\\"')
                stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx')
                return False if stderr.read() else True

    def get_vm_hw_version(self, session, vmname):
        """
        Getting the hardware version of the Virtual machine
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual Machine
        :return:<dict> the command and the version
        """
        command = f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep  virtualHW.version'
        stdin, stdout, stderr = session.exec_command(command)
        r = stdout.read().decode()
        mod = {}
        if r:
            mod['command'] = command
            mod['out'] = r
        else:
            mod['command'] = command
            mod['out'] = ''
        return mod

    def verify_vm_hw_version(self, session, vmname, version):
        """
        Checking the hardware Version of the virtual Machine
        :param session: paramiko SSHClient object
        :param vmname: Name of the Virtual Machine
        :param version: proper hardware version
        :return:<boolean> returns true if the version is match
        """
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{vmUtil.get_datastore(session, vmname)}/{vmname}/{vmname}.vmx | grep  virtualHW.version')
        r = stdin.read().decode()
        _LOGGER.debug(f'Hardware Version of the Virtual Machine : {r}')
        st = re.search('"(.*?)"', r)
        if st:
            st = st.group()
            return True if st.strip().strip('"') == version else False
        else:
            return False

