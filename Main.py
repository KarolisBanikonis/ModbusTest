#!/usr/bin/env python

# Standard library imports
import time

# Third party imports
from reprint import output

# Local imports
from Libraries.FileMethods import read_file, close_all_instances, generate_file_name
from Clients.SSHClient import SSHClient
from Clients.Modbus import Modbus
from DataModules.ModuleLoader import ModuleLoader
from Libraries.SSHMethods import get_router_model

CONFIGURATION_FILE = "config.json"
PARAMETERS_FILE = "registers.json"
name = "Report"
CSV_REPORT_FILE = f"Reports/{generate_file_name(name)}.csv"

def main():
    configuration, file1 = read_file(CONFIGURATION_FILE)
    data, file2 = read_file(PARAMETERS_FILE)
    ssh_client = SSHClient(configuration['Settings'][0])
    modbus = Modbus(configuration['Settings'][0])
    instances = [file1, file2, ssh_client.ssh, modbus.client]
    modbus_is_setup_valid = modbus.setup_modbus()
    if(modbus_is_setup_valid == False):
        close_all_instances(instances)
    ssh_connected = ssh_client.ssh_connect()
    if(ssh_connected == False):
        close_all_instances(instances)
    model = get_router_model(ssh_client, configuration['Settings'][0]['MODEL'])
    CSV_REPORT_FILE = f"Reports/{generate_file_name(model)}.csv"
    module_loader = ModuleLoader(ssh_client, configuration['Settings'][0]['MODULES'])
    module_instances = module_loader.init_modules(CSV_REPORT_FILE, modbus, data)
    test_count = [0, 0] # test_number, correct_number

    with output(output_type="list", initial_len=5, interval=0) as output_list:
        while True:
            modbus_connected = modbus.try_connect()
            if(modbus_connected == False):
                close_all_instances(instances)
            else:
                # Remove CSV report's contents if it exists, otherwise create it
                # delete_file_content(CSV_REPORT_FILE)
                # 0 - System, 1 - Network, 2 - Mobile, 3 - GPS
                for module in module_instances:
                    test_count = module.read_all_data(output_list, test_count)
            
            time.sleep(10)

if __name__ == "__main__":
    main()