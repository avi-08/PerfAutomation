import paramiko
from prettytable import PrettyTable
import re

class HostUtil:
    def __init__(self):
        pass

    def get_nics(self, client):
        print('details of the nics\n')
        stdin, stdout, stderr = client.exec_command('esxcfg-nics --list')
        a = stdout.read().decode()
        print(a)
        a = re.sub(' +', ' ', a).rstrip()
        a = a.split('\n')
        b = a[0].rstrip().split(' ')
        x = PrettyTable()
        x.title = 'NICs details'
        del b[8]
        # print(b)
        x.field_names = b
        for nic in a[1:]:
            a1 = nic.split(' ')
            b1 = a1[8:]
            b1 = ' '.join(b1)
            del a1[8:]
            a1.append(b1)
            # print (a1)
            x.add_row(a1)
        return x

    def get_mpath(self, client):
        print('mpath details\n')
        stdin, stdout, stderr = client.exec_command('esxcfg-mpath --list')
        return stdout.read().decode()

    def get_logical_device(self, client):
        print('logical devices known to the system')
        stdin, stdout, stderr = client.exec_command('esxcfg-scsidevs --compact-list')
        return stdout.read().decode()

    def get_vmknic(self, client):
        print('VMkernal NICs\n')
        stdin, stdout, stderr = client.exec_command('esxcfg-vmknic --list')
        return stdout.read().decode()

    def get_vswitch(self, client):
        print('Vswitch details and port group details\n')
        stdin, stdout, stderr = client.exec_command('esxcfg-vswitch --list')
        a = stdout.read().decode()
        print(a)

    def get_hw_cpu(self, client):
        print('Hardware CPU Details\n')
        stdin, stdout, stderr = client.exec_command('esxcli hardware cpu list')
        return stdout.read().decode()

    def get_hw_memory(self, client):
        print('Hardware Memory Details\n')
        stdin, stdout, stderr = client.exec_command('esxcli hardware memory get')
        a = stdout.read().decode().lstrip().rstrip()
        a = re.sub(' +', ' ', a).split('\n')
        x = PrettyTable()
        x.title = 'Hardware Memory Details'
        x.field_names = ['key', 'value']
        b = {}
        for i in a:
            i = i.split(':')
            b[i[0]] = i[1]
            x.add_row(i)
        return (b)

    def get_platform_details(self, client):
        print('Platform details \n')
        stdin, stdout, stderr = client.exec_command('esxcli hardware platform get')
        a = stdout.read().decode().rstrip().lstrip()
        a = re.sub(' +', ' ', a).split('\n')
        x = PrettyTable()
        x.title = a[0]
        b = {}
        x.field_names = ['key', 'value']
        for i in a[1:]:
            i = i.split(':')
            b[i[0]] = i[1]
            x.add_row(i)
        return b

    def get_hw_clock(self, client):
        print('hardware clock Time\n')
        stdin, stdout, stderr = client.exec_command('esxcli hardware clock get')
        return stdout.read().decode()

    def get_host_ip(self, client):
        print('IPv4 addresses assigned to VMkernel network interfaces\n')
        stdin, stdout, stderr = client.exec_command('esxcli network ip interface ipv4 get')
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
        stdin, stdout, stderr = client.exec_command('esxcli  network ip dns server list')
        a = stdout.read().decode()
        a = a.rstrip().lstrip().split(':')
        b[a[0]] = [a[1]]
        stdin, stdout, stderr = client.exec_command('esxcli network ip get')
        a = stdout.read().decode()
        a = a.rstrip().lstrip().split(':')
        b[a[0]] = [a[1]]
        return b

    def get_vm_details(self, client):
        print('List of Virtual Machine in Host\n')
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
        print('List of Standard vSwitch\n')
        stdin, stdout, stderr = client.exec_command('esxcli network vswitch standard list')
        return stdout.read().decode()

    def get_vswitch_vds(self, client):
        print('List of Distributed vSwitch\n')
        stdin, stdout, stderr = client.exec_command('esxcli network vswitch dvs vmware list')
        return stdout.read().decode()

    def get_cpu_info(self, client):
        print('Get CPU info \n')
        stdin, stdout, stderr = client.exec_command('vsish -ep get /hardware/cpu/cpuInfo')
        return stdout.read().decode()

    def get_physical_adapter(self, client):
        print('Physical Storage Adapter')
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
        print('Virtual flash SSD device')
        stdin, stdout, stderr = client.exec_command('esxcli storage vflash device list')
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

    def get_network(self, client):
        stdin, stdout, stderr = client.exec_command('esxcli  network ip dns server list')
        a = stdout.read().decode()
        a = a.rstrip().lstrip().split(':')
        x = PrettyTable()
        x.add_column(a[0], (a[1],))
        stdin, stdout, stderr = client.exec_command('esxcli network ip get')
        a = stdout.read().decode()
        a = a.rstrip().lstrip().split(':')
        x.add_column(a[0], (a[1],))
        print(self.get_host_ip(client))
        return x