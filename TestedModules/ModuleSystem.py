# Local imports
from MainModules.Module import Module
from Libraries.SSHMethods import gsmctl_call, get_parsed_ubus_data

class ModuleSystem(Module):

    def __init__(self, data, ssh, modbus, info, report):
        super().__init__(data, ssh, modbus, info, report, __class__.__name__)
        # self.module_name = __class__.__name__

    def convert_ref_signal(self, read_data):
        # a = ~ read_data
        # a += 1
        # print(f"{a}")
        return read_data - 65536

    def read_all_data(self, output_list, test_count):
        self.logger.info(f"Started {self.module_name} testing!")
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        self.report.open_report()
        memory = test_count[2]
        for i in range(len(self.data)):
            current = self.data[i]
            result = self.modbus.read_registers(current, output_list)
            function_name = f"get_modbus_and_device_data_read_register_count_{current['number']}_{current['source']}"
            modbus_data, final_data = getattr(self, function_name)(result, current, output_list)
            results = self.check_if_results_match(modbus_data, final_data)
            self.change_test_count(results)
            past_memory = memory
            memory = self.info.get_used_memory(output_list)
            cpu_usage = self.info.get_cpu_usage(output_list)
            memory_difference = memory - past_memory
            total_mem_difference = self.info.mem_used_at_start - memory
            self.report.writer.writerow([self.total_number, self.module_name, current['name'], current['address'], results[0], results[1], results[2], '', cpu_usage, total_mem_difference, memory_difference])
            self.print_test_results(output_list, current, results[0], results[1], cpu_usage, total_mem_difference)
        self.report.close()
        self.logger.info(f"Module - {self.module_name} tests are over!")
        return [self.total_number, self.correct_number, memory]

    def get_modbus_and_device_data_read_register_count_1_ubus(self, result, current, output_list):
        modbus_data, parsed_data = self.get_modbus_and_device_data_for_number_1(result, current, output_list)
        if(current['address'] == 324):
            final_data = parsed_data['result'][0][current['parse']]
        elif(current['address'] == 325):
            final_data = parsed_data['result'][1][current['parse']]
        return modbus_data, final_data

    def get_modbus_and_device_data_read_register_count_2_ubus(self, result, current, output_list):
        if(current['address'] == 3):
            modbus_data = self.convert_ref_signal(result[1])
            parsed_data = get_parsed_ubus_data(self.ssh, current, output_list)
            final_data = parsed_data['mobile'][0][current['parse']]
        else:
            modbus_data, final_data = self.get_modbus_and_device_data_for_number_2(result, current, output_list)
        return modbus_data, final_data

    def get_modbus_and_device_data_read_register_count_2_gsmctl(self, result, current, output_list):
        modbus_data = self.convert_reg_number(result)
        final_data = gsmctl_call(self.ssh, current['flag'], output_list)
        return modbus_data, final_data

    def get_modbus_and_device_data_read_register_count_16_ubus(self, result, current, output_list):
        modbus_data, parsed_data = self.get_modbus_and_device_data_for_number_16(result, current, output_list)
        if(current['address'] == 39):
            final_data = parsed_data['mnfinfo'][current['parse']]
        else:
            final_data = parsed_data[current['parse']]
        return modbus_data, final_data