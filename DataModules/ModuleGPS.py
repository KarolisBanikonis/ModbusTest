# Third party imports
from colorama import Fore, Style

# Local imports
from DataModules.Module import Module
from Libraries.FileMethods import remove_char
from Libraries.ConversionMethods import convert_timestamp_to_date, convert_string_to_date
from Libraries.SSHMethods import try_enable_gps

class ModuleGPS(Module):

    def __init__(self, csv_file_name, modbus, data, ssh):
        super().__init__(csv_file_name, modbus, data, ssh)
        self.module_name = __class__.__name__

    def read_all_data(self, output_list, test_count):
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        try_enable_gps(self.ssh)
        self.csv_report.open_report()
        self.csv_report.set_writer()
        self.csv_report.write_header_1(self.module_name)
        for i in range(len(self.data)):
            self.test_number = i + 1
            current = self.data[i]
            result = self.modbus.read_registers(current)
            if(current['number'] == 16):
                modbus_data = self.convert_reg_text(result)
                modbus_data = remove_char(modbus_data, "\x00")
                parsed_data = self.get_parsed_ubus_data(current)
                if(current['address'] == 147):
                    #modbus = timestamp x 1000
                    #ubus = datetime in string
                    modbus_data = convert_timestamp_to_date(int(modbus_data)) # MIGHT NEED TO /= 1000?
                    # print(f"MODBUS = {modbus_data} typeof {type(modbus_data)}")
                    final_data_string = parsed_data['coordinates'][current['parse']]
                    final_data = convert_string_to_date(final_data_string)
                    # print(f"UBUS = {final_data} typeof {type(final_data)}")
                elif(current['address'] == 163):
                    modbus_data = convert_string_to_date(modbus_data)
                    timestamp = [parsed_data[current['parse']]]
                    final_data = convert_timestamp_to_date(timestamp[0])
            elif(current['number'] == 2):
                modbus_data = self.convert_reg_number(result)
                parsed_data = self.get_parsed_ubus_data(current)
                final_data = parsed_data[current['parse']]
            results = self.check_if_results_match(modbus_data, final_data)
            self.change_test_count(results)
            results.insert(0, self.test_number)
            results.insert(1, current['name'])
            self.csv_report.write_data(results)
            output_list[0] = f"Tests were done - {self.total_number}."
            output_list[1] = f"{Fore.GREEN}Tests passed - {self.correct_number}.{Style.RESET_ALL}{Fore.RED} Tests failed - {self.total_number - self.correct_number}.{Style.RESET_ALL}"
            output_list[2] = f"Module being tested - {self.module_name}."
            output_list[3] = f"Testing - {current['name']}. Address - {current['address']}."
            output_list[4] = f"Value from Modbus - {modbus_data}. Value from router - {final_data}."
            # print(self.format_data(current['name'], modbus_data))
        # self.print_total_module_test_results()
        self.write_csv_module_end_results()
        return [self.total_number, self.correct_number]