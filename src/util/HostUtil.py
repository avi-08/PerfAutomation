import math, re
from src.util import ParserUtil


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
        a1 = a.split('\n\n')
        aa = a1[0].split('\n')
        b = {}
        b['Switch Name'] = list()
        b['Num Ports'] = list()
        b['Used Ports'] = list()
        b['Configured Ports'] = list()
        b['MTU'] = list()
        b['Uplinks'] = list()
        keys = re.split('\s{2,}', aa[0].strip())
        for i in range(1, len(aa)):
            value = re.split('\s{2,}', aa[i].strip())
            for i, key in enumerate(keys):
                b[key].append(value[i])
        # print (b)
        return b

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
        a = eval(stdout.read().decode())
        stdin, stdout, stderr = client.exec_command('vsish -ep get  /hardware/cpu/cpuModelName')
        a['cpuModelName'] = stdout.read().decode()
        return a

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

    def get_filesystem(self, client):
        """
        DataStore and its detail
        :param client: paramiko SSHClient object
        :return:<dict> Datastore Details
        """
        stdin, stdout, stderr = client.exec_command('esxcli storage filesystem list')
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
        for i, size in enumerate(b['Size']):
            s = float(b['Size'][i]) / 1.074e+9
            b['Size'][i] = str(math.ceil(s * 100) / 100) + ' GB'
            s = float(b['Free'][i]) / 1.074e+9
            b['Free'][i] = str(math.ceil(s * 100) / 100) + ' GB'
        return b

    def get_pg_name(self, client):
        """
        PortGroup name
        :param client:  paramiko SSHClient object
        :return: <dict> portGroup details
        """
        stdin, stdout, stderr = client.exec_command('esxcfg-vswitch --list')
        a = stdout.read().decode()
        a1 = a.split('\n\n')
        aa = a1[1].split('\n')
        b = {}
        b['PortGroup Name'] = list()
        b['VLAN ID'] = list()
        b['Used Ports'] = list()
        b['Uplinks'] = list()
        keys = re.split('\s{2,}', aa[0].strip())
        for i in range(1, len(aa)):
            value = re.split('\s{2,}', aa[i].strip())
            for j, key in enumerate(keys):
                b[key].append(value[j])
        return b

    def get_dvs_name(self, client):
        """
        Distributed Virtual Switch Details
        :param client: paramiko SSHClient object
        :return: <dict> dvs Details
        """
        stdin, stdout, stderr = client.exec_command('esxcfg-vswitch --list')
        a = stdout.read().decode()
        a1 = a.split('\n\n')
        aa = a1[2].split('\n')
        b = {}
        b['DVS Name'] = list()
        b['Num Ports'] = list()
        b['Used Ports'] = list()
        b['Configured Ports'] = list()
        b['MTU'] = list()
        b['Uplinks'] = list()
        keys = re.split('\s{2,}', aa[0].strip())
        keys = re.split('\s{2,}', aa[0].strip())
        for i in range(1, len(aa)):
            value = re.split('\s{2,}', aa[i].strip())
            for j, key in enumerate(keys):
                b[key].append(value[j])
        return b

    def get_dvport_id(self, client):
        """
        :param client: paramiko SSHClient object
        :return: <dict> dvport Id
        """
        stdin, stdout, stderr = client.exec_command('esxcfg-vswitch --list')
        a = stdout.read().decode()
        a1 = a.split('\n\n')
        aa = a1[3].split('\n')
        b = {}
        b['DVPort ID'] = list()
        b['In Use'] = list()
        b['Client'] = list()
        keys = re.split('\s{2,}', aa[0].strip())
        for i in range(1, len(aa)):
            value = re.split('\s{2,}', aa[i].strip())
            if value[1] == '1':
                for j, key in enumerate(keys):
                    b[key].append(value[j])
        return b

    def get_logical_device_details(self, client):
        """
        Logical device details
        :param client: paramiko SSHClient object
        :return: <dict>  logical device Details
        """
        stdin, stdout, stderr = client.exec_command('esxcfg-scsidevs --compact-list')
        a = stdout.read().decode()
        a1 = a.split('\n\n')
        aa = a1[0].split('\n')
        b = {}
        b['Device UID'] = list()
        b['Device Type'] = list()
        b['Size'] = list()
        b['Multipath'] = list()
        b['PluginDisplay Name'] = list()
        keys = re.split('\s{2,}', aa[0].strip())
        del keys[4]
        del keys[2]
        keys.append('Multipath')
        keys.append('PluginDisplay Name')
        for i in range(1, len(aa) - 1):
            value = re.split('\s{2,}', aa[i].strip())
            del value[2]
            for i, key in enumerate(keys):
                b[key].append(value[i])
        return b

    def hardware_detail_compact(self, client):
        """
        Hardware Detail for compact version
        :param client: paramiko SSHClient object
        :return: <dict> hardware Details for compact version
        """
        b = {}
        a = self.get_cpu_info(client)
        b['CPU Model Name'] = a['cpuModelName']
        b[
            'CPU sockets'] = f"{a['numPackages']} sockets, {(str(int(int(a['numCores'])/int(a['numPackages']))))} cores per socket\n"
        ls = []
        ss = self.get_vswitch(client)
        ds = self.get_dvs_name(client)
        for i in ss['Uplinks']:
            ls += i.split(',')
        for i in ds['Uplinks']:
            ls += i.split(',')
        a = self.get_nics(client)
        t = list()
        for l in ls:
            for i, val in enumerate(a['Name']):
                if l == val:
                    t.append(i)
        s = ''
        for no in t:
            for i, ai in enumerate(a):
                if i == 0 or i == 2 or i == 4 or i == 8:
                    for i, data in enumerate(a[ai]):
                        if i == no:
                            s += data + ' - '
            s += '\n'
        b['NIC Details'] = s
        t = ss['Switch Name'] + ds['DVS Name']
        b['Switch Name'] = ','.join(t)
        return b

    def get_server_details(self, client):
        """
        server Details for Compact version
        :param client: paramiko SSHClient object
        :return: <dict>  server details
        """
        b = {}
        a = self.get_platform_details(client)
        b['Model&Make'] = a[' Vendor Name'].strip() + ' ' + a[' Product Name']
        b['Serial Number'] = a[' Serial Number'].strip()
        a = self.get_cpu_info(client)
        b['Sockets'] = a['numPackages']
        b['core per Socket'] = (str(int(int(a['numCores']) / int(a['numPackages']))))
        c = re.search('(@.*)', a['cpuModelName'])
        c = c.group()
        c = c.strip('@').strip('"').strip()
        b['CPU Speed'] = c
        a = self.get_hw_memory(client)
        b['Physical Memory'] = a['Physical Memory']
        a = self.get_logical_device_details(client)
        b['No of HDD'] = len(a['Device UID'])
        a = self.get_nics(client)
        b['No of NIC'] = len(a['Description'])
        return b

    def get_current_powerstatus(self, client):
        """
        Getting the Current power Policy
        :return: <dict> current Power policy
        """
        stdin, stdout, stderr = client.exec_command('vsish  -ep get power/currentPolicy')
        a = eval(stdout.read().decode())
        return a

    def get_hoststats(self, client):
        """
        getting the host status
        :param client: paramiko SSHClient object
        :return: <dict> get the host status
        """
        stdin, stdout, stderr = client.exec_command('vsish  -ep get /power/hostStats')
        a = eval(stdout.read().decode())
        return a

    def get_pcpu_power_mgmt_states(self, client):
        stdin, stdout, stderr = client.exec_command('vsish  -ep get /power/pcpu/0/state')
        a = eval(stdout.read().decode())
        return a

    def list_env_details(self, client):
        parse = ParserUtil.Parser()
        f = open("env_details.txt", "a+")
        b = {}
        a = parse.dict_to_table(self.get_platform_details(client), '', False)
        b['platform Details'] = a
        c = parse.dict_to_table(b, 'Hardware Details', False)
        f.write(str(c))
        f.write('\n')
        b = {}
        a = self.get_cpu_info(client)
        a = parse.dict_to_table(a, '', False)
        b['CPU'] = a
        c = parse.dict_to_table(b, 'CPU Details', False)
        print(c)
        f.write(str(c))
        f.write('\n')
        b = {}
        a = parse.dict_to_table(self.get_hw_memory(client), '', False)
        b['Hardware Memory'] = a
        c  = parse.dict_to_table(b, 'Hardware Memory Details', False)
        print(c)
        f.write(str(c))
        f.write('\n')
        b = {}
        # a = parse.dict_to_table(self.get_physical_adapter(client),'')
        # b['Physical adapter Details'] = a
        # a = dict_to_table(self.get_vflash(client),'',False)
        # b['vFlash Details'] = a
        a = parse.dict_to_table(self.get_filesystem(client), "fileSystem")
        b['File System'] = a
        # a = parse.dict_to_table(self.get_logical_device_details(client),'')
        # b['Logical device'] = a
        c = parse.dict_to_table(b, 'Storage Details', False)
        print(c)
        f.write(str(c))
        f.write('\n')
        b = {}
        a = parse.dict_to_table(self.get_nics(client), '')
        b['NIC Details'] = a
        # a= parse.dict_to_table(self.get_host_ip(client),'VMkernal details')
        # b['VMKernal Details'] = a
        a = parse.dict_to_table(self.get_vswitch(client), '')
        b['vswitch Detail'] = a
        a = parse.dict_to_table(self.get_pg_name(client), '')
        b['Port group name'] = a
        a = parse.dict_to_table(self.get_dvs_name(client), '')
        b['DVS details'] = a
        a = parse.dict_to_table(self.get_dvport_id(client), '')
        b['DVport ID'] = a
        a = parse.dict_to_table(self.get_vm_details(client), '')
        b['Virtual Machine'] = a
        c = parse.dict_to_table(b, 'Network Details', False)
        print(c)
        f.write(str(c))
        f.write('\n')
        b = {}
        a = parse.dict_to_table(self.get_current_powerstatus(client), '', False)
        b['Current Power Policy'] = a
        a = parse.dict_to_table(self.get_hoststats(client), '', False)
        b['Host status'] = a
        a = parse.dict_to_table(self.get_pcpu_power_mgmt_states(client), '', False)
        b['PCPU power management states'] = a
        c = parse.dict_to_table(b, 'System State', False)
        print(c)
        f.write(str(c))
        f.write('\n')
        f.close()

    def list_env_detail_compact(self, client):
        parse = ParserUtil.Parser()
        f = open("env_details_compact.txt", "a+")
        a = self.hardware_detail_compact(client)
        c = parse.dict_to_table(a, 'Hardware Details', False)
        print(c)
        f.write(str(c))
        c = parse.dict_to_table(self.get_server_details(client), 'Servers Information', False)
        print(c)
        f.write('\n')
        f.write(str(c))
        f.close()