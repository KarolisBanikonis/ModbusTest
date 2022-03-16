import unittest

import Libraries.DataMethods as test
# from Libraries.DataMethods import get_first_digit

class test_DataMethods(unittest.TestCase):

    def test_get_first_digit(self):
        data = "sdfsdfsdf5sdf13"
        result = test.get_first_digit(data)
        self.assertEqual(int(result), 5)

    def test_aa(self):
        self.assertEqual(3, 3)

if __name__ == '__main__':
    unittest.main()