import smtplib, ssl

class EmailClient:

    def __init__(self, conf, model_name):
        self.allowed = conf['EMAIL_USE']
        self.port = conf['PORT']
        self.smtp = conf['SMTP']
        self.username = conf['USER']
        self.password = conf['PASSWORD']
        self.receiver = conf['RECEIVER']
        self.message = conf['HEADER'] + model_name + conf['MESSAGE']

    def send_email(self):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp, self.port, context=context) as server:
            server.login(self.username, self.password)
            server.sendmail(self.username, self.receiver, self.message)