# Standard library imports
import smtplib, ssl
import socket

# Local imports
from Libraries.DataMethods import remove_colour_tags
from MainModules.Logger import init_logger
from Libraries.PrintMethods import print_error

class EmailClient:

    def __init__(self, conf):
        '''Set settings required for sending emails.'''

        self.allowed = True
        self.port = 465
        self.smtp = conf['SMTP']
        self.username = conf['USER']
        self.password = conf['PASSWORD']
        self.receiver = conf['RECEIVER']
        self.interval = conf['INTERVAL_HOURS']
        self.message = "Subject: Tests summary\n\n Tests summary:\n\n"
        self.logger = init_logger(__name__)

    def send_email(self, output_list):
        '''Send an email to recipient.'''

        if(self.allowed):
            text = self.message
            for i in range(4):
                text += remove_colour_tags(f"{output_list[i]}\n")

            context = ssl.create_default_context()
            try:
                with smtplib.SMTP_SSL(self.smtp, self.port, context=context) as server:
                    server.login(self.username, self.password)
                    server.sendmail(self.username, self.receiver, text)
                self.logger.info("Email was sent!")
            except (smtplib.SMTPAuthenticationError, socket.gaierror) as err:
                if(isinstance(err, smtplib.SMTPAuthenticationError)):
                    error_text = f"Email sending failed, check login credentials : {err}"
                elif(isinstance(err, socket.gaierror)):
                    error_text = f"Email sending failed, check SMTP value : {err}"
                self.logger.error(error_text)
                print_error(error_text, output_list, "RED")
                self.allowed = False