# Standard library imports
import time

# Third party imports
from pyModbusTCP.client import ModbusClient

# Local imports
from MainModules.ConnectionFailedError import ConnectionFailedError
from MainModules.Logger import log_msg

class Modbus:

    def __init__(self, conf):
        """
        Initializes Modbus object. Set settings required for establishing Modbus connection.

            Parameters:
                conf (ConfigurationModule): module that holds configuration information
        """
        self.host = conf['SERVER_HOST']
        self.port = conf['MODBUS_PORT']
        self.connect_attempts = conf['RECONNECT_ATTEMPTS']
        self.timeout = conf['TIMEOUT']
        self.client = ModbusClient(timeout=0.5)

    def setup_modbus(self, print_mod):
        """
        Configuration data validation and initial setup.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
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
            print_mod.error(error_text)
            log_msg(__name__, "critical", error_text)
            return False
        self.client.port(self.port)
        log_msg(__name__, "info", "Modbus setup is successful!")
        return True

    def try_to_reconnect(self, print_mod):
        """
        Try to establish connection via Modbus TCP with server.
        If connection is not made, try to establish connection set amount of times.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                True, if connection was established
                Raises ConnectionFailedError exception, if connection was not established
        """
        if not self.client.is_open():
            time.sleep(0.3)
            if not self.client.open():
                try_connect_nr = 0
                while(try_connect_nr < self.connect_attempts):
                    try_connect_nr += 1
                    error_text = f"Reconnecting Modbus attempt nr. {try_connect_nr} out of {self.connect_attempts}!"
                    log_msg(__name__, "critical", error_text)
                    print_mod.warning(error_text)
                    time.sleep(self.timeout)
                    if not self.client.is_open():
                        self.client.open()
                    if self.client.is_open():
                        print_mod.clear_warning()
                        return True
                raise ConnectionFailedError("Connection failed - Modbus.")
            else:
                return True

    def read_registers(self, register_params, print_mod):
        """
        Read server's registers values via Modbus TCP.

            Parameters:
                register_params (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                register_data (list): data that holds Modbus server's registers
        """
        is_connected = self.try_to_reconnect(print_mod)
        if is_connected:
            registers_data = self.client.read_holding_registers(register_params['address'], register_params['number'])
        self.client.close()
        return registers_data

    def read(self, print_mod, address, number):
        is_connected = self.try_to_reconnect(print_mod)
        if is_connected:
            registers_data = self.client.read_holding_registers(address, number)
        self.client.close()
        return registers_data

    def write_many(self, print_mod, address, value):
        writed = None
        is_connected = self.try_to_reconnect(print_mod)
        if is_connected:
            writed = self.client.write_multiple_registers(address, value)
        self.client.close()
        return writed

    def write_one(self, print_mod, address, value):
        writed = None
        is_connected = self.try_to_reconnect(print_mod)
        if is_connected:
            writed = self.client.write_single_register(address, value)
        self.client.close()
        return writed