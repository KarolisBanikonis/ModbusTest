# Local imports
from MainModules.Module import Module
from Libraries.DataMethods import remove_char
from Libraries.SSHMethods import get_concrete_ubus_data

class ModuleNetwork(Module):

    def __init__(self, data, ssh, modbus, info, report):
        super().__init__(data, ssh, modbus, info, report)
        self.module_name = __class__.__name__

    def format_ip(self, numbers):
        ip = ""
        for i in range(len(numbers)):
            ip += numbers[i]
            if(i != 3):
                ip += "."
        return ip
    
    def convert_reg_ip(self, read_data):
        numbers = []
        for i in range(len(read_data)):
            temp = format(read_data[i], '016b')
            numbers.append(str(self.binary_to_decimal(temp[0:8])))
            numbers.append(str(self.binary_to_decimal(temp[8:16])))
        ip = self.format_ip(numbers)
        return ip

    def read_all_data(self, output_list, test_count):
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        self.report.open_report()
        memory = test_count[2]
        for i in range(len(self.data)):
            current = self.data[i]
            result = self.modbus.read_registers(current, output_list)
            if(current['address'] == 55):
                modbus_data = self.convert_reg_text(result)
                final_data_with_colon = get_concrete_ubus_data(self.ssh, current, output_list)# returns lower case
                final_data = remove_char(final_data_with_colon, ':')
            #WAN IP       neeed to add check if it is Null
            if(current['address'] == 139):
                modbus_data = self.convert_reg_ip(result)
                final_data = self.ssh.ssh_issue_command("curl ifconfig.me") # !!! checking only public id
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
        
                