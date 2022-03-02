#!/usr/bin/env python

# Standard library imports
import time

# Third party imports


# Local imports
from Libraries.FileMethods import read_file, load_module, close_all_instances, delete_file_content
from Libraries.SSHMethods import try_enable_gps, ssh_get_uci_hwinfo
from Clients.SSHClient import SSHClient
from Clients.Modbus import Modbus
from DataModules.ModuleSystem import ModuleSystem
from DataModules.ModuleNetwork import ModuleNetwork
from DataModules.ModuleLoader import ModuleLoader

CONFIGURATION_FILE = "config.json"
PARAMETERS_FILE = "registers.json"
CSV_REPORT_FILE = "Reports/modbus_test_report.csv"
MODULES_DIRECTORY = "DataModules."

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
    dual_sim_status = ssh_get_uci_hwinfo(ssh_client, "dual_sim")
    module_loader = ModuleLoader(ssh_client, configuration['Settings'][0]['MODULES'], dual_sim_status)
    module_instances = module_loader.init_modules(CSV_REPORT_FILE, modbus, data)

    while True:
        modbus_connected = modbus.try_connect()
        if(modbus_connected == False):
            close_all_instances(instances)
        else:
            # Remove CSV report's contents if it exists, otherwise create it
            can_open = delete_file_content(CSV_REPORT_FILE)
            if(can_open == False):
                close_all_instances(instances)
            # 0 - System, 1 - Network, 2 - Mobile, 3 - GPS
            for module in module_instances:
                module.read_all_data()
        
        time.sleep(10)

if __name__ == "__main__":
    main()