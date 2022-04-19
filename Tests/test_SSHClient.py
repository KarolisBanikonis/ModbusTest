# Standard library imports
import unittest

# Third party imports
from parameterized import parameterized

# Local imports
from MainModules.PrintModule import PrintModule
from Clients.SSHClient import SSHClient

class test_SSHClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.print_mod = PrintModule()

    @classmethod
    def tearDownClass(cls):
        del cls.print_mod

    @parameterized.expand([
        [{"SERVER_HOST": "192.168.1.1",
        "USERNAME": "wrongusername",
        "PASSWORD": "password",
        "RECONNECT_ATTEMPTS": 7,
        "TIMEOUT": 2}, False],
        [{"SERVER_HOST": "wrong_host",
        "USERNAME": "root",
        "PASSWORD": "Admin123",
        "RECONNECT_ATTEMPTS": 7,
        "TIMEOUT": 2}, False],
        [{"SERVER_HOST": "192.168.1.1",
        "USERNAME": "root",
        "PASSWORD": "Admin123",
        "RECONNECT_ATTEMPTS": 7,
        "TIMEOUT": 2}, True]
    ])
    def test_setup_ssh(self, configuration, is_data_correct):
        ssh_client = SSHClient(configuration, self.print_mod)
        if(ssh_client.setup_error is None and not is_data_correct):
            self.fail("Setup was successful with wrong data.")
        elif(ssh_client.setup_error is not None and is_data_correct):
            self.fail("Setup was not successful with correct data.")