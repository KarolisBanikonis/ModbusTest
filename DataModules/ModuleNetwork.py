from DataModules.Module import Module
from Libraries.FileMethods import string_to_json
from Libraries.FileMethods import remove_char
from Libraries.SSHMethods import ubus_call

class ModuleNetwork(Module):

    def __init__(self, modbus, data, ssh):
        super().__init__(modbus, data, ssh)

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
        print("---- Network Module ----")
        for i in range(len(self.data)):
            current = self.data[i]
            result = self.modbus.client.read_holding_registers(current['address'], current['number'])
            if(current['address'] == 55):
                modbus_data = self.convert_reg_text(result)
                actual_data = ubus_call(self.ssh, current['service'], current['procedure'])
                parsed_data = string_to_json(actual_data)
                final_data = remove_char(parsed_data['macaddr'], ':') # returns lower case
            #WAN IP       neeed to add check if it is Null
            if(current['address'] == 139):
                modbus_data = self.convert_reg_ip(result)
                final_data = self.ssh.ssh_issue_command("curl ifconfig.me") # !!! checking only public id
            self.check_if_results_match(modbus_data, final_data, i + 1)
            print(self.format_data(current['name'], modbus_data))
        self.print_module_test_results()
                