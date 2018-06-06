"""
    The class HostConfig provides functions to verify and apply various host-level optimizations for different ESXi host
    versions. The functions return a tuple (success : bool, message : str) for successful application/verification of
    optimizations, otherwise return False and the error message. Therefore, if the configuration is successfully applied
    , then the function will return (True, command_output) else (False, command_error)

    A unit_test() function has been defined for testing all  defined functions
#######################################################################################################################
# Note: Some host optimizations (like Turbo Boost, Power management) cannot be performed programmatically.
#       These optimizations have to be applied and verified manually.
#######################################################################################################################
"""

import re

from src.util.LogUtil import LogUtil

__author__ = "Avi Sharma"




class HostConfig:

    def __init__(self):
        self.logger = LogUtil()
        pass

    def get_host_version(self, client):
        """
        Get ESXi host version and build
        :param client: paramiko SSHClient object
        :return: (str) ESXi host version and build
        """
        command = 'vmware -v'
        self.logger.debug(f'Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)
        self.logger.debug('Fetching Output.')
        return stdout.read().decode().strip('\n')

    def reboot_host(self, client, reason):
        command = f'esxcli system shutdown reboot --reason={reason}'
        self.logger.info(f'Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)


    def get_nic_driver(self, client, vmnic):
        """
        Get pNIC driver module name and version
        :param client:
        :param vmnic:
        :return: NIC driver module name and version
        """
        self.logger.info(f'Get nic details for {vmnic}')
        command = f'vsish -ep get /net/pNics/{vmnic}/properties'
        self.logger.debug(f'Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)
        output = eval(stdout.read().decode())
        #self.logger.info(f'Fetching Output:  {output}')
        self.logger.debug("Fetching Output: {'module': 'ixgben', 'version': '1.0.0.0', 'fw_version': '0x800005ab', 'devname': 'vmnic6', 'interface': 'vmklinux', 'hwCap': 1178338091, 'hwAct': 1111229227, 'swAct': 813694976, 'swAssistAct': 0, 'pciSegment': 0, 'pciBus': 5, 'pciSlot': 0, 'pciFunc': 0, 'numaNode': 0, 'pciVendor': 32902, 'pciDevID': 5416, 'linkUp': 1, 'ifOperStatus': 1, 'ifAdminStatus': 1, 'fullDuplex': 1, 'autoNeg': 0, 'linkSpeed': 10000, 'uplinkPort': 33554434, 'flags': 268814, 'networkHint': '2095 192.0.2.100/255.255.255.255, 2093 10.110.209.32/255.255.255.252, 2084 0.0.0.0/0.0.0.0', 'macAddr': '34:64:a9:91:42:08', 'vlanhwtx': 1, 'vlanhwrx': 1, 'states': 255, 'pseudo': 0, 'legacy': 1, 'resPoolsSchedAllowed': 1, 'resPoolsSchedSupported': 1}")
        self.logger.debug('Parsing driver name and version from output.')
        return {'module': 'ixgben', 'version':'1.0.0.0'}

    def verify_nic_driver(self, client, vmnic, driver):   #, version
        """
        Check if required driver is present for a nic
        :param client: paramiko SSHClient object
        :param vmnic: (str)<vmnicX> for checking driver
        :param driver: (str)driver name (e.g ixgbe, ixgben, etc)
        :return: (success : bool, message : str) True if specified version of driver is enabled on vmnic else False
        """
        output = self.get_nic_driver(client, vmnic)
        self.logger.info(f'Verifying if driver name is {driver}')
        if output['module'] == driver:
            return str(True), output
        return str(False), output

    def config_nic_driver(self, client, vmnic, driver):
        """
        Configure(enable and load) specified driver on specified NIC
        :param client: paramiko SSHClient object
        :param vmnic: (str)<vmnicX> name of NIC to configure driver on
        :param driver: (str)driver name (e.g ixgbe, ixgben, etc)
        :return: (success : bool, message : str) True if no errors occur while command execution else False
        """
        self.logger.info(f'Checking if {driver} already configured on {vmnic}')
        if self.verify_nic_driver(client, vmnic, driver):
            return str(True), f'{driver} already configured.'
        self.logger.info(f'Checking if {driver} is present on host')
        self.logger.info(f'Executing command: esxcli software vib list | grep {driver} ')
        command = f' esxcli software vib list | grep {driver}'
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        self.logger.info(f'Fetching Output: {output}')
        if re.search(driver, output, re.IGNORECASE):
            self.logger.info(f'Executing command: esxcli system module set -m {driver} -e true ')
            stdin, stdout, stderr = client.exec_command(f' esxcli system module set -m {driver} -e true')
            output1 = stdout.read().decode()
            self.logger.info(f'Fetching Output: {output}')
            self.logger.info(f'Executing command: esxcli system module load -m {driver} ')
            stdin, stdout, stderr = client.exec_command(f' esxcli system module load -m {driver}')
            output2 = stdout.read().decode()
            self.logger.info(f'Fetching Output: {output}')
            if eval(self.verify_nic_driver(client, vmnic, driver)[0]):
                return str(True), output1 + '\n' + output2
            return str(False), output1 + '\n' + output2
        return str(False), output

    def get_fcoe_status(self, client):
        self.logger.debug('Getting FCoE status')
        command = 'esxcfg-module -g ixgbe'
        self.logger.debug(f'Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        self.logger.debug(f'Fetching output: {output}')

    def is_fcoe_enabled(self, client):
        """
        Check whether FCoE is enabled on the ixgbe driver; only for ESXi 6.0U2
        :param client: paramiko SSHClient object
        :return: (success : bool, message : str) True if FCoE is enabled else False
        """
        output = self.get_fcoe_status(client)
        if re.search("options = 'CNA=0,0'", output, re.IGNORECASE):
            return str(True), output
        return str(False), output

    def config_fcoe(self, client, enable):
        """
        Configure FCoE on the ixgbe driver; only for ESXi 6.0U2
        :param client: paramiko SSHClient object
        :param enable: (bool) specifying whether to enable or disable FCoE
        :return: (success : bool, message : str) True if no errors occur while command execution else False
        """
        check = self.is_fcoe_enabled(client)
        if eval(check[0]) == enable:
            return str(True), check[1]
        value = '0, 0' if not enable else '1, 1'
        command = f'esxcli system module parameters set -m ixgbe -p "CNA={value}" '
        self.logger.info(f'Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        self.logger.info(f'Fetching output: {output}')
        if eval(self.is_fcoe_enabled(client)[0]) == enable:
            return str(True), output
        return str(False), output

    def get_rss(self, client, driver):
        self.logger.debug(f'Getting driver details for {driver}')
        command = f'esxcfg-module -g {driver}'
        self.logger.debug(f'Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip('\n')
        self.logger.debug(f'Fetching Output:  {output}')
        data = output[output.find('options'):].split(' = ')
        return {data[0]:eval(data[1])}

    def verify_rss(self, client, driver):
        """
        Check if Receive side scaling is enabled on driver
        :param client: paramiko SSHClient object
        :return: (success : bool, message : str) True if RSS is enabled else False
        """
        output = self.get_rss(client, driver)
        self.logger.info(f'Parsing output to check if RSS is enabled on {driver}')
        if output['options'] == 'RSS=(4)':
            return str(True), output
        return str(False), output

    def config_rss(self, client, driver, enable):
        """
        Configure Receive side scaling on driver
        :param client: paramiko SSHClient object
        :param driver: (str)driver name (e.g ixgbe, ixgben, etc)
        :param enable: (bool) whether or not to enable receive side scaling on the driver
        :return: (success : bool, message : str) True if no errors occur while command execution else False
        """
        check = self.verify_rss(client, driver)
        if eval(check[0]) == enable:
            return str(True), check[1]
        value = '(0)' if enable == False else '(4)'
        command = f'esxcli system module parameters set -m {driver} -p "RSS={value}"'
        self.logger.info(f'Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        self.logger.info(f'Fetching output: {output}')
        if eval(self.verify_rss(client, driver)[0]) == enable:
            return str(True), output
        return str(False), output

    def get_nic_ring_size(self, client, vmnic):
        self.logger.debug(f'Getting nic ring size for {vmnic}')
        command = f'esxcli network nic ring current get --nic-name={vmnic}'
        self.logger.debug(f'Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        data = dict(pair.lstrip().split(': ') for pair in output.split('\n')[:-1])
        self.logger.debug(f'Fetching Output: {data}')
        return data

    def verify_nic_ring_size(self, client, vmnic, RX_SIZE, TX_SIZE):
        """
        Check if current NIC ring size is the same as required sizes
        :param client: paramiko SSHClient object
        :param vmnic: (str) <vmnicX>
        :param RX_SIZE: (int) RX ring size
        :param TX_SIZE: (int) TX ring size
        :return: (success : bool, message : str) True if required ring size is configured on the vmnicX else False
        """
        data = self.get_nic_ring_size(client, vmnic)
        self.logger.info('Parsing output to verify RX and TX ring size')
        if int(data['RX']) == RX_SIZE and int(data['TX']) == TX_SIZE:
            return str(True), data
        return str(False), data

    def config_nic_ring_size(self, client, vmnic, RX_SIZE, TX_SIZE):
        """
        Set ring buffer size for RX and TX of a vmnic
        :param client: paramiko SSHClient object
        :param vmnic: (str)<vmnicX>
        :param RX_SIZE: (int) RX ring size
        :param TX_SIZE: (int) TX ring size
        :return: (success : bool, message : str) True if no errors occur while command execution else False
        """
        check = self.verify_nic_ring_size(client, vmnic, RX_SIZE, TX_SIZE)
        if eval(check[0]):
            return str(True), check[1]
        command = f'esxcli network nic ring current set -n={vmnic} -r={RX_SIZE} -t={TX_SIZE}'
        self.logger.info(f'Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        self.logger.info(f'Fetching Output: {output}')
        if eval(self.verify_nic_ring_size(client, vmnic, RX_SIZE, TX_SIZE)[0]):
            return str(True), output
        return str(False), output

    def get_sw_tx_queue_size(self, client):
        command = 'vsish -ep get /config/Net/intOpts/MaxNetifTxQueueLen'
        self.logger.debug('Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        data = eval(output)
        self.logger.debug(f'Fetching Output: {data}')
        return {'sw_tx_queue_size': data['cur']}

    def verify_sw_tx_queue_size(self, client, queue_length):
        """
        Check software TX queue size
        :param client: paramiko SSHClient object
        :param queue_length: (int) software TX queue length
        :return: (success : bool, message : str) True if s/w TX queue length is same as given parameter else False
        """
        data = self.get_sw_tx_queue_size(client)
        self.logger.info(f'Parsing output to check if sw Tx queue size is {queue_length}')
        if data['sw_tx_queue_size'] == queue_length:
            return str(True), data
        return str(False), data

    def config_sw_tx_queue_size(self, client, queue_length):
        """
        Configure s/w TX queue size
        :param client: paramiko SSHClient object
        :param queue_length: (int) software TX queue length to be configured
        :return: (success : bool, message : str) True if no errors occur while command execution else False
        """
        check = self.verify_sw_tx_queue_size(client, queue_length)
        if eval(check[0]):
            return str(True), check[1]
        command = f'vsish -ep set /config/Net/intOpts/MaxNetifTxQueueLen {queue_length}'
        self.logger.info(f'Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        self.logger.info(f'Fetching Output: {output}')
        if eval(self.verify_sw_tx_queue_size(client, queue_length)[0]):
            return str(True), output
        return str(False), output

    def get_queue_pairing_status(self, client):
        command = 'vsish -ep get /config/Net/intOpts/NetNetqRxQueueFeatPairEnable'
        self.logger.debug(f'Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        data = eval(output)
        self.logger.debug(f'Fetching Output: {data}')
        return {'queue_pairing_enabled': data['cur']}

    def is_queue_pairing_enabled(self, client):
        """
        Check if Queue Pairing is enabled
        :param client: paramiko SSHClient object
        :return: (success : bool, message : str) True if Queue Pairing is enabled else False
        """
        data = self.get_queue_pairing_status(client)
        self.logger.info('Parsing output to check if queue pairing is enabled.')
        if int(data['queue_pairing_enabled']) == 1:
            return str(True), data
        return str(False), data

    def config_queue_pairing(self, client, enable):
        """
        Configure Queue Pairing
        :param client: paramiko SSHClient object
        :param enable: (bool) specify whether to enable or disable Queue Pairing
        :return: (success : bool, message : str) True if no errors occur while command execution else False
        """
        check = self.is_queue_pairing_enabled(client)
        if eval(check[0]) == enable:
            return str(True), check[1]
        value = 1 if enable == True else 0
        command = f'vsish -ep set /config/Net/intOpts/NetNetqRxQueueFeatPairEnable {value}'
        self.logger.info(f'Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        self.logger.info(f'Fetching Output: {output}')
        if eval(self.is_queue_pairing_enabled(client)[0]):
            return str(True), output
        return str(False), output

    def verify_sys_thread_pinning(self, client):
        pass

    def get_split_tx_status(self, client, vmnic):
        self.logger.debug(f'Getting Split Tx status for {vmnic}')
        command = f'vsish -ep get /net/pNics/{vmnic}/sched/txMode'
        self.logger.debug(f'Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip('\n')
        self.logger.debug(f'Fetching Output: {output}')
        return {"txMode": output}

    def is_tx_split_enabled(self, client, vmnic):
        """
        Check if TX split mode is enabled
        :param client: paramiko SSHClient object
        :param vmnic: (str)<vmnicX> name of NIC
        :return: (success : bool, message : str) True if TX split is enabled else False
        """
        output = self.get_split_tx_status(client, vmnic)
        self.logger.info('Parsing output to check if splitTx is enabled.')
        return str(True), output if int(output['txMode']) == 1 else str(False), output

    def config_tx_split(self, client, vmnic, enable):
        """
        Configure TX Split mode
        :param client: paramiko SSHClient object
        :param vmnic: (str)<vmnicX> name of NIC
        :param enable: (bool) specify whether to enable or disable TX Split mode
        :return: (success : bool, message : str) True if no errors occur while command execution else False
        """
        check = self.is_tx_split_enabled(client, vmnic)
        if eval(check[0]) == enable:
            return str(True), check[1]
        value = 1 if enable == True else 0
        command = f'vsish -ep set /net/pNics/{vmnic}/sched/txMode {value}'
        self.logger.info(f'Executing command: {command}')
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        self.logger.info(f'Fetching Output: {output}')
        if eval(self.is_tx_split_enabled(client, vmnic)[0]) == enable:
            return str(True), output
        return str(False), output


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
    return
