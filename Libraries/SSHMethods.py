# Local imports
from Libraries.FileMethods import extract_status

def ssh_get_modules_status(ssh, modules):
    status_list = []
    for i in range(len(modules)):
        _stdin, _stdout,_stderr = ssh.ssh.exec_command(f"uci get hwinfo.hwinfo.{modules[i]['name']}")
        output = _stdout.read().decode()
        status_list.append(extract_status(output))
    return status_list

def ubus_call(ssh, service, procedure):
    output = ssh.ssh_issue_command(f"ubus -v call {service} {procedure}")
    return output

def gsmctl_call(ssh, flag):
    output = ssh.ssh_issue_command(f"gsmctl -{flag}")
    return output