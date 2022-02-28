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
        self.modules = configuration['MODULES']

    def ssh_connect(self):
        self.ssh.connect(self.host, username=self.username, password=self.password)

    def ssh_get_modules_status(self):
        status_list = []
        self.ssh_connect()
        for i in range(len(self.modules)):
            _stdin, _stdout,_stderr = self.ssh.exec_command(f"uci get hwinfo.hwinfo.{self.modules[i]['name']}")
            output = _stdout.read().decode()
            status_list.append(extract_status(output))
        self.ssh.close()
        return status_list

    def ssh_issue_command(self, command):
        self.ssh_connect()
        _stdin, _stdout,_stderr = self.ssh.exec_command(command)
        output = _stdout.read().decode()
        self.ssh.close()
        return output

    def ubus_call(self, service, procedure):
        output = self.ssh_issue_command(f"ubus -v call {service} {procedure}")
        return output