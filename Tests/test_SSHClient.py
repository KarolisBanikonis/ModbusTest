# Standard library imports
import unittest

# Third party imports
from parameterized import parameterized

# Local imports
from MainModules.PrintModule import PrintModule
from MainModules.ConfigurationModule import ConfigurationModule
from Clients.SSHClient import SSHClient

class test_SSHClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.print_mod = PrintModule()
        cls.configuration_file = "config.json"
        cls.conf = ConfigurationModule(cls.configuration_file, cls.print_mod)

    @classmethod
    def tearDownClass(cls):
        del cls.print_mod
        del cls.configuration_file
        del cls.conf

    @parameterized.expand([
        [{"SERVER_HOST": "192.168.1.1",
        "USERNAME": "wrongusername",
        "PASSWORD": "password",
        "RECONNECT_ATTEMPTS": 7,
        "TIMEOUT": 2}],
        [{"SERVER_HOST": "wrong_host",
        "USERNAME": "root",
        "PASSWORD": "Admin123",
        "RECONNECT_ATTEMPTS": 7,
        "TIMEOUT": 2}]
    ])
    def test_setup_ssh_with_wrong_data(self, configuration):
        ssh_client = SSHClient(configuration, self.print_mod)
        if(ssh_client.setup_error is None):
            self.fail("Setup was successful with wrong data.")

    def test_setup_ssh_with_correct_data(self):
        ssh_client = SSHClient(self.conf.get_main_settings(), self.print_mod)
        if(ssh_client.setup_error is not None):
            fail_text = ("Setup was not successful with data" +
                f" from '{self.configuration_file}' file.")
            self.fail(fail_text)