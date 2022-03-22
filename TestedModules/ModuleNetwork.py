# Local imports
from MainModules.Module import Module
from Libraries.DataMethods import remove_char
from MainModules.Logger import log_msg

class ModuleNetwork(Module):

    def __init__(self, data, ssh, modbus, info, report):
        """
        Initializes ModuleNetwork object.

            Parameters:
                data (dict): data read from JSON format parameters file
                ssh (SSHClient): module required to make connection to server via SSH
                modbus (Modbus): module required to make connection to server via Modbus TCP
                info (InformationModule): module designed to monitor device's resources usage
                report (ReportModule): module designed to write test results to report file
        """
        super().__init__(data, ssh, modbus, info, report, __class__.__name__)

    def format_ip(self, numbers):
        """
        Formats number list to IP address 

            Parameters:
                numbers (list): list of numbers
            Returns:
                ip (str): formatted IP address
        """
        ip = ""
        for i in range(len(numbers)):
            ip += numbers[i]
            if(i != 3):
                ip += "."
        return ip
    
    def convert_modbus_to_ip(self, modbus_registers_data):
        """
        Converts via Modbus TCP received registers values to IP address

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
            Returns:
                ip (str): formatted IP address
        """
        numbers = []
        for i in range(len(modbus_registers_data)):
            temp = format(modbus_registers_data[i], '016b')
            numbers.append(str(self.binary_to_decimal(temp[0:8])))
            numbers.append(str(self.binary_to_decimal(temp[8:16])))
        ip = self.format_ip(numbers)
        return ip

    def add_interfaces_ip_to_list(self, ubus_data):
        """
        Parses JSON format data to get a list of IP addresses

            Parameters:
                ubus_data (list): information about device's interfaces received using ubus tool
            Returns:
                ip_list (list): list of IP addresses that device uses
        """
        ip_list = []
        for interface in ubus_data:
            if(interface['up'] == True):
                if(len(interface['ipv4-address']) != 0):
                    ip_list.append(interface['ipv4-address'][0]['address'])
        return ip_list

    def read_all_data(self, print_mod, test_count):
        """
        Performs all tests of ModuleNetwork module.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
                test_count (list): list that saves values of total tests number, correct tests number and last memory usage
            Returns:
                unnamed (list): list that saves values of total tests number, correct tests number and last memory usage
        """
        log_msg(__name__, "info", f"Started {self.module_name} testing!")
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        self.report.open_report()
        memory = test_count[2]
        for i in range(len(self.data)):
            param_values = self.data[i]
            # Specific function for every register address
            function_name = f"get_modbus_and_device_data_register_nr_{param_values['address']}"
            modbus_data, device_data = getattr(self, function_name)(param_values, print_mod)
            results = self.check_if_results_match(modbus_data, device_data)
            self.change_test_count(results[2])
            past_memory = memory
            memory = self.info.get_used_memory(print_mod)
            cpu_usage = self.info.get_cpu_usage(print_mod)
            memory_difference = memory - past_memory
            total_mem_difference = self.info.mem_used_at_start - memory
            self.report.writer.writerow([self.total_number, self.module_name, param_values['name'], param_values['address'], results[0], results[1], results[2], '', cpu_usage, total_mem_difference, memory_difference])
            self.print_test_results(print_mod, param_values, results[0], results[1], cpu_usage, total_mem_difference)
        self.report.close()
        log_msg(__name__, "info", f"Module - {self.module_name} tests are over!")
        return [self.total_number, self.correct_number, memory]
        
    def get_modbus_and_device_data_register_nr_55(self, param_values, print_mod):
        """
        Finds converted received data via Modbus TCP and device data when starting register number is 55

            Parameters:
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (str): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
        """
        modbus_registers_data = self.modbus.read_registers(param_values, print_mod)
        modbus_data = self.convert_modbus_to_text(modbus_registers_data)
        device_data_with_colon = self.get_device_data(param_values, print_mod)# returns lower case
        device_data = remove_char(device_data_with_colon, ':')
        return modbus_data, device_data

    def get_modbus_and_device_data_register_nr_139(self, param_values, print_mod):
        """
        Finds converted received data via Modbus TCP and device data when starting register number is 139

            Parameters:
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (str): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
        """
        interfaces = self.get_device_data(param_values, print_mod)
        device_data = self.add_interfaces_ip_to_list(interfaces)
        if(device_data is not None):
            if(len(device_data) <= 2): #loopback and lan?
                modbus_data = None
                device_data = None
            else:
                modbus_registers_data = self.modbus.read_registers(param_values, print_mod)
                modbus_data = self.convert_modbus_to_ip(modbus_registers_data)
                # interfaces = get_concrete_ubus_data(self.ssh, param_values, print_mod)
                # device_data = self.add_interfaces_ip_to_list(interfaces)
        return modbus_data, device_data