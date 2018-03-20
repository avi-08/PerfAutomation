"""
    Basic Utility for the VM(s)
"""
from __future__ import print_function
import  re

class VmUtility:

    def __init__(self):
        pass

    # Get VMid
    def get_vm_id(client, vmName):
        """

        :param vmName: Name of the Virtual Machine
        :return: Virtual machine ID
        """
        stdin, stdout, stderr = client.exec_command(f'vim-cmd vmsvc/getallvms | grep {vmName}')
        return (stdout.read().decode().split(' ')[0])

    # Power on VM
    def power_on_vm(client, vmName):
        """

        :param vmName: Name of the Virtual Machine
        :return:
        """
        # print(f'PowerOn: {vmName}')
        vmid = VmUtility.get_vm_id(client, vmName)
        if len(vmid) == 0:
            print('vm not found')
        else:
            stdin, stdout, stderr = client.exec_command('vim-cmd vmsvc/power.on {}'.format(int(vmid)))

    # Power off VM
    def power_off_vm(client, vmName):
        """

        :param vmName: Name of the Virtual Machine
        :return:
        """
        vmid = VmUtility.get_vm_id(client, vmName)
        print(f'Vmid :{vmid}')
        if len(vmid) == 0:
            print('vm not found')
        else:
            stdin, stdout, stderr = client.exec_command('vim-cmd vmsvc/power.off {}'.format(int(vmid)))

    # Function to Read .vmx file
    def readVMX(client, datastore, vmName):
        """
        
        :param datastore: datastore where Virtual machine is deployed
        :param vmName: name of the virtual machine
        :return: virtual machine's .vmx file data
        """
        stdin, stdout, stderr = client.exec_command(f'cat vmfs/volumes/{datastore}/{vmName}/{vmName}.vmx')
        return (stdout.read().decode())

    #To get datastore of a VM
    def get_datastore(client, vmName):
        """
        
        :param vmName: Name of the virtual machine
        :return: Name of the datastore
        """
        stdin, stdout, stderr = client.exec_command(
            f'vim-cmd vmsvc/get.config {get_vm_id(client,vmName)} | grep vmPathname -i')
        r = stdout.read().decode()
        st = re.search('\[(.*?)\]', r)
        if st:
            datastore = st.group()
            datastore = datastore.strip('[').strip(']')
            if ' ' in datastore:
                return datastore.replace(' ', '\ ', 1)
            else:
                return datastore

    def get_vcpu_core(self,session,vmName):
        """

        :param session:
        :param vmName: Name of the virtual machine.
        :return: number of the cpu core for the virtual machine.
        """
        return 3


    #Getting the hardware Details
    def cpu_speed(self,session):
        """

        :param session:
        :return:
        """
        return '2596'

    #To get the vnic number
    def get_vnic_no(client, vmName):
        """
        
        :param vmName: Name of the Virtual Machine
        :return: vnic no. for that virtual machine
        """
        stdin, stdout, stderr = client.exec_command(f'cat vmfs/volumes/{get_datastore(client, vmName)}/{vmName}/test.vmx | grep ether -i')
        st = stdout.read().decode()
        m = re.search('[0-9]', st)
        if m:
            number = m.group()
            return number
        return '0'