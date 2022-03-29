import unittest
from parameterized import parameterized

import Libraries.FileMethods as test

class test_FileMethods(unittest.TestCase):

    @parameterized.expand([
        ["config.json"],
        ["registers.json"],
        ["TestedModules/ModuleSystem.py"]
    ])
    def test_check_existing_file(self, path_to_file):
        try:
            test.check_file_exists(path_to_file)
        except FileNotFoundError:
            self.fail("File was not found!")

    @parameterized.expand([
        ["notexisting.json"],
        ["TestedModules/NoModule.py"],
        ["notworking.txt"]
    ])
    def test_check_not_existing_file(self, path_to_file):
        with self.assertRaises(FileNotFoundError):
            test.check_file_exists(path_to_file)

    @parameterized.expand([
        ["config.json"],
        ["registers.json"],
        ["TestedModules/ModuleSystem.py"]
    ])
    def test_open_existing_file(self, path_to_file):
        file = test.open_file(path_to_file, "r")
        self.assertIsNotNone(file)

    @parameterized.expand([
        ["notexisting.json"],
        ["TestedModules/NoModule.py"],
        ["notworking.txt"]
    ])
    def test_open_not_existing_file(self, path_to_file):
        file = test.open_file(path_to_file, "r")
        self.assertIsNone(file)