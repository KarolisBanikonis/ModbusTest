# Local imports
from DataModules.Module import Module
from Libraries.FileMethods import remove_char

class ModuleNetwork(Module):

    def __init__(self, csv_file_name, modbus, data, ssh):
        super().__init__(csv_file_name, modbus, data, ssh)
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
            numbers.append(str(self.binaryToDecimal(temp[0:8])))
            numbers.append(str(self.binaryToDecimal(temp[8:16])))
        ip = self.format_ip(numbers)
        return ip

    def read_all_data(self):
        self.reset_correct_number()
        self.csv_report.open_report()
        self.csv_report.set_writer()
        print("---- Network Module ----")
        self.csv_report.write_header_1(self.module_name)
        for i in range(len(self.data)):
            self.test_number = i + 1
            current = self.data[i]
            result = self.modbus.read_registers(current)
            if(current['address'] == 55):
                modbus_data = self.convert_reg_text(result)
                parsed_data = self.get_parsed_ubus_data(current)
                final_data = remove_char(parsed_data['macaddr'], ':') # returns lower case
            #WAN IP       neeed to add check if it is Null
            if(current['address'] == 139):
                modbus_data = self.convert_reg_ip(result)
                final_data = self.ssh.ssh_issue_command("curl ifconfig.me") # !!! checking only public id
            results = self.check_if_results_match(modbus_data, final_data)
            self.print_current_test_result(results)
            results.insert(0, self.test_number)
            results.insert(1, current['name'])
            self.csv_report.write_data(results)
            print(self.format_data(current['name'], modbus_data))
        self.print_total_module_test_results()
        self.write_csv_module_end_results()
        
                