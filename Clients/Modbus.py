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
        '''Set settings required for establishing Modbus connection.'''

        self.logger = init_logger(__name__)
        self.host = configuration['SERVER_HOST']
        self.port = configuration['MODBUS_PORT']
        self.connect_attempts = configuration['RECONNECT_ATTEMPTS']
        self.timeout = configuration['TIMEOUT']
        self.client = ModbusClient(timeout=0.5)

    def setup_modbus(self):
        '''Configuration data validation and initial setup.'''

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

    def try_to_reconnect(self, print_status):
        '''
        Try to establish connection via Modbus TCP with server.
        If connection is not made, try to establish connection set amount of times.
        '''

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
                        return True
                    # if(try_connect_nr >= self.connect_attempts):
                raise ConnectionFailedError("Connection failed - Modbus.")
            else:
                return True

    def read_registers(self, data, print_status):
        '''Read server's registers values via Modbus TCP.'''

        is_connected = self.try_to_reconnect(print_status)
        if is_connected:
            registers_data = self.client.read_holding_registers(data['address'], data['number'])
        self.client.close()
        return registers_data