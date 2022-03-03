# Local imports
from DataModules.Module import Module
from Libraries.FileMethods import remove_char, get_value_in_parenthesis
from Libraries.SSHMethods import ssh_get_uci_hwinfo

class ModuleMobile(Module):

    def __init__(self, csv_file_name, modbus, data, ssh):
        super().__init__(csv_file_name, modbus, data, ssh)
        self.module_name = __class__.__name__
        self.sim = 1
        self.dual_sim_status = ssh_get_uci_hwinfo(self.ssh, "dual_sim")

    def read_all_data(self):
        self.total_number = len(self.data[0]['SIM1'])
        self.read_data(self.data[0]['SIM1'])
        if(self.dual_sim_status == "1"):
            self.sim = 2
            self.total_number = len(self.data[1]['SIM2'])
            self.read_data(self.data[1]['SIM2'])

    def read_data(self, data_area):
        self.reset_correct_number()
        self.csv_report.open_report()
        self.csv_report.set_writer()
        print(f"---- Mobile Module SIM{self.sim}----")
        self.csv_report.write_header_1(f"{self.module_name} SIM{self.sim}")
        for i in range(len(data_area)):
            self.test_number = i + 1
            current = data_area[i]
            result = self.modbus.read_registers(current)
            if(current['number'] == 16):
                modbus_data = self.convert_reg_text(result)
                if(current['address'] == 348 or current['address'] == 103 or current['address'] == 119): # maybe dont need if?
                    modbus_data = remove_char(modbus_data, "\x00")
                parsed_data = self.get_parsed_ubus_data(current)
                final_data = parsed_data['mobile'][current['parse']]
                if(current['address'] == 119):
                    final_data = get_value_in_parenthesis(final_data)
            elif(current['number'] == 2):
                modbus_data = self.convert_reg_number(result)
                # Not really found? = 185, 187, 189, 191, 193, 195
                parsed_data = self.get_parsed_ubus_data(current)
                final_data = parsed_data[current['parse']]
            elif(current['number'] == 1):
                modbus_data = result[0]
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