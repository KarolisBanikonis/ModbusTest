# Standard library imports
from sys import platform

# Third party imports
from apscheduler.schedulers.background import BackgroundScheduler

# Local imports
from Clients.EmailClient import EmailClient
from Clients.FTPClient import FTPClient

class Scheduler:

    def __init__(self, email_settings, ftp_settings, report, print_mod):
        """
        Initializes Scheduler object.

            Parameters:
                email_settings (dict): configuration infromation for
                    sending emails
                ftp_settings (dict): configuration information for 
                    uploading report to FTP server
                report (ReportModule): module designed to write test results to report file
                print_mod (PrintModule): module designed for printing to terminal
        """
        self.scheduler = BackgroundScheduler()
        self.email = EmailClient(email_settings)
        self.send_email_periodically([print_mod])
        if(ftp_settings['FTP_USE'] and platform == "linux"):
            self.ftp = FTPClient(ftp_settings, report)
            self.ftp.store_report(print_mod)
            self.store_ftp_periodically([print_mod])
        self.start()

    def start(self):
        """
        Start scheduling jobs.
        """
        self.scheduler.start()

    def send_email_periodically(self, print_mod):
        """
        Add job to send emails periodically.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
            and also it contains information that is sent in an email
        """
        self.scheduler.add_job(self.email.send_email, 'interval',
            hours=self.email.interval, args=print_mod)

    def store_ftp_periodically(self, print_mod):
        """
        Add job to upload report to FTP server periodically.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
        """
        self.scheduler.add_job(self.ftp.store_report, 'interval',
            minutes=self.ftp.interval, args=print_mod)