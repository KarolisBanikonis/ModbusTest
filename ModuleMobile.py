from Module import Module

class ModuleMobile(Module):

    def __init__(self, modbus, data, ssh, dual_sim):
        super().__init__(modbus, data, ssh)
        self.dual_sim = dual_sim

    def read_all_data(self): #data_area = SIM1, SIM2
        self.read_data(self.data[0]['SIM1'])
        if(self.dual_sim == "1"):
            print("---- DUAL SIM ----")
            self.read_data(self.data[1]['SIM2'])


    def read_data(self, data_area):
        print("---- Mobile Module ----")
        for i in range(len(data_area)):
            current = data_area[i]
            result = self.modbus.client.read_holding_registers(current['address'], current['number'])
            if(current['number'] == 16):
                converted_data = self.convert_reg_text(result)
            elif(current['number'] == 2):
                converted_data = self.convert_reg_number(result)
            elif(current['number'] == 1):
                converted_data = result[0]
            print(self.format_data(current['name'], converted_data))