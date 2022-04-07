# Standard library imports
from datetime import datetime
import unittest

# Local imports
from MainModules.PrintModule import PrintModule
from MainModules.ConfigurationModule import ConfigurationModule
from Clients.SSHClient import SSHClient
from MainModules.RegistersModule import RegistersModule
from MainModules.Module import Module
from Clients.Modbus import Modbus
from MainModules.InformationModule import InformationModule
from MainModules.ReportModule import ReportModule

# Third party imports
from parameterized import parameterized

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

    @parameterized.expand([
        ["DATA1", "data1"],
        ["d a t a 1", "data1"],
        ["D A T A 1", "data1"]
    ])
    def test_format_string_for_checking(self, data, actual):
        calculated = self.module.format_string_for_checking(data)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        ["84.15.161.183", ["192.168.1.1", "127.0.0.1", "84.15.161.183"], ("Passed", "84.15.161.183")],
        ["10.0.1.54", ["192.168.1.1", "127.0.0.1", "84.15.161.183"],
        ("Failed", ["192.168.1.1", "127.0.0.1", "84.15.161.183"])],
        ["10.1.1.30", ["10.1.1.30"], ("Passed", "10.1.1.30")]
    ])
    def test_check_if_list_pass(self, str_data, list_data, actual):
        calculated = self.module.check_if_list_pass(str_data, list_data)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        ["0", "0", "Passed"],
        ["rutx09", "rutx09", "Passed"],
        ["0", "1", "Failed"]
    ])
    def test_check_if_strings_pass(self, str_data1, str_data2, actual):
        calculated = self.module.check_if_strings_pass(str_data1, str_data2)
        self.assertEqual(calculated, actual)

    # Default error value is 10
    @parameterized.expand([
        [44821, 44823, "Passed"],
        [667, 678, "Failed"],
        [101, 111, "Passed"]
    ])
    def test_check_if_ints_pass(self, int_data1, int_data2, actual):
        calculated = self.module.check_if_ints_pass(int_data1, int_data2)
        self.assertEqual(calculated, actual)

    # Default error value is 0.1
    @parameterized.expand([
        [44821.1, 44823.5, "Failed"],
        [1551.263, 1551.3184, "Passed"],
        [1.1, 1.3, "Failed"]
    ])
    def test_check_if_floats_pass(self, f_data1, f_data2, actual):
        calculated = self.module.check_if_floats_pass(f_data1, f_data2)
        self.assertEqual(calculated, actual)

    # Default error value is 60 seconds
    @parameterized.expand([
        [datetime(2001,10,5,13,20,1), datetime(2001,10,5,13,21,2), "Failed"],
        [datetime(2001,10,5,13,20,1), datetime(2001,10,5,13,21,1), "Passed"],
        [datetime(2022,6,1,18,4,19), datetime(2022,6,1,18,56,19), "Failed"]
    ])
    def test_check_if_datetime_pass(self, date_data1, date_data2, actual):
        calculated = self.module.check_if_datetime_pass(date_data1, date_data2)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        ["0", "0", ["0", "0", "Passed"]],
        ["RUTX 09", "rutx09", ["rutx09", "rutx09", "Passed"]],
        ["0", "1", ["0", "1", "Failed"]]
    ])
    def test_check_if_results_match_str(self, data1: str, data2: str, actual):
        calculated = self.module.check_if_results_match(data1, data2)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        ["84.15.161.183", ["192.168.1.1", "127.0.0.1", "84.15.161.183"],
        ["84.15.161.183", "84.15.161.183", "Passed"]],
        ["10.0.1.54", ["192.168.1.1", "127.0.0.1", "84.15.161.183"],
        ["10.0.1.54", ["192.168.1.1", "127.0.0.1", "84.15.161.183"], "Failed"]],
        ["10.1.1.30", ["10.1.1.30"],
        ["10.1.1.30", "10.1.1.30", "Passed"]]
    ])
    def test_check_if_results_match_list(self, data1: str, data2: list, actual):
        calculated = self.module.check_if_results_match(data1, data2)
        self.assertEqual(calculated, actual)

    # Default error value is 10
    @parameterized.expand([
        [44821, 44823, [44821, 44823, "Passed"]],
        [667, 678, [667, 678, "Failed"]],
        [101, 111, [101, 111, "Passed"]]
    ])
    def test_check_if_results_match_int(self, data1: int, data2: int, actual):
        calculated = self.module.check_if_results_match(data1, data2)
        self.assertEqual(calculated, actual)

    # Default error value is 0.1
    @parameterized.expand([
        [44821.1, 44823.5, [44821.1, 44823.5, "Failed"]],
        [1551.263, 1551.3184, [1551.263, 1551.3184, "Passed"]],
        [1.1, 1.3, [1.1, 1.3, "Failed"]]
    ])
    def test_check_if_results_match_float(self, data1: float, data2: float, actual):
        calculated = self.module.check_if_results_match(data1, data2)
        self.assertEqual(calculated, actual)

    # Default error value is 0.1
    @parameterized.expand([
        [44821, 44823.5, [44821, 44823.5, "Failed"]],
        [1551, 1551.0184, [1551, 1551.0184, "Passed"]],
        [1, 1.3, [1, 1.3, "Failed"]]
    ])
    def test_check_if_results_match_int_and_float(self, data1: int, data2: float, actual):
        calculated = self.module.check_if_results_match(data1, data2)
        self.assertEqual(calculated, actual)

    # Default error value is 10
    @parameterized.expand([
        [44821, "44823", [44821, 44823, "Passed"]],
        [667, "678", [667, 678, "Failed"]],
        [101, "111", [101, 111, "Passed"]]
    ])
    def test_check_if_results_match_int_and_str(self, data1: int, data2: str, actual):
        calculated = self.module.check_if_results_match(data1, data2)
        self.assertEqual(calculated, actual)

    # Default error value is 60 seconds
    @parameterized.expand([
        [datetime(2001,10,5,13,20,1), datetime(2001,10,5,13,21,2), 
        [datetime(2001,10,5,13,20,1), datetime(2001,10,5,13,21,2), "Failed"]],
        [datetime(2001,10,5,13,20,1), datetime(2001,10,5,13,21,1), 
        [datetime(2001,10,5,13,20,1), datetime(2001,10,5,13,21,1), "Passed"]],
        [datetime(2022,6,1,18,4,19), datetime(2022,6,1,18,56,19), 
        [datetime(2022,6,1,18,4,19), datetime(2022,6,1,18,56,19), "Failed"]]
    ])
    def test_check_if_results_match_datetime(self, data1: datetime, data2: datetime, actual):
        calculated = self.module.check_if_results_match(data1, data2)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        [None, None, [None, None, "Passed"]],
        [None, "some_data", ["Error", "some_data", "Failed"]],
        ["Write error", None, ["Write error", None, "Failed"]]
    ])
    def test_check_if_results_match_default(self, data1, data2, actual):
        calculated = self.module.check_if_results_match(data1, data2)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        [(10, 10), 10],
        [10, (10, 10)],
        [{"key":"value"}, "some_data"]
    ])
    def test_check_if_results_match_unknown_types(self, data1, data2):
        with self.assertRaises(TypeError):
            self.module.check_if_results_match(data1, data2)