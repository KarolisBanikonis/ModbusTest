#!/usr/bin/env python

# Standard library imports
import time

# Third party imports
from reprint import output
from colorama import Fore, Style

# Local imports
from Libraries.FileMethods import read_file, close_all_instances
from DataModules.ModuleLoader import ModuleLoader
from DataModules.ConfigurationModule import ConfigurationModule
from DataModules.InformationModule import InformationModule
from Clients.SSHClient import SSHClient
from Clients.Modbus import Modbus

CONFIGURATION_FILE = "config.json"
PARAMETERS_FILE = "registers.json"

def main():
    conf = ConfigurationModule(CONFIGURATION_FILE)
    data = read_file(PARAMETERS_FILE)
    ssh_client = SSHClient(conf.get_all_data())
    ssh_connected = ssh_client.ssh_connect()
    if(ssh_connected == False):
        close_all_instances([ssh_client])
    info = InformationModule(ssh_client, conf)
    modbus = Modbus(conf.get_all_data())
    modbus_is_setup_valid = modbus.setup_modbus()
    if(modbus_is_setup_valid == False):
        close_all_instances([ssh_client.ssh, modbus.client])
    module_loader = ModuleLoader(conf, ssh_client)
    module_instances = module_loader.init_modules(data, modbus, info)
    test_count = [0, 0, info.get_memory()] # test_number, correct_number, used_ram

    with output(output_type="list", initial_len=6, interval=0) as output_list:
        while True:
            modbus_connected = modbus.try_connect()
            if(modbus_connected == False):
                close_all_instances([ssh_client.ssh, modbus.client])
            else:
                # Remove CSV report's contents if it exists, otherwise create it
                # delete_file_content(CSV_REPORT_FILE)
                # 0 - System, 1 - Network, 2 - Mobile, 3 - GPS
                for module in module_instances:
                    test_count = module.read_all_data(output_list, test_count)
                time.sleep(1)
            
            # time.sleep(10)

if __name__ == "__main__":
    main()