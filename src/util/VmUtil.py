"""
    Basic Utility for the VM(s)
"""
from __future__ import print_function
import logging
import re
_LOGGER = logging.getLogger(__name__)

class VmUtility:

    def __init__(self):
        pass

    #get virtual machine list
    def get_vm_list(self, client):
        """
        getting the Virtual machine list in that host
        :param client:
        :return: list of virtual machime(s) in host
        """
        a=[]
        _LOGGER.debug(f'Executing command : esxcli vm process list |grep display -i')
        stdin, stdout, stderr = client.exec_command('esxcli vm process list |grep display -i')
        r = stdout.read().decode()
        if r:
            a = re.sub(' +', ' ', r.replace('Display Name:', '')).strip(' ').split(' ')
            _LOGGER.debug(f' List of Virtual machine : {a}')
            return a
        else:
            return a

    # Extracting NUMA node of the virtual Machine
    def get_numa_node(self, session, vmname):
        _LOGGER.debug(f'cat vmfs/volumes/{self.get_datastore(session, vmname)}/{vmname}/test.vmx | grep numa.nodeAffinity')
        stdin, stdout, stderr = session.exec_command(f'cat vmfs/volumes/{self.get_datastore(session, vmname)}/{vmname}/test.vmx | grep numa.nodeAffinity')
        r = stdout.read().decode()
        _LOGGER.info(f'command Result : {r}')
        st = re.search('"(.*?)"', r)
        if st:
            status = st.group()
            status = status.strip('"')
            print(f'numa node in vmx : {status}')
            return status
        else:
            return False

    # Get VMid
    def get_vm_id(self, client, vmname):
        """

        :param vmname: Name of the Virtual Machine
        :return: Virtual machine ID
        """
        _LOGGER.debug(f'Executing command : vim-cmd vmsvc/getallvms | grep {vmname} ')
        stdin, stdout, stderr = client.exec_command(f'vim-cmd vmsvc/getallvms | grep {vmname}')
        r = stdout.read().decode()
        _LOGGER.debug(f'command Result : {r}')
        return r.split(' ')[0]

    # Power on VM
    def power_on_vm(self, client, vmname):
        """

        :param vmname: Name of the Virtual Machine
        :return:
        """
        vmid = self.get_vm_id(client, vmname)
        if len(vmid) == 0:
            _LOGGER.error(f'virtual machine {vmname} of id: {vmid} is not found')
            print('vm not found')
        else:
            _LOGGER.info(f'power on vm : {vmname}')
            _LOGGER.debug(f'Executing command : vim-cmd vmsvc/power.on {int(vmid)}')
            stdin, stdout, stderr = client.exec_command('vim-cmd vmsvc/power.on {}'.format(int(vmid)))
            _LOGGER.debug(stdout.read().decode())

    # Power off VM
    def power_off_vm(self, client, vmname):
        """

        :param vmname: Name of the Virtual Machine
        :return:
        """
        vmid = self.get_vm_id(client, vmname)
        # print(f'Vmid :{vmid}')
        if len(vmid) == 0:
            _LOGGER.error(f'virtual machine {vmname} of id: {vmid} is not found')
            print('vm not found')
        else:
            _LOGGER.debug(f'Executing command : vim-cmd vmsvc/power.off {int(vmid)}')
            _LOGGER.info(f'power off vm : {vmname}')
            stdin, stdout, stderr = client.exec_command('vim-cmd vmsvc/power.off {}'.format(int(vmid)))
            _LOGGER.debug(stdout.read().decode())

    # Function to Read .vmx file
    def read_vmx(self, client, vmname):
        """
        
        :param datastore: datastore where Virtual machine is deployed
        :param vmname: name of the virtual machine
        :return: virtual machine's .vmx file data
        """
        _LOGGER.debug(f'Executing command : cat vmfs/volumes/{self.get_datastore(client, vmname)}/{vmname}/test.vmx')
        stdin, stdout, stderr = client.exec_command(f'cat vmfs/volumes/{self.get_datastore(client, vmname)}/{vmname}/test.vmx')
        return (stdout.read().decode())

    #To get datastore of a VM
    def get_datastore(self, client, vmname):
        """
        
        :param vmname: Name of the virtual machine
        :return: Name of the datastore
        """
        stdin, stdout, stderr = client.exec_command(f'vim-cmd vmsvc/get.config { self.get_vm_id(client, vmname)} | grep vmPathname -i')
        r = stdout.read().decode()
        st = re.search('\[(.*?)\]', r)
        if st:
            datastore = st.group()
            datastore = datastore.strip('[').strip(']')
            if ' ' in datastore:
                return datastore.replace(' ', '\ ', 1)
            else:
                return datastore

    def get_vcpu_core(self,client ,vmname):
        """

        :param session:
        :param vmname: Name of the virtual machine.
        :return: number of the cpu core for the virtual machine.
        """
        _LOGGER.debug(f'Eccuting command : cat vmfs/volumes/{self.get_datastore(client, vmname)}/{vmname}/test.vmx | gerp numvcpus -i')
        stdin, stdout, stderr = client.exec_command(f'cat vmfs/volumes/{self.get_datastore(client, vmname)}/{vmname}/test.vmx | grep numvcpus -i')
        st = stdout.read().decode()
        m = re.search('"(.*?)"', st)
        if m:
            vcpu = m.group()
            _LOGGER.debug(f'{vmname} - Number of vcpu :{vcpu}')
            vcpu = vcpu.strip('"')
            # print(vcpu)
            return vcpu
        else:
            return 0


    #Getting the hardware Details
    def get_cpu_speed(self,session):
        """

        :param session:
        :return:
        """
        return 2596

    #To get the vnic number
    def get_vnic_no(self, client, vmname):
        """
        
        :param client: 
        :param vmname: Name of the Virtual Machine 
        :return: 
        """ 
        # stdin, stdout, stderr = client.exec_command(f'cat vmfs/volumes/{self.get_datastore(client, vmname)}/{vmname}/test.vmx | grep networkName -i')
        stdin, stdout, stderr = client.exec_command(f'vim-cmd vmsvc/get.config {self.get_vm_id(client,vmname)}  | grep ether -i')
        st = stdout.read().decode()
        # m = re.search('\d', st)
        vm_vnic = [int(s) for s in re.findall(r'-?\d+?\d*', st)]
        # print(vm_vnic)
        if len(vm_vnic):
            return vm_vnic
        else:
            return 0

    def get_vm_memory(self, client, vmname):

        stdin, stdout, stderr = client.exec_command(f'cat vmfs/volumes/{self.get_datastore(client, vmname)}/{vmname}/test.vmx | grep memSize -i')
        r = stdout.read().decode()
        m = re.search('"(.*?)"',r)
        if m:
            memsize = m.group()
            memsize = memsize.strip('"')
            return memsize

