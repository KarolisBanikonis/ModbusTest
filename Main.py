#!/usr/bin/env python

# Standard library imports
import time

# Third party imports


# Local imports
from Libraries.FileMethods import read_file
from Libraries.FileMethods import load_module
from Libraries.FileMethods import program_quit
from Libraries.SSHMethods import ssh_get_modules_status
from Clients.SSHClient import SSHClient
from Clients.Modbus import Modbus
from DataModules.ModuleSystem import ModuleSystem
from DataModules.ModuleNetwork import ModuleNetwork

CONFIGURATION_FILE = "config.json"
PARAMETERS_FILE = "registers.json"
MODULES_DIRECTORY = "DataModules."

def main():
    configuration, file1 = read_file(CONFIGURATION_FILE)
    data, file2 = read_file(PARAMETERS_FILE)
    ssh_client = SSHClient(configuration['Settings'][0])
    modbus = Modbus(configuration['Settings'][0])
    opened_files = [file1, file2]
    ssh_connected = ssh_client.ssh_connect()
    if(ssh_connected == False):
        program_quit(opened_files, ssh_client, modbus)
    modules_enabled = ssh_get_modules_status(ssh_client, configuration['Settings'][0]['MODULES'])
    # ---- System Module ----
    module_system = ModuleSystem(modbus, data['System'], ssh_client)
    # ---- Network Module ----
    module_network = ModuleNetwork(modbus, data['Network'], ssh_client)
    # ---- Mobile Module ----
    if(modules_enabled[0] == "1"):
        mobile = load_module(MODULES_DIRECTORY + 'ModuleMobile')
        module_mobile = mobile.ModuleMobile(modbus, data['Mobile'], ssh_client, modules_enabled[1]) #pass if dual_sim is enabled
    # ---- GPS Module ----
    if(modules_enabled[2] == "1"):
    # check if it is turned and accordingly turn it on
        gps_enabled = ssh_client.ssh_issue_command("uci get gps.gpsd.enabled")
        if(gps_enabled == "0"):
            ssh_client.ssh_issue_command("uci set gps.gpsd.enabled='1'")
            ssh_client.ssh_issue_command("uci commit gps.gpsd")
        gps = load_module(MODULES_DIRECTORY + 'ModuleGPS')
        module_gps = gps.ModuleGPS(modbus, data['GPS'], ssh_client)

    while True:
        modbus_connected = modbus.check_connection()
        print(modbus_connected)
        if(modbus_connected == False):
            program_quit(opened_files, ssh_client, modbus)
        else:
            pass
            # ---- System Module ----
            module_system.read_all_data()
            # ---- Network Module ----
            module_network.read_all_data()
            # ---- Mobile Module ----
            if(modules_enabled[0] == "1"):
                module_mobile.read_all_data()
            # ---- GPS Module ----
            if(modules_enabled[2] == "1"):
                module_gps.read_all_data()
        
        time.sleep(50)

if __name__ == "__main__":
    main()