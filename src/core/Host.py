"""
    The class HostConfig provides functions to verify and apply various host-level optimizations for different ESXi host
    versions. The functions return True for successful application/verification of optimizations, otherwise return False
    A unit_test() function has been defined for testing all  defined functions
#######################################################################################################################
# Note: Some host optimizations (like Turbo Boost, Power management) cannot be performed programmatically.
#       These optimizations have to be applied and verified manually.
#######################################################################################################################
"""

import re

__author__ = "Avi Sharma"


class HostConfig:

    def __init__(self):
        pass

    def get_host_version(self, client):
        """
        Get ESXi host version and build
        :param client: paramiko SSHClient object
        :return: (str) ESXi host version and build
        """
        stdin, stdout, stderr = client.exec_command('vmware -v')
        return stdout.read().decode()

    def is_hyperthreading_enabled(self, client):
        """
        Check if hyper threading is enabled
        :param client: paramiko SSHClient object
        :return: (bool)True if hyper threading is enabled else False
        """
        stdin, stdout, stderr = client.exec_command('esxcli system settings kernel list | grep hyperthreading')
        return True if re.sub(' +', ' ', stdout.read().decode().strip()).split(' ')[-3].upper() == 'TRUE' else False

    def config_hyperthreading(self, client, enable):
        """
        Configure hyper threading
        :param client: paramiko SSHClient object
        :param enable: (bool) specifying whether to enable or disable hyper threading
        :return: (bool) True if no errors occur while command execution else False
        """
        if self.is_hyperthreading_enabled(client) == enable:
            return True
        else:
            stdin, stdout, stderr = client.exec_command(f'esxcli system settings kernel set -s hyperhreading -v {enable}')
            return False if stderr.read() else True

    def verify_nic_driver(self, client, vmnic, driver):   #, version
        """
        Check if required driver is present for a nic
        :param client: paramiko SSHClient object
        :param vmnic: (str)<vmnicX> for checking driver
        :param driver: (str)driver name (e.g ixgbe, ixgben, etc)
        :return: (bool) True if specified version of driver is enabled on vmnic else False
        """
        stdin, stdout, stderr = client.exec_command(f'vsish -ep get /net/pNics/{vmnic}/properties')
        properties = eval(stdout.read().decode())
        return True if (properties['module'] == driver) else False

    def config_nic_driver(self, client, vmnic, driver):
        """
        Configure(enable and load) specified driver on specified NIC
        :param client: paramiko SSHClient object
        :param vmnic: (str)<vmnicX> name of NIC to configure driver on
        :param driver: (str)driver name (e.g ixgbe, ixgben, etc)
        :return: (bool) True if no errors occur while command execution else False
        """
        if self.verify_nic_driver(client, vmnic, driver):
            return True
        stdin, stdout, stderr = client.exec_command(f' esxcli software vib list | grep {driver}')
        if stdout.read().decode().find(driver) > -1:
            stdin, stdout, stderr = client.exec_command(f' esxcli system module set -m {driver} -e true')
            stdin, stdout, stderr = client.exec_command(f' esxcli system module load -m {driver}')
        return True

    def is_fcoe_enabled(self, client):
        """
        Check whether FCoE is enabled on the ixgbe driver; only for ESXi 6.0U2
        :param client: paramiko SSHClient object
        :return: (bool) True if FCoE is enabled else False
        """
        stdin, stdout, stderr = client.exec_command('esxcfg-module -g ixgbe')
        return True if stdout.read().decode().find("options = 'CNA=0,0'") > -1 else False

    def config_fcoe(self, client, enable):
        """
        Configure FCoE on the ixgbe driver; only for ESXi 6.0U2
        :param client: paramiko SSHClient object
        :param enable: (bool) specifying whether to enable or disable FCoE
        :return: (bool) True if no errors occur while command execution else False
        """
        if self.is_fcoe_enabled(client) == enable:
            return True
        else:
            value = '0, 0' if not enable else '1, 1'
            stdin, stdout, stderr = client.exec_command(f'esxcli system module parameters set -m ixgbe -p "CNA={value}" ')
            return True if len(stdout.readline()) == 0 else False

    def verify_rss(self, client, driver):
        """
        Check if Receive side scaling is enabled on driver
        :param client: paramiko SSHClient object
        :return: (bool) True if RSS is enabled else False
        """
        stdin, stdout, stderr = client.exec_command(f'esxcfg-module -g {driver}')
        return True if stdout.read().decode().find("options = 'RSS=(4)") > -1 else False

    def config_rss(self, client, driver, enable):
        """
        Configure Receive side scaling on driver
        :param client: paramiko SSHClient object
        :param driver: (str)driver name (e.g ixgbe, ixgben, etc)
        :param enable: (bool) whether or not to enable receive side scaling on the driver
        :return: (bool) True if no errors occur while command execution else False
        """
        if self.verify_rss(client, driver) == enable:
            return True
        else:
            value = '(0)' if enable == True else '(4)'
            stdin, stdout, stderr = client.exec_command(f'esxcli system module parameters set -m {driver} -p "RSS={value}"')
            return True \
                #if len(stdout.readline()) == 0 else False

    def verify_nic_ring_size(self, client, vmnic, RX_SIZE, TX_SIZE):
        """
        Check if current NIC ring size is the same as required sizes
        :param client: paramiko SSHClient object
        :param vmnic: (str) <vmnicX>
        :param RX_SIZE: (int) RX ring size
        :param TX_SIZE: (int) TX ring size
        :return: (bool) True if required ring size is configured on the vmnicX else False
        """
        stdin, stdout, stderr = client.exec_command(f'esxcli network nic ring current get --nic-name={vmnic}')
        data = dict(pair.lstrip().split(': ') for pair in stdout.read().decode().split('\n')[:-1])
        return True if int(data['RX']) == RX_SIZE and int(data['TX']) == TX_SIZE else False

    def config_nic_ring_size(self, client, vmnic, RX_SIZE, TX_SIZE):
        """
        Set ring buffer size for RX and TX of a vmnic
        :param client: paramiko SSHClient object
        :param vmnic: (str)<vmnicX>
        :param RX_SIZE: (int) RX ring size
        :param TX_SIZE: (int) TX ring size
        :return: (bool) True if no errors occur while command execution else False
        """
        if self.verify_nic_ring_size(client, vmnic, RX_SIZE, TX_SIZE):
            return True
        stdin, stdout, stderr = client.exec_command(
            f'esxcli network nic ring current set -n={vmnic} -r={RX_SIZE} -t={TX_SIZE}')
        return True if len(stdout.readline()) == 0 else False

    def verify_sw_tx_queue_size(self, client, queue_length):
        """
        Check software TX queue size
        :param client: paramiko SSHClient object
        :param queue_length: (int) software TX queue length
        :return: (bool) True if s/w TX queue length is same as given parameter else False
        """
        stdin, stdout, stderr = client.exec_command('vsish -ep get /config/Net/intOpts/MaxNetifTxQueueLen')
        data = eval(stdout.read().decode())
        return True if data['cur'] == queue_length else False

    def config_sw_tx_queue_size(self, client, queue_length):
        """
        Configure s/w TX queue size
        :param client: paramiko SSHClient object
        :param queue_length: (int) software TX queue length to be configured
        :return: (bool) True if no errors occur while command execution else False
        """
        if self.verify_sw_tx_queue_size(client, queue_length):
            return True
        else:
            stdin, stdout, stderr = client.exec_command(
                f'vsish -ep set /config/Net/intOpts/MaxNetifTxQueueLen {queue_length}')
            return True if int(stdout.readline()) == queue_length else False

    def is_queue_pairing_enabled(self, client):
        """
        Check if Queue Pairing is enabled
        :param client: paramiko SSHClient object
        :return: (bool) True if Queue Pairing is enabled else False
        """
        stdin, stdout, stderr = client.exec_command('vsish -ep get /config/Net/intOpts/NetNetqRxQueueFeatPairEnable')
        data = eval(stdout.read().decode())
        return True if int(data['cur']) == 1 else False

    def config_queue_pairing(self, client, enable):
        """
        Configure Queue Pairing
        :param client: paramiko SSHClient object
        :param enable: (bool) specify whether to enable or disable Queue Pairing
        :return: (bool) True if no errors occur while command execution else False
        """
        if self.is_queue_pairing_enabled(client) == enable:
            return True
        value = 1 if enable == True else 0
        stdin, stdout, stderr = client.exec_command(
            f'vsish -ep set /config/Net/intOpts/NetNetqRxQueueFeatPairEnable {value}')
        return True if int(stdout.readline()) == value else False

    def verify_sys_thread_pinning(client):
        pass

    def config_sys_thread_pinning(client):
        pass

    def is_tx_split_enabled(self, client, vmnic):
        """
        Check if TX split mode is enabled
        :param client: paramiko SSHClient object
        :param vmnic: (str)<vmnicX> name of NIC
        :return: (bool) True if TX split is enabled else False
        """
        stdin, stdout, stderr = client.exec_command(f'vsish -ep get /net/pNics/{vmnic}/sched/txMode')
        return True if int(stdout.read().decode()) == 1 else False

    def config_tx_split(self, client, vmnic, enable):
        """
        Configure TX Split mode
        :param client: paramiko SSHClient object
        :param vmnic: (str)<vmnicX> name of NIC
        :param enable: (bool) specify whether to enable or disable TX Split mode
        :return: (bool) True if no errors occur while command execution else False
        """
        if self.is_tx_split_enabled(client, vmnic) == enable:
            return True
        value = 1 if enable == True else 0
        stdin, stdout, stderr = client.exec_command(f'vsish -ep set /net/pNics/{vmnic}/sched/txMode {value}')
        return True if len(stdout.readline()) == 0 else False


def unit_test():
    """
    Sample function to test above functions
    """
    # from src.util import HostSession

    #_NICS = []
    #_HOST = '10.107.182.18'
    #_USERNAME = 'root'
    #_PASSWORD = 'ca$hc0w'

    # conf = HostConfig()
    # client = HostSession.HostSession().connect(host=_HOST, username=_USERNAME, password=_PASSWORD, ssl=False)

    #def get_vmnic(client):
    #    stdin, stdout, stderr = client.exec_command('esxcli network nic list')
    #    for line in stdout.readlines()[2:]:
    #        _NICS.append(line[:7].strip())

    # Check if hyperthreading is enabled
    # print(conf.is_hyperthreading_enabled(client))

    # Configure hyperthreading
    # print(conf.config_hyperthreading(client, enable=False))

    # Get list of vmnic for hosts
    # print(conf.get_vmnic(client))

    # Check if required driver is present for a nic; Requires call to get_vmnic()
    # print([conf.verify_nic_driver(client, nic, 'ixbgen', '1.0.0.0') for nic in _NICS])

    # Check s/w TX queue size
    # print(conf.verify_sw_tx_queue_size(client, 2000))

    # Check if queue pairing is enabled
    # print(conf.is_queue_pairing_enabled(client))

    # Configure queue pairing
    # print(conf.config_queue_pairing(client, False))

    # Check if TX split mode is enabled; Requires call to get_vmnic()
    # print([conf.is_tx_split_enabled(client, nic) for nic in _NICS])

    # Configure TX split mode; Requires call to get_vmnic()
    # print([conf.config_tx_split(client, nic, True) for nic in _NICS])

    # Check NIC ring size; Requires call to get_vmnic()
    # print([conf.verify_nic_ring_size(client, nic, RX_SIZE=992, TX_SIZE=1024) for nic in _NICS])

    # HostSession.HostSession().disconnect(client)
    pass
