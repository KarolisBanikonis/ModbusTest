# Standard library imports
from datetime import datetime

# Local imports
from DataModules.Module import Module

class ModuleGPS(Module):

    def __init__(self, csv_file_name, modbus, data, ssh):
        super().__init__(csv_file_name, modbus, data, ssh)
        self.module_name = __class__.__name__

    def read_all_data(self):
        self.csv_report.open_report()
        self.csv_report.set_writer()
        print("---- GPS Module ----")
        self.csv_report.write_header_1(self.module_name)
        for i in range(len(self.data)):
            self.test_number = i + 1
            current = self.data[i]
            # result = self.modbus.read_registers(current)
            result = self.modbus.client.read_holding_registers(current['address'], current['number'])
            # if(result == None):
                # modbus_data = None
            if(current['number'] == 16):
                # CONVERSIONS DO NOT WORK YET FOR 147, 163
                modbus_data = self.convert_reg_text(result)
                parsed_data = self.get_parsed_ubus_data(current)
                if(current['address'] == 147):
                    final_data = parsed_data['coordinates'][current['parse']]
                elif(current['address'] == 163):
                    timestamp = [parsed_data[current['parse']]]
                    final_data = datetime.utcfromtimestamp(timestamp[0]).strftime('%Y-%m-%d %H:%M:%S')
                    print(final_data)
            elif(current['number'] == 2):
                modbus_data = self.convert_reg_number(result)
                parsed_data = self.get_parsed_ubus_data(current)
                final_data = parsed_data[current['parse']]
            results = self.check_if_results_match(modbus_data, final_data)
            self.print_current_test_result(results)
            results.insert(0, self.test_number)
            results.insert(1, current['name'])
            self.csv_report.write_data(results)
            print(self.format_data(current['name'], modbus_data))
        self.print_total_module_test_results()
        self.write_csv_module_end_results()