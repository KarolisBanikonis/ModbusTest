#!/usr/bin/env python

# Standard library imports
from importlib import import_module
import time

# Third party imports


# Local imports
from FileMethods import file_exists
from FileMethods import read_file
from FileMethods import load_module
from SSHClient import SSHClient
from Modbus import Modbus
from ModuleSystem import ModuleSystem
from ModuleNetwork import ModuleNetwork

CONFIGURATION_FILE = "config.json"
PARAMETERS_FILE = "registers.json"

def main():
    file_exists(CONFIGURATION_FILE)
    file_exists(PARAMETERS_FILE)
    configuration = read_file(CONFIGURATION_FILE)
    ssh_client = SSHClient(configuration['Settings'][0])
    modbus = Modbus(configuration['Settings'][0]['SERVER_HOST'], configuration['Settings'][0]['SERVER_PORT'])
    modules_enabled = ssh_client.ssh_get_modules_status()
    data = read_file(PARAMETERS_FILE)
    # ---- System Module ----
    module_system = ModuleSystem(modbus, data['System'], ssh_client)
    # ---- Network Module ----
    module_network = ModuleNetwork(modbus, data['Network'], ssh_client)
    # ---- Mobile Module ----
    if(modules_enabled[0] == "1"):
        mobile = load_module('ModuleMobile')
        module_mobile = mobile.ModuleMobile(modbus, data['Mobile'], ssh_client, modules_enabled[1]) #pass if dual_sim is enabled
    # ---- GPS Module ----
    if(modules_enabled[2] == "1"):
    # check if it is turned and accordingly turn it on
        gps_enabled = ssh_client.ssh_issue_command("uci get gps.gpsd.enabled")
        if(gps_enabled == "0"):
            ssh_client.ssh_issue_command("uci set gps.gpsd.enabled='1'")
            ssh_client.ssh_issue_command("uci commit gps.gpsd")
        gps = load_module('ModuleGPS')
        module_gps = gps.ModuleGPS(modbus, data['GPS'], ssh_client)

    while True:
        modbus.check_connection()

        # if open() is ok, read register
        if modbus.client.is_open():
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