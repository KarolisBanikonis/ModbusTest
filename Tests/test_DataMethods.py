# Standard library imports
import unittest

# Third party imports
from parameterized import parameterized

# Local imports
import Libraries.DataMethods as test

class test_DataMethods(unittest.TestCase):

    @parameterized.expand([
        ["random5str13", 5],
        ["some1value", 1],
        ["str916512131", 9]
    ])
    def test_get_first_digit(self, input, actual):
        calculated = test.get_first_digit(input)
        self.assertEqual(int(calculated), actual)

    @parameterized.expand([
        ["random 5 str 13", [5, 13]],
        ["some 1 value", [1]],
        ["str 916 512 131", [916, 512, 131]]
    ])
    def test_get_all_digits(self, input, actual):
        calculated = test.get_numbers_in_string(input)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        ["00:1e:42:32:c8:1d", ":", "001e4232c81d"],
        ["00 1e 42 32 c8 1d", " ", "001e4232c81d"],
        ["001e4232c81d\x00", "\x00", "001e4232c81d"]
    ])
    def test_remove_char(self, input, characters, actual):
        calculated = test.remove_char(input, characters)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        ["4G+ (lte)", "lte"],
        ["4G+ (lte-a)", "lte-a"],
        ["(first)(second)", "first"]
    ])
    def test_get_value_in_parenthesis(self, input, actual):
        calculated = test.get_first_value_in_parenthesis(input)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        ["/dev/root 15.6M 15.6M 0 100% /rom", "15.6M"],
        ["tmpfs 121.4M 192.0K 121.2M 0% /tmp", "192.0K"],
        ["/dev/ubi0_2 92.4M 348.0K 87.3M 0% /overlay", "348.0K"]
    ])
    def test_get_used_memory(self, input, actual):
        calculated = test.get_used_memory_from_string(input)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        ["[32mTests passed - 8.[31m", "Tests passed - 8."],
        ["[30mTests [39mpassed - [37m8.[39m", "Tests passed - 8."],
        ["[0mTests [1mpassed [36m- 8.[49m", "Tests passed - 8."]
    ])
    def test_remove_colour_tag(self, input, actual):
        calculated = test.remove_colour_tags(input)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        ["mobile_info '{\"modem\":\"your_modem_id\"}'", "your_modem_id", "id1", "mobile_info '{\"modem\":\"id1\"}'"],
        ["get '{\"period\":\"day\",\"sim\":1,\"modem\":\"your_modem_id\",\"current\":true}'", "your_modem_id", "modem55", "get '{\"period\":\"day\",\"sim\":1,\"modem\":\"modem55\",\"current\":true}'"],
        ["command:\"your_modem_id\"", "your_modem_id", "specified_id", "command:\"specified_id\""]
    ])
    def test_replace_pattern(self, input, pattern, id, actual):
        calculated = test.replace_pattern(input, pattern, id)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        ["'first''second'", "first"],
        ["random'text'input", "text"],
        ["dataone'two''three'", "two"]
    ])
    def test_get_value_in_quotes(self, input, actual):
        calculated = test.get_first_value_in_quotes(input)
        self.assertEqual(calculated, actual)

    def test_get_current_date_in_string(self):
        calculated = test.get_current_date_as_string()
        self.assertIs(str, type(calculated))