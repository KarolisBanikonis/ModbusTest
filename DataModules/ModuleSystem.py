# Local imports
from DataModules.Module import Module
from Libraries.SSHMethods import gsmctl_call, get_parsed_ubus_data
from Libraries.CSVMethods import open_report

class ModuleSystem(Module):

    def __init__(self, csv_file_name, modbus, data, ssh):
        super().__init__(csv_file_name, modbus, data, ssh)
        self.module_name = __class__.__name__

    def convert_ref_signal(self, read_data):
        # a = ~ read_data
        # a += 1
        # print(f"{a}")
        return read_data - 65536

    def read_all_data(self, output_list, test_count):
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        report, writer = open_report(self.report_path)
        for i in range(len(self.data)):
            current = self.data[i]
            if(current['name'] == "Model"):
                continue
            result = self.modbus.read_registers(current)
            # CHECK BY SOURCE FIRST
            if(current['source'] == "ubus" and current['number'] == 16):
                modbus_data = self.convert_reg_text(result)
                parsed_data = get_parsed_ubus_data(self.ssh, current)
                if(current['address'] == 39): #different parse
                    final_data = parsed_data['mnfinfo'][current['parse']]
                else:
                    final_data = parsed_data[current['parse']]
            elif(current['source'] == "ubus" and current['number'] == 2):
                if(current['address'] == 3):
                    modbus_data = self.convert_ref_signal(result[1])
                else:
                    modbus_data = self.convert_reg_number(result)
                parsed_data = get_parsed_ubus_data(self.ssh, current)
                if(current['address'] == 3):
                    final_data = parsed_data['mobile'][0][current['parse']]
                else:
                    final_data = parsed_data[current['parse']]
            elif(current['source'] == "ubus" and current['number'] == 1):
                modbus_data = result[0]
                parsed_data = get_parsed_ubus_data(self.ssh, current)
                if(current['address'] == 324):
                    final_data = parsed_data['result'][0][current['parse']]
                elif(current['address'] == 325):
                    final_data = parsed_data['result'][1][current['parse']]
            elif(current['source'] == "gsmctl"): #only signal uses gsmctl
                modbus_data = self.convert_reg_number(result)
                final_data = gsmctl_call(self.ssh, current['flag'])
            results = self.check_if_results_match(modbus_data, final_data)
            self.change_test_count(results)
            writer.writerow([self.total_number, self.module_name, current['name'], current['address'], results[0], results[1], results[2]])
            self.print_test_results(output_list, current, results[0], results[1])
        report.close()
        return [self.total_number, self.correct_number]