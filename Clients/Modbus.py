# Standard library imports
import time

# Third party imports
from pyModbusTCP.client import ModbusClient

# Local imports
from MainModules.ConnectionFailedError import ConnectionFailedError
from Libraries.PrintMethods import print_error
from MainModules.Logger import init_logger

class Modbus:

    def __init__(self, conf):
        """
        Initializes Modbus object. Set settings required for establishing Modbus connection.

            Parameters:
                conf (ConfigurationModule): module that holds configuration information
        """
        self.logger = init_logger(__name__)
        self.host = conf['SERVER_HOST']
        self.port = conf['MODBUS_PORT']
        self.connect_attempts = conf['RECONNECT_ATTEMPTS']
        self.timeout = conf['TIMEOUT']
        self.client = ModbusClient(timeout=0.5)

    def setup_modbus(self):
        """
        Configuration data validation and initial setup.

            Returns:
                True, if configuration was successful
                False, if configuration was not successful
        """
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

    def try_to_reconnect(self, output_list):
        """
        Try to establish connection via Modbus TCP with server.
        If connection is not made, try to establish connection set amount of times.

            Parameters:
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                True, if connection was established
                Raises ConnectionFailedError exception, if connection was not established
        """
        if not self.client.is_open():
            if not self.client.open():
                try_connect_nr = 0
                while(try_connect_nr < self.connect_attempts):
                    try_connect_nr += 1
                    error_text = f"Reconnecting Modbus attempt nr. {try_connect_nr} out of {self.connect_attempts}!"
                    self.logger.critical(error_text)
                    print_error(error_text, output_list, "YELLOW")
                    time.sleep(self.timeout)
                    if not self.client.is_open():
                        self.client.open()
                    if self.client.is_open():
                        print_error("", output_list)
                        return True
                    # if(try_connect_nr >= self.connect_attempts):
                raise ConnectionFailedError("Connection failed - Modbus.")
            else:
                return True

    def read_registers(self, register_params, output_list):
        """
        Read server's registers values via Modbus TCP.

            Parameters:
                register_params (dict): current register's parameters information
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                register_data (list): data that holds Modbus server's registers
        """
        is_connected = self.try_to_reconnect(output_list)
        if is_connected:
            registers_data = self.client.read_holding_registers(register_params['address'], register_params['number'])
        self.client.close()
        return registers_data