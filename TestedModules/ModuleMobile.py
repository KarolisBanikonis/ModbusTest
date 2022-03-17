# Local imports
from MainModules.Module import Module
from Libraries.DataMethods import remove_char, get_value_in_parenthesis, replace_modem_id
from Libraries.SSHMethods import ssh_get_uci_hwinfo, get_router_id

class ModuleMobile(Module):

    def __init__(self, data, ssh, modbus, info, report):
        super().__init__(data, ssh, modbus, info, report, __class__.__name__)
        # self.module_name = __class__.__name__
        self.dual_sim_status = ssh_get_uci_hwinfo(self.ssh, "dual_sim")
        self.modem_id = get_router_id(self.ssh, data[0]['ModemId'])
        self.change_data_with_modem_id()

    def change_data_with_modem_id(self):
        for data in self.data[0]['SIM1']:
            data['procedure'] = replace_modem_id(data['procedure'], self.modem_id)
        if(self.dual_sim_status == "1"):
            for data in self.data[1]['SIM2']:
                data['procedure'] = replace_modem_id(data['procedure'], self.modem_id)

    def read_all_data(self, output_list, test_count): #check if sim is inserted
        self.logger.info(f"Started {self.module_name} testing!")
        self.report.open_report()
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        self.memory = test_count[2]
        self.read_data(self.data[0]['SIM1'], output_list)
        if(self.dual_sim_status == "1"):
            self.read_data(self.data[1]['SIM2'], output_list)
        self.report.close()
        self.logger.info(f"Module - {self.module_name} tests are over!")
        return [self.total_number, self.correct_number, self.memory]

    def read_data(self, data_area, output_list):
        for i in range(len(data_area)):
            current = data_area[i]
            result = self.modbus.read_registers(current, output_list)
            function_name = f"get_modbus_and_device_data_read_register_count_{current['number']}"
            modbus_data, final_data = getattr(self, function_name)(result, current, output_list)
            results = self.check_if_results_match(modbus_data, final_data)
            self.change_test_count(results)
            past_memory = self.memory
            self.memory = self.info.get_used_memory(output_list)
            cpu_usage = self.info.get_cpu_usage(output_list)
            memory_difference = self.memory - past_memory
            total_mem_difference = self.info.mem_used_at_start - self.memory
            self.report.writer.writerow([self.total_number, self.module_name, current['name'], current['address'], results[0], results[1], results[2], '', cpu_usage, total_mem_difference, memory_difference])
            self.print_test_results(output_list, current, results[0], results[1], cpu_usage, total_mem_difference)

    def get_modbus_and_device_data_read_register_count_16(self, result, current, output_list):
        modbus_data, parsed_data = self.get_modbus_and_device_data_for_number_16(result, current, output_list)
        final_data = parsed_data['mobile'][current['parse']]
        if(current['address'] == 119):
            final_data = get_value_in_parenthesis(final_data)
        return modbus_data, final_data

    def get_modbus_and_device_data_read_register_count_1(self, result, current, output_list):
        modbus_data, parsed_data = self.get_modbus_and_device_data_for_number_1(result, current, output_list)
        final_data = parsed_data[current['parse']]
        return modbus_data, final_data

    def get_modbus_and_device_data_read_register_count_2(self, result, current, output_list):
        modbus_data, final_data = self.get_modbus_and_device_data_for_number_2(result, current, output_list)
        return modbus_data, final_data