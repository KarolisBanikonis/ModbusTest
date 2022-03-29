from distutils.log import info
import unittest
from parameterized import parameterized

from MainModules.PrintModule import PrintModule
from MainModules.ConfigurationModule import ConfigurationModule
from Clients.SSHClient import SSHClient
from MainModules.RegistersModule import RegistersModule
from MainModules.Module import Module
from Clients.Modbus import Modbus
from MainModules.InformationModule import InformationModule
from MainModules.ReportModule import ReportModule

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
        'InformationModule'), cls.print_mod)
        cls.report = ReportModule(cls.info)
        cls.module = Module(cls.registers, cls.ssh_client, cls.modbus, cls.info, cls.report, "Module")

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
        [[0, 0], 0],
        [[1, 0], 1],
        [None, None]
    ])
    def test_convert_modbus_to_int_1(self, read_data, actual):
        calculated = self.module.convert_modbus_to_int_1(read_data)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        [[3, 20158], 216766],
        [[2511, 57822], 164618718],
        [None, None]
    ])
    def test_convert_modbus_to_int_2(self, read_data, actual):
        calculated = self.module.convert_modbus_to_int_2(read_data)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        [[29797, 29556], "test"],
        [[25976, 24941, 28780, 101], "example"],
        [None, None]
    ])
    def test_convert_modbus_to_text(self, read_data, actual):
        calculated = self.module.convert_modbus_to_text(read_data)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        ["1110001", 113],
        ["111011101", 477],
        ["11100010101", 1813]
    ])
    def test_convert_binary_to_decimal(self, data, actual):
        calculated = self.module.binary_to_decimal(data)
        self.assertEqual(calculated, actual)

    