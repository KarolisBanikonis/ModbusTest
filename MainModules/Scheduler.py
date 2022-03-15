# Standard library imports
from sys import platform

# Third party imports
from apscheduler.schedulers.background import BackgroundScheduler

class Scheduler:

    def __init__(self, ftp, email):
        self.ftp = ftp
        self.email = email
        self.scheduler = BackgroundScheduler()
        allow_status = self.ftp.allowed.casefold()
        if(allow_status == "yes" and platform == "linux"):
            self.scheduler.add_job(self.ftp.store_report, 'interval', minutes=self.ftp.interval)
    
    def start(self):
        self.scheduler.start()

    def send_email(self, output_list):
        allow_status = self.email.allowed.casefold()
        if(allow_status == "yes"):
            self.scheduler.add_job(self.email.send_email, 'interval', hours=self.email.interval, args=output_list)