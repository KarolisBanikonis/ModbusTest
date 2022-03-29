import unittest
from parameterized import parameterized
from datetime import datetime

import Libraries.ConversionMethods as test

class test_ConversionMethods(unittest.TestCase):

    @parameterized.expand([
        [1648448820, datetime(2022, 3, 28, 6, 27)],
        [1500000000, datetime(2017, 7, 14, 2, 40)],
        [1550000000, datetime(2019, 2, 12, 19, 33, 20)]
    ])
    def test_convert_timestamp_to_date(self, input, actual):
        calculated = test.convert_timestamp_to_date(input)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        ["2022-03-28 06:36:49", datetime(2022, 3, 28, 6, 36, 49)],
        ["2020-07-10 10:15:57", datetime(2020, 7, 10, 10, 15, 57)],
        ["2015-01-29 19:23:07", datetime(2015, 1, 29, 19, 23, 7)]
    ])
    def test_convert_string_to_date(self, input, actual):
        calculated = test.convert_string_to_date(input)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        ["105.5M", 110624768],
        ["2914.7M", 3056284467],
        ["844K", 864256]
    ])
    def test_convert_string_to_bytes(self, input, actual):
        calculated = test.convert_string_to_bytes(input)
        self.assertEqual(calculated, actual)

    @parameterized.expand([
        ["helloworld", [104, 101, 108, 108, 111, 119, 111, 114, 108, 100]],
        ["testinput", [116, 101, 115, 116, 105, 110, 112, 117, 116]],
        ["exampletext", [101, 120, 97, 109, 112, 108, 101, 116, 101, 120, 116]]
    ])
    def test_convert_text_to_decimal(self, input, actual):
        calculated = test.convert_text_to_decimal(input)
        self.assertEqual(calculated, actual)

if __name__ == '__main__':
    unittest.main()