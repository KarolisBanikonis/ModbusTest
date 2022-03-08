# Local imports
from MainModules.Module import Module
from Libraries.DataMethods import remove_char
from Libraries.ConversionMethods import convert_timestamp_to_date, convert_string_to_date
from Libraries.SSHMethods import try_enable_gps, get_parsed_ubus_data, get_concrete_ubus_data

class ModuleGPS(Module):

    def __init__(self, data, ssh, modbus, info, report):
        super().__init__(data, ssh, modbus, info, report)
        self.module_name = __class__.__name__

    def read_all_data(self, output_list, test_count):
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        try_enable_gps(self.ssh)
        self.report.open_report()
        memory = test_count[2]
        for i in range(len(self.data)):
            current = self.data[i]
            result = self.modbus.read_registers(current, output_list)
            if(current['number'] == 16):
                modbus_data = self.convert_reg_text(result)
                modbus_data = remove_char(modbus_data, "\x00")
                parsed_data = get_parsed_ubus_data(self.ssh, current, output_list)
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
                    timestamp = parsed_data[current['parse']]
                    final_data = convert_timestamp_to_date(timestamp)
            elif(current['number'] == 2):
                modbus_data = self.convert_reg_number(result)
                final_data = get_concrete_ubus_data(self.ssh, current, output_list)
                # final_data = parsed_data[current['parse']]
            results = self.check_if_results_match(modbus_data, final_data)
            self.change_test_count(results)
            past_memory = memory
            memory = self.info.get_used_memory(output_list)
            cpu_usage = self.info.get_cpu_usage(output_list)
            memory_difference = memory - past_memory
            self.report.writer.writerow([self.total_number, self.module_name, current['name'], current['address'], results[0], results[1], results[2], '', cpu_usage, memory, memory_difference])
            self.print_test_results(output_list, current, results[0], results[1], cpu_usage, memory_difference)
        self.report.close()
        return [self.total_number, self.correct_number, memory]