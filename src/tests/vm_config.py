from src.core.vnf import VmTuning
from src.util import HostSession
import json

datastore = 'Datastore1'
vmName = 'TEST-VM'
def vm_config():
    hosts = json.load(open(r'..\env_conf\host.json'))
    for host in hosts['HOST_DETAILS']:
        client = HostSession.HostSession().connect(host['HOST'], host['USER'], host['PASSWORD'], False)
        print(host['HOST'])
        print(f'Latency Sensitivity set to High and Reserved :{VmTuning.verify_latencySensitivity(client)}')
        # if VmTuning.verify_latencySensitivity(client) == False:
        """
               Config need to be done.
        """
        print(f'Vmnic Adapter type (vmxnet):{VmTuning.vnic_adapter_type(client,datastore,vmName)}')
        print(f'vNIC TX thread allocation :{VmTuning.verify_vnic_tx_thread(client,datastore,vmName)}')
        if VmTuning.verify_vnic_tx_thread(client,datastore,vmName) == False:
            """
            config for TX thread Allocation
            """
        print(f'Numa Affinity :{VmTuning.verify_numa_NodeAffinity(client,datastore,vmName)}')
        print(f'system context : {VmTuning.verify_SysContext(client,datastore,vmName)}')

        print(f'Vm config is Completed')
        client.close()

vm_config()