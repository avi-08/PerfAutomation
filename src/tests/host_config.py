"""
    This is a script that will call functions to verify, apply and validate hypervisor level optimizations.
    ## Note: The BIOS level optimizations are not supported with the 'exception' of hyperthreading. They need to be applied manually.
    This script tunes ESXi hosts for following properties according to best practices for the particular version of host
    1. Check if appropriate NIC driver and driver version are loaded and running on host;configurations made accordingly
    2. Check if driver options(FCoE, RSS) are configured; configurations made accordingly
    3. Check if size of ring buffers for physical NICs is set at required values; configurations made accordingly
    4. Check if size of software TX queues is set at required values; configurations made accordingly
    5. Check if Queue pairing is enabled; configurations made accordingly
    6. Check if TX split mode is enabled; configurations made accordingly
    These checks are performed as per the values provided in the host.conf file. Tester can choose to go with the
    default configs of the ESXi host or to change some of them or to change them all.

"""
import json
import logging

from src.core import Host
from src.util import HostSession, LogUtil

_LOGGER = logging.getLogger(__name__)


def host_config(keep_defaults=False):
    """
    script for performing host optimizations with values specified in host.json
    Steps involved:
    1. Login to hosts using SSH client
    2. Perform optimizations
    3. Logout from ssh session
    :param keep_defaults: (bool) if True, skips the configuration of host and just gets the values of default settings on host
    :return: (bool) True If all optimizations are applied successfully else False.
    """
    hosts = json.load(open(r'env_conf\host.json'))
    # Create object of HostConfig() to access functions
    config_host = Host.HostConfig()
    for host in hosts['HOST_DETAILS']:
        client = HostSession.HostSession().connect(host['HOST'], host['USER'], host['PASSWORD'], False)
        _NICS = host['NICS'].split(',')
        ver = config_host.get_host_version(client)
        if ver.find('6.5') > -1:
            params = hosts['ESXI65']
            _LOGGER.info(f'ESXi version details: {ver}')
            _LOGGER.info(f'Checking if Hyper threading enabled: {config_host.is_hyperthreading_enabled(client)}')
            success = config_host.config_hyperthreading(client, enable=params["ENABLE_HYPERTHREADING"])
            if success:
                _LOGGER.info(f'Hyperthreading configuration(enable={params["ENABLE_HYPERTHREADING"]})success:{success}')
            else:
                _LOGGER.error(
                    f'Hyper threading configuration (enable={params["ENABLE_HYPERTHREADING"]}) success: {success}')
                return False

            _LOGGER.info(f'Configuring NICS {_NICS} with {params["NIC_DRIVER"]}')
            for nic in _NICS:
                success = config_host.config_nic_driver(client, nic, params['NIC_DRIVER']['NAME'])
                if success:
                    _LOGGER.info(f'{nic} configuration success: {success}')
                else:
                    _LOGGER.error(f'{nic} configuration success: {success}')
                    return False

            _LOGGER.info(f'Checking if RSS enabled: {config_host.verify_rss(client, params["NIC_DRIVER"])}')
            success = config_host.config_rss(client, params["NIC_DRIVER"], enable=params["ENABLE_RSS"])
            if success:
                _LOGGER.info(f'RSS configuration(enable = {params["ENABLE_RSS"]}) success : {success}')
            else:
                _LOGGER.info(f'RSS configuration(enable = {params["ENABLE_RSS"]}) success : {success}')
                return False

            for nic in _NICS:
                _LOGGER.info(f'Configuring Physical NIC Ring Size as {params["NIC_BUFFER_SIZE"]} on {nic} : \
                 isSet = {config_host.verify_nic_ring_size(client, nic, params["NIC_BUFFER_SIZE"]["RX"], params["NIC_BUFFER_SIZE"]["TX"])} : \
                 config success={config_host.config_nic_ring_size(client, nic, params["NIC_BUFFER_SIZE"]["RX"], params["NIC_BUFFER_SIZE"]["TX"])} ')

            _LOGGER.info(f'Configuring SW TX queue length as {params["SW_TX_QUEUE"]}: isSet={config_host.verify_sw_tx_queue_size(client, params["SW_TX_QUEUE"])} \
             : config success = {config_host.config_sw_tx_queue_size(client, params["SW_TX_QUEUE"])}')

            _LOGGER.info(f'Checking if Queue Pairing enabled: {config_host.is_queue_pairing_enabled(client)}')
            success = config_host.config_queue_pairing(client, enable=params["ENABLE_QUEUE_PAIRING"])
            if success:
                _LOGGER.info(f'Queue Pairing configuration(enable={params["ENABLE_QUEUE_PAIRING"]}) success: {success}')
            else:
                _LOGGER.error(f'Queue Pairing configuration(enable={params["ENABLE_QUEUE_PAIRING"]})success: {success}')

            for nic in _NICS:
                _LOGGER.info(f'Configuring Split TX mode  ={params["ENABLE_TX_SPLIT"]}: isEnabled={config_host.is_tx_split_enabled(client, nic)} \
                                     : config success = {config_host.config_tx_split(client, nic, enable=params["ENABLE_TX_SPLIT"])}')

        else:
            params = hosts['ESXI60U2']
            _LOGGER.info(ver)
            _LOGGER.info(f'Hyper threading enabled: {config_host.is_hyperthreading_enabled(client)}')
            _LOGGER.info(
                f'Configure Hyper threading: enable={params["ENABLE_HYPERTHREADING"]} config success={config_host.config_hyperthreading(client, enable=params["ENABLE_HYPERTHREADING"])}')

            _LOGGER.info(f'NICS {_NICS}')
            _LOGGER.info(f'Configuring {params["NIC_DRIVER"]}')
            for nic in _NICS:
                _LOGGER.info("{} : config={}".format(nic, config_host.config_nic_driver(client, nic, params['NIC_DRIVER']['NAME'])))

            _LOGGER.info(f'RSS enabled: {config_host.verify_rss(client, params["NIC_DRIVER"])}')
            _LOGGER.info(
                f'Configuring RSS: enable = {params["ENABLE_RSS"]} success={config_host.config_rss(client, params["NIC_DRIVER"], enable=params["ENABLE_RSS"])}')

            for nic in _NICS:
                _LOGGER.info(f'Configuring Physical NIC Ring Size as {params["NIC_BUFFER_SIZE"]} on {nic} : \
                             isSet = {config_host.verify_nic_ring_size(client, nic, params["NIC_BUFFER_SIZE"]["RX"], params["NIC_BUFFER_SIZE"]["TX"])} : \
                             config success={config_host.config_nic_ring_size(client, nic, params["NIC_BUFFER_SIZE"]["RX"], params["NIC_BUFFER_SIZE"]["TX"])} ')

            _LOGGER.info(f'Configuring SW TX queue length as {params["SW_TX_QUEUE"]}: isSet={config_host.verify_sw_tx_queue_size(client, params["SW_TX_QUEUE"])} \
                         : config success = {config_host.config_sw_tx_queue_size(client, params["SW_TX_QUEUE"])}')

            _LOGGER.info(f'Configuring Queue Pairing enabled ={params["ENABLE_QUEUE_PAIRING"]}: isEnabled={config_host.is_queue_pairing_enabled(client)} \
                                     : config success = {config_host.config_queue_pairing(client, enable=params["ENABLE_QUEUE_PAIRING"])}')

            for nic in _NICS:
                _LOGGER.info(f'Configuring Split TX mode  ={params["ENABLE_TX_SPLIT"]}: isEnabled={config_host.is_tx_split_enabled(client, nic)} \
                                                 : config success = {config_host.config_tx_split(client, nic, enable=params["ENABLE_TX_SPLIT"])}')
        HostSession.HostSession().disconnect(client)