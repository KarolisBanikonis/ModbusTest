# Standard library imports
import unittest

# Third party imports
from parameterized import parameterized

# Local imports
from MainModules.PrintModule import PrintModule
from Clients.Modbus import Modbus

class test_Modbus(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.print_mod = PrintModule()

    @classmethod
    def tearDownClass(cls):
        del cls.print_mod

    @parameterized.expand([
        [{"SERVER_HOST": "wrong_host",
        "MODBUS_PORT": 502,
        "RECONNECT_ATTEMPTS": 7,
        "TIMEOUT": 2}, False],
        [{"SERVER_HOST": "192.168.1.1",
        "MODBUS_PORT": 70000,
        "RECONNECT_ATTEMPTS": 7,
        "TIMEOUT": 2}, False],
        [{"SERVER_HOST": "192.168.1.1",
        "MODBUS_PORT": 502,
        "RECONNECT_ATTEMPTS": 7,
        "TIMEOUT": 2}, True]
    ])
    def test_setup_modbus(self, configuration, is_data_correct):
        modbus_client = Modbus(configuration, self.print_mod)
        if(modbus_client.setup_error is None and not is_data_correct):
            self.fail("Setup was successful with wrong data.")
        elif(modbus_client.setup_error is not None and is_data_correct):
            self.fail("Setup was not successful with correct data.")