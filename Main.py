#!/usr/bin/env python

# Standard library imports
import time

# Third party imports
from reprint import output

# Local imports
from Libraries.FileMethods import read_file, close_all_instances
from DataModules.ModuleLoader import ModuleLoader
from DataModules.ConfigurationModule import ConfigurationModule

CONFIGURATION_FILE = "config.json"
PARAMETERS_FILE = "registers.json"

def main():
    conf = ConfigurationModule(CONFIGURATION_FILE)
    # configuration = read_file(CONFIGURATION_FILE)
    data = read_file(PARAMETERS_FILE)
    # ssh_client = SSHClient(configuration_module.get_all_data())
    # modbus = Modbus(conf.get_all_data())
    # instances = [conf.ssh_client.ssh, modbus.client]
    # modbus_is_setup_valid = modbus.setup_modbus()
    # if(modbus_is_setup_valid == False):
        # close_all_instances(instances)
    # ssh_connected = ssh_client.ssh_connect()
    # if(ssh_connected == False):
    #     close_all_instances(instances)
    # configuration_module.get_tmp_used_memory(ssh_client)
    # model = configuration_module.conf_get_router_model(ssh_client)
    # configuration_module.conf_get_cpu_count(ssh_client)
    # model = get_router_model(ssh_client, configuration_module.get_data('MODEL'))
    # CSV_REPORT_FILE = f"Reports/{generate_file_name(conf.router_model)}.csv"
    # write_router_name_and_header(CSV_REPORT_FILE, conf.router_model)
    module_loader = ModuleLoader(conf) #conf.ssh_client, conf.get_data('MODULES')
    module_instances = module_loader.init_modules(conf, data) # gal paduot cia config moduli?
    test_count = [0, 0] # test_number, correct_number

    with output(output_type="list", initial_len=5, interval=0) as output_list:
        while True:
            modbus_connected = conf.modbus.try_connect()
            if(modbus_connected == False):
                close_all_instances([conf.ssh_client.ssh, conf.modbus.client])
            else:
                # Remove CSV report's contents if it exists, otherwise create it
                # delete_file_content(CSV_REPORT_FILE)
                # 0 - System, 1 - Network, 2 - Mobile, 3 - GPS
                for module in module_instances:
                    test_count = module.read_all_data(output_list, test_count)
            
            time.sleep(10)

if __name__ == "__main__":
    main()