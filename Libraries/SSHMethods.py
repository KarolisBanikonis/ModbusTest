# Standard library imports
import json

# Local imports
from Libraries.FileMethods import extract_status
from DataModules import ModuleCSV

def ssh_get_uci_hwinfo(ssh, module):
    output = ssh.ssh_issue_command(f"uci get hwinfo.hwinfo.{module}")
    return extract_status(output)

def ubus_call(ssh, service, procedure):
    output = ssh.ssh_issue_command(f"ubus -v call {service} {procedure}")
    return output

def get_parsed_ubus_data(ssh, current_data):
        actual_data = ubus_call(ssh, current_data['service'], current_data['procedure'])
        parsed_data = json.loads(actual_data)
        return parsed_data

def gsmctl_call(ssh, flag):
    output = ssh.ssh_issue_command(f"gsmctl -{flag}")
    return output

def try_enable_gps(ssh):
    gps_enabled = ssh.ssh_issue_command("uci get gps.gpsd.enabled")
    if(extract_status(gps_enabled) == "0"):
        ssh.ssh_issue_command("uci set gps.gpsd.enabled='1'")
        ssh.ssh_issue_command("uci commit gps.gpsd")
        ssh.ssh_issue_command("/etc/init.d/gpsd start")

def get_router_model(ssh, data):
    parsed_data = get_parsed_ubus_data(ssh, data)
    modem_model = parsed_data['mnfinfo'][data['parse']]
    return modem_model