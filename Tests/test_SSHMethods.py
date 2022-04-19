# Standard library imports
import unittest

# Third party imports
from parameterized import parameterized

# Local imports
from MainModules.PrintModule import PrintModule
from MainModules.ConfigurationModule import ConfigurationModule
from MainModules.RegistersModule import RegistersModule
from Clients.SSHClient import SSHClient
import Libraries.SSHMethods as test

class test_SSHMethods(unittest.TestCase):
    # Tests checked with RUTX09 and RUT955 devices, results may differ with other devices.
    @classmethod
    def setUpClass(cls):
        CONFIGURATION_FILE = "config.json"
        REGISTERS_FILE = "registers.json"
        cls.print_mod = PrintModule()
        cls.conf = ConfigurationModule(CONFIGURATION_FILE, cls.print_mod)
        cls.registers = RegistersModule(REGISTERS_FILE, cls.print_mod)
        cls.ssh_client = SSHClient(cls.conf.get_main_settings(), cls.print_mod)

    @classmethod
    def tearDownClass(cls):
        cls.ssh_client.close()
        del cls.print_mod
        del cls.conf
        del cls.registers
        del cls.ssh_client

    def setUp(self):
        if(self.ssh_client.setup_error is not None):
            self.skipTest(self.ssh_client.setup_error)

    @parameterized.expand([
        ["ethernet", 1],
        ["mobile", 1],
        ["dual_sim", 1]
    ])
    def test_get_uci_hwinfo(self, subsystem, actual):
        calculated = test.ssh_get_uci_hwinfo(self.ssh_client, subsystem, self.print_mod)
        self.assertEqual(calculated, actual)

    def test_get_modem_id(self):
        register_params = self.registers.data['InformationModule']['ModemId']
        calculated = test.get_modem_id(self.ssh_client, register_params, self.print_mod)
        self.assertIsInstance(calculated, str)
        self.assertGreater(len(calculated), 0)

    @parameterized.expand([
        [{"service":"system", "procedure":"info"}],
        [{"service":"vuci.system", "procedure":"version"}],
        [{"service":"vuci.system", "procedure":"cpu_time"}]
    ])
    def test_get_device_json_ubus_data(self, command_params):
        calculated = test.get_device_json_ubus_data(self.ssh_client, command_params, self.print_mod)
        self.assertIsInstance(calculated, dict)
        self.assertGreater(len(calculated), 0)

    def test_gsmctl_call(self):
        calculated = test.gsmctl_call(self.ssh_client, "c", self.print_mod)
        calculated = int(calculated)
        self.assertGreaterEqual(calculated, 0)

    def test_get_mobile_apn(self):
        calculated = test.get_mobile_apn(self.ssh_client, self.print_mod, "mob1s1a1")
        self.assertIsInstance(calculated, str)

    def test_get_device_model(self):
        register_params = self.registers.data['InformationModule']['Model']
        calculated = test.get_device_model(self.ssh_client, register_params, self.print_mod)
        self.assertIsInstance(calculated, str)
        self.assertLessEqual(len(calculated), 6)

    @parameterized.expand([
        ["/rom"],
        ["/tmp"],
        ["/log"]
    ])
    def test_get_df_used_memory(self, mount_loc):
        calculated = test.get_df_used_memory(self.ssh_client, mount_loc, self.print_mod)
        self.assertIsInstance(calculated, int)
        self.assertGreaterEqual(calculated, 0)