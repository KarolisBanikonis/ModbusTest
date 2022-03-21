#!/usr/bin/env python

# Standard library imports
import time

# Third party imports
from reprint import output

# Local imports
from Libraries.FileMethods import close_all_instances
from MainModules.ConnectionFailedError import ConnectionFailedError
from MainModules.ModuleLoader import ModuleLoader
from MainModules.ConfigurationModule import ConfigurationModule
from MainModules.InformationModule import InformationModule
from MainModules.RegistersModule import RegistersModule
from Clients.SSHClient import SSHClient
from Clients.Modbus import Modbus
from Clients.FTPClient import FTPClient
from Clients.EmailClient import EmailClient
from MainModules.ReportModule import ReportModule
from Libraries.PrintMethods import print_error
from Libraries.DataMethods import get_current_data_as_string
from MainModules.Scheduler import Scheduler
from MainModules.Logger import log_msg

CONFIGURATION_FILE = "config.json"
REGISTERS_FILE = "registers.json"

def main():
    conf = ConfigurationModule(CONFIGURATION_FILE)
    registers = RegistersModule(REGISTERS_FILE)
    # data = read_json_file(REGISTERS_FILE)
    ssh_client = SSHClient(conf.get_main_settings())
    info = InformationModule(ssh_client, registers.get_param(registers.data, 'InformationModule'))
    report = ReportModule(info)
    modbus = Modbus(conf.get_main_settings())
    modbus_is_setup_valid = modbus.setup_modbus()
    if(modbus_is_setup_valid == False):
        close_all_instances([ssh_client.ssh])
    module_loader = ModuleLoader(conf, ssh_client)
    module_instances = module_loader.init_modules(registers.data, modbus, info, report)
    test_count = [0, 0, info.mem_used_at_start] # test_number, correct_number, used_ram
    if(conf.get_param(conf.get_ftp_settings(), 'FTP_USE')):
        ftp_client = FTPClient(conf.get_ftp_settings(), report)
    email = EmailClient(conf.get_email_settings())
    scheduler = Scheduler(ftp_client, email)

    with output(output_type="list", initial_len=8, interval=0) as output_list:
        # scheduler.send_email_periodically([output_list])
        scheduler.store_ftp_periodically([output_list])
        scheduler.start()
        try:
            while True:
                output_list[0] = f"Model - {info.router_model}. Start time: {get_current_data_as_string('%Y-%m-%d-%H-%M')}."
                # 0 - System, 1 - Network, 2 - Mobile, 3 - GPS
                for module in module_instances:
                    test_count = module.read_all_data(output_list, test_count)
                time.sleep(2)
        except (ConnectionFailedError, KeyboardInterrupt, AttributeError, TypeError) as err:
            if(isinstance(err, ConnectionFailedError)):
                error_text = f"Connection stopped: {err}"
            elif(isinstance(err, KeyboardInterrupt)):
                error_text = "User stopped tests with KeyboardInterrupt."
            elif(isinstance(err, AttributeError)):
                error_text = f"Such attribute does not exist: {err}"
            elif(isinstance(err, TypeError)):
                error_text = f"Type error: {err}"
            print_error(error_text, output_list, "RED")
            log_msg(__name__, "critical", error_text)
        finally:
            log_msg(__name__, "critical", "Program is terminated!")
            close_all_instances([ssh_client.ssh, modbus.client])

if __name__ == "__main__":
    main()