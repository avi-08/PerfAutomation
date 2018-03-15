"""
    This module deals with VM configurations, verification and other controls
"""
from __future__ import print_function
import paramiko
import re

__author__ = 'Somanath'

host='10.107.182.19'
username='root'
password='ca$hc0w'
datastore ='Datastore1'
vmName= 'TEST-VM'
result={}
mat_list=[]


# Function to Read .vmx file
def readVMX(client, datastore, vmName):
    print('\nReading {}.vmx file'.format(vmName))
    stdin, stdout, stderr = client.exec_command(f'cat vmfs/volumes/{datastore}/{vmName}/{vmName}.vmx')
    return (stdout.read().decode())


# Get VMid
def get_vm_id(client, vmName):
    stdin, stdout, stderr = client.exec_command(f'vim-cmd vmsvc/getallvms | grep {vmName}')
    return (stdout.read().decode().split(' ')[0])


# Power off VM's
def power_off_vm(client, vmName):
    print(f'PowerOff: {vmName}')
    vmid = get_vm_id(client, vmName)
    stdin, stdout, stderr = client.exec_command('vim-cmd vmsvc/power.off {}'.format(int(vmid)))


# Power on VM's
def power_on_vm(client, vmName):
    print(f'PowerOn: {vmName}')
    vmid = get_vm_id(client, vmName)
    stdin, stdout, stderr = client.exec_command('vim-cmd vmsvc/power.on {}'.format(int(vmid)))


# Verify the NUMA Affinity
def NUMAaffinity(client, vmnic='vmnic0'):
    stdin, stdout, stderr = client.exec_command(f'vsish -e get /net/pNics/{vmnic}/properties | grep NUMA')
    numaNode = stdout.read().decode()
    # return numaNode.strip('\n').split(':')[1]
    return re.sub(' +', ' ', numaNode.strip('\n')).split(':')[1]


# Replace the string the file
def replace_parameter_vmx(client, datastore, vmName, original, new):
    # sed -i 's/numa.nodeAffinity = 0/numa.nodeAffinity="0"/g'
    stdin, stdout, stderr = client.exec_command(f'sed -i \'s/{original}/{new}/g\' vmfs/volumes/{datastore}/{vmName}/{vmName}.vmx')


# add perameter to the .vmx file
def add_parameter_vmx(client, datastore, vmName, data):
    stdin, stdout, stderr = client.exec_command(
        'echo "{}" >> vmfs/volumes/{}/{}/{}.vmx'.format(data, datastore, vmName,vmName))


# SET numa.nodeAffinity value
def set_numa_NodeAffinity(client, datastore, vmName, numanode):
    data = readVMX(client, datastore, vmName)
    data1 = f'numa.nodeAffinity = "{numanode}"'
    power_off_vm(client, vmName)
    add_parameter_vmx(client, datastore, vmName, data1)
    replace_parameter_vmx(client, datastore, vmName, data1.replace('"', ''), data1)
    power_on_vm(client, vmName)

# Verify NUMA Affinity in config proprity
def verify_numa_NodeAffinity(client,datastore, vmName):
    print('verify the numa nodeAffinity')
    data1 =f'numa.nodeAffinity = "{NUMAaffinity(client)}"'
    stdin , stdout, stderr = client.exec_command(f'cat vmfs/volumes/{datastore}/{vmName}/{vmName}.vmx | grep numa.node')
    numaNode = stdout.read().decode()
    if len(numaNode)!= 0:
        if int(numaNode.strip('\n').split('=')[1].replace('"','')) == int(NUMAaffinity(client)):
            return True
        else:
            replace_parameter_vmx(client,datastore,vmName,data1.replace('"',''),data1)
    else:
        set_numa_NodeAffinity(client,datastore,vmName, NUMAaffinity(client))


# Verify the Vnic TX thread Allocation
def verify_vnic_tx_thread(client, datastore, vmName):
    print('\nVnic TX thread Alllocation')
    stdin , stdout, stderr = client.exec_command(f'cat vmfs/volumes/{datastore}/{vmName}/{vmName}.vmx | grep ctxPerDev')
    return True if len(stdout.read().decode()) else False

# Verify the SysContext
def verify_SysContext(client, datastore, vmName):
    print ('\nSys Context')
    stdin , stdout, stderr = client.exec_command(f'cat vmfs/volumes/{datastore}/{vmName}/{vmName}.vmx | grep sched.cpu.latencySensitivity.sysContexts')
    return True if len(stdout.read().decode()) else False

# Verify the Vnic Adapter
def vnic_adapter_type(client,datastore, vmName):
    print ('\nVnic Adapter type (vmxnet) :')
    stdin , stdout, stderr = client.exec_command(f'cat vmfs/volumes/{datastore}/{vmName}/{vmName}.vmx | grep vmxnet')
    # print(stdout.read())
    return True if len(stdout.read()) != 0 else False

# Verify the CPU pinning is proper
def verify_cpuPinning():
    for key, value in result.items():
        for i in range(1, len(mat_list) - 1):
            if key == mat_list[i][23] and value == mat_list[i][1]:
                print('valid')
                break
        # if i != (len(mat_list) - 1):
        #    print('cpuid not pinned :{}'.format(key))

# check the values are reservation are enabled
def latency_value_check(latencySensitivity, exclaff):
    return True if latencySensitivity == -1 and exclaff > 0 else False

def verify_latencySensitivity(self, client):
    """
    Verify the Latency Sensitivity feature

    :param client:
    :return:
    """
    print('verifing the Latency Sensitivity on vm(s)')
    stdin, stdout, stderr = client.exec_command('net-stats -i 3 -t WicQv -A')
    d = eval(stdout.read().decode())
    data = d['stats'][0]['vcpus']
    for i in data:
        if data[i]['name'] != 'net-stats':
            result[i] = int(data[i]['exclaff'])
            if latency_value_check(int(data[i]['latencySensitivity']), int(data[i]['exclaff'])) == True:
                result[i] = int(data[i]['exclaff'])
                # print("Latency Sensitivity for VCPU:{} is valid".format(data[i]['name']))
            # else:
            # print("Latency Sensitivity for VCPU:{} is ***not-valid***".format(data[i]['name']))
    stdin, stdout, stderr = client.exec_command('sched-stats -t pcpu-stats')
    schedStats = stdout.read().decode()
    data = re.sub(' +', ' ', schedStats).split('\n')
    for i in range(len(data)):
        mat_list.append(data[i].split(' '))

    # cross Verifing the Latency Sensitivity
    verify_cpuPinning()

def getSession():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host,username=username, password=password, port=22)
        print('connecting ...')
        return client
    except paramiko.SSHException as e:
        print(e.args)
        client.close()

client = getSession()

client.close()