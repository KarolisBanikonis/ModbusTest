# Standard library imports
import unittest

# Third party imports
from parameterized import parameterized

# Local imports
from MainModules.PrintModule import PrintModule
from MainModules.ConfigurationModule import ConfigurationModule
from MainModules.RegistersModule import RegistersModule
from MainModules.InformationModule import InformationModule
from MainModules.ReportModule import ReportModule
from Clients.SSHClient import SSHClient
from Clients.Modbus import Modbus
from TestedModules.ModuleGPS import ModuleGPS

class test_Module(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        CONFIGURATION_FILE = "config.json"
        REGISTERS_FILE = "registers.json"
        cls.print_mod = PrintModule()
        cls.conf = ConfigurationModule(CONFIGURATION_FILE, cls.print_mod)
        cls.registers = RegistersModule(REGISTERS_FILE, cls.print_mod)
        cls.ssh_client = SSHClient(cls.conf.get_main_settings(), cls.print_mod)
        cls.modbus = Modbus(cls.conf.get_main_settings(), cls.print_mod)
        cls.info = InformationModule(cls.ssh_client, cls.registers.get_param(cls.registers.data,
            'InformationModule'), cls.print_mod, cls.conf.get_param(cls.conf.data, 'ModbusWrite'))
        cls.report = ReportModule(cls.info)
        cls.module = ModuleGPS(cls.registers, cls.ssh_client, cls.modbus, cls.info, cls.report)

    @classmethod
    def tearDownClass(cls):
        cls.ssh_client.close()
        cls.modbus.close()
        del cls.print_mod
        del cls.conf
        del cls.registers
        del cls.ssh_client
        del cls.modbus
        del cls.info
        del cls.report
        del cls.module

    def setUp(self):
        if(self.ssh_client.setup_error is not None):
            self.skipTest(self.ssh_client.setup_error)
        elif(self.modbus.setup_error is not None):
            self.skipTest(self.modbus.setup_error)

    @parameterized.expand([
        ["0x66", "0x0066"],
        ["0x661", "0x0661"],
        ["0x6", "0x0006"]
    ])
    def test_format_ip_address(self, hex_data, actual):
        calculated = self.module.format_hex_data(hex_data)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        [[7902, 23362], 54.966911],
        [[399, 48961], 23.944826],
        [[26214, 26175], 0.9]
    ])
    def test_convert_modbus_to_float(self, registers_data, actual):
        calculated = self.module.convert_modbus_to_float(registers_data)
        self.assertEqual(calculated, actual)