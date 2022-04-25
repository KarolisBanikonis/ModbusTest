# Local imports
from MainModules.Module import Module
from Libraries.DataMethods import remove_char
from Libraries.Logger import log_msg

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
        self.action = self.READ_ACTION

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
            ip += str(numbers[i])
            if(i != 3):
                ip += "."
        return ip

    def convert_modbus_to_ip(self, modbus_registers_data):
        """
        Converts via Modbus TCP received registers values to IP address

            Parameters:
                modbus_registers_data (list): list that holds Modbus server's registers values
            Returns:
                ip (str): formatted IP address
        """
        numbers = []
        for i in range(len(modbus_registers_data)):
            temp = format(modbus_registers_data[i], '016b')
            numbers.append(self.binary_to_decimal(temp[0:8]))
            numbers.append(self.binary_to_decimal(temp[8:16]))
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
                test_count (list): list that saves values of total tests number,
                    correct tests number and last memory usage
            Returns:
                (list): list that saves values of total tests number,
                    correct tests number and last memory usage
        """
        log_msg(__name__, "info", f"Started {self.module_name} testing!")
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        self.report.open_report()
        self.memory = test_count[2]
        for i in range(len(self.data)):
            param_values = self.data[i]
            modbus_registers_data = self.modbus.read_registers(param_values, print_mod)
            # Specific function for every register address
            method_name = f"get_modbus_and_device_data_register_nr_{param_values['address']}"
            modbus_data, device_data = self.call_data_collect_method(method_name, print_mod,
                modbus_registers_data, param_values)
            if(modbus_data == self.DATA_COLLECT_FAIL):
                continue
            self.check_and_write_test_results(modbus_data, device_data, print_mod, param_values)
        self.report.close()
        log_msg(__name__, "info", f"Module - {self.module_name} tests are over!")
        return [self.total_number, self.correct_number, self.memory]

    def get_modbus_and_device_data_register_nr_55(self, modbus_registers_data, param_values, print_mod):
        """
        Finds converted received data via Modbus TCP and device data
            when starting register number is 55

            Parameters:
                modbus_registers_data (list): list that holds Modbus server's registers values
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (str): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
        """
        modbus_data = self.convert_modbus_to_text(modbus_registers_data)
        device_data_with_colon = self.get_device_data(param_values, print_mod)# Returns lower case
        device_data = remove_char(device_data_with_colon, ':')
        return modbus_data, device_data

    def get_modbus_and_device_data_register_nr_139(self, modbus_registers_data, param_values, print_mod):
        """
        Finds converted received data via Modbus TCP and device data
            when starting register number is 139

            Parameters:
                modbus_registers_data (list): list that holds Modbus server's registers values
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (str): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
        """
        interfaces = self.get_device_data(param_values, print_mod)
        device_data = self.add_interfaces_ip_to_list(interfaces)
        if(device_data is not None):
            if(len(device_data) <= 2): #loopback and lan
                modbus_data = None
                device_data = None
        if(modbus_registers_data is not None):
            modbus_data = self.convert_modbus_to_ip(modbus_registers_data)
        return modbus_data, device_data