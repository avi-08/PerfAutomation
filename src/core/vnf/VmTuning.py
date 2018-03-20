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
import paramiko
import re
from src.util import VmUtil

__author__ = "Somanath"


class VmTunning :

    def __init__(self):
        pass

    """
        configration function for the Virtual machine optimization
    """

    # configration of the latency sensitivity
    def config_latency_sensitivity(session, vmName):
        """

        :param vmName: Name of the virtual machine
        :return:
        """
        data = VmUtil.read_vmx(session, vmName)
        data = data.replace('sched.cpu.latencySensitivity = "normal"', 'sched.cpu.latencySensitivity = "high"')
        data = data.replace('"', '\\"')
        stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx')

    # configure CPU reservation and shares

    # configure Memory reservation and shares

    # configuring the NIC adapter type
    def config_nic_adapter_type(session, vmName, exist, flag, adapter):
        """

        :param vmName: Name of the Virtual machine
        :param exist: adapter that exist already configured with
        :param flag: bool value
        :param adapter: Adapter need to be configured
        :return:
        """
        data = VmUtil.read_vmx(session, vmName)
        if flag:
            data = data.replace(f'ethernet{VmUtil.get_vnic_no(session,vmName)}.virtualDev = "{exist}"','ethernet{get_vnic_no(session,vmName)}.virtualDev = "{adapter}"')
            data = data.replace('"', '\\"')
            stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx')
        else:
            data += f'ethernet{VmUtil.get_vnic_no(session,vmName)}.virtualDev = "{adapter}"'
            data = data.replace('"', '\\"')
            stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx')

    # configuring the TX thread allocation
    def config_tx_thread_allocation(session, vmName, flag):
        """

        :param vmName: Name of the Virtual Machine
        :param flag: bool value
        :return:
        """
        data = VmUtil.read_vmx(session, vmName)
        if flag:
            data += f'ethernet{VmUtil.get_vnic_no(session,vmName)}.ctxPerDev = "1"'
            data = data.replace('"', '\\"')
            stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx')
        else:
            data = data.replace(f'ethernet{VmUtil.get_vnic_no(session,vmName)}.ctxPerDev = "0"','ethernet{get_vnic_no(session,vmName)}.ctxPerDev = "1"')
            data = data.replace('"', '\\"')
            stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx')

    # configuration SysContext
    def config_sys_context(session, vmName, old, vcpu, flag):
        """

        :param vmName: Name of the virtual machine
        :param old: Thread that is already configured
        :param vcpu: Thread(s) need to be configured
        :param flag: bool value
        :return: bool value
        """
        data = VmUtil.read_vmx(session, vmName)
        if flag:
            data = data.replace(f'sched.cpu.latencySensitivity.sysContexts = "{old}"',f'sched.cpu.latencySensitivity.sysContexts = "{vcpu}"')
            data = data.replace('"', '\\"')
            stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx')
            return True
        else:
            data += f'sched.cpu.latencySensitivity.sysContexts = "{vcpu}"'
            data = data.replace('"', '\\"')
            stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx')
            return True

    # configuration of cpu reservation
    def config_cpu_reservation(self,session, vmName,old, max_size, flag):
        """

        :param session:
        :param vmName: Name of the Virtual machine
        :param old: reservation that exist already
        :param max_size: maximum reservation can be done
        :param flag: bool value
        :return:
        """
        data = VmUtil.read_vmx(session, vmName)
        if flag:
            data = data.replace(f'sched.cpu.min = "{old}"', f'sched.cpu.min = "{max_size}"')
            data = data.replace('"', '\\"')
            stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx')
            return True
        else:
            data += f'sched.cpu.min = "{max_size}"'
            data = data.replace('"', '\\"')
            stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx')
            return True

    # configuration cpu share
    def config_cpu_share(self,session,vmName,old,flag):
        data = VmUtil.read_vmx(session, vmName)
        if flag:
            data = data.replace(f'sched.cpu.shares = "{old}"','sched.cpu.shares = "high"')
            data = data.replace('"', '\\"')
            stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx')
            return True
        else:
            data += 'sched.cpu.shares = "high"'
            data = data.replace('"', '\\"')
            stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx')
            return True

    #configuration on Memory share
    def config_mem_share(self,session,vmName,old,flag):
        data = VmUtil.read_vmx(session, vmName)
        if flag:
            data = data.replace(f'sched.mem.shares = "{old}"','sched.mem.shares = "high"')
            data = data.replace('"', '\\"')
            stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx')
            return True
        else:
            data += 'sched.mem.shares = "high"'
            data = data.replace('"', '\\"')
            stdin, stdout, stderr = session.exec_command(f'echo "{data}" > vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx')
            return True

    #configuration on Memory reservation

    """
        verification  function for virtual machine optimization 
    """

    # latency Sensitivity
    def verify_latency_sensitivity(session, vmName):
        """

        :param vmName: Name of the Virtual machine
        :return: bool value
        """
        vmid = VmUtil.get_vm_id(session, vmName)
        if vmid != '':
            stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx | grep latency')
            r = stdout.read().decode()
            st = re.search('"(.*?)"', r)
            if st:
                status = st.group()
                return status.strip('"').strip('"')

    # verification of CPU reservation
    def verify_cpu_reservation(self,session,vmName):
        """

        :param session:
        :param vmName: Name of the virtual machine
        :return: True if reservation is set to maximum
        """
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx | grep sched.cpu.min -i')
        r = stdout.read().decode()
        st = re.search('"(.*?)"', r)
        max_size = int(VmTunning.get_vcpu_core(session, vmName)) * int(VmTunning.cpu_speed(session))
        if st:
            status = st.group()
            if int(status.strip('"')) == max_size:
                return True
            else:
                VmTunning.config_cpu_reservation(session, vmName, status.strip('"'), max_size, True)
        else:
            VmTunning.config_cpu_reservation(session, vmName, '', max_size , False)

    # verification of CPU share
    def verify_cpu_share(self,session,vmName):
        """

        :param session:
        :param vmName: Name of the virtual machine
        :return: True if CPU share is set to high
        """
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx | grep sched.cpu.shares -i')
        r = stdout.read().decode()
        st = re.search('"(.*?)"', r)
        if st:
            status = st.group()
            if status.strip('"') == 'high':
                return True
            else:
                VmTunning.config_cpu_share(session, vmName, status.strip('"'), True)
        else:
            VmTunning.config_cpu_share(session, vmName, '', False)

    # verification of Memory shares
    def verify_mem_share(self, session, vmName):
        """

        :param session:
        :param vmName: Name of the virtual machine
        :return: True if Memory share is set to high
        """
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx | grep sched.mem.shares -i')
        r = stdout.read().decode()
        st = re.search('"(.*?)"', r)
        if st:
            status = st.group()
            if status.strip('"') == 'high':
                return True
            else:
                VmTunning.config_mem_share(session, vmName, status.strip('"'), True)
        else:
            VmTunning.config_mem_share(session, vmName, '', False)

    # verification of Memory reservation
    def verify_mem_reservation(self, session, vmName ):
        """

        :param session:
        :param vmName: Name of the virtual machine
        :return: True if Memory reservation is set to maximum
        """
        pass

    # verification of the Virtual NIC adapter
    def verify_nic_adapter_type(session, vmName, adapter):
        """

        :param vmName: Name of the Virtual machine
        :param adapter: Adapter to be configured
        :return: True if configured
        """
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx | grep virtualDev -i')
        r = stdout.read().decode()
        st = re.search('"(.*?)"', r)
        if st:
            apapter_type = st.group()
            if (apapter_type.strip('"')) == adapter:
                return True
            else:
                VmTunning.config_nic_adapter_type(session, vmName, apapter_type, True, adapter)
        else:
            VmTunning.config_nic_adapter_type(session, vmName, "", False, adapter)

    # verification of the Tx thread allocation is enable
    def verify_tx_thread_allocation(session, vmName):
        """

        :param vmName: Name of the Virtual Machine
        :return: True if configured
        """
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx | grep ctxPerDev -i')
        r = stdout.read().decode()
        st = re.search('"(.*?)"', r)
        if st:
            status = st.group()
            return True if int(status.strip('"')) == 1 else False
        else:
            VmTunning.config_tx_thread_allocation(session, vmName, True)

    # verification of sysContext
    def verify_sys_context(session, vmName, vcpu):
        """

        :param vmName: Name of the Virtual Machine
        :param vcpu: number of thread(s) to be pinned
        :return: True if configured
        """
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{VmUtil.get_datastore(session, vmName)}/{vmName}/test.vmx | grep sched.cpu.latencySensitivity.sysContexts -i')
        r = stdout.read().decode()
        print(r)
        st = re.search('"(.*?)"', r)
        if st:
            cpu = st.group()
            if int(cpu.strip('"')) == vcpu:
                return True
            else:
                return VmTunning.config_sys_context(session, vmName, int(cpu), vcpu, True)
        else:
            return VmTunning.config_sys_context(session, vmName, 0, vcpu, False)

    # verification of NUMA affinity