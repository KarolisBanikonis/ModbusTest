# Standard library imports
from datetime import datetime
import math
import re
import os

# Third party imports
from colorama import Fore, Style

# Local imports
from Libraries.SSHMethods import ubus_call
from Libraries.FileMethods import string_to_json
from DataModules.ModuleCSV import ModuleCSV

class Module:

    MID_ERROR = 10      #might need to add more values
    MOBILE_ERROR = 10000
    DATATIME_ERROR = 60
    RESULT_PASSED = "Passed"
    RESULT_FAILED = "Failed"

    def __init__(self, csv_file_name, modbus, data, ssh):
        self.modbus = modbus
        self.data = data
        self.ssh = ssh
        self.total_number = 0
        self.correct_number = 0
        self.csv_report = ModuleCSV(csv_file_name, [modbus.client, ssh.ssh])
        self.module_name = ""
        
    def print_test_results(self, output_list, current_json, modbus_data, final_data):
        output_list[0] = f"Tests were done - {self.total_number}."
        output_list[1] = f"{Fore.GREEN}Tests passed - {self.correct_number}.{Style.RESET_ALL}{Fore.RED} Tests failed - {self.total_number - self.correct_number}.{Style.RESET_ALL}"
        output_list[2] = f"Module being tested - {self.module_name}."
        output_list[3] = f"Testing - {current_json['name']}. Address - {current_json['address']}."
        output_list[4] = f"Value from Modbus - {modbus_data}. Value from router - {final_data}."

    def convert_reg_number(self, read_data):
        bin_temp1 = format(read_data[0], '08b')
        bin_temp2 = format(read_data[1], '08b')
        bin_str = (f"{bin_temp1}{bin_temp2}")
        result = self.binaryToDecimal(bin_str)
        return result

    def convert_reg_text(self, read_data):
        text = ""
        for i in range(len(read_data)):
            if(read_data[i] != 0):
                two_symbols = read_data[i].to_bytes((read_data[i].bit_length() + 7) // 8, 'big').decode()
                text += two_symbols 
            else:
                break
        return text

    def binaryToDecimal(self, n):
        return int(n, 2)

    def format_data(self, information, value):
        return f"{information}: {value}"

    def convert_string_for_errors(self, data):
        if(type(data) == str):
            data = data.casefold()#.translate(str.maketrans('', '', string.whitespace))
            pattern = re.compile(r'\s+')
            data = re.sub(pattern, '', data)
            return data

    def check_if_strings_equal(self, data1, data2):
        if(data1 == data2):
            return self.RESULT_PASSED
        else:
            return self.RESULT_FAILED

    def check_error_value(self, data1, data2):
        if(math.fabs(data1 - data2) > self.MID_ERROR):
            return self.RESULT_FAILED
        else:
            return self.RESULT_PASSED

    def check_datetime_error_value(self, data1, data2):
        difference = data1 - data2
        # print(f"DIFFERENCE = {difference.seconds}")
        if(math.fabs(difference.seconds) > self.DATATIME_ERROR):
            return self.RESULT_FAILED
        else:
            return self.RESULT_PASSED

    #Parsed data from registers.json can have string and int values
    #Parsed data from ubus can have string and int as well
    def check_if_results_match(self, modbus_data, actual_data):
        if(type(modbus_data) == str):
            modbus_data = self.convert_string_for_errors(modbus_data)
            actual_data = self.convert_string_for_errors(actual_data)
            is_data_equal = self.check_if_strings_equal(modbus_data, actual_data)
        elif(type(modbus_data) == int):
            if(actual_data != int):
                actual_data = int(actual_data)
            is_data_equal = self.check_error_value(modbus_data, actual_data)
        elif(type(modbus_data) == datetime):
            is_data_equal = self.check_datetime_error_value(modbus_data, actual_data)
        return [modbus_data, actual_data, is_data_equal] # I could create class with these
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    #results: modbus_data, actual_data, is_data_equal
    def change_test_count(self, results):
        self.total_number += 1
        if(results[2] == True):
            self.correct_number += 1
        # print(f"Tests were done - {self.total_number}", end='\r', flush=True)
        # print(f"Tests passed - {self.correct_number}", end='\r', flush=True)
        # with ManagedScreen() as screen:
        #     screen._print_at(f"Tests were done - {self.total_number}\n", 0, 0, 0)
        #     screen._print_at(f"Tests passed - {self.correct_number}", 0, 0, 0)
        #     screen.refresh()
        #     sleep(0.05)
            # print(f"Test Nr. {self.test_number} out of {self.total_number} is successful!", end='\r', flush=True)
        # self.stdscr.addstr(0, 0, f"Tests were done - {self.total_number}")
        # self.stdscr.addstr(1, 0, f"Tests passed - {self.correct_number}")
            # print(f"Test Nr. {self.test_number} out of {self.total_number} is not successful!", end='\r', flush=True)
            # print(f"{results[0]} not equals {results[1]}")

    def print_total_module_test_results(self):
        print(f"Successful: {self.correct_number}, Not successful: {self.total_number - self.correct_number}, Total: {self.total_number}.")