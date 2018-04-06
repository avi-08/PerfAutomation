import math
from prettytable import PrettyTable
import re


class HostUtil:
    def __init__(self):
        pass

    def get_nics(self, client):
        """
        Print the list of NICs and their settings.
        :param client: paramiko SSHClient object
        :return: <dict> NIC details
        """

        stdin, stdout, stderr = client.exec_command('esxcfg-nics --list')
        a = stdout.read().decode()
        a = re.sub(' +', ' ', a).rstrip()
        a = a.split('\n')
        b = a[0].rstrip().split(' ')
        del b[8]
        q = dict()
        q[b[0]], q[b[1]], q[b[2]] = [], [], []
        q[b[3]], q[b[4]], q[b[5]] = [], [], []
        q[b[6]], q[b[7]], q[b[8]] = [], [], []
        for nic in a[1:]:
            a1 = nic.split(' ')
            b1 = a1[8:]
            b1 = ' '.join(b1)
            del a1[8:]
            a1.append(b1)
            for i in range(0, len(a1)):
                q[b[i]].append(a1[i])
        return q

    def get_mpath(self, client):
        """
        List all Paths on the system with their detailed information.
        :param client: paramiko SSHClient object
        :return: <str> mpath Details
        """
        print('mpath details\n')
        stdin, stdout, stderr = client.exec_command('esxcfg-mpath --list')
        return stdout.read().decode()

    def get_logical_device(self, client):
        """
         List all Logical Devices known on this system with device information.
        :param client: paramiko SSHClient object
        :return: <str>
        """
        print('logical devices known to the system')
        stdin, stdout, stderr = client.exec_command('esxcfg-scsidevs --compact-list')
        return stdout.read().decode()

    def get_vmknic(self, client):
        """
        List VMkernel NICs.
        :param client: paramiko SSHClient object
        :return: <str> vmknic
        """
        print('VMkernal NICs\n')
        stdin, stdout, stderr = client.exec_command('esxcfg-vmknic --list')
        return stdout.read().decode()

    def get_vswitch(self, client):
        """
        List all the virtual switches.
        :param client: paramiko SSHClient object
        :return: <str> Virtual Switch Details
        """
        stdin, stdout, stderr = client.exec_command('esxcfg-vswitch --list')
        a = stdout.read().decode()
        print(a)

    def get_hw_cpu(self, client):
        """
        List all of the CPUs on this host.
        :param client: paramiko SSHClient object
        :return: <str>  Haedware Details
        """
        stdin, stdout, stderr = client.exec_command('esxcli hardware cpu list')
        return stdout.read().decode()

    def get_hw_memory(self, client):
        """
        Get information about memory.
        :param client: paramiko SSHClient object
        :return: <dict> Physical Memory details
        """
        stdin, stdout, stderr = client.exec_command('esxcli hardware memory get')
        a = stdout.read().decode().lstrip().rstrip()
        a = re.sub(' +', ' ', a).split('\n')
        b = {}
        for i in a:
            i = i.split(':')
            b[i[0]] = i[1]
        gib = float(int(re.sub('[a-zA-Z]', '', b['Physical Memory'])) / 1.074e+9)
        b['Physical Memory'] = str(math.ceil(gib * 100) / 100) + ' Gibibyte'
        return (b)

    def get_platform_details(self, client):
        """
        Get information about the platform
        :param client: paramiko SSHClient object
        :return: <dict> General Details
        """
        stdin, stdout, stderr = client.exec_command('esxcli hardware platform get')
        a = stdout.read().decode().rstrip().lstrip()
        a = re.sub(' +', ' ', a).split('\n')
        b = {}
        for i in a[1:]:
            i = i.split(':')
            b[i[0]] = i[1]
        stdin, stdout, stderr = client.exec_command('esxcli hardware clock get')
        a = stdout.read().decode()
        b['clock'] = a
        return b

    def get_hw_clock(self, client):
        """
        Disply the current hardware clock time.
        :param client: paramiko SSHClient object
        :return: <str> hardware clock of the host
        """
        print('hardware clock Time\n')
        stdin, stdout, stderr = client.exec_command('esxcli hardware clock get')
        return stdout.read().decode()

    def get_host_ip(self, client):
        """
         List the IPv4 addresses assigned to VMkernel network interfaces.
        :param client: paramiko SSHClient object
        :return: <dict> Host Network details
        """
        stdin, stdout, stderr = client.exec_command('esxcli network ip interface ipv4 get')
        a = stdout.read().decode()
        a = a.split('\n')
        data = re.sub(' +', ' ', a[1])
        c = {}
        s = count = 0
        for i in data:
            if i == ' ':
                c[a[0][s:count].strip()] = a[2][s:count].strip()
                s = count + 1
                count += 1
            count += 1
        stdin, stdout, stderr = client.exec_command('esxcli  network ip dns server list')
        a = stdout.read().decode()
        a = a.strip().split(': ')
        c[a[0]] = a[1]
        stdin, stdout, stderr = client.exec_command('esxcli network ip get')
        a = stdout.read().decode()
        a = a.strip().split(': ')
        c[a[0]] = a[1]
        return c

    def get_vm_details(self, client):
        """
        List networking information for the VM's that have active ports.
        :param client: paramiko SSHClient object
        :return: <dic> virtual machine details
        """
        stdin, stdout, stderr = client.exec_command('esxcli network vm list')
        a = stdout.read().decode()
        a = a.split('\n')
        data = re.sub(' +', ' ', a[1])
        l = []
        b = {}
        s = count = 0
        for i in data:
            if i == ' ':
                l.append((s, count))
                s = count + 1
                count += 1
            count += 1
        l.append((s, len(a[1])))
        for q in l:
            lt = []
            for i in a:
                lt.append(i[q[0]:q[1]].strip())
            key = lt[0]
            del lt[0:2]
            lt.remove('')
            b[key] = lt

        return b

    def get_vswitch_standard(self, client):
        """
        List the virtual switches current on the ESXi host
        :param client: paramiko SSHClient object
        :return: <str> Virtual Standard switch Details
        """
        print('List of Standard vSwitch\n')
        stdin, stdout, stderr = client.exec_command('esxcli network vswitch standard list')
        return stdout.read().decode()

    def get_vswitch_vds(self, client):
        """
        List the VMware vDs currently configured on the ESXi host.
        :param client: paramiko SSHClient object
        :return: <str> Virtual Distributed switch
        """
        print('List of Distributed vSwitch\n')
        stdin, stdout, stderr = client.exec_command('esxcli network vswitch dvs vmware list')
        return stdout.read().decode()

    def get_cpu_info(self, client):
        """
        Hardware CPU information
        :param client: paramiko SSHClient object
        :return: <dict> Host CPU information
        """
        stdin, stdout, stderr = client.exec_command('vsish -ep get /hardware/cpu/cpuInfo')
        return stdout.read().decode()

    def get_physical_adapter(self, client):
        """
         List all the SCSI Host Bus Adapters on the system.
        :param client: paramiko SSHClient object
        :return: <dict> Physial storage adapter details
        """
        stdin, stdout, stderr = client.exec_command('esxcli storage core adapter list')
        a = stdout.read().decode()
        a = a.split('\n')
        data = re.sub(' +', ' ', a[1])
        l = []
        b = {}
        s = count = 0
        for i in data:
            if i == ' ':
                l.append((s, count))
                s = count + 1
                count += 1
            count += 1
        l.append((s, len(a[1])))
        for q in l:
            lt = []
            for i in a:
                lt.append(i[q[0]:q[1]].strip())
            key = lt[0]
            del lt[0:2]
            lt.remove('')
            b[key] = lt
        return b

    def get_vflash(self, client):
        """
        List vflash SSD devices.
        :param client: paramiko SSHClient object
        :return: <dict> Virtual flash device details
        """
        stdin, stdout, stderr = client.exec_command('esxcli storage vflash device list')
        a = stdout.read().decode()
        a = a.split('\n')
        data = re.sub(' +', ' ', a[1])
        l = []
        b = {}
        c = {}
        s = count = 0
        for i in data:
            if i == ' ':
                l.append((s, count))
                c[a[0][s:count].strip()] = a[2][s:count].strip()
                s = count + 1
                count += 1
            count += 1
        l.append((s, len(a[1])))
        for q in l:
            lt = []
            for i in a:
                lt.append(i[q[0]:q[1]].strip())
            key = lt[0]
            del lt[0:2]
            lt.remove('')
            b[key] = lt
        return c
