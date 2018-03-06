import base64

import paramiko


class HostSession:
    """
    Class for creating and disconnecting ssh sessions with host(s)
    """

    def __init__(self):
        """

        """
        pass

    def connect(self, host, user, password, ssl=False, port=22):
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
                print("Connecting to host using ssl......")
                client.get_host_keys().add(host, 'ssh-rsa', key)
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(host, username=user, password=password, port=port)
                print("Connected to", host)
                return client
            else:
                print("Connecting to host......")
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(host, username=user, password=password, port=port)
                print("Connected to", host)
                return client
        except paramiko.AuthenticationException as authex:
            print("Authentication Exception", authex.args)
        except paramiko.SSHException as sshex:
            print("Authentication Exception", sshex.args)
        except Exception as ex:
            print("Connection Error Exception", ex.args)

    def disconnect(self, session):
        """

        :param session: PSSH or SSH object to disconnect session
        :return: None
        """
        print("Disconnecting from host......")
        session.close()
        print("Disconnected.")


