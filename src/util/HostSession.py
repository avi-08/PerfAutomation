import pssh.exceptions
from pssh.pssh_client import ParallelSSHClient, SSHClient
from pssh.utils import load_private_key


class HostSession():
    """
    Class for creating and disconnecting ssh sessions with host(s)
    """

    def __init__(self):
        """

        """
        pass

    def connect(self, hosts, user, password, ssl=True, port=22):
        """

        :param hosts: single host(FQDN or IP) or a list of hosts to connect with
        :param user: username(s) of host(s) to connect
        :param password: password(s) of host(s) to connect
        :param ssl: whether secure connection is to be established or not; default is True
        :param port: port number to connect to; default is 22 for ssh
        :return: a session(SSHClient or ParallelSSHClient) object for the requested hosts
        """

        if isinstance(hosts, list):
            try:
                if(ssl):
                    pass
                else:
                    print("Connecting to hosts......")
                    client = ParallelSSHClient(hosts, user=user, password=password, port=port)
                    print("Connected to", hosts)
                    return client
            except pssh.AuthenticationException as authex:
                print("Authentication Exception", authex.args)
            except pssh.ConnectionErrorException as connex:
                print("Connection Error Exception", connex.args)
            except pssh.SSHException as sshex:
                print("Authentication Exception", sshex.args)
        elif isinstance(hosts, str):
            try:
                if (ssl):
                    pass
                else:
                    print("Connecting to host......")
                    client = SSHClient(hosts, user=user, password=password, port=port)
                    print("Connected to", hosts)
                    return client
            except pssh.AuthenticationException as authex:
                print("Authentication Exception", authex.args)
            except pssh.ConnectionErrorException as connex:
                print("Connection Error Exception", connex.args)
            except pssh.SSHException as sshex:
                print("Authentication Exception", sshex.args)


    def disconnect(self, session):
        """

        :param session: PSSH or SSH object to disconnect session
        :return: None
        """

        if isinstance(session, SSHClient):
            pass
        elif isinstance(session, ParallelSSHClient):
            pass


