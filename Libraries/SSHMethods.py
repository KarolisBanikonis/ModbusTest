# Standard library imports
import json

# Local imports
from Libraries.DataMethods import get_first_digit, get_used_memory_from_string
from Libraries.DataMethods import get_first_value_in_quotes
from Libraries.ConversionMethods import convert_string_to_bytes

def ssh_get_uci_hwinfo(ssh, subsystem, print_mod):
    """
    Check if specified device's subsystem is enabled via SSH.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            subsystem (str): which device's subsystem should be checked
            print_mod (PrintModule): module designed for printing to terminal
        Returns:
            state (int): is device subsystem enabled or not: 1 or 0
    """
    output = ssh.ssh_issue_command(f"uci get hwinfo.hwinfo.{subsystem}", print_mod)
    state = get_first_digit(output)
    return state

def ubus_call(ssh, service, procedure, print_mod):
    """
    Call specified procedure with ubus tool via SSH to get information about device.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            service (str): which device's service should be checked
            procedure (str): which service's procedure should be called
            print_mod (PrintModule): module designed for printing to terminal
        Returns:
            output (str): information about device in string format
    """
    output = ssh.ssh_issue_command(f"ubus -v call {service} {procedure}", print_mod)
    return output

def get_modem_id(ssh, register_params, print_mod):
    """
    Call procedure with ubus tool via SSH to get device's modem id.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            register_params (dict): current register's parameters information
            print_mod (PrintModule): module designed for printing to terminal
        Returns:
            modem_id (str): device's modem id
    """
    parsed_data = get_device_json_ubus_data(ssh, register_params, print_mod)
    modem_id = parsed_data[register_params['parse1']][0][register_params['parse2']]
    return modem_id

def get_device_json_ubus_data(ssh, register_params, print_mod):
    """
    Call procedure with ubus tool via SSH to get information about device.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            register_params (dict): current register's parameters information
            print_mod (PrintModule): module designed for printing to terminal
        Returns:
            output (dict): information about device
    """
    real_data = ubus_call(ssh, register_params['service'], register_params['procedure'], print_mod)
    parsed_data = json.loads(real_data)
    return parsed_data

def gsmctl_call(ssh, flag, print_mod):
    """
    Call procedure with gsmctl tool via SSH to get exact data about device.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            flag (str): what flag should be used when using gsmctl
            print_mod (PrintModule): module designed for printing to terminal
        Returns:
            output (int): exact data about device
    """
    output = ssh.ssh_issue_command(f"gsmctl -{flag}", print_mod)
    return output

def enable_gps_service(ssh):
    """
    Enables GPS service on device.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            print_mod (PrintModule): module designed for printing to terminal
    """
    ssh.ssh.exec_command("uci set gps.gpsd.enabled='1'")
    ssh.ssh.exec_command("uci commit gps")
    ssh.ssh.exec_command("/etc/init.d/gpsd restart")

def get_mobile_apn(ssh, print_mod, interface):
    """
    Gets specified mobile interface's APN stored in configuration file.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            print_mod (PrintModule): module designed for printing to terminal
            interface (str): mobile interface's name
        Returns:
            output (str): specified mobile interface's APN
    """
    command = f"cat /etc/config/network | grep -A 10 {interface} | grep 'option apn'"
    output = ssh.ssh_issue_command(command, print_mod)
    if(output is not None):
        output = get_first_value_in_quotes(output)
    return output

def get_device_model(ssh, param_values, print_mod):
    """
    Call procedure with ubus tool via SSH to get device's model.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            param_values (dict): parameters information for ubus tool
            print_mod (PrintModule): module designed for printing to terminal
        Returns:
            model_name (str): device's model name
    """
    parsed_data = get_device_json_ubus_data(ssh, param_values, print_mod)
    model_name = parsed_data[param_values['parse1']][param_values['parse2']]
    model_name = model_name[0:6]
    return model_name

def get_df_used_memory(ssh, mounted_on, print_mod):
    """
    Get how much used memory is on specified mount location.

        Parameters:
            ssh (SSHClient): module required to make connection to server via SSH
            mounted_on (str): what mount location should be checked
            print_mod (PrintModule): module designed for printing to terminal
        Returns:
            bytes (int): used memory in bytes
    """
    data = ssh.ssh_issue_command(f"df -h | grep {mounted_on}", print_mod)
    string_data = get_used_memory_from_string(data)
    bytes = convert_string_to_bytes(string_data)
    return bytes