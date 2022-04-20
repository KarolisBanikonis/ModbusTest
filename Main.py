#!/usr/bin/env python

# Standard library imports
import time

# Third party imports

# Local imports
from Libraries.FileMethods import close_all_instances
from Libraries.DataMethods import get_current_date_as_string
from Libraries.Logger import log_msg
from MainModules.ConnectionFailedError import ConnectionFailedError
from MainModules.ModuleLoader import ModuleLoader
from MainModules.ConfigurationModule import ConfigurationModule
from MainModules.InformationModule import InformationModule
from MainModules.RegistersModule import RegistersModule
from MainModules.ReportModule import ReportModule
from MainModules.Scheduler import Scheduler
from MainModules.PrintModule import PrintModule
from Clients.SSHClient import SSHClient
from Clients.Modbus import Modbus

CONFIGURATION_FILE = "config.json"
REGISTERS_FILE = "registers.json"

def main():
    print_mod = PrintModule()
    conf = ConfigurationModule(CONFIGURATION_FILE, print_mod)
    registers = RegistersModule(REGISTERS_FILE, print_mod)
    ssh_client = SSHClient(conf.get_main_settings(), print_mod)
    if(ssh_client.setup_error is not None):
        quit()
    modbus = Modbus(conf.get_main_settings(), print_mod)
    if(modbus.setup_error is not None):
        close_all_instances([ssh_client])
    info = InformationModule(ssh_client,
        registers.get_param(registers.data, 'InformationModule'),
        print_mod, conf.get_param(conf.data, 'ModbusWrite'))
    report = ReportModule(info)
    module_loader = ModuleLoader(registers.get_modules_data(), ssh_client, print_mod)
    module_instances = module_loader.init_modules(registers.data, modbus, info, report)
    scheduler = Scheduler(conf.get_email_settings(), conf.get_ftp_settings(),
        report, print_mod)
    current_date = get_current_date_as_string('%Y-%m-%d-%H-%M')
    terminal_header = f"Model - {info.router_model}. Start time: {current_date}."
    print_mod.print_at_row(0, terminal_header)
    test_count = [0, 0, info.mem_used_at_start] # test_number, correct_number, used_ram
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
        close_all_instances([ssh_client, modbus])

if __name__ == "__main__":
    main()