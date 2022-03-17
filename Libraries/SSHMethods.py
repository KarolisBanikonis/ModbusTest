# Standard library imports
import json

# Local imports
from Libraries.DataMethods import get_first_digit, get_used_memory_from_string
from Libraries.ConversionMethods import convert_string_to_bytes

def ssh_get_uci_hwinfo(ssh, module):
    output = ssh.ssh_issue_command(f"uci get hwinfo.hwinfo.{module}")
    return get_first_digit(output)

def ubus_call(ssh, service, procedure, print_status=None):
    output = ssh.ssh_issue_command(f"ubus -v call {service} {procedure}", print_status)
    return output

def get_router_id(ssh, current_data):
    parsed_data = get_parsed_ubus_data(ssh, current_data)
    modem_id = parsed_data[current_data['parse1']][0][current_data['parse2']]
    return modem_id

def get_parsed_ubus_data(ssh, current_data, print_status=None):
    actual_data = ubus_call(ssh, current_data['service'], current_data['procedure'], print_status)
    parsed_data = json.loads(actual_data) # CIA NULUZTA
    return parsed_data

def get_concrete_ubus_data(ssh, current_data, print_status=None):
    parsed_data = get_parsed_ubus_data(ssh, current_data, print_status)
    concrete_data = parsed_data[current_data['parse']]
    return concrete_data

def gsmctl_call(ssh, flag, print_status=None):
    output = ssh.ssh_issue_command(f"gsmctl -{flag}", print_status)
    return output

def try_enable_gps(ssh):
    gps_enabled = ssh.ssh_issue_command("uci get gps.gpsd.enabled")
    if(get_first_digit(gps_enabled) == "0"):
        ssh.ssh.exec_command("uci set gps.gpsd.enabled='1'")
        ssh.ssh.exec_command("uci commit gps")
        ssh.ssh.exec_command("/etc/init.d/gpsd restart")

def get_router_model(ssh, data):
    parsed_data = get_parsed_ubus_data(ssh, data)
    modem_model = parsed_data['mnfinfo'][data['parse']]
    return modem_model[0:6]

def get_df_used_memory(ssh, mounted_on):
    data = ssh.ssh_issue_command(f"df -h | grep {mounted_on}")
    string_data = get_used_memory_from_string(data)
    bytes = convert_string_to_bytes(string_data)
    return bytes

def get_cpu_count(ssh):
    output = ssh.ssh_issue_command("grep 'model name' /proc/cpuinfo | wc -l")
    return int(get_first_digit(output))