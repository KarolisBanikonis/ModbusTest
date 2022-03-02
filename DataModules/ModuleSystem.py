# Local imports
from DataModules.Module import Module
from Libraries.SSHMethods import gsmctl_call

class ModuleSystem(Module):

    def __init__(self, csv_file_name, modbus, data, ssh):
        super().__init__(csv_file_name, modbus, data, ssh)
        self.module_name = __class__.__name__

    def convert_ref_signal(self, read_data):
        # a = ~ read_data
        # a += 1
        # print(f"{a}")
        return read_data - 65536

    def read_all_data(self):
        self.reset_correct_number()
        self.csv_report.open_report()
        self.csv_report.set_writer()
        print("---- System Module ----")
        self.csv_report.write_header_1(self.module_name)
        for i in range(len(self.data)):
            self.test_number = i + 1
            current = self.data[i]
            result = self.modbus.read_registers(current)
            # CHECK BY SOURCE FIRST
            if(current['source'] == "ubus" and current['number'] == 16):
                modbus_data = self.convert_reg_text(result)
                parsed_data = self.get_parsed_ubus_data(current)
                if(current['address'] == 39): #different parse
                    final_data = parsed_data['mnfinfo'][current['parse']]
                else:
                    final_data = parsed_data[current['parse']]
            elif(current['source'] == "ubus" and current['number'] == 2):
                if(current['address'] == 3):
                    modbus_data = self.convert_ref_signal(result[1])
                else:
                    modbus_data = self.convert_reg_number(result)
                parsed_data = self.get_parsed_ubus_data(current)
                if(current['address'] == 3):
                    final_data = parsed_data['mobile'][0][current['parse']]
                else:
                    final_data = parsed_data[current['parse']]
            elif(current['source'] == "ubus" and current['number'] == 1):
                modbus_data = result[0]
                parsed_data = self.get_parsed_ubus_data(current)
                if(current['address'] == 324):
                    final_data = parsed_data['result'][0][current['parse']]
                elif(current['address'] == 325):
                    final_data = parsed_data['result'][1][current['parse']]
            elif(current['source'] == "gsmctl"): #only signal uses gsmctl
                modbus_data = self.convert_reg_number(result)
                final_data = gsmctl_call(self.ssh, current['flag'])
            results = self.check_if_results_match(modbus_data, final_data)
            self.print_current_test_result(results)
            results.insert(0, self.test_number)
            results.insert(1, current['name'])
            self.csv_report.write_data(results)
            print(self.format_data(current['name'], modbus_data))
        self.print_total_module_test_results()
        self.write_csv_module_end_results()