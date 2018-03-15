import json

from src.core import Host
from src.util import HostSession


def host_config(settings, keep_defaults=False):
    hosts = json.load(open(r'env_conf\host.json'))
    for host in hosts['HOST_DETAILS']:
        client = HostSession.HostSession().connect(host['HOST'], host['USER'], host['PASSWORD'], False)
        _NICS = host['NICS'].split(',')
        ver = Host.get_host_version(client)
        if ver.find('6.5') > -1:
            params = hosts['ESXI65']
            print(ver)
            print(f'Hyper threading enabled: {Host.is_hyperthreading_enabled(client)}')
            print(f'Configure Hyper threading: enable={params["ENABLE_HYPERTHREADING"]} config success={Host.config_hyperthreading(client, enable=params["ENABLE_HYPERTHREADING"])}')

            print(f'NICS {_NICS}')
            print(f'Configuring {params["NIC_DRIVER"]}')
            for nic in _NICS:
                print("{} : config={}".format(nic, Host.config_nic_driver(client, nic, params['NIC_DRIVER']['NAME'])))

            print(f'RSS enabled: {Host.verify_rss(client, params["NIC_DRIVER"])}')
            print(f'Configuring RSS: enable = {params["ENABLE_RSS"]} success={Host.config_rss(client, params["NIC_DRIVER"], enable=params["ENABLE_RSS"])}')

            for nic in _NICS:
                print(f'Configuring Physical NIC Ring Size as {params["NIC_BUFFER_SIZE"]} on {nic} : \
                 isSet = {Host.verify_nic_ring_size(client, nic, params["NIC_BUFFER_SIZE"]["RX"], params["NIC_BUFFER_SIZE"]["TX"])} : \
                 config success={Host.config_nic_ring_size(client, nic, params["NIC_BUFFER_SIZE"]["RX"], params["NIC_BUFFER_SIZE"]["TX"])} ')

            print(f'Configuring SW TX queue length as {params["SW_TX_QUEUE"]}: isSet={Host.verify_sw_tx_queue_size(client, params["SW_TX_QUEUE"])} \
             : config success = {Host.config_sw_tx_queue_size(client, params["SW_TX_QUEUE"])}')

            print(f'Configuring Queue Pairing enabled ={params["ENABLE_QUEUE_PAIRING"]}: isEnabled={Host.is_queue_pairing_enabled(client)} \
                         : config success = {Host.config_queue_pairing(client, enable=params["ENABLE_QUEUE_PAIRING"])}')

            for nic in _NICS:
                print(f'Configuring Split TX mode  ={params["ENABLE_TX_SPLIT"]}: isEnabled={Host.is_tx_split_enabled(client, nic)} \
                                     : config success = {Host.config_tx_split(client, nic, enable=params["ENABLE_TX_SPLIT"])}')

            print("Config complete")

            # Get list of vmnic for hosts
            # print(get_vmnic(client))

            # Check if required driver is present for a nic; Requires call to get_vmnic()
            # print([verify_nic_driver(client, nic, 'ixbgen', '1.0.0.0') for nic in NICS])

            # Check s/w TX queue size
            # print(verify_sw_tx_queue_size(client, 2000))

            # Check if queue pairing is enabled
            # print(is_queue_pairing_enabled(client))

            # Configure queue pairing
            # print(config_queue_pairing(client, False))

            # Check if TX split mode is enabled; Requires call to get_vmnic()
            # print([is_tx_split_enabled(client, nic) for nic in NICS])

            # Configure TX split mode; Requires call to get_vmnic()
            # print([config_tx_split(client, nic, True) for nic in NICS])

            # Check NIC ring size; Requires call to get_vmnic()
            # print([verify_nic_ring_size(client, nic, RX_SIZE=992, TX_SIZE=1024) for nic in NICS])

        else:
            pass
        HostSession.HostSession().disconnect(client)