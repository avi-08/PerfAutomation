import base64
import logging

import paramiko

from src.util.LogUtil import LogUtil


class HostSession:
    """
    Class for creating and disconnecting ssh sessions with host(s)
    """

    def __init__(self):
        """

        """
        self.logger = LogUtil()
        pass

    def connect(self, host, user, password, ssl=False, port=22):
        """
        Function that creates a ssh session with the host and returns an object of paramiko.SSHClient
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
                self.logger.info("Connecting to host using ssl......")
                client.get_host_keys().add(host, 'ssh-rsa', key)
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(host, username=user, password=password, port=port)
                self.logger.info(f"Connected to {host}")
                return client
            else:
                self.logger.info("Connecting to host......")
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(host, username=user, password=password, port=port)
                self.logger.info(f"Connected to {host}")
                return client
        except paramiko.AuthenticationException as authex:
            self.logger.exception(f"Authentication Exception {authex.args}")
        except paramiko.SSHException as sshex:
            self.logger.exception(f"SSH Exception {sshex.agrs}")
        except Exception as ex:
            self.logger.exception(f"Connection Error Exception {ex.args}")

    def disconnect(self, client):
        """
        Function to close the ssh session with host,
        :param client: paramiko.SSHClient object to disconnect session
        :return: None
        """
        self.logger.info(f"Disconnecting from {client.get_transport().getpeername()[0]}......")
        client.close()
        self.logger.info("Disconnected.")


