# Standard library imports

# Local imports
from DataModules.Module import Module
from Libraries.FileMethods import remove_char
from Libraries.ConversionMethods import convert_timestamp_to_date, convert_string_to_date
from Libraries.SSHMethods import try_enable_gps

class ModuleGPS(Module):

    def __init__(self, csv_file_name, modbus, data, ssh):
        super().__init__(csv_file_name, modbus, data, ssh)
        self.module_name = __class__.__name__

    def read_all_data(self):
        try_enable_gps(self.ssh)
        self.reset_correct_number()
        self.csv_report.open_report()
        self.csv_report.set_writer()
        print("---- GPS Module ----")
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
            print(self.format_data(current['name'], modbus_data))
        self.print_total_module_test_results()
        self.write_csv_module_end_results()