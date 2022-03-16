# Standard library imports
from sys import platform

# Third party imports
from apscheduler.schedulers.background import BackgroundScheduler

class Scheduler:

    def __init__(self, ftp, email):
        self.ftp = ftp
        self.email = email
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        self.scheduler.start()

    def send_email_periodically(self, output_list):
        if(self.email.allowed):
            self.scheduler.add_job(self.email.send_email, 'interval', seconds=self.email.interval, args=output_list)

    def store_ftp_periodically(self, output_list):
        if(self.ftp.allowed and platform == "linux"):
            self.scheduler.add_job(self.ftp.store_report, 'interval', seconds=self.ftp.interval, args=output_list)