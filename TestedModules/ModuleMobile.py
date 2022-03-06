# Local imports
from MainModules.Module import Module
from Libraries.FileMethods import remove_char, get_value_in_parenthesis
from Libraries.SSHMethods import ssh_get_uci_hwinfo, get_parsed_ubus_data
from Libraries.CSVMethods import open_report

class ModuleMobile(Module):

    def __init__(self, data, ssh, modbus, info):
        super().__init__(data, ssh, modbus, info)
        self.module_name = __class__.__name__
        self.sim = 1
        self.dual_sim_status = ssh_get_uci_hwinfo(self.ssh, "dual_sim")

    def read_all_data(self, output_list, test_count):
        report, writer = open_report(self.report_path)
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        self.memory = test_count[2]
        self.read_data(self.data[0]['SIM1'], output_list, writer)
        if(self.dual_sim_status == "1"):
            self.sim = 2
            self.read_data(self.data[1]['SIM2'], output_list, writer)
        report.close()
        return [self.total_number, self.correct_number, self.memory]

    def read_data(self, data_area, output_list, writer):
        for i in range(len(data_area)):
            current = data_area[i]
            result = self.modbus.read_registers(current)
            if(current['number'] == 16):
                modbus_data = self.convert_reg_text(result)
                if(current['address'] == 348 or current['address'] == 103 or current['address'] == 119): # maybe dont need if?
                    modbus_data = remove_char(modbus_data, "\x00")
                parsed_data = get_parsed_ubus_data(self.ssh, current)
                final_data = parsed_data['mobile'][current['parse']]
                if(current['address'] == 119):
                    final_data = get_value_in_parenthesis(final_data)
            elif(current['number'] == 2):
                modbus_data = self.convert_reg_number(result)
                # Not really found? = 185, 187, 189, 191, 193, 195
                parsed_data = get_parsed_ubus_data(self.ssh, current)
                final_data = parsed_data[current['parse']]
            elif(current['number'] == 1):
                modbus_data = result[0]
                parsed_data = get_parsed_ubus_data(self.ssh, current)
                final_data = parsed_data[current['parse']]
            results = self.check_if_results_match(modbus_data, final_data)
            self.change_test_count(results)
            past_memory = self.memory
            self.memory = self.info.get_used_memory()
            cpu_usage = self.info.get_cpu_usage()
            memory_difference = self.memory - past_memory
            writer.writerow([self.total_number, self.module_name, current['name'], current['address'], results[0], results[1], results[2], '', cpu_usage, self.memory, memory_difference])
            self.print_test_results(output_list, current, results[0], results[1])