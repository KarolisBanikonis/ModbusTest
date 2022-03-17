# Standard library imports
import time

# Third party imports
from pyModbusTCP.client import ModbusClient

# Local imports
from MainModules.ConnectionFailedError import ConnectionFailedError
from Libraries.PrintMethods import print_error
from MainModules.Logger import init_logger

class Modbus:

    def __init__(self, configuration):
        self.logger = init_logger(__name__)
        self.host = configuration['SERVER_HOST']
        self.port = configuration['MODBUS_PORT']
        self.connect_attempts = configuration['RECONNECT_ATTEMPTS']
        self.timeout = configuration['TIMEOUT']
        self.client = ModbusClient()
        # uncomment this line to see debug message
        # client.debug(True)

    # Might need to make setters

    def setup_modbus(self):
        self.client.host(self.host)
        error_text = ""
        if(type(self.port) != int):
            error_text = "Modbus port must be integer value!"
        elif(self.port < 1 or self.port > 65535):
            error_text = "Modbus port value must be between 1 and 65535!"
        if(error_text != ""):
            print(error_text)
            self.logger.critical(error_text)
            return False
        self.client.port(self.port)
        self.logger.info("Modbus setup is successful!")
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
        if not self.client.is_open():
            if not self.client.open():
                try_connect_nr = 0
                while(try_connect_nr < self.connect_attempts):
                    try_connect_nr += 1
                    error_text = f"Reconnecting Modbus attempt nr. {try_connect_nr} out of {self.connect_attempts}!"
                    self.logger.critical(error_text)
                    print_error(error_text, print_status, "YELLOW")
                    time.sleep(self.timeout)
                    if not self.client.is_open():
                        self.client.open()
                    if self.client.is_open():
                        print_error("", print_status)
                        break
                    if(try_connect_nr >= self.connect_attempts):
                        raise ConnectionFailedError("Connection failed - Modbus.")

        if self.client.is_open():
            registers_data = self.client.read_holding_registers(data['address'], data['number'])
        self.client.close()
        return registers_data





    # def read_registers(self, data, print_status): #with auto open, close
    #     try_connect_nr = 0
    #     while(try_connect_nr < self.connect_attempts):
    #         try_connect_nr += 1
    #         time.sleep(0.7)
    #         registers_data = self.client.read_holding_registers(data['address'], data['number'])
    #         if(registers_data != None):
    #             if(try_connect_nr > 1):
    #                 print_error("", print_status)
    #             return registers_data
    #         else:
    #             error_text = f"Reconnecting Modbus attempt nr. {try_connect_nr} out of {self.connect_attempts}!"
    #             self.logger.critical(error_text)
    #             time.sleep(self.timeout) # only on Linux needed
    #             print_error(error_text, print_status, "YELLOW")
    #     raise ConnectionFailedError("Connection failed - Modbus.")

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