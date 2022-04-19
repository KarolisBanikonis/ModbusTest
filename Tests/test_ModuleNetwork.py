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
from TestedModules.ModuleNetwork import ModuleNetwork

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
        cls.module = ModuleNetwork(cls.registers, cls.ssh_client, cls.modbus, cls.info, cls.report)

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
        [[84, 15, 161, 183], "84.15.161.183"],
        [[10, 0, 0, 20], "10.0.0.20"],
        [[10, 1, 7, 153], "10.1.7.153"]
    ])
    def test_format_ip_address(self, numbers_list, actual):
        calculated = self.module.format_ip(numbers_list)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        [[21519, 41399], "84.15.161.183"],
        [[2560, 20], "10.0.0.20"],
        [[2561, 1945], "10.1.7.153"]
    ])
    def test_convert_modbus_to_ip(self, registers_data, actual):
        calculated = self.module.convert_modbus_to_ip(registers_data)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        [[{'interface': 'lan', 'up': True, 'ipv4-address':[{'address': '192.168.1.1',
            'mask': 24}]}], ["192.168.1.1"]],
        [[{'interface': 'mob1s1a1_4', 'up': True, 'ipv4-address':[{'address': '84.15.161.183',
            'mask': 32}]}], ["84.15.161.183"]],
        [[{'interface': 'mob1s1a1', 'up': True, 'ipv4-address':[]}], []]
    ])
    def test_add_interfaces_ip_to_list(self, interfaces_data, actual):
        calculated = self.module.add_interfaces_ip_to_list(interfaces_data)
        self.assertEqual(calculated, actual)