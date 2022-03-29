# Standard library imports

# Third party imports
import paramiko

# Local imports
from MainModules.ConnectionFailedError import ConnectionFailedError
from MainModules.Logger import log_msg

class SSHClient:

    def __init__(self, conf, print_mod):
        """
        Initializes SSHClient object. Set settings required for establishing SSH connection.

            Parameters:
                conf (ConfigurationModule): module that holds configuration information
                print_mod (PrintModule): module designed for printing to terminal
        """
        self.ssh = paramiko.client.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host = conf['SERVER_HOST']
        self.username = conf['USERNAME']
        self.password = conf['PASSWORD']
        self.connect_attempts = conf['RECONNECT_ATTEMPTS']
        self.timeout = conf['TIMEOUT']
        self.setup_error = self.init_ssh_setup(print_mod)

    def init_ssh_setup(self, print_mod):
        """
        Data validation for making connections via SSH.
        Trying to establish connection for the first time in program.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                None, if setup was successful
                error_text (str): occurred error's text, if setup was not successful
        """
        try:
            self.ssh.connect(self.host, username=self.username, password=self.password, timeout=self.timeout)
            log_msg(__name__, "info", "SSH setup is successful!")
            return None
        except (paramiko.AuthenticationException, paramiko.ssh_exception.NoValidConnectionsError, OSError) as err:
            error_text = ""
            if(isinstance(err, paramiko.AuthenticationException)):
                error_text = "SSH Authentication failed, check your credentials!"
            elif(isinstance(err, paramiko.ssh_exception.NoValidConnectionsError)):
                error_text = f"Not valid SSH connection: {err}"
            else: #OSError
                error_text = f"SSH connection failed, check host value: {err}"
            print_mod.error(error_text)
            log_msg(__name__, "critical", error_text)
            return error_text

    def close(self):
        """Closes SSH connection."""
        self.ssh.close()

    def try_ssh_connect(self, print_mod):
        """
        Try to establish connection via SSH with server.
        If connection is not made, try to establish connection set amount of times.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
        """
        state = self.ssh.get_transport().is_active()
        if(state):
            return
        else:
            try_connect_nr = 0
            while(try_connect_nr < self.connect_attempts):
                try_connect_nr += 1
                error_text = f"Reconnecting SSH attempt nr. {try_connect_nr} out of {self.connect_attempts}!"
                log_msg(__name__, "critical", error_text)
                print_mod.warning(error_text)
                connected = self.ssh_connect()
                if(connected):
                    print_mod.clear_warning()
                    return
            raise ConnectionFailedError("Connection failed - SSH.")

    def ssh_connect(self):
        """Try to establish connection via SSH with server once."""
        try:
            self.ssh.connect(self.host, username=self.username, password=self.password, timeout=self.timeout)
            return True
        except OSError:
            return False

    def ssh_issue_command(self, command, print_mod):
        """
        Execute a command on the SSH server.

            Parameters:
                command (str): command that should be executed on SSH server
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                output (str): what output command produces 
        """
        try:
            self.try_ssh_connect(print_mod)
            _stdin, _stdout,_stderr = self.ssh.exec_command(command)
            output = _stdout.read().decode()
            if(output == None or output == ""):
                output = self.ssh_issue_command(command, print_mod)
        except (ConnectionResetError, EOFError):
            output = self.ssh_issue_command(command, print_mod)
        return output