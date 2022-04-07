import smtplib
import socket
import unittest
from parameterized import parameterized

from MainModules.PrintModule import PrintModule
from Clients.EmailClient import EmailClient

class test_EmailClient(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.print_mod = PrintModule()

    @classmethod
    def tearDownClass(cls):
        del cls.print_mod

    @parameterized.expand([
        [{"SMTP": "smtp.gmail.com",
        "USER": "labas0113@gmail.com",
        "PASSWORD": "belekas111",
        "RECEIVER": "labas0113@gmail.com",
        "INTERVAL_HOURS": 1}, False ],
        [{"SMTP": "smtp.gmail.com",
        "USER": "labas0113@gmail.com",
        "PASSWORD": "badpassword",
        "RECEIVER": "labas0113@gmail.com",
        "INTERVAL_HOURS": 1}, True],
        [{"SMTP": "badsmtp",
        "USER": "labas0113@gmail.com",
        "PASSWORD": "belekas111",
        "RECEIVER": "labas0113@gmail.com",
        "INTERVAL_HOURS": 1}, True]
    ])
    def test_send_email(self, configuration, bad_configuration_data):
        email = EmailClient(configuration)
        if(not bad_configuration_data):
            try:
                email.send_email(self.print_mod)
            except:
                self.fail("Error while sending email!")
        else:
            email.send_email(self.print_mod)
            self.assertFalse(email.allowed)
