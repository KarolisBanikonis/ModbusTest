# Standard library imports
import time

# Third party imports
from pyModbusTCP.client import ModbusClient

# Local imports
from MainModules.ConnectionFailedError import ConnectionFailedError
from Libraries.PrintMethods import print_error

class Modbus:

    def __init__(self, configuration):
        self.host = configuration['SERVER_HOST']
        self.port = configuration['MODBUS_PORT']
        self.connect_attempts = configuration['RECONNECT_ATTEMPTS']
        self.timeout = configuration['TIMEOUT']
        self.client = ModbusClient(auto_open=True, auto_close=True, timeout=0.1)
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

    def try_connect(self):
        if self.client.is_open() == False:
            if self.client.open() == False:
                return False
            else:
                return True
        # else:
        #     return True

    def read_registers(self, data, print_status):
        # self.try_reconnect(print_status)
        try_connect_nr = 0
        while(try_connect_nr < self.connect_attempts):
            try_connect_nr += 1
            time.sleep(0.7)
            registers_data = self.client.read_holding_registers(data['address'], data['number'])
            if(registers_data != None):
                if(try_connect_nr > 1):
                    print_error("", print_status)
                return registers_data
            else:
                error_text = f"Reconnecting Modbus attempt nr. {try_connect_nr} out of {self.connect_attempts}!"
                time.sleep(self.timeout) # only on Linux needed
                print_error(error_text, print_status, "YELLOW")
        return registers_data

    def try_reconnect(self, print_status=None):
        time.sleep(0.7)
        # state = self.try_connect()
        # if(state):
        #     return
        # else:
        # print("IN RECONNECT MODBUS")
        try_connect_nr = 0
        while(try_connect_nr < self.connect_attempts):
            try_connect_nr += 1
            state = self.try_connect()
            if(state):
                if(print_status != None):
                    print_error("", print_status)
                    return
            if(print_status != None):
                error_text = f"Reconnecting Modbus attempt nr. {try_connect_nr} out of {self.connect_attempts}!"
                # time.sleep(self.timeout) # only on Linux needed
                print_error(error_text, print_status, "YELLOW")
                
        raise ConnectionFailedError("Connection failed - Modbus.")

    # def try_reconnect(self, print_status=None):
    #     state = self.client.is_open()
    #     if(state):
    #         return
    #     else:
    #         connected = self.client.open() # It is always closed(except first)
    #         if(connected):
    #             return
    #         try_connect_nr = 0
    #         while(try_connect_nr < self.CONNECT_ATTEMPTS):
    #             try_connect_nr += 1
    #             if(print_status != None):
    #                 print_status[7] = print_with_colour(f"Reconnecting Modbus attempt nr. {try_connect_nr} out of {self.CONNECT_ATTEMPTS}!", "YELLOW")
    #             state = self.client.is_open()
    #             if(state):
    #                 if(print_status != None):
    #                     print_status[7] = ""
    #                 return
    #             else:
    #                 connected = self.client.open()
    #             if(connected):
    #                 if(print_status != None):
    #                     print_status[7] = ""
    #                 return
    #         raise ConnectionFailedError("Connection failed - Modbus.")