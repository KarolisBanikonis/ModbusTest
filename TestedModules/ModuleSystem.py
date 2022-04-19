# Local imports
from MainModules.Module import Module
from Libraries.SSHMethods import gsmctl_call
from Libraries.Logger import log_msg

class ModuleSystem(Module):

    def __init__(self, data, ssh, modbus, info, report):
        """
        Initializes ModuleSystem object.

            Parameters:
                data (dict): data read from JSON format parameters file
                ssh (SSHClient): module required to make connection to server via SSH
                modbus (Modbus): module required to make connection to server via Modbus TCP
                info (InformationModule): module designed to monitor device's resources usage
                report (ReportModule): module designed to write test results to report file
        """
        super().__init__(data, ssh, modbus, info, report, __class__.__name__)
        self.action = self.READ_ACTION

    def convert_modbus_to_signal(self, read_data):
        """
        Converts via Modbus TCP received registers values to mobile signal strength

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
            Returns:
                signal_strength (int): mobile signal strength
        """
        if(read_data is None):
            return read_data
        signal_strength = read_data[1] - 65536
        return signal_strength

    def read_all_data(self, print_mod, test_count):
        """
        Performs all tests of ModuleSystem module.

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
            method_name = f"get_modbus_and_device_data_register_count_{param_values['number']}_{param_values['source']}"
            modbus_data, device_data = self.call_data_collect_method(method_name, print_mod,
                modbus_registers_data, param_values)
            if(modbus_data == self.DATA_COLLECT_FAIL):
                continue
            self.check_and_write_test_results(modbus_data, device_data, print_mod, param_values)
        self.report.close()
        log_msg(__name__, "info", f"Module - {self.module_name} tests are over!")
        return [self.total_number, self.correct_number, self.memory]

    def get_modbus_and_device_data_register_count_1_ubus(self, modbus_registers_data, param_values, print_mod):
        """
        Finds converted received data via Modbus TCP and device data
            when read register count is 1 and ubus is used to get device data

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int): parsed data received via SSH
        """
        modbus_data = self.convert_modbus_to_int_1(modbus_registers_data)
        device_data = self.get_device_data(param_values, print_mod)
        return f"{modbus_data}", f"{device_data}"

    def get_modbus_and_device_data_register_count_2_ubus(self, modbus_registers_data, param_values, print_mod):
        """
        Finds converted received data via Modbus TCP and device data
            when read register count is 2 and ubus is used to get device data

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int): parsed data received via SSH
        """
        if(param_values['address'] == 3):
            modbus_data = self.convert_modbus_to_signal(modbus_registers_data)
        else:
            modbus_data = self.convert_modbus_to_int_2(modbus_registers_data)
        device_data = self.get_device_data(param_values, print_mod)
        return modbus_data, device_data

    def get_modbus_and_device_data_register_count_2_gsmctl(self, modbus_registers_data, param_values, print_mod):
        """
        Finds converted received data via Modbus TCP and device data
            when read register count is 2 and gsmctl is used to get device data

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int): parsed data received via SSH
        """
        modbus_data = self.convert_modbus_to_int_2(modbus_registers_data)
        device_data = gsmctl_call(self.ssh, param_values['flag'], print_mod)
        return modbus_data, device_data

    def get_modbus_and_device_data_register_count_16_ubus(self, modbus_registers_data, param_values, print_mod):
        """
        Finds converted received data via Modbus TCP and device data
            when read register count is 16 and ubus is used to get device data

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (str): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
        """
        modbus_data = self.convert_modbus_to_text(modbus_registers_data)
        device_data = self.get_device_data(param_values, print_mod)
        return modbus_data, device_data