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
from Clients.EmailClient import EmailClient
from MainModules.ReportModule import ReportModule
from Libraries.PrintMethods import print_error
from Libraries.DataMethods import get_current_data_as_string
from MainModules.FTPError import FTPError
from MainModules.Scheduler import Scheduler

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
    test_count = [0, 0, info.mem_used_at_start] # test_number, correct_number, used_ram
    ftp_client = FTPClient(conf.get_ftp_data(), report)
    email = EmailClient(conf.get_email_data())
    scheduler = Scheduler(ftp_client, email)

    with output(output_type="list", initial_len=8, interval=0) as output_list:
        scheduler.send_email([output_list])
        scheduler.start()
        while True:
            output_list[0] = f"Model - {info.router_model}. Start time: {get_current_data_as_string('%Y-%m-%d-%H-%M')}."
            # 0 - System, 1 - Network, 2 - Mobile, 3 - GPS
            try:
                for module in module_instances:
                    test_count = module.read_all_data(output_list, test_count)
                # email.send_email(output_list)
                time.sleep(2)
            except FTPError as err:
                print_error(err, output_list, "RED")
            except ConnectionFailedError as err:
                # print_error(f"Connection stopped: {err}", output_list, "RED")
                close_all_instances([ssh_client.ssh, modbus.client])
            except KeyboardInterrupt as err:
                report.write_end_header()
                print_error("User stopped tests with KeyboardInterrupt.", output_list, "RED")
                close_all_instances([ssh_client.ssh, modbus.client])
            # finally:
            #     close_all_instances([ssh_client.ssh, modbus.client])

if __name__ == "__main__":
    main()