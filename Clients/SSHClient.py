# Third party imports
from socket import timeout
import paramiko
import time

# Local imports

class SSHClient:

    CONNECT_ATTEMPTS = 5

    def __init__(self, configuration):
        self.ssh = paramiko.client.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host = configuration['SERVER_HOST']
        self.username = configuration['USERNAME']
        self.password = configuration['PASSWORD']

    def try_ssh_connect(self):
        state = self.ssh.get_transport().is_active()
        if(state):
            return True
        else:
            try_connect_nr = 0
            while(try_connect_nr <= self.CONNECT_ATTEMPTS):
                try_connect_nr += 1
                connected = self.ssh_connect()
                if(connected):
                    return True
            return False

    def ssh_connect(self):
        try:
            self.ssh.connect(self.host, username=self.username, password=self.password, timeout=1)
            return True
        except paramiko.AuthenticationException:
            print("SSH Authentication failed, check your credentials!")
            return False
        except paramiko.ssh_exception.NoValidConnectionsError as err:
            print(f"Not valid SSH connection: {err}")
            return False
        except TimeoutError as err:
            print(f"Check if you have valid connection: {err}")
            return False
        except OSError as err:
            print(f"SSH connection failed, check host value: {err}")
            return False

    def ssh_issue_command(self, command):
        # connected = self.try_ssh_connect()
        _stdin, _stdout,_stderr = self.ssh.exec_command(command)
        output = _stdout.read().decode()
        return output