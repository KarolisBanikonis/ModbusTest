# Standard library imports
import time

# Third party imports
from pyModbusTCP.client import ModbusClient

# Local imports
from MainModules.ConnectionFailedError import ConnectionFailedError

class Modbus:

    CONNECT_ATTEMPTS = 7
    SLEEP_TIME = 0.2

    def __init__(self, configuration):
        self.host = configuration['SERVER_HOST']
        self.port = configuration['MODBUS_PORT']
        self.client = ModbusClient(auto_open=True, auto_close=True, timeout=1)
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
        connected = self.try_new()
        registers_data = self.client.read_holding_registers(data['address'], data['number'])
        if(registers_data == "" or registers_data == None):
            # self.try_new()
            # self.read_registers(data)
            # raise ConnectionFailedError("Connection failed - In Modbus read reg.")
            time.sleep(self.SLEEP_TIME)
            connected = self.try_new()
            registers_data = self.read_registers(data)
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

    def try_new(self):
        state = self.client.is_open()
        if(state):
            return True
        else:
            try_connect_nr = 0
            while(try_connect_nr < self.CONNECT_ATTEMPTS):
                try_connect_nr += 1
                connected = self.client.open()
                if(connected):
                    return True
            raise ConnectionFailedError("Connection failed - Modbus.")