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
from MainModules.Logger import init_logger

class Module:

    DEFAULT_ERROR_VALUE = 10
    MOBILE_ERROR_VALUE = 104857 #~0.1MB
    DATATIME_ERROR = 60
    RESULT_PASSED = "Passed"
    RESULT_FAILED = "Failed"

    def __init__(self, data, ssh, modbus, info, report, module_name):
        self.module_name = module_name
        self.logger = init_logger(module_name)
        self.data = data
        self.ssh = ssh
        self.modbus = modbus
        self.info = info
        self.report = report
        self.total_number = 0
        self.correct_number = 0
        
    def print_test_results(self, output_list, current_json, modbus_data, final_data, cpu, ram):
        output_list[1] = f"Tests were done - {self.total_number}."
        output_list[2] = f"{print_with_colour(f'Tests passed - {self.correct_number}.', 'GREEN')}{print_with_colour(f' Tests failed - {self.total_number - self.correct_number}.', 'RED')}"
        output_list[3] = f"CPU usage - {cpu}. RAM usage: {ram}."
        output_list[4] = f"Module being tested - {self.module_name}."
        output_list[5] = f"Testing - {current_json['name']}. Address - {current_json['address']}."
        output_list[6] = f"Value from Modbus - {modbus_data}. Value from router - {final_data}."

    def convert_reg_number(self, read_data):
        if(read_data == None):
            return read_data
        bin_temp1 = format(read_data[0], '08b')
        bin_temp2 = format(read_data[1], '08b')
        bin_str = (f"{bin_temp1}{bin_temp2}")
        result = self.binary_to_decimal(bin_str)
        return result

    def convert_reg_text(self, read_data):
        if(read_data == None):
            return read_data
        text = ""
        for i in range(len(read_data)):
            if(read_data[i] != 0):
                two_symbols = read_data[i].to_bytes((read_data[i].bit_length() + 7) // 8, 'big').decode()
                text += two_symbols 
            else:
                break
        return text

    def binary_to_decimal(self, n):
        return int(n, 2)

    def __format_string_for_checking(self, data):
        if(type(data) == str):
            data = data.casefold()#.translate(str.maketrans('', '', string.whitespace))
            pattern = re.compile(r'\s+')
            data = re.sub(pattern, '', data)
            return data

    def __check_if_strings_pass(self, data1, data2):
        if(data1 == data2):
            return self.RESULT_PASSED
        else:
            return self.RESULT_FAILED

    def __check_if_numbers_pass(self, data1, data2):
        used_error_value = self.DEFAULT_ERROR_VALUE
        if(self.module_name == "ModuleMobile"):
            used_error_value = self.MOBILE_ERROR_VALUE
        if(math.fabs(data1 - data2) > used_error_value):
            return self.RESULT_FAILED
        else:
            return self.RESULT_PASSED

    def __check_if_datetime_pass(self, data1, data2):
        difference = data1 - data2
        # print(f"DIFFERENCE = {difference.seconds}")
        if(math.fabs(difference.seconds) > self.DATATIME_ERROR):
            return self.RESULT_FAILED
        else:
            return self.RESULT_PASSED

    @dispatch(str, str)
    def check_if_results_match(self, modbus_data, actual_data):
        modbus_data = self.__format_string_for_checking(modbus_data)
        actual_data = self.__format_string_for_checking(actual_data)
        is_data_equal = self.__check_if_strings_pass(modbus_data, actual_data)
        return [modbus_data, actual_data, is_data_equal] # I could create class with these

    @dispatch(str, list)
    def check_if_results_match(self, modbus_data, actual_data):
        for data in actual_data:
            is_data_equal = self.__check_if_strings_pass(modbus_data, data)
            if(is_data_equal == self.RESULT_PASSED):
                actual_data = data
                break
        return [modbus_data, actual_data, is_data_equal]

    @dispatch((int, int), (int, float))
    def check_if_results_match(self, modbus_data, actual_data):
        is_data_equal = self.__check_if_numbers_pass(modbus_data, actual_data)
        return [modbus_data, actual_data, is_data_equal]

    @dispatch(int, str)
    def check_if_results_match(self, modbus_data, actual_data):
        actual_data = int(actual_data)
        is_data_equal = self.__check_if_numbers_pass(modbus_data, actual_data)
        return [modbus_data, actual_data, is_data_equal]

    @dispatch(datetime, datetime)
    def check_if_results_match(self, modbus_data, actual_data):
        is_data_equal = self.__check_if_datetime_pass(modbus_data, actual_data)
        return [modbus_data, actual_data, is_data_equal]

    @dispatch(object, object)
    def check_if_results_match(self, modbus_data, actual_data):
        if(modbus_data == None and actual_data == None):
            is_data_equal = self.RESULT_PASSED
            return [modbus_data, actual_data, is_data_equal]
        elif(modbus_data == None):
            modbus_data = "Error"
            possible_pass_values = ["N/A", "-"]
            is_data_equal = self.RESULT_FAILED
            for pass_value in possible_pass_values:
                if(pass_value == actual_data):
                    is_data_equal = self.RESULT_PASSED
                    break
            return [modbus_data, actual_data, is_data_equal]
        else:
            raise TypeError("Check results operation can not be performed with these arguments.")

    #results: modbus_data, actual_data, is_data_equal

    def change_test_count(self, is_data_equal):
        self.total_number += 1
        if(is_data_equal == self.RESULT_PASSED):
            self.correct_number += 1

    def get_modbus_and_device_data_for_number_16(self, modbus_data, current, output_list):
        if(modbus_data != None):
            modbus_data = self.convert_reg_text(modbus_data)
            modbus_data = remove_char(modbus_data, "\x00") # this step needed for 348, 103, 119(mobile), also gps
        parsed_data = get_parsed_ubus_data(self.ssh, current, output_list)
        return modbus_data, parsed_data

    def get_modbus_and_device_data_for_number_2(self, modbus_data, current, output_list):
        if(modbus_data != None):
            modbus_data = self.convert_reg_number(modbus_data)
        final_data = get_concrete_ubus_data(self.ssh, current, output_list)
        return modbus_data, final_data

    def get_modbus_and_device_data_for_number_1(self, modbus_data, current, output_list):
        if(modbus_data != None):
            modbus_data = modbus_data[0]
        parsed_data = get_parsed_ubus_data(self.ssh, current, output_list)
        return modbus_data, parsed_data