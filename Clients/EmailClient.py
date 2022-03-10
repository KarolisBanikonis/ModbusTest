import smtplib, ssl

# Local imports
from Libraries.DataMethods import remove_colour_tags

class EmailClient:

    def __init__(self, conf):
        self.allowed = conf['EMAIL_USE']
        self.port = conf['PORT']
        self.smtp = conf['SMTP']
        self.username = conf['USER']
        self.password = conf['PASSWORD']
        self.receiver = conf['RECEIVER']
        self.interval = conf['INTERVAL_HOURS']
        self.message = "Subject: Tests summary\n\n Tests summary:\n\n"

    def send_email(self, output_list):
        text = self.message
        for i in range(4):
            text += remove_colour_tags(f"{output_list[i]}\n")

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp, self.port, context=context) as server:
            server.login(self.username, self.password)
            server.sendmail(self.username, self.receiver, text)