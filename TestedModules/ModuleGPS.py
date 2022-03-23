# Standard library imports
import struct

# Third party imports

# Local imports
from MainModules.Module import Module
from Libraries.ConversionMethods import convert_timestamp_to_date, convert_string_to_date
from Libraries.SSHMethods import enable_gps_service
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

    def read_all_data(self, print_mod, test_count):
        """
        Performs all tests of ModuleGPS module.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
                test_count (list): list that saves values of total tests number, correct tests number and last memory usage
            Returns:
                (list): list that saves values of total tests number, correct tests number and last memory usage
        """
        log_msg(__name__, "info", f"Started {self.module_name} testing!")
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        self.report.open_report()
        memory = test_count[2]
        for i in range(len(self.data)):
            param_values = self.data[i]
            modbus_registers_data = self.modbus.read_registers(param_values, print_mod)
            function_name = f"get_modbus_and_device_data_type_{param_values['type']}"
            modbus_data, device_data = getattr(self, function_name)(modbus_registers_data, param_values, print_mod)
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

    def get_modbus_and_device_data_type_timestamp(self, modbus_registers_data, param_values, print_mod): #147
        """
        Finds converted received data via Modbus TCP and device data when register holds timestamp type information

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (datetime): converted data received via Modbus TCP
                device_data (datetime): parsed data received via SSH
        """
        modbus_data = self.convert_modbus_to_text(modbus_registers_data)
        #modbus = timestamp x 1000
        #ubus = datetime in string
        modbus_data = convert_timestamp_to_date(int(modbus_data)) # MIGHT NEED TO /= 1000?
        device_data_str = self.get_device_data(param_values, print_mod)
        device_data = convert_string_to_date(device_data_str)
        return modbus_data, device_data

    def get_modbus_and_device_data_type_date(self, modbus_registers_data, param_values, print_mod): #163
        """
        Finds converted received data via Modbus TCP and device data when register holds date type information

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (datetime): converted data received via Modbus TCP
                device_data (datetime): parsed data received via SSH
        """
        modbus_data = self.convert_modbus_to_text(modbus_registers_data)
        modbus_data = convert_string_to_date(modbus_data)
        timestamp = self.get_device_data(param_values, print_mod)
        device_data = convert_timestamp_to_date(timestamp)
        return modbus_data, device_data

    def get_modbus_and_device_data_type_int(self, modbus_registers_data, param_values, print_mod):
        """
        Finds converted received data via Modbus TCP and device data when register holds integer type information

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int): parsed data received via SSH
        """
        modbus_data = self.convert_modbus_to_int_2(modbus_registers_data)
        device_data = self.get_device_data(param_values, print_mod)
        return modbus_data, device_data

    def get_modbus_and_device_data_type_float(self, modbus_registers_data, param_values, print_mod):
        """
        Finds converted received data via Modbus TCP and device data when register holds float type information

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (float): converted data received via Modbus TCP
                device_data (float): parsed data received via SSH
        """
        modbus_data = self.convert_modbus_to_float(modbus_registers_data)
        device_data = self.get_device_data(param_values, print_mod)
        return modbus_data, device_data

    def convert_modbus_to_float(self, modbus_registers_data):
        """
        Converts received data via Modbus TCP to float type data

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
            Returns:
                result (float): converted data to float value
                None, if modbus_registers_data is None
        """
        if(modbus_registers_data is None):
            return None
        hex_bytes = []
        for register_data in modbus_registers_data:
            hex_data = hex(register_data)
            hex_bytes.append(hex_data[2:4])
            hex_bytes.append(hex_data[4:6])
        hex_bytes.reverse()
        hex_result = ""
        for hex_byte in hex_bytes:
            hex_result += hex_byte
        result = struct.unpack('!f', bytes.fromhex(hex_result))[0]
        result = round(result, 6)
        return result

    # def convert_modbus_to_float(self, modbus_registers_data):
    #     if(modbus_registers_data is None):
    #         return modbus_registers_data
    #     # [1, 2, 3, 4] bytes
    #     decoder = BinaryPayloadDecoder.fromRegisters(modbus_registers_data, byteorder=Endian.Little, wordorder=Endian.Little,)
    #     decoded_value = decoder.decode_32bit_float()
    #     decoded_value = round(decoded_value, 6)
    #     return decoded_value