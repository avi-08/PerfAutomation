"""
    This is a script that will call functions to verify, apply and validate hypervisor level optimizations.
    ## Note: The BIOS level optimizations are not supported. They need to be applied manually.
    This script tunes ESXi hosts for following properties according to best practices for the particular version of host
    1. Check if appropriate NIC driver and driver version are loaded and running on host;configurations made accordingly
    2. Check if driver options(FCoE, RSS) are configured; configurations made accordingly
    3. Check if size of ring buffers for physical NICs is set at required values; configurations made accordingly
    4. Check if size of software TX queues is set at required values; configurations made accordingly
    5. Check if Queue pairing is enabled; configurations made accordingly
    6. Check if TX split mode is enabled; configurations made accordingly
    These checks are performed as per the values provided in the host.conf file. Tester can choose to go with the
    default configs of the ESXi host or to change some of them or to change them all. Command line switches are provided
    for the corresponding usecase.

"""
import logging

from src.core.host import Host
from src.util import HostSession
from src.env_conf import settings

logger = logging.getLogger(__name__)


def host_config(keep_defaults=False):
    """
    Apply host optimizations with values specified in host.json(BIOS optimizations not supported)
    Steps involved:
    1. Login to hosts using SSH client
    2. Perform optimizations
    3. Logout from ssh session
    :param keep_defaults: (bool) if True, skips the configuration of host and just gets the values of default settings on host
    :return: (bool) True If all optimizations are applied successfully else False.
    """
    hosts = settings.getValue('HOST_DETAILS')
    # Create object of HostConfig() to access functions
    config_host = Host.HostConfig()
    for host in hosts:
        client = HostSession.HostSession().connect(host['HOST'], host['USER'], host['PASSWORD'], False)
        _NICS = host['NICS'].split(',')
        logger.info(f'Getting ESXi version details')
        ver = config_host.get_host_version(client)
        logger.info(f'{ver}')
        logger.info('Start applying optimizations for the specific Esxi version')
        if ver.find('6.5') > -1:
            logger.info('Getting configuration settings from host.json')
            params = settings.getValue('ESXI65')
            logger.info(f'Configuring NICS {_NICS} for driver module: {params["NIC_DRIVER"]}')
            for nic in _NICS:
                logger.info(f'Configuring {nic}')
                success, message = config_host.config_nic_driver(client, nic, params['NIC_DRIVER']['NAME'])
                if eval(success):
                    logger.info(f'{nic} driver configuration success: {eval(success)}')
                else:
                    logger.error(f'{nic} driver configuration success: {eval(success)}')
                    logger.info(f'host output: {message}')
                    HostSession.HostSession().disconnect(client)
                    return False

            logger.info(f'RSS to be enabled: {params["ENABLE_RSS"]}')
            logger.info('Configuring RSS')
            success, message = config_host.config_rss(client, params["NIC_DRIVER"]['NAME'], enable=params["ENABLE_RSS"])
            if eval(success):
                logger.info(f'RSS configuration success : {eval(success)}')
            else:
                logger.info(f'RSS configuration success : {eval(success)}')
                logger.info(f'host output: {message}')
                HostSession.HostSession().disconnect(client)
                return False

            for nic in _NICS:
                logger.info(f'Configuring Physical NIC Ring Size as {params["NIC_BUFFER_SIZE"]} on {nic}')
                success, message = config_host.config_nic_ring_size(client, nic, params["NIC_BUFFER_SIZE"]["RX"], params["NIC_BUFFER_SIZE"]["TX"])
                if eval(success):
                    logger.info(f'{nic} ring size configuration success: {eval(success)}')
                else:
                    logger.error(f'{nic} ring size configuration success: {eval(success)}')
                    logger.info(f'host output: {message}')
                    HostSession.HostSession().disconnect(client)
                    return False

            logger.info(f'Configuring SW TX queue length as {params["SW_TX_QUEUE"]}')
            success, message = config_host.config_sw_tx_queue_size(client, params["SW_TX_QUEUE"])
            if eval(success):
                logger.info(f'Software TX queue configuration success: {eval(success)}')
            else:
                logger.error(f'Software TX queue configuration success: {eval(success)}')
                logger.info(f'host output: {message}')
                HostSession.HostSession().disconnect(client)
                return False

            logger.info(f'Queue Pairing to be enabled: {params["ENABLE_QUEUE_PAIRING"]}')
            success, message = config_host.config_queue_pairing(client, enable=params["ENABLE_QUEUE_PAIRING"])
            if eval(success):
                logger.info(f'Queue Pairing configuration success: {eval(success)}')
            else:
                logger.info(f'Queue Pairing configuration success: {eval(success)}')
                logger.info(f'host output: {message}')
                HostSession.HostSession().disconnect(client)
                return False

            logger.info(f'Split TX mode to be enabled: {params["ENABLE_TX_SPLIT"]}')
            for nic in _NICS:
                logger.info(f'Configuring Split TX on {nic}')
                success, message = config_host.config_tx_split(client, nic, enable=params["ENABLE_TX_SPLIT"])
                if eval(success):
                    logger.info(
                        f'Split TX configuration success: {eval(success)}')
                else:
                    logger.error(
                        f'Split TX configuration success: {eval(success)}')
                    logger.info(f'host output: {message}')
                    HostSession.HostSession().disconnect(client)
                    return False
        else:
            logger.info('Getting configuration settings from host.json')
            params = settings.getValue('ESXI60U2')
            logger.info(ver)
            logger.info(f'Hyper threading enabled: {config_host.is_hyperthreading_enabled(client)}')
            logger.info(
                f'Configure Hyper threading: enable={params["ENABLE_HYPERTHREADING"]} config success={config_host.config_hyperthreading(client, enable=params["ENABLE_HYPERTHREADING"])}')

            logger.info(f'NICS {_NICS}')
            logger.info(f'Configuring {params["NIC_DRIVER"]}')
            for nic in _NICS:
                logger.info("{} : config={}".format(nic, config_host.config_nic_driver(client, nic, params['NIC_DRIVER']['NAME'])))

            logger.info(f'RSS enabled: {config_host.verify_rss(client, params["NIC_DRIVER"])}')
            logger.info(
                f'Configuring RSS: enable = {params["ENABLE_RSS"]} success={config_host.config_rss(client, params["NIC_DRIVER"]["NAME"], enable=params["ENABLE_RSS"])}')

            for nic in _NICS:
                logger.info(f'Configuring Physical NIC Ring Size as {params["NIC_BUFFER_SIZE"]} on {nic} : \
                             isSet = {config_host.verify_nic_ring_size(client, nic, params["NIC_BUFFER_SIZE"]["RX"], params["NIC_BUFFER_SIZE"]["TX"])} : \
                             config success={config_host.config_nic_ring_size(client, nic, params["NIC_BUFFER_SIZE"]["RX"], params["NIC_BUFFER_SIZE"]["TX"])} ')

            logger.info(f'Configuring SW TX queue length as {params["SW_TX_QUEUE"]}: isSet={config_host.verify_sw_tx_queue_size(client, params["SW_TX_QUEUE"])} \
                         : config success = {config_host.config_sw_tx_queue_size(client, params["SW_TX_QUEUE"])}')

            logger.info(f'Configuring Queue Pairing enabled ={params["ENABLE_QUEUE_PAIRING"]}: isEnabled={config_host.is_queue_pairing_enabled(client)} \
                                     : config success = {config_host.config_queue_pairing(client, enable=params["ENABLE_QUEUE_PAIRING"])}')

            for nic in _NICS:
                logger.info(f'Configuring Split TX mode  ={params["ENABLE_TX_SPLIT"]}: isEnabled={config_host.is_tx_split_enabled(client, nic)} \
                                                 : config success = {config_host.config_tx_split(client, nic, enable=params["ENABLE_TX_SPLIT"])}')
        HostSession.HostSession().disconnect(client)
        return True


def get_host_config():
    hosts = settings.getValue('HOST_DETAILS')
    # Create object of HostConfig() to access functions
    config_host = Host.HostConfig()
    for host in hosts:
        client = HostSession.HostSession().connect(host['HOST'], host['USER'], host['PASSWORD'], False)
        _NICS = host['NICS'].split(',')
        logger.info(f'Getting ESXi version details')
        ver = config_host.get_host_version(client)
        logger.info(f'{ver}')
        logger.info('Start applying optimizations for the specific Esxi version')
        if ver.find('6.5') > -1:
            config = Host.HostConfig()
            for nic in _NICS:
                config.get_nic_ring_size(client, nic)
            for nic in _NICS:
                config.get_split_tx_status(client, nic)
            config.get_rss(client, 'ixgben')
            for nic in _NICS:
                config.get_nic_driver(client, nic)

        HostSession.HostSession().disconnect(client)
    pass
