# Local imports
from MainModules.Module import Module
from Libraries.DataMethods import remove_char
from Libraries.SSHMethods import get_concrete_ubus_data, get_parsed_ubus_data

class ModuleNetwork(Module):

    def __init__(self, data, ssh, modbus, info, report):
        super().__init__(data, ssh, modbus, info, report, __class__.__name__)
        # self.module_name = __class__.__name__

    def format_ip(self, numbers):
        ip = ""
        for i in range(len(numbers)):
            ip += numbers[i]
            if(i != 3):
                ip += "."
        return ip
    
    def convert_reg_ip(self, read_data):
        # if(read_data == None):
        #     return
        numbers = []
        for i in range(len(read_data)):
            temp = format(read_data[i], '016b')
            numbers.append(str(self.binary_to_decimal(temp[0:8])))
            numbers.append(str(self.binary_to_decimal(temp[8:16])))
        ip = self.format_ip(numbers)
        return ip

    def add_interfaces_ip_to_list(self, ubus_data):
        ip_list = []
        for interface in ubus_data:
            if(interface['up'] == True):
                if(len(interface['ipv4-address']) != 0):
                    ip_list.append(interface['ipv4-address'][0]['address'])
        return ip_list

    def read_all_data(self, output_list, test_count):
        self.logger.info(f"Started {self.module_name} testing!")
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        self.report.open_report()
        memory = test_count[2]
        for i in range(len(self.data)):
            current = self.data[i]
            # Specific function for every register address
            function_name = f"get_modbus_and_device_data_read_register_nr_{current['address']}"
            modbus_data, final_data = getattr(self, function_name)(current, output_list)
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
        
    def get_modbus_and_device_data_read_register_nr_55(self, current, output_list):
        result = self.modbus.read_registers(current, output_list)
        modbus_data = self.convert_reg_text(result)
        final_data_with_colon = get_concrete_ubus_data(self.ssh, current, output_list)# returns lower case
        final_data = remove_char(final_data_with_colon, ':')
        return modbus_data, final_data

    def get_modbus_and_device_data_read_register_nr_139(self, current, output_list):
        ubus_data = get_concrete_ubus_data(self.ssh, current, output_list)
        final_data = self.add_interfaces_ip_to_list(ubus_data)
        if(len(final_data) <= 2):
            modbus_data = None
            final_data = None
        else:
            result = self.modbus.read_registers(current, output_list)
            modbus_data = self.convert_reg_ip(result)
            ubus_data = get_concrete_ubus_data(self.ssh, current, output_list)
            final_data = self.add_interfaces_ip_to_list(ubus_data)
        return modbus_data, final_data