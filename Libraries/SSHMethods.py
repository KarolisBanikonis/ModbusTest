# Standard library imports
import json

# Local imports
from Libraries.DataMethods import get_first_digit, get_used_memory_from_string
from Libraries.ConversionMethods import convert_string_to_bytes

def ssh_get_uci_hwinfo(ssh, subsystem):
    """
    Check if specified device's subsystem is enabled via SSH.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            subsystem (str): which device's subsystem should be checked
        Returns:
            state (int): is device subsystem enabled or not: 1 or 0
    """
    output = ssh.ssh_issue_command(f"uci get hwinfo.hwinfo.{subsystem}")
    state = get_first_digit(output)
    return state

def ubus_call(ssh, service, procedure, output_list=None):
    """
    Call specified procedure with ubus tool via SSH to get information about device.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            service (str): which device's service should be checked
            procedure (str): which service's procedure should be called
            output_list (reprint.reprint.output.SignalList): list required for printing to terminal
        Returns:
            output (str): information about device in string format
    """
    output = ssh.ssh_issue_command(f"ubus -v call {service} {procedure}", output_list)
    return output

def get_modem_id(ssh, register_params):
    """
    Call procedure with ubus tool via SSH to get device's modem id.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            register_params (dict): current register's parameters information
        Returns:
            modem_id (str): device's modem id
    """
    parsed_data = get_parsed_ubus_data(ssh, register_params)
    modem_id = parsed_data[register_params['parse1']][0][register_params['parse2']]
    return modem_id

def get_parsed_ubus_data(ssh, register_params, output_list=None):
    """
    Call procedure with ubus tool via SSH to get information about device.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            register_params (dict): current register's parameters information
            output_list (reprint.reprint.output.SignalList): list required for printing to terminal
        Returns:
            output (dict): information about device
    """
    actual_data = ubus_call(ssh, register_params['service'], register_params['procedure'], output_list)
    parsed_data = json.loads(actual_data) # CIA NULUZTA
    return parsed_data

def get_concrete_ubus_data(ssh, register_params, output_list=None):
    """
    Call procedure with ubus tool via SSH to get exact parsed data about device.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            register_params (dict): current register's parameters information
            output_list (reprint.reprint.output.SignalList): list required for printing to terminal
        Returns:
            output (dict): exact parsed data about device
    """
    parsed_data = get_parsed_ubus_data(ssh, register_params, output_list)
    concrete_data = parsed_data[register_params['parse']]
    return concrete_data

def gsmctl_call(ssh, flag, output_list=None):
    """
    Call procedure with gsmctl tool via SSH to get exact data about device.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            flag (str): what flag should be used when using gsmctl
            output_list (reprint.reprint.output.SignalList): list required for printing to terminal
        Returns:
            output (int): exact data about device
    """
    output = ssh.ssh_issue_command(f"gsmctl -{flag}", output_list)
    return output

def try_enable_gps(ssh):
    """
    Tries to enable GPS service on device.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
    """
    gps_enabled = ssh.ssh_issue_command("uci get gps.gpsd.enabled")
    if(get_first_digit(gps_enabled) == 0):
        ssh.ssh.exec_command("uci set gps.gpsd.enabled='1'")
        ssh.ssh.exec_command("uci commit gps")
        ssh.ssh.exec_command("/etc/init.d/gpsd restart")

def get_router_model(ssh, param_values):
    """
    Call procedure with ubus tool via SSH to get device's model.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            param_values (dict): parameters information for ubus tool
    """
    parsed_data = get_parsed_ubus_data(ssh, param_values)
    modem_model = parsed_data['mnfinfo'][param_values['parse']]
    return modem_model[0:6]

def get_df_used_memory(ssh, mounted_on):
    """
    Get how much used memory is on specified mount location.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            mounted_on (str): what mount location should be checked
    """
    data = ssh.ssh_issue_command(f"df -h | grep {mounted_on}")
    string_data = get_used_memory_from_string(data)
    bytes = convert_string_to_bytes(string_data)
    return bytes

def get_cpu_count(ssh): #unused really
    output = ssh.ssh_issue_command("grep 'model name' /proc/cpuinfo | wc -l")
    return get_first_digit(output)