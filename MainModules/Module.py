# Standard library imports
from datetime import datetime
import math
import re

# Third party imports
from multipledispatch import dispatch

# Local imports
# from Libraries.PrintMethods import print_with_colour
from Libraries.DataMethods import remove_char
from Libraries.SSHMethods import get_parsed_ubus_data

class Module:

    DEFAULT_ERROR_VALUE = 10
    MOBILE_ERROR_VALUE = 104857 #~0.1MB
    DATATIME_ERROR = 60
    GPS_ERROR_VALUE_FLOAT = 0.1
    GPS_ERROR_VALUE_INT = 1
    RESULT_PASSED = "Passed"
    RESULT_FAILED = "Failed"

    def __init__(self, data, ssh, modbus, info, report, module_name):
        """
        Initializes Module object.

            Parameters:
                data (dict): data read from JSON format parameters file
                ssh (SSHClient): module required to make connection to server via SSH
                modbus (Modbus): module required to make connection to server via Modbus TCP
                info (InformationModule): module designed to monitor device's resources usage
                report (ReportModule): module designed to write test results to report file
                module_name (str): name of subclass module that calls this constructor
        """
        self.module_name = module_name
        self.data = data
        self.ssh = ssh
        self.modbus = modbus
        self.info = info
        self.report = report
        self.total_number = 0
        self.correct_number = 0

    def print_test_results(self, print_mod, param_values, modbus_data, device_data, cpu, ram):
        """
        Prints current test's results to terminal.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
                param_values (dict): current register's parameters information
                modbus_data (str): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
                cpu (str): current CPU usage
                ram (str): current RAM usage
        """
        print_mod.print_at_row(1, f"Tests were done - {self.total_number}.")
        print_mod.print_at_row(2, f"{print_mod.colour_text(f'Tests passed - {self.correct_number}.', 'GREEN')}{print_mod.colour_text(f' Tests failed - {self.total_number - self.correct_number}.', 'RED')}")
        print_mod.print_at_row(3, f"CPU usage - {cpu}. RAM usage: {ram}.")
        print_mod.print_at_row(4, f"Module being tested - {self.module_name}.")
        print_mod.print_at_row(5, f"Testing - {param_values['name']}. Address - {param_values['address']}.")
        print_mod.print_at_row(6, f"Value from Modbus - {modbus_data}. Value from router - {device_data}.")

    def convert_modbus_to_int_1(self, modbus_data):
        """
        Performs default data conversions when 1 register was read

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
            Returns:
                modbus_data (int): converted data received via Modbus TCP
        """
        if(modbus_data is None):
            return modbus_data
        modbus_data = modbus_data[0]
        return modbus_data

    def convert_modbus_to_int_2(self, modbus_registers_data):
        """
        Converts via Modbus TCP received registers values to integer number

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
            Returns:
                result (int): converted data to integer value
        """
        if(modbus_registers_data is None):
            return modbus_registers_data
        bin_temp1 = format(modbus_registers_data[0], '08b')
        bin_temp2 = format(modbus_registers_data[1], '08b')
        bin_str = (f"{bin_temp1}{bin_temp2}")
        result = self.binary_to_decimal(bin_str)
        return result

    def convert_modbus_to_text(self, modbus_registers_data):
        """
        Converts via Modbus TCP received registers values to string format value

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
            Returns:
                modbus_data (str): converted data to string value
        """
        if(modbus_registers_data is None):
            return modbus_registers_data
        text = ""
        for i in range(len(modbus_registers_data)):
            if(modbus_registers_data[i] != 0):
                two_symbols = modbus_registers_data[i].to_bytes((modbus_registers_data[i].bit_length() + 7) // 8, 'big').decode()
                text += two_symbols 
            else:
                break
        modbus_data = remove_char(text, "\x00") # this step needed for 348, 103, 119(mobile), also gps
        return modbus_data

    def binary_to_decimal(self, binary_number):
        """
        Converts binary number to decimal number

            Parameters:
                binary_number (str): binary number that should be converted to decimal number
            Returns:
                result (int): converted decimal number
        """
        result = int(binary_number, 2)
        return result

    def __format_string_for_checking(self, data):
        """
        Formats the string data for test result checking

            Parameters:
                data (str): data that should be formmated
            Returns:
                data (str): formmated data
        """
        data = data.casefold()
        pattern = re.compile(r'\s+')
        data = re.sub(pattern, '', data)
        return data

    def __check_if_list_pass(self, modbus_data, device_data):
        """
        Checks if test is successful when received data's type is string

            Parameters:
                modbus_data (str): converted data received via Modbus TCP
                device_data (list): parsed data received via SSH
            Returns:
                result (str): result of test
        """
        result = self.RESULT_FAILED
        for data in device_data:
            if(modbus_data == data):
                result = self.RESULT_PASSED
                break
        return result

    def __check_if_strings_pass(self, modbus_data, device_data):
        """
        Checks if test is successful when received data's type is string

            Parameters:
                modbus_data (str): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
            Returns:
                (str): result of test
        """
        if(modbus_data == device_data):
            return self.RESULT_PASSED
        else:
            return self.RESULT_FAILED

    def __check_if_ints_pass(self, modbus_data, device_data):
        """
        Checks if test is successful when received data's type is integer or float

            Parameters:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int): parsed data received via SSH
            Returns:
                (str): result of test
        """
        used_error_value = self.DEFAULT_ERROR_VALUE
        if(self.module_name == "ModuleMobile"):
            used_error_value = self.MOBILE_ERROR_VALUE
        elif(self.module_name == "ModuleGPS"):
            used_error_value = self.GPS_ERROR_VALUE_INT
        if(math.fabs(modbus_data - device_data) > used_error_value):
            return self.RESULT_FAILED
        else:
            return self.RESULT_PASSED

    def __check_if_floats_pass(self, modbus_data, device_data):
        """
        Checks if test is successful when received data's type is integer or float

            Parameters:
                modbus_data (int|float): converted data received via Modbus TCP
                device_data (float): parsed data received via SSH
            Returns:
                (str): result of test
        """
        used_error_value = self.GPS_ERROR_VALUE_FLOAT
        if(math.fabs(modbus_data - device_data) > used_error_value):
            return self.RESULT_FAILED
        else:
            return self.RESULT_PASSED

    def __check_if_datetime_pass(self, data1, data2):
        """
        Checks if test is successful when received data's type is date

            Parameters:
                modbus_data (datetime): converted data received via Modbus TCP
                device_data (datetime): parsed data received via SSH
            Returns:
                (str): result of test
        """
        difference = math.fabs((data1-data2).total_seconds())
        if(difference > self.DATATIME_ERROR):
            return self.RESULT_FAILED
        else:
            return self.RESULT_PASSED

    @dispatch(str, str)
    def check_if_results_match(self, modbus_data, device_data):
        """
        Formats given modbus, device data and checks if test is successful

            Parameters:
                modbus_data (str): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
            Returns:
                (list): list that saves values of modbus_data, device_data and test result
        """
        modbus_data = self.__format_string_for_checking(modbus_data)
        device_data = self.__format_string_for_checking(device_data)
        is_data_equal = self.__check_if_strings_pass(modbus_data, device_data)
        return [modbus_data, device_data, is_data_equal]

    @dispatch(str, list)
    def check_if_results_match(self, modbus_data, device_data):
        """
        Formats given modbus, device data and checks if test is successful

            Parameters:
                modbus_data (str): converted data received via Modbus TCP
                device_data (list): parsed data received via SSH
            Returns:
                (list): list that saves values of modbus_data, device_data and test result
        """
        is_data_equal = self.__check_if_list_pass(modbus_data, device_data)
        return [modbus_data, device_data, is_data_equal]

    @dispatch(int, int)
    def check_if_results_match(self, modbus_data, device_data):
        """
        Formats given modbus, device data and checks if test is successful

            Parameters:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int): parsed data received via SSH
            Returns:
                (list): list that saves values of modbus_data, device_data and test result
        """
        is_data_equal = self.__check_if_ints_pass(modbus_data, device_data)
        return [modbus_data, device_data, is_data_equal]

    @dispatch((int, float), (float, float))
    def check_if_results_match(self, modbus_data, device_data):
        """
        Formats given modbus, device data and checks if test is successful

            Parameters:
                modbus_data (int|float): converted data received via Modbus TCP
                device_data (float): parsed data received via SSH
            Returns:
                (list): list that saves values of modbus_data, device_data and test result
        """
        is_data_equal = self.__check_if_floats_pass(modbus_data, device_data)
        return [modbus_data, device_data, is_data_equal]

    @dispatch(int, str)
    def check_if_results_match(self, modbus_data, device_data):
        """
        Formats given modbus, device data and checks if test is successful

            Parameters:
                modbus_data (int): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
            Returns:
                (list): list that saves values of modbus_data, device_data and test result
        """
        device_data = int(device_data)
        is_data_equal = self.__check_if_ints_pass(modbus_data, device_data)
        return [modbus_data, device_data, is_data_equal]

    @dispatch(datetime, datetime)
    def check_if_results_match(self, modbus_data, device_data):
        """
        Formats given modbus, device data and checks if test is successful

            Parameters:
                modbus_data (datetime): converted data received via Modbus TCP
                device_data (datetime): parsed data received via SSH
            Returns:
                (list): list that saves values of modbus_data, device_data and test result
        """
        is_data_equal = self.__check_if_datetime_pass(modbus_data, device_data)
        return [modbus_data, device_data, is_data_equal]

    @dispatch(object, object)
    def check_if_results_match(self, modbus_data, device_data):
        """
        Formats given modbus, device data and checks if test is successful

            Parameters:
                modbus_data (object): converted data received via Modbus TCP
                device_data (object): parsed data received via SSH
            Returns:
                (list): list that saves values of modbus_data, device_data and test result
        """
        if(modbus_data is None and device_data is None):
            is_data_equal = self.RESULT_PASSED
            return [modbus_data, device_data, is_data_equal]
        elif(modbus_data is None):
            modbus_data = "Error"
            is_data_equal = self.RESULT_FAILED
            return [modbus_data, device_data, is_data_equal]
        else:
            raise TypeError("Check results operation can not be performed with these arguments.")

    def change_test_count(self, is_data_equal):
        """
        Updates total and correct test numbers

            Parameters:
                is_data_equal (bool): is data received from modbus equals to data stored in device
        """
        self.total_number += 1
        if(is_data_equal == self.RESULT_PASSED):
            self.correct_number += 1

    def __check_if_value_exists(self, data, key):
        """
        Check if specified key exists 

            Parameters:
                key (str): what parameter value is requested
            Returns:
                True, if exists
                False, if it is not
        """
        if(type(data) == dict):
            if(key in data.keys()):
                return True
            else:
                return False

    def get_device_data(self, param_values, print_mod):
        """
        Finds device data.

            Parameters:
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                device_data (float): parsed data received via SSH
        """
        parsed_data = get_parsed_ubus_data(self.ssh, param_values, print_mod)
        if(self.__check_if_value_exists(param_values, 'parse')):
            device_data = parsed_data[param_values['parse']]
        elif(self.__check_if_value_exists(param_values, 'index')):
            device_data = parsed_data[param_values['parse1']][0][param_values['parse2']]
        elif(not self.__check_if_value_exists(param_values, 'parse')):
            device_data = parsed_data[param_values['parse1']][param_values['parse2']]
        else:
            device_data = None
        return device_data