#!/usr/bin/env python

# Standard library imports
import time

# Third party imports
from reprint import output
import paramiko
import socket

# Local imports
from Libraries.FileMethods import read_file, close_all_instances, terminate_program
from MainModules.ConnectionFailedError import ConnectionFailedError
from MainModules.ModuleLoader import ModuleLoader
from MainModules.ConfigurationModule import ConfigurationModule
from MainModules.InformationModule import InformationModule
from Clients.SSHClient import SSHClient
from Clients.Modbus import Modbus
from MainModules.ReportModule import ReportModule

CONFIGURATION_FILE = "config.json"
PARAMETERS_FILE = "registers.json"

def main():
    conf = ConfigurationModule(CONFIGURATION_FILE)
    data = read_file(PARAMETERS_FILE)
    ssh_client = SSHClient(conf.get_all_data())
    ssh_connected = ssh_client.ssh_connect()
    if(ssh_connected == False):
        terminate_program()
    info = InformationModule(ssh_client, data['InformationModule'][0])
    report = ReportModule(info)
    modbus = Modbus(conf.get_all_data())
    modbus_is_setup_valid = modbus.setup_modbus()
    if(modbus_is_setup_valid == False):
        close_all_instances([ssh_client.ssh, modbus.client])
    module_loader = ModuleLoader(conf, ssh_client)
    module_instances = module_loader.init_modules(data, modbus, info, report)
    test_count = [0, 0, info.get_used_memory()] # test_number, correct_number, used_ram

    with output(output_type="list", initial_len=8, interval=0) as output_list:
        while True:
            modbus_connected = modbus.try_connect()
            if(modbus_connected == False):
                close_all_instances([ssh_client.ssh, modbus.client])
            else:
                # Remove CSV report's contents if it exists, otherwise create it
                # delete_file_content(CSV_REPORT_FILE)
                output_list[0] = f"Model - {info.router_model}"
                # 0 - System, 1 - Network, 2 - Mobile, 3 - GPS
                for module in module_instances:
                    # test_count = module.read_all_data(output_list, test_count)
                    # try:
                    test_count = module.read_all_data(output_list, test_count)
                    # except ConnectionResetError as err:
                    #     output_list[7] = f"Connection stopped: {err}"
                    #     close_all_instances([ssh_client.ssh, modbus.client])
                    # except socket.error as err:
                    #     output_list[7] = f"Socket error: {err}"
                    #     close_all_instances([ssh_client.ssh, modbus.client])
                    # except paramiko.SSHException as err:
                    #     output_list[7] = f"SSH connection stopped: {err}"
                    #     close_all_instances([ssh_client.ssh, modbus.client])

                time.sleep(1)
            
            # time.sleep(10)

if __name__ == "__main__":
    main()