# Local imports
from DataModules.Module import Module
from Libraries.SSHMethods import gsmctl_call
from colorama import Fore, Style

class ModuleSystem(Module):

    def __init__(self, csv_file_name, modbus, data, ssh):
        super().__init__(csv_file_name, modbus, data, ssh)
        self.module_name = __class__.__name__
        self.print_router_model()

    def print_router_model(self):
        parsed_data = self.get_parsed_ubus_data(self.data[0])
        self.modem_model = parsed_data['mnfinfo'][self.data[0]['parse']]
        print(self.modem_model)

    def convert_ref_signal(self, read_data):
        # a = ~ read_data
        # a += 1
        # print(f"{a}")
        return read_data - 65536

    def read_all_data(self, output_list, test_count):
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        # self.reset_correct_number()
        self.csv_report.open_report()
        self.csv_report.set_writer()
        self.csv_report.write_header_1(self.module_name)
        # with output(output_type="list", initial_len=2, interval=0) as output_list:
        for i in range(len(self.data)):
            self.test_number = i# + 1
            current = self.data[i]
            if(current['name'] == "Model"):
                continue
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
            self.change_test_count(results)
            results.insert(0, self.test_number)
            results.insert(1, current['name'])
            self.csv_report.write_data(results)
            # print(self.format_data(current['name'], modbus_data))
            output_list[0] = f"Tests were done - {self.total_number}."
            output_list[1] = f"{Fore.GREEN}Tests passed - {self.correct_number}.{Style.RESET_ALL}{Fore.RED} Tests failed - {self.total_number - self.correct_number}.{Style.RESET_ALL}"
            output_list[2] = f"Module being tested - {self.module_name}."
            output_list[3] = f"Testing - {current['name']}. Address - {current['address']}."
            output_list[4] = f"Value from Modbus - {modbus_data}. Value from router - {final_data}."


        # self.print_total_module_test_results()
        self.write_csv_module_end_results()
        return [self.total_number, self.correct_number]