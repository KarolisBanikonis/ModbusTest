# Standard library imports
from datetime import datetime
import math
import re

# Third party imports
from multipledispatch import dispatch

# Local imports
from Libraries.PrintMethods import print_with_colour
from Libraries.DataMethods import remove_char
from Libraries.SSHMethods import get_parsed_ubus_data, get_concrete_ubus_data

class Module:

    DEFAULT_ERROR_VALUE = 10
    MOBILE_ERROR_VALUE = 104857 #~0.1MB
    DATATIME_ERROR = 60
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

    def print_test_results(self, output_list, param_values, modbus_data, device_data, cpu, ram):
        """
        Prints current test's results to terminal.

            Parameters:
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
                param_values (dict): current register's parameters information
                modbus_data (str): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
                cpu (str): current CPU usage
                ram (str): current RAM usage
        """
        output_list[1] = f"Tests were done - {self.total_number}."
        output_list[2] = f"{print_with_colour(f'Tests passed - {self.correct_number}.', 'GREEN')}{print_with_colour(f' Tests failed - {self.total_number - self.correct_number}.', 'RED')}"
        output_list[3] = f"CPU usage - {cpu}. RAM usage: {ram}."
        output_list[4] = f"Module being tested - {self.module_name}."
        output_list[5] = f"Testing - {param_values['name']}. Address - {param_values['address']}."
        output_list[6] = f"Value from Modbus - {modbus_data}. Value from router - {device_data}."

    def convert_reg_number(self, modbus_registers_data):
        """
        Converts via Modbus TCP received registers values to integer number

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
            Returns:
                result (int): converted data to integer value
        """
        if(modbus_registers_data == None):
            return modbus_registers_data
        bin_temp1 = format(modbus_registers_data[0], '08b')
        bin_temp2 = format(modbus_registers_data[1], '08b')
        bin_str = (f"{bin_temp1}{bin_temp2}")
        result = self.binary_to_decimal(bin_str)
        return result

    def convert_reg_text(self, modbus_registers_data):
        """
        Converts via Modbus TCP received registers values to string format value

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
            Returns:
                text (str): converted data to string value
        """
        if(modbus_registers_data == None):
            return modbus_registers_data
        text = ""
        for i in range(len(modbus_registers_data)):
            if(modbus_registers_data[i] != 0):
                two_symbols = modbus_registers_data[i].to_bytes((modbus_registers_data[i].bit_length() + 7) // 8, 'big').decode()
                text += two_symbols 
            else:
                break
        return text

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

    def __check_if_strings_pass(self, modbus_data, device_data):
        """
        Checks if test is successful when received data's type is string

            Parameters:
                modbus_data (str): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
            Returns:
                unnamed (str): result of test
        """
        if(modbus_data == device_data):
            return self.RESULT_PASSED
        else:
            return self.RESULT_FAILED

    def __check_if_numbers_pass(self, modbus_data, device_data):
        """
        Checks if test is successful when received data's type is integer or float

            Parameters:
                modbus_data (int|float): converted data received via Modbus TCP
                device_data (int|float): parsed data received via SSH
            Returns:
                unnamed (str): result of test
        """
        used_error_value = self.DEFAULT_ERROR_VALUE
        if(self.module_name == "ModuleMobile"):
            used_error_value = self.MOBILE_ERROR_VALUE
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
                unnamed (str): result of test
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
                unnamed (list): list that saves values of modbus_data, device_data and test result
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
                unnamed (list): list that saves values of modbus_data, device_data and test result
        """
        for data in device_data:
            is_data_equal = self.__check_if_strings_pass(modbus_data, data)
            if(is_data_equal == self.RESULT_PASSED):
                device_data = data
                break
        return [modbus_data, device_data, is_data_equal]

    @dispatch((int, int), (int, float))
    def check_if_results_match(self, modbus_data, device_data):
        """
        Formats given modbus, device data and checks if test is successful

            Parameters:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int|float): parsed data received via SSH
            Returns:
                unnamed (list): list that saves values of modbus_data, device_data and test result
        """
        is_data_equal = self.__check_if_numbers_pass(modbus_data, device_data)
        return [modbus_data, device_data, is_data_equal]

    @dispatch(float, float)
    def check_if_results_match(self, modbus_data, device_data):
        """
        Formats given modbus, device data and checks if test is successful

            Parameters:
                modbus_data (float): converted data received via Modbus TCP
                device_data (float): parsed data received via SSH
            Returns:
                unnamed (list): list that saves values of modbus_data, device_data and test result
        """
        is_data_equal = self.__check_if_numbers_pass(modbus_data, device_data)
        return [modbus_data, device_data, is_data_equal]

    @dispatch(int, str)
    def check_if_results_match(self, modbus_data, device_data):
        """
        Formats given modbus, device data and checks if test is successful

            Parameters:
                modbus_data (int): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
            Returns:
                unnamed (list): list that saves values of modbus_data, device_data and test result
        """
        device_data = int(device_data)
        is_data_equal = self.__check_if_numbers_pass(modbus_data, device_data)
        return [modbus_data, device_data, is_data_equal]

    @dispatch(datetime, datetime)
    def check_if_results_match(self, modbus_data, device_data):
        """
        Formats given modbus, device data and checks if test is successful

            Parameters:
                modbus_data (datetime): converted data received via Modbus TCP
                device_data (datetime): parsed data received via SSH
            Returns:
                unnamed (list): list that saves values of modbus_data, device_data and test result
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
                unnamed (list): list that saves values of modbus_data, device_data and test result
        """
        if(modbus_data == None and device_data == None):
            is_data_equal = self.RESULT_PASSED
            return [modbus_data, device_data, is_data_equal]
        elif(modbus_data == None):
            modbus_data = "Error"
            possible_pass_values = ["N/A", "-"]
            is_data_equal = self.RESULT_FAILED
            for pass_value in possible_pass_values:
                if(pass_value == device_data):
                    is_data_equal = self.RESULT_PASSED
                    break
            return [modbus_data, device_data, is_data_equal]
        else:
            raise TypeError("Check results operation can not be performed with these arguments.")

    #results: modbus_data, actual_data, is_data_equal

    def change_test_count(self, is_data_equal):
        """
        Updates total and correct test numbers

            Parameters:
                is_data_equal (bool): is data received from modbus equals to data stored in device
        """
        self.total_number += 1
        if(is_data_equal == self.RESULT_PASSED):
            self.correct_number += 1

    def convert_data_for_16_registers(self, modbus_data, param_values, output_list):
        """
        Performs default data conversions when 16 registers were read

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                modbus_data (str): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
        """
        if(modbus_data != None):
            modbus_data = self.convert_reg_text(modbus_data)
            modbus_data = remove_char(modbus_data, "\x00") # this step needed for 348, 103, 119(mobile), also gps
        parsed_data = get_parsed_ubus_data(self.ssh, param_values, output_list)
        return modbus_data, parsed_data

    def convert_data_for_2_registers(self, modbus_data, param_values, output_list):
        """
        Performs default data conversions when 2 registers were read

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int): parsed data received via SSH
        """
        if(modbus_data != None):
            modbus_data = self.convert_reg_number(modbus_data)
        final_data = get_concrete_ubus_data(self.ssh, param_values, output_list)
        return modbus_data, final_data

    def convert_data_for_register(self, modbus_data, param_values, output_list):
        """
        Performs default data conversions when 1 register was read

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int): parsed data received via SSH
        """
        if(modbus_data != None):
            modbus_data = modbus_data[0]
        parsed_data = get_parsed_ubus_data(self.ssh, param_values, output_list)
        return modbus_data, parsed_data