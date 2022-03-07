# Third party imports
from pyModbusTCP.client import ModbusClient

class Modbus:

    def __init__(self, configuration):
        self.host = configuration['SERVER_HOST']
        self.port = configuration['MODBUS_PORT']
        self.client = ModbusClient(auto_open=True, auto_close=True)
        # uncomment this line to see debug message
        # client.debug(True)

    # Might need to make setters

    def setup_modbus(self):
        self.client.host(self.host)
        if(type(self.port) != int):
            print("Modbus port must be integer value!")
            return False
        if(self.port < 1 or self.port > 65535):
            print("Modbus port value must be between 1 and 65535!")
            return False
        self.client.port(self.port)
        return True

    def read_registers(self, data):
        registers_data = self.client.read_holding_registers(data['address'], data['number'])
        return registers_data

    def try_connect(self):
        if self.client.is_open() == False:
            if self.client.open() == False:
                print(f"Modbus not able to connect to {self.host}:{self.port}")
                return False
            else:
                return True
        else:
            return True