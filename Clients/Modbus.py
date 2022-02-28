# Third party imports
from pyModbusTCP.client import ModbusClient

class Modbus:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = ModbusClient(auto_open=True, auto_close=True)
        self.client.host(host)
        self.client.port(port)
        # uncomment this line to see debug message
        # client.debug(True)

    # Might need to make setters

    #sitas neveikia
    def read_registers(self, data):
        self.client.read_holding_registers(data['address'], data['number'])

    #sitas neveikia
    def connect_to_server(self):
        if self.client.is_open() == False:
            if self.client.open() == False:
                print(f"Not able to connect to {self.host}:{self.port}")
                return False
            else:
                return True
        else:
            return True

    def check_connection(self):
        if not self.client.is_open():
                if not self.client.open():
                    print(f"Not able to connect to {self.host}:{self.port}")
                    return False
                else:
                    return True