from DataModules.Module import Module
from Libraries.FileMethods import string_to_json
from Libraries.SSHMethods import gsmctl_call, ubus_call

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
            current = self.data[i]
            # result = self.modbus.read_registers(current)
            result = self.modbus.client.read_holding_registers(current['address'], current['number'])
            # CHECK BY SOURCE FIRST
            if(current['source'] == "ubus" and current['number'] == 16):
                modbus_data = self.convert_reg_text(result)
                actual_data = ubus_call(self.ssh, current['service'], current['procedure'])
                parsed_data = string_to_json(actual_data)
                if(current['address'] == 39): #different parse
                    final_data = parsed_data['mnfinfo'][current['parse']]
                else:
                    final_data = parsed_data[current['parse']]
            elif(current['source'] == "ubus" and current['number'] == 2):
                if(current['address'] == 3):
                    modbus_data = self.convert_ref_signal(result[1])
                else:
                    modbus_data = self.convert_reg_number(result)
                actual_data = ubus_call(self.ssh, current['service'], current['procedure'])
                parsed_data = string_to_json(actual_data)
                if(current['address'] == 3):
                    final_data = parsed_data['mobile'][0][current['parse']]
                else:
                    final_data = parsed_data[current['parse']]
                print(f"{final_data} typeof {type(final_data)}")
            elif(current['source'] == "ubus" and current['number'] == 1):
                modbus_data = result[0]
                actual_data = ubus_call(self.ssh, current['service'], current['procedure'])
                parsed_data = string_to_json(actual_data)
                if(current['address'] == 324):
                    final_data = parsed_data['result'][0][current['parse']]
                elif(current['address'] == 325):
                    final_data = parsed_data['result'][1][current['parse']]
            elif(current['source'] == "gsmctl"): #only signal uses gsmctl
                modbus_data = self.convert_reg_number(result)
                actual_data = gsmctl_call(self.ssh, current['flag'])
                final_data = int(actual_data)

            self.check_if_results_match(modbus_data, final_data, i + 1)
            print(self.format_data(current['name'], modbus_data))
        self.print_module_test_results()