#!/usr/bin/env python

# Standard library imports
import time

# Third party imports

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
from Libraries.DataMethods import get_current_data_as_string
from MainModules.Scheduler import Scheduler
from MainModules.Logger import log_msg
from MainModules.PrintModule import PrintModule
from TestedModules.ModuleWrite import ModuleWrite #nutrint paskui

CONFIGURATION_FILE = "config.json"
REGISTERS_FILE = "registers.json"

def main():
    print_mod = PrintModule()
    conf = ConfigurationModule(CONFIGURATION_FILE, print_mod)
    registers = RegistersModule(REGISTERS_FILE, print_mod)
    ssh_client = SSHClient(conf.get_main_settings(), print_mod)
    info = InformationModule(ssh_client, registers.get_param(registers.data, 'InformationModule'), print_mod)
    report = ReportModule(info)
    modbus = Modbus(conf.get_main_settings())
    modbus_is_setup_valid = modbus.setup_modbus(print_mod)
    # apn0 = modbus.write_many(print_mod, 207, [1, 110, 117, 115, 116, 97, 116, 121, 116, 97, 115])
    # apn1 = modbus.write_many(print_mod, 207, [1]) # default - bangapro
    # apn2 = modbus.write_many(print_mod, 207, [1, 119, 97, 112]) # wap
    # apn3 = modbus.write_many(print_mod, 207, [1, 98, 97, 110, 103, 97, 112, 114, 111]) # bangapro
    # test_count = [0, 0, info.mem_used_at_start]
    # write_module = ModuleWrite(registers.get_param(registers.data, 'ModuleWrite'), ssh_client, modbus, info, report)
    # while(True):
    #     test_count = write_module.read_all_data(print_mod, test_count)
    if(modbus_is_setup_valid == False):
        close_all_instances([ssh_client.ssh])
    module_loader = ModuleLoader(conf, ssh_client, print_mod)
    module_instances = module_loader.init_modules(registers.data, modbus, info, report)
    test_count = [0, 0, info.mem_used_at_start] # test_number, correct_number, used_ram
    if(conf.get_param(conf.get_ftp_settings(), 'FTP_USE')):
        ftp_client = FTPClient(conf.get_ftp_settings(), report)
    email = EmailClient(conf.get_email_settings())
    scheduler = Scheduler(ftp_client, email)
    # scheduler.send_email_periodically([print_mod])
    scheduler.store_ftp_periodically([print_mod])
    scheduler.start()
    terminal_header = f"Model - {info.router_model}. Start time: {get_current_data_as_string('%Y-%m-%d-%H-%M')}."
    print_mod.print_at_row(0, terminal_header)
    try:
        while True:
            # 0 - System, 1 - Network, 2 - Mobile, 3 - GPS, 4 - Write
            for module in module_instances:
                test_count = module.read_all_data(print_mod, test_count)
            time.sleep(2)
    except (ConnectionFailedError, KeyboardInterrupt, TypeError) as err:
        if(isinstance(err, ConnectionFailedError)):
            error_text = f"Connection stopped: {err}"
        elif(isinstance(err, KeyboardInterrupt)):
            error_text = "User stopped tests with KeyboardInterrupt."
        elif(isinstance(err, TypeError)):
            error_text = f"Type error: {err}"
        print_mod.error(error_text)
        log_msg(__name__, "critical", error_text)
    finally:
        log_msg(__name__, "critical", "Program is terminated!")
        close_all_instances([ssh_client.ssh, modbus.client])

if __name__ == "__main__":
    main()