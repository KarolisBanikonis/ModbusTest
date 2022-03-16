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
from Libraries.FileMethods import delete_file_content
from MainModules.Scheduler import Scheduler
from MainModules.Logger import init_logger, get_log_file_path, Logger

LOG_FILE = get_log_file_path()
CONFIGURATION_FILE = "config.json"
PARAMETERS_FILE = "registers.json"

def main():
    logger = init_logger(__name__)
    delete_file_content(LOG_FILE)
    conf = ConfigurationModule(CONFIGURATION_FILE)
    data = read_file(PARAMETERS_FILE, logger)
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
        scheduler.send_email_periodically([output_list])
        scheduler.store_ftp_periodically([output_list])
        scheduler.start()
        try:
            while True:
                output_list[0] = f"Model - {info.router_model}. Start time: {get_current_data_as_string('%Y-%m-%d-%H-%M')}."
                # 0 - System, 1 - Network, 2 - Mobile, 3 - GPS
                for module in module_instances:
                    test_count = module.read_all_data(output_list, test_count)
                time.sleep(2)
        except (ConnectionFailedError, KeyboardInterrupt, AttributeError) as err:
            if(isinstance(err, ConnectionFailedError)):
                error_text = f"Connection stopped: {err}"
            elif(isinstance(err, KeyboardInterrupt)):
                error_text = "User stopped tests with KeyboardInterrupt."
            elif(isinstance(err, AttributeError)):
                error_text = f"Such attribute does not exist: {err}"
            print_error(error_text, output_list, "RED")
            logger.critical(error_text)
        finally:
            report.write_end_header()
            logger.info("Program is terminated!")
            close_all_instances([ssh_client.ssh, modbus.client])

if __name__ == "__main__":
    main()