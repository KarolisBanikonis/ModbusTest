# Third party imports
import paramiko

# Local imports
from Libraries.FileMethods import extract_status

class SSHClient:

    def __init__(self, configuration):
        self.ssh = paramiko.client.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host = configuration['SERVER_HOST']
        self.username = configuration['USERNAME']
        self.password = configuration['PASSWORD']

    def ssh_connect(self):
        try:
            self.ssh.connect(self.host, username=self.username, password=self.password)
            return True
        except paramiko.AuthenticationException:
            print("SSH Authentication failed, check your credentials!")
            return False
        except paramiko.ssh_exception.NoValidConnectionsError as err:
            print(f"Not valid SSH connection: {err}")
            return False
        except OSError as err:
            print(f"SSH connection failed, check host value: {err}")
            return False

    def ssh_issue_command(self, command):
        _stdin, _stdout,_stderr = self.ssh.exec_command(command)
        output = _stdout.read().decode()
        # self.ssh.close()
        return output