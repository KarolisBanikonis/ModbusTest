#!/usr/bin/env python

# Standard library imports
import time

# Third party imports
from reprint import output

# Local imports
from Libraries.FileMethods import read_file, close_all_instances
from MainModules.ConnectionFailedError import ConnectionFailedError
from MainModules.ModuleLoader import ModuleLoader
from MainModules.ConfigurationModule import ConfigurationModule
from MainModules.InformationModule import InformationModule
from Clients.SSHClient import SSHClient
from Clients.Modbus import Modbus
from Clients.FTPClient import FTPClient
from MainModules.ReportModule import ReportModule
from Libraries.PrintMethods import print_with_colour
from MainModules.FTPError import FTPError

CONFIGURATION_FILE = "config.json"
PARAMETERS_FILE = "registers.json"

def main():
    conf = ConfigurationModule(CONFIGURATION_FILE)
    data = read_file(PARAMETERS_FILE)
    ssh_client = SSHClient(conf.get_all_data())
    ssh_connected = ssh_client.first_ssh_connect()
    if(ssh_connected == False):
        quit()
    info = InformationModule(ssh_client, data['InformationModule'][0])
    report = ReportModule(info)
    modbus = Modbus(conf.get_all_data())
    modbus_is_setup_valid = modbus.setup_modbus()
    if(modbus_is_setup_valid == False):
        close_all_instances([ssh_client.ssh, modbus.client])
    module_loader = ModuleLoader(conf, ssh_client)
    module_instances = module_loader.init_modules(data, modbus, info, report)
    test_count = [0, 0, info.get_used_memory()] # test_number, correct_number, used_ram
    ftp_client = FTPClient(conf.get_ftp_data(), report)

    with output(output_type="list", initial_len=8, interval=0) as output_list:
        while True:
            output_list[0] = f"Model - {info.router_model}"
            # 0 - System, 1 - Network, 2 - Mobile, 3 - GPS
            try:
                for module in module_instances:
                    test_count = module.read_all_data(output_list, test_count)
                    # ftp_client.store_report()
                time.sleep(1)
            except FTPError as err:
                output_list[7] = print_with_colour(err, "RED")
            except ConnectionFailedError as err:
                output_list[7] = print_with_colour(f"Connection stopped: {err}", "RED")
                close_all_instances([ssh_client.ssh, modbus.client])
            except KeyboardInterrupt as err:
                output_list[7] = print_with_colour("User stopped tests with KeyboardInterrupt.", "RED")
                close_all_instances([ssh_client.ssh, modbus.client])
            # finally:
            #     close_all_instances([ssh_client.ssh, modbus.client])

if __name__ == "__main__":
    main()