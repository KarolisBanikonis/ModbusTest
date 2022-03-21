# Local imports
from MainModules.Module import Module
from Libraries.SSHMethods import gsmctl_call, get_parsed_ubus_data
from Libraries.DataMethods import get_first_digit
from MainModules.Logger import log_msg

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

    def convert_reg_signal(self, read_data):
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

    def read_all_data(self, output_list, test_count):
        """
        Performs all tests of ModuleSystem module.

            Parameters:
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
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
            modbus_registers_data = self.modbus.read_registers(param_values, output_list)
            function_name = f"get_modbus_and_device_data_register_count_{param_values['number']}_{param_values['source']}"
            modbus_data, device_data = getattr(self, function_name)(modbus_registers_data, param_values, output_list)
            results = self.check_if_results_match(modbus_data, device_data)
            self.change_test_count(results[2])
            past_memory = memory
            memory = self.info.get_used_memory(output_list)
            cpu_usage = self.info.get_cpu_usage(output_list)
            memory_difference = memory - past_memory
            total_mem_difference = self.info.mem_used_at_start - memory
            self.report.writer.writerow([self.total_number, self.module_name, param_values['name'], param_values['address'], results[0], results[1], results[2], '', cpu_usage, total_mem_difference, memory_difference])
            self.print_test_results(output_list, param_values, results[0], results[1], cpu_usage, total_mem_difference)
        self.report.close()
        log_msg(__name__, "info", f"Module - {self.module_name} tests are over!")
        return [self.total_number, self.correct_number, memory]

    def get_modbus_and_device_data_register_count_1_ubus(self, modbus_registers_data, param_values, output_list):
        """
        Finds converted received data via Modbus TCP and device data when read register count is 1 and ubus is used to get device data

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int): parsed data received via SSH
        """
        modbus_data, parsed_data = self.convert_data_for_register(modbus_registers_data, param_values, output_list)
        device_data = get_first_digit(parsed_data[param_values['parse']])
        return modbus_data, device_data

    def get_modbus_and_device_data_register_count_2_ubus(self, modbus_registers_data, param_values, output_list):
        """
        Finds converted received data via Modbus TCP and device data when read register count is 2 and ubus is used to get device data

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int): parsed data received via SSH
        """
        if(param_values['address'] == 3):
            modbus_data = self.convert_reg_signal(modbus_registers_data)
            parsed_data = get_parsed_ubus_data(self.ssh, param_values, output_list)
            device_data = parsed_data['mobile'][0][param_values['parse']]
        else:
            modbus_data, device_data = self.convert_data_for_2_registers(modbus_registers_data, param_values, output_list)
        return modbus_data, device_data

    def get_modbus_and_device_data_register_count_2_gsmctl(self, modbus_registers_data, param_values, output_list):
        """
        Finds converted received data via Modbus TCP and device data when read register count is 2 and gsmctl is used to get device data

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int): parsed data received via SSH
        """
        modbus_data = self.convert_reg_number(modbus_registers_data)
        device_data = gsmctl_call(self.ssh, param_values['flag'], output_list)
        return modbus_data, device_data

    def get_modbus_and_device_data_register_count_16_ubus(self, modbus_registers_data, param_values, output_list):
        """
        Finds converted received data via Modbus TCP and device data when read register count is 16 and ubus is used to get device data

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                modbus_data (str): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
        """
        modbus_data, parsed_data = self.convert_data_for_16_registers(modbus_registers_data, param_values, output_list)
        if(param_values['address'] == 39):
            device_data = parsed_data['mnfinfo'][param_values['parse']]
        else:
            device_data = parsed_data[param_values['parse']]
        return modbus_data, device_data