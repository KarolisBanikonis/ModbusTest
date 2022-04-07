import unittest
from parameterized import parameterized

from MainModules.ModuleLoader import ModuleLoader
from MainModules.PrintModule import PrintModule
from MainModules.ConfigurationModule import ConfigurationModule
from Clients.SSHClient import SSHClient
from MainModules.RegistersModule import RegistersModule
from Clients.Modbus import Modbus
from MainModules.InformationModule import InformationModule
from MainModules.ReportModule import ReportModule

class test_ModuleLoader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        CONFIGURATION_FILE = "config.json"
        REGISTERS_FILE = "registers.json"
        cls.print_mod = PrintModule()
        cls.conf = ConfigurationModule(CONFIGURATION_FILE, cls.print_mod)
        cls.registers = RegistersModule(REGISTERS_FILE, cls.print_mod)
        cls.ssh_client = SSHClient(cls.conf.get_main_settings(), cls.print_mod)
        cls.module_loader = ModuleLoader(cls.conf.get_data('MODULES'), cls.ssh_client, cls.print_mod)
        cls.modbus = Modbus(cls.conf.get_main_settings(), cls.print_mod)
        cls.info = InformationModule(cls.ssh_client, cls.registers.get_param(cls.registers.data,
        'InformationModule'), cls.print_mod, cls.conf.get_param(cls.conf.data, 'ModbusWrite'))
        cls.report = ReportModule(cls.info)

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
        del cls.module_loader

    def setUp(self):
        if(self.ssh_client.setup_error is not None):
            self.skipTest(self.ssh_client.setup_error)
        elif(self.modbus.setup_error is not None):
            self.skipTest(self.modbus.setup_error)
    
    @parameterized.expand([
        ["ModuleSystem", "ModuleSystemInstance"],
        ["Module1", None],
        ["ModuleWrite", "ModuleWriteInstance"]
    ])
    def test_load_module(self, module_name, actual):
        calculated = self.module_loader.load_module(module_name)
        if(actual is None):
            self.assertIsNone(calculated)
        else:
            self.assertIsNotNone(calculated)

    def test_init_modules(self):
        calculated = self.module_loader.init_modules(self.registers.data, self.modbus, self.info, self.report)
        self.assertGreater(len(calculated), 0)