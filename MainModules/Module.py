# Standard library imports
from datetime import datetime
import math
import re

# Third party imports
from multipledispatch import dispatch

# Local imports
from Libraries.DataMethods import remove_char, get_current_date_as_string
from Libraries.SSHMethods import get_device_json_ubus_data
from Libraries.Logger import log_msg
from MainModules.MethodIsNotCallableError import MethodIsNotCallableError

class Module:

    DEFAULT_ERROR_VALUE = 10
    MOBILE_ERROR_VALUE = 104857 #~0.1MB
    DATATIME_ERROR = 60
    GPS_ERROR_VALUE_FLOAT = 0.1
    GPS_ERROR_VALUE_INT = 1
    RESULT_PASSED = "Passed"
    RESULT_FAILED = "Failed"
    MODBUS_WRITE_ERROR = "Write error"
    READ_ACTION = "Read"
    WRITE_ACTION = "Write"
    DATA_COLLECT_FAIL = "Collect fail"

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
        self.action = "Not defined"
        self.memory = 0

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
        passed = f"Tests passed - {self.correct_number}. "
        failed = f"Tests failed - {self.total_number - self.correct_number}."
        print_mod.print_at_row(2,
            (f"{print_mod.colour_text(passed, 'GREEN')}" +
            f"{print_mod.colour_text(failed, 'RED')}"))
        print_mod.print_at_row(3, f"CPU usage - {cpu}. RAM usage: {ram}.")
        print_mod.print_at_row(4, f"Module being tested - {self.module_name}.")
        print_mod.print_at_row(5, (f"Testing - {param_values['name']}. " +
            f"Address - {param_values['address']}."))
        print_mod.print_at_row(6, (f"Value from Modbus - {modbus_data}." +
            f"Value from router - {device_data}."))

    def call_data_collect_method(self, method_name, print_mod, additional_data, param_values):
        """
        Call a method to get Modbus TCP and device data.

            Parameters:
                method_name (str): method's name which should be called
                print_mod (PrintModule): module designed for printing to terminal
                additional_data (list|bool): if it is module that reads values from Modbus TCP
                    then this parameter is list which that holds Modbus server's registers values
                    if it is module that writes values with Modbus TCP then this parameter
                    is bool value which indicates is writing performed first time
                param_values (dict): current register's parameters information
            Returns:
                modbus_data (str|int|float|datetime): if it is module that reads
                    values from Modbus TCP, then
                    it is converted data received via Modbus TCP
                    if it is module that writes values with Modbus TCP then
                    it is what data was written with Modbus TCP
                device_data (str|int|float|datetime): parsed data received via SSH
        """
        try:
            method = getattr(self, method_name)
            is_callable = callable(method)
            if(is_callable):
                modbus_data, device_data = method(additional_data, param_values, print_mod)
                return modbus_data, device_data
            else:
                raise MethodIsNotCallableError(f"Method '{str(method)}' is not callable!")
        except (AttributeError, MethodIsNotCallableError) as err:
            if(isinstance(err, AttributeError)):
                warning_text = f"Such attribute does not exist: {err}"
            elif(isinstance(err, MethodIsNotCallableError)):
                warning_text = err
            print_mod.warning(warning_text)
            log_msg(__name__, "warning", warning_text)
            return self.DATA_COLLECT_FAIL, self.DATA_COLLECT_FAIL

    def check_and_write_test_results(self, modbus_data, device_data, print_mod, param_values):
        """
        Checks if test passed and writes results to terminal and report.

            Parameters:
                modbus_data (str|int|float|datetime): if it is module that reads
                    values from Modbus TCP, then
                    it is converted data received via Modbus TCP
                    if it is module that writes values with Modbus TCP then
                    it is what data was written with Modbus TCP
                device_data (str|int|float|datetime): parsed data received via SSH
                print_mod (PrintModule): module designed for printing to terminal
                param_values (dict): current register's parameters information
        """
        results = self.check_if_results_match(modbus_data, device_data)
        self.change_test_count(results[2])
        past_memory = self.memory
        self.memory = self.info.get_used_memory(print_mod)
        cpu_usage = self.info.get_cpu_usage(print_mod)
        memory_difference = self.memory - past_memory
        total_mem_difference = self.info.mem_used_at_start - self.memory
        date = get_current_date_as_string()
        self.report.writer.writerow([date, self.total_number, self.module_name,
            param_values['name'], param_values['address'], results[0], results[1], results[2],
            self.action, cpu_usage, total_mem_difference, memory_difference])
        self.print_test_results(print_mod, param_values, results[0], results[1],
            cpu_usage, total_mem_difference)

    def convert_modbus_to_int_1(self, modbus_registers_data):
        """
        Performs default data conversions when 1 register was read

            Parameters:
                modbus_registers_data (list|None): list that holds Modbus server's registers values
                    or None if read was not successful
            Returns:
                result (int): converted data to int value, if list was passed
                None, if None was passed
        """
        if(modbus_registers_data is None):
            return None
        result = modbus_registers_data[0]
        return result

    def convert_modbus_to_int_2(self, modbus_registers_data):
        """
        Converts via Modbus TCP received registers values to integer number

            Parameters:
                modbus_registers_data (list|None): list that holds Modbus server's registers values
                    or None if read was not successful
            Returns:
                result (int): converted data to int value, if list was passed
                None, if None was passed
        """
        if(modbus_registers_data is None):
            return None
        bin_temp1 = format(modbus_registers_data[0], '016b') #08b buvo
        bin_temp2 = format(modbus_registers_data[1], '016b') #08b buvo
        bin_str = (f"{bin_temp1}{bin_temp2}")
        result = self.binary_to_decimal(bin_str)
        return result

    def convert_modbus_to_text(self, modbus_registers_data):
        """
        Converts via Modbus TCP received registers values to string format value

            Parameters:
                modbus_registers_data (list|None): list that holds Modbus server's registers values
                    or None if read was not successful
            Returns:
                result (str): converted data to string value, if list was passed
                None, if None was passed
        """
        if(modbus_registers_data is None):
            return None
        text = ""
        for i in range(len(modbus_registers_data)):
            if(modbus_registers_data[i] != 0):
                bits = modbus_registers_data[i].bit_length() + 7
                two_symbols = modbus_registers_data[i].to_bytes(bits // 8, 'big').decode()
                text += two_symbols
            else:
                break
        # This step is needed for 348, 103, 119(mobile) registers, also gps
        result = remove_char(text, "\x00")
        return result

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

    def format_string_for_checking(self, data):
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

    def check_if_list_pass(self, modbus_data, device_data):
        """
        Checks if test is successful when device_data's type is list

            Parameters:
                modbus_data (str): converted data received via Modbus TCP
                device_data (list): parsed data received via SSH
            Returns:
                result (str): result of test
                device_data (str|list): returns str if result passes, otherwise it may return list
        """
        result = self.RESULT_FAILED
        for data in device_data:
            if(modbus_data == data):
                result = self.RESULT_PASSED
                device_data = modbus_data
                break
        return result, device_data

    def check_if_strings_pass(self, modbus_data, device_data):
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

    def check_if_ints_pass(self, modbus_data, device_data):
        """
        Checks if test is successful when received data's type is integer

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

    def check_if_floats_pass(self, modbus_data, device_data):
        """
        Checks if test is successful when received data's type is float

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

    def check_if_datetime_pass(self, modbus_data, device_data):
        """
        Checks if test is successful when received data's type is datetime

            Parameters:
                modbus_data (datetime): converted data received via Modbus TCP
                device_data (datetime): parsed data received via SSH
            Returns:
                (str): result of test
        """
        difference = math.fabs((modbus_data-device_data).total_seconds())
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
        modbus_data = self.format_string_for_checking(modbus_data)
        device_data = self.format_string_for_checking(device_data)
        is_data_equal = self.check_if_strings_pass(modbus_data, device_data)
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
        is_data_equal, device_data = self.check_if_list_pass(modbus_data, device_data)
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
        is_data_equal = self.check_if_ints_pass(modbus_data, device_data)
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
        is_data_equal = self.check_if_floats_pass(modbus_data, device_data)
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
        is_data_equal = self.check_if_ints_pass(modbus_data, device_data)
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
        is_data_equal = self.check_if_datetime_pass(modbus_data, device_data)
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
        elif(modbus_data == self.MODBUS_WRITE_ERROR):
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

    def check_if_value_exists(self, data, key):
        """
        Check if specified key exists

            Parameters:
                key (str): what parameter value is requested
            Returns:
                True, if it exists
                False, if it does not exist
        """
        if(type(data) == dict):
            if(key in data.keys()):
                return True
            else:
                return False
        else:
                return False

    def get_device_data(self, param_values, print_mod):
        """
        Finds device data.

            Parameters:
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                device_data (int|str|float|None): parsed data received via SSH
        """
        json_data = get_device_json_ubus_data(self.ssh, param_values, print_mod)
        if(self.check_if_value_exists(param_values, 'parse')):
            device_data = json_data[param_values['parse']]
        elif(self.check_if_value_exists(param_values, 'index')):
            device_data = json_data[param_values['parse1']][0][param_values['parse2']]
        elif(not self.check_if_value_exists(param_values, 'parse')):
            device_data = json_data[param_values['parse1']][param_values['parse2']]
        else:
            device_data = None
        return device_data