from DataModules.Module import Module

class ModuleGPS(Module):

    def __init__(self, modbus, data, ssh):
        super().__init__(modbus, data, ssh)

    def read_all_data(self):
        print("---- GPS Module ----")
        for i in range(len(self.data)):
            current = self.data[i]
            # result = self.modbus.read_registers(current) nnn
            result = self.modbus.client.read_holding_registers(current['address'], current['number'])
            if(result == None):
                converted_data = None
            elif(current['number'] == 16):
                converted_data = self.convert_reg_text(result)
            elif(current['number'] == 2):
                converted_data = self.convert_reg_number(result)
            print(self.format_data(current['name'], converted_data))