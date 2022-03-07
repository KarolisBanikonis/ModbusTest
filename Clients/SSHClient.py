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

    # def raise_error(self, value):
    #     if(value != None):


    def try_ssh_connect(self):
        state = self.ssh.get_transport().is_active()
        if(state):
            return True
        else:
            try_connect_nr = 0
            while(try_connect_nr < self.CONNECT_ATTEMPTS):
                try_connect_nr += 1
                connected = self.ssh_connect()
                if(connected):
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

    def ssh_issue_command(self, command):
        connected = self.try_ssh_connect()
        # try:
        _stdin, _stdout,_stderr = self.ssh.exec_command(command)
        output = _stdout.read().decode()
        try_connect_nr = 0
        if(output == "" or output == None):
            # while(try_connect_nr < self.CONNECT_ATTEMPTS):
            #     try_connect_nr += 1
            #     time.sleep(self.SLEEP_TIME)
            #     self.try_ssh_connect()
            #     self.ssh_issue_command(command)
            # raise ConnectionFailedError("Connection failed - In SSH command exec.")
            time.sleep(self.SLEEP_TIME)
            self.try_ssh_connect()
            output = self.ssh_issue_command(command)
        # except ConnectionResetError as err:
        #     time.sleep(self.SLEEP_TIME)
        #     self.ssh_issue_command(command)
        return output