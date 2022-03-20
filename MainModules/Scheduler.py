# Standard library imports
from sys import platform

# Third party imports
from apscheduler.schedulers.background import BackgroundScheduler

class Scheduler:

    def __init__(self, ftp, email):
        """
        Initializes Scheduler object.

            Parameters:
                ftp (FTPClient): module designed to upload report to FTP server
                email (EmailClient): module designed to send emails
        """
        self.ftp = ftp
        self.email = email
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        """
        Start scheduling jobs.
        """
        self.scheduler.start()

    def send_email_periodically(self, output_list):
        """
        Add job to send emails periodically.

            Parameters:
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            and also it is information that is sent in an email
        """
        if(self.email.allowed):
            self.scheduler.add_job(self.email.send_email, 'interval', seconds=self.email.interval, args=output_list)

    def store_ftp_periodically(self, output_list):
        """
        Add job to upload report to FTP server periodically.

            Parameters:
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
        """
        if(self.ftp.allowed and platform == "linux"):
            self.scheduler.add_job(self.ftp.store_report, 'interval', seconds=self.ftp.interval, args=output_list)