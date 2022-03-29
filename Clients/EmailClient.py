# Standard library imports
import smtplib, ssl
import socket

# Local imports
from Libraries.DataMethods import remove_colour_tags, remove_char
from MainModules.Logger import log_msg

class EmailClient:

    def __init__(self, conf):
        """
        Initializes EmailClient object. Set settings required for sending emails.

            Parameters:
                conf (ConfigurationModule): module that holds configuration information
        """
        self.allowed = True
        self.port = 465
        self.smtp = conf['SMTP']
        self.username = conf['USER']
        self.password = conf['PASSWORD']
        self.receiver = conf['RECEIVER']
        self.interval = conf['INTERVAL_HOURS']
        self.message = "Subject: Tests summary\n\nTests summary:\n\n"

    def send_email(self, print_mod):
        """
        Send an email to recipient.

            Parameters:
                print_mod (PrintModule): module stores information which needs to be send in email
        """
        if(self.allowed):
            text = self.message
            for i in range(4):
                colourless_text = remove_colour_tags(f"{print_mod.print_list[i]}\n")
                text += remove_char(colourless_text, "\x1b")

            context = ssl.create_default_context()
            try:
                with smtplib.SMTP_SSL(self.smtp, self.port, context=context) as server:
                    server.login(self.username, self.password)
                    server.sendmail(self.username, self.receiver, text)
                log_msg(__name__, "info", "Email was sent!")
            except (smtplib.SMTPAuthenticationError, socket.gaierror) as err:
                if(isinstance(err, smtplib.SMTPAuthenticationError)):
                    error_text = f"Email sending failed, check login credentials : {err}"
                elif(isinstance(err, socket.gaierror)):
                    error_text = f"Email sending failed, check SMTP value : {err}"
                log_msg(__name__, "error", error_text)
                print_mod.warning(error_text)
                self.allowed = False