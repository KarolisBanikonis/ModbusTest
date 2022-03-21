# Standard library imports

# Third party imports
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

# Local imports
from MainModules.Module import Module
from Libraries.ConversionMethods import convert_timestamp_to_date, convert_string_to_date
from Libraries.SSHMethods import enable_gps_service, get_concrete_ubus_data
from MainModules.Logger import log_msg

class ModuleGPS(Module):

    def __init__(self, data, ssh, modbus, info, report):
        """
        Initializes ModuleGPS object.

            Parameters:
                data (dict): data read from JSON format parameters file
                ssh (SSHClient): module required to make connection to server via SSH
                modbus (Modbus): module required to make connection to server via Modbus TCP
                info (InformationModule): module designed to monitor device's resources usage
                report (ReportModule): module designed to write test results to report file
        """
        super().__init__(data, ssh, modbus, info, report, __class__.__name__)
        enable_gps_service(self.ssh)

    def read_all_data(self, output_list, test_count):
        """
        Performs all tests of ModuleGPS module.

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
            function_name = f"get_modbus_and_device_data_type_{param_values['type']}"
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

    def get_modbus_and_device_data_type_timestamp(self, modbus_registers_data, param_values, output_list): #147
        """
        Finds converted received data via Modbus TCP and device data when register holds timestamp type information

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                modbus_data (datetime): converted data received via Modbus TCP
                device_data (datetime): parsed data received via SSH

        """
        # modbus_data, parsed_data = self.convert_data_for_2_registers(modbus_registers_data, param_values, output_list)

        modbus_data, parsed_data = self.convert_data_for_16_registers(modbus_registers_data, param_values, output_list)
        #modbus = timestamp x 1000
        #ubus = datetime in string
        modbus_data = convert_timestamp_to_date(int(modbus_data)) # MIGHT NEED TO /= 1000?
        device_data_str = parsed_data['coordinates'][param_values['parse']]
        device_data = convert_string_to_date(device_data_str)
        return modbus_data, device_data

    def get_modbus_and_device_data_type_date(self, modbus_registers_data, param_values, output_list): #163
        """
        Finds converted received data via Modbus TCP and device data when register holds date type information

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                modbus_data (datetime): converted data received via Modbus TCP
                device_data (datetime): parsed data received via SSH

        """
        modbus_data, parsed_data = self.convert_data_for_16_registers(modbus_registers_data, param_values, output_list)
        modbus_data = convert_string_to_date(modbus_data)
        timestamp = parsed_data[param_values['parse']]
        device_data = convert_timestamp_to_date(timestamp)
        return modbus_data, device_data

    def get_modbus_and_device_data_type_int(self, modbus_registers_data, param_values, output_list):
        """
        Finds converted received data via Modbus TCP and device data when register holds integer type information

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int): parsed data received via SSH

        """
        modbus_data, device_data = self.convert_data_for_2_registers(modbus_registers_data, param_values, output_list)
        return modbus_data, device_data

    def get_modbus_and_device_data_type_float(self, modbus_registers_data, param_values, output_list):
        """
        Finds converted received data via Modbus TCP and device data when register holds float type information

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                modbus_data (float): converted data received via Modbus TCP
                device_data (float): parsed data received via SSH

        """
        if(modbus_registers_data is not None):
            modbus_data = self.convert_float_number(modbus_registers_data)
        device_data = get_concrete_ubus_data(self.ssh, param_values, output_list)
        return modbus_data, device_data

    def convert_float_number(self, modbus_registers_data):
        """
        Finds converted received data via Modbus TCP and device data when register holds timestamp type information

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
            Returns:
                decoded_value (float): converted data to float value
        """
        # [1, 2, 3, 4] bytes
        decoder = BinaryPayloadDecoder.fromRegisters(modbus_registers_data, byteorder=Endian.Little, wordorder=Endian.Little,)
        decoded_value = decoder.decode_32bit_float()
        decoded_value = round(decoded_value, 6)
        return decoded_value