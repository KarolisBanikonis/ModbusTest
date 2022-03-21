# Standard library imports

# Third party imports
import paramiko

# Local imports
from MainModules.ConnectionFailedError import ConnectionFailedError
from Libraries.PrintMethods import print_error
from MainModules.Logger import log_msg

class SSHClient:

    def __init__(self, conf):
        """
        Initializes SSHClient object. Set settings required for establishing SSH connection.

            Parameters:
                    conf (ConfigurationModule): module that holds configuration information
        """
        self.ssh = paramiko.client.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host = conf['SERVER_HOST']
        self.username = conf['USERNAME']
        self.password = conf['PASSWORD']
        self.connect_attempts = conf['RECONNECT_ATTEMPTS']
        self.timeout = conf['TIMEOUT']
        self.init_ssh_setup()

    def init_ssh_setup(self):
        """
        Data validation for making connections via SSH.
        Trying to establish connection for the first time in program.
        """
        try:
            self.ssh.connect(self.host, username=self.username, password=self.password, timeout=self.timeout)
            log_msg(__name__, "info", "SSH setup is successful!")
        except (paramiko.AuthenticationException, paramiko.ssh_exception.NoValidConnectionsError, OSError) as err:
            error_text = ""
            if(isinstance(err, paramiko.AuthenticationException)):
                error_text = "SSH Authentication failed, check your credentials!"
            elif(isinstance(err, paramiko.ssh_exception.NoValidConnectionsError)):
                error_text = f"Not valid SSH connection: {err}"
            else: #OSError
                error_text = f"SSH connection failed, check host value: {err}"
            print(error_text)
            log_msg(__name__, "critical", error_text)
            quit()

    def try_ssh_connect(self, output_list=None):
        """
        Try to establish connection via SSH with server.
        If connection is not made, try to establish connection set amount of times.

            Parameters:
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
        """
        state = self.ssh.get_transport().is_active()
        if(state):
            return
        else:
            try_connect_nr = 0
            while(try_connect_nr < self.connect_attempts):
                try_connect_nr += 1
                if(output_list != None):
                    error_text = f"Reconnecting SSH attempt nr. {try_connect_nr} out of {self.connect_attempts}!"
                    log_msg(__name__, "critical", error_text)
                    print_error(error_text, output_list, "YELLOW")
                connected = self.ssh_connect()
                if(connected):
                    if(output_list != None):
                        print_error("", output_list)
                    return
            raise ConnectionFailedError("Connection failed - SSH.")

    def ssh_connect(self):
        """Try to establish connection via SSH with server once."""
        try:
            self.ssh.connect(self.host, username=self.username, password=self.password, timeout=self.timeout)
            return True
        except OSError:
            return False

    def ssh_issue_command(self, command, output_list=None):
        """
        Execute a command on the SSH server.

            Parameters:
                command (str): command that should be executed on SSH server
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                output (str): what output command produces 
        """
        try:
            self.try_ssh_connect(output_list)
            _stdin, _stdout,_stderr = self.ssh.exec_command(command)
            output = _stdout.read().decode()
            if(output == None or output == ""):
                output = self.ssh_issue_command(command, output_list)
        except (ConnectionResetError, EOFError):
            output = self.ssh_issue_command(command, output_list)
        return output