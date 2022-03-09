# Standard library imports

# Third party imports
import paramiko

# Local imports
from MainModules.ConnectionFailedError import ConnectionFailedError
from Libraries.PrintMethods import print_with_colour

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
            return
        else:
            try_connect_nr = 0
            while(try_connect_nr < self.CONNECT_ATTEMPTS):
                try_connect_nr += 1
                if(print_status != None):
                    print_status[7] = print_with_colour(f"Reconnecting SSH attempt nr. {try_connect_nr} out of {self.CONNECT_ATTEMPTS}!", "YELLOW")
                connected = self.ssh_connect()
                if(connected):
                    if(print_status != None):
                        print_status[7] = ""
                    return
            raise ConnectionFailedError("Connection failed - SSH.")

    def ssh_connect(self):
        try:
            self.ssh.connect(self.host, username=self.username, password=self.password, timeout=1)
            return True
        except OSError:
            return False

    def first_ssh_connect(self):
        try:
            self.ssh.connect(self.host, username=self.username, password=self.password, timeout=1)
            return True
        except (paramiko.AuthenticationException, paramiko.ssh_exception.NoValidConnectionsError, OSError) as err:
            error_text = ""
            if(isinstance(err, paramiko.AuthenticationException)):
                error_text = "SSH Authentication failed, check your credentials!"
            elif(isinstance(err, paramiko.ssh_exception.NoValidConnectionsError)):
                error_text = f"Not valid SSH connection: {err}"
            else: #OSError
                error_text = f"SSH connection failed, check host value: {err}"
            print(error_text)
            return False

    def ssh_issue_command(self, command, print_status=None):
        # self.try_ssh_connect(print_status)
        try:
            self.try_ssh_connect(print_status)
            _stdin, _stdout,_stderr = self.ssh.exec_command(command)
            output = _stdout.read().decode()
            if(output == "" or output == None):
                print("IF STATEMENT")
                output = self.ssh_issue_command(command, print_status)
        except ConnectionResetError:
            print("ConnectionResetError")
            output = self.ssh_issue_command(command, print_status)
        return output