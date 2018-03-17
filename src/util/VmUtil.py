"""
    Basic Utility for the VM(s)
"""
from __future__ import print_function

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
        print('\nReading {}.vmx file'.format(vmName))
        stdin, stdout, stderr = client.exec_command(f'cat vmfs/volumes/{datastore}/{vmName}/{vmName}.vmx')
        return (stdout.read().decode())