from DataModules.Module import Module
from Libraries.FileMethods import string_to_json

class ModuleSystem(Module):

    def __init__(self, modbus, data, ssh):
        super().__init__(modbus, data, ssh)

    def convert_ref_signal(self, read_data):
        # a = ~ read_data
        # a += 1
        # print(f"{a}")
        return read_data - 65536

    def read_all_data(self):
        print("---- System Module ----")
        for i in range(len(self.data)):
            # modbus_data = ""
            current = self.data[i]
            # result = self.modbus.read_registers(current)
            result = self.modbus.client.read_holding_registers(current['address'], current['number'])
            if(current['number'] == 16):
                modbus_data = self.convert_reg_text(result)
            elif(current['number'] == 2):
                #Signal strength
                if(current['address'] == 3):
                    modbus_data = self.convert_ref_signal(result[1])
                elif(current['address'] == 5): #temperature check with gsmctl -c
                    modbus_data = self.convert_reg_number(result)
                else:
                    modbus_data = self.convert_reg_number(result)
                    actual_data = self.ssh.ubus_call(current['service'], current['procedure'])
                    # actual_data = self.ssh.ssh_issue_command("ubus -v call system info")
                    parsed_data = string_to_json(actual_data)
                    final_data = parsed_data[current['parse']]
                    print(final_data)
                    self.check_if_results_match(modbus_data, final_data, i + 1)
            elif(current['number'] == 1):
                modbus_data = result[0]
            print(self.format_data(current['name'], modbus_data))