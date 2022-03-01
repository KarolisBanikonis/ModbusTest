from DataModules.Module import Module
from Libraries.SSHMethods import ubus_call
from Libraries.FileMethods import string_to_json, remove_char, get_value_in_parenthesis

class ModuleMobile(Module):

    def __init__(self, modbus, data, ssh, dual_sim):
        super().__init__(modbus, data, ssh)
        self.dual_sim = dual_sim

    def read_all_data(self): #data_area = SIM1, SIM2
        self.total_number = len(self.data[0]['SIM1'])
        self.read_data(self.data[0]['SIM1'])
        # if(self.dual_sim == "1"):
        #     print("---- DUAL SIM ----")
        #     self.total_number = len(self.data[1]['SIM2'])
        #     self.read_data(self.data[1]['SIM2'])


    def read_data(self, data_area):
        print("---- Mobile Module ----")
        for i in range(len(data_area)):
            current = data_area[i]
            result = self.modbus.client.read_holding_registers(current['address'], current['number'])
            if(current['source'] == "ubus" and current['number'] == 16):
                modbus_data = self.convert_reg_text(result)
                if(current['address'] == 348 or current['address'] == 103 or current['address'] == 119): # maybe dont need if?
                    modbus_data = remove_char(modbus_data, "\x00")
                actual_data = ubus_call(self.ssh, current['service'], current['procedure'])
                parsed_data = string_to_json(actual_data)
                final_data = parsed_data['mobile'][current['parse']]
                if(current['address'] == 119):
                    final_data = get_value_in_parenthesis(final_data)
                # self.check_if_results_match(modbus_data, final_data, i + 1)
            elif(current['source'] == "ubus" and current['number'] == 2):
                modbus_data = self.convert_reg_number(result)
                # Not really found? = 185, 187, 189, 191, 193, 195
                actual_data = ubus_call(self.ssh, current['service'], current['procedure'])
                parsed_data = string_to_json(actual_data)
                final_data = parsed_data[current['parse']]
                # self.check_if_results_match(modbus_data, final_data, i + 1)
            elif(current['number'] == 1):
                modbus_data = result[0]
                actual_data = ubus_call(self.ssh, current['service'], current['procedure'])
                parsed_data = string_to_json(actual_data)
                final_data = parsed_data[current['parse']]
            self.check_if_results_match(modbus_data, final_data, i + 1)
            print(self.format_data(current['name'], modbus_data))
        self.print_module_test_results()