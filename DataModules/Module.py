import math

class Module:

    MID_ERROR = 10 #might need to add more values

    def __init__(self, modbus, data, ssh):
        self.modbus = modbus
        self.data = data
        self.ssh = ssh
        self.total_number = len(data)
        self.correct_number = 0

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
            data = data.casefold()
            return data

    def check_if_strings_equal(self, data1, data2):
        if(data1 == data2):
            return True
        else:
            return False

    def check_error_value(self, data1, data2):
        if(math.fabs(data1 - data2) > self.MID_ERROR):
            return False
        else:
            return True

    #Parsed data from registers.json can have string and int values
    #Parsed data from ubus can have string and int as well
    def check_if_results_match(self, modbus_data, actual_data, test_number):
        if(type(modbus_data) == str):
            self.convert_string_for_errors(modbus_data)
            self.convert_string_for_errors(actual_data)
            is_data_equal = self.check_if_strings_equal(modbus_data, actual_data)
        elif(type(modbus_data) == int):
            if(actual_data != int):
                actual_data = int(actual_data)
            is_data_equal = self.check_error_value(modbus_data, actual_data)
        if(is_data_equal == True):
            self.correct_number += 1
            print(f"Test Nr. {test_number} out of {self.total_number} is successful!")
        else:
            print(f"Test Nr. {test_number} out of {self.total_number} is not successful!")
            print(f"{modbus_data} not equals {actual_data}")

    def print_module_test_results(self):
        print(f"Successful: {self.correct_number}, Not successful: {self.total_number - self.correct_number}, Total: {self.total_number}.")