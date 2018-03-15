import base64
import logging

import paramiko

from src.util import LogUtil

_LOGGER = logging.getLogger(__name__)


class HostSession:
    """
    Class for creating and disconnecting ssh sessions with host(s)
    """

    def __init__(self):
        """

        """
        pass

    def connect(self, host, user, password, ssl=True, port=22):
        """

        :param host: host(FQDN or IP) to connect with
        :param user: username of host to connect
        :param password: password of host to connect
        :param ssl: whether secure connection is to be established or not; default is True
        :param port: port number to connect to; default is 22 for ssh
        :return: a session(SSHClient) object for the requested host
        """

        try:
            client = paramiko.SSHClient()
            if ssl:
                key = paramiko.RSAKey(data=base64.b64decode(b'AAAA'))
                #print("Connecting to host using ssl......")
                client.get_host_keys().add(host, 'ssh-rsa', key)
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(host, username=user, password=password, port=port)
                #print("Connected to", host)
                return client
            else:
                _LOGGER.info("Connecting to host......")
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(host, username=user, password=password, port=port)
                _LOGGER.info(f"Connected to {host}")
                return client
        except paramiko.AuthenticationException as authex:
            _LOGGER.exception(f"Authentication Exception {authex.args}")
        except paramiko.SSHException as sshex:
            _LOGGER.exception(f"Authentication Exception {sshex.agrs}")
        except Exception as ex:
            _LOGGER.exception(f"Connection Error Exception {ex.args}")
    def disconnect(self, client):
        """

        :param client: PSSH or SSH object to disconnect session
        :return: None
        """
        _LOGGER.info(f"Disconnecting from {client.get_transport().getpeername()[0]}......")
        #print("Disconnecting from host......")
        client.close()
        _LOGGER.info("Disconnected.")
        #print("Disconnected.")


