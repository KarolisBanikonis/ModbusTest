# Standard library imports
import time

# Third party imports
import paramiko

# Local imports
from MainModules.ConnectionFailedError import ConnectionFailedError

class SSHClient:

    CONNECT_ATTEMPTS = 7
    SLEEP_TIME = 0.2

    def __init__(self, configuration):
        self.ssh = paramiko.client.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host = configuration['SERVER_HOST']
        self.username = configuration['USERNAME']
        self.password = configuration['PASSWORD']

    def try_ssh_connect(self, print_status=None):
        state = self.ssh.get_transport().is_active()
        if(state):
            return True
        else:
            try_connect_nr = 0
            while(try_connect_nr < self.CONNECT_ATTEMPTS):
                try_connect_nr += 1
                if(print_status != None):
                    print_status[7] = f"Reconnecting SSH attempt nr {try_connect_nr} out of {self.CONNECT_ATTEMPTS}!"
                connected = self.ssh_connect()
                if(connected):
                    if(print_status != None):
                        print_status[7] = ""
                    return True
            raise ConnectionFailedError("Connection failed - SSH.")

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
            # print(f"SSH connection failed, check host value: {err}")
            return False

    def ssh_issue_command(self, command, print_status=None):
        connected = self.try_ssh_connect()
        try:
            _stdin, _stdout,_stderr = self.ssh.exec_command(command)
            output = _stdout.read().decode()
            if(output == "" or output == None):
                # raise ConnectionFailedError("Connection failed - In SSH command exec.")
                time.sleep(self.SLEEP_TIME)
                self.try_ssh_connect(print_status)
                output = self.ssh_issue_command(command, print_status)
        except ConnectionResetError as err:
            time.sleep(self.SLEEP_TIME)
            output = self.ssh_issue_command(command, print_status)
        return output