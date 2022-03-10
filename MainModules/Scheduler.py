# Standard library imports
import datetime

# Third party imports
from apscheduler.schedulers.background import BackgroundScheduler

class Scheduler:

    def __init__(self, ftp, email):
        self.ftp = ftp
        self.email = email
        self.scheduler = BackgroundScheduler()
        if(self.ftp.allowed.casefold() != "yes"):
            self.scheduler.add_job(self.ftp.store_report, 'interval', minutes=self.ftp.interval)
    
    def start(self):
        self.scheduler.start()

    def send_email(self, output_list):
        if(self.email.allowed.casefold() != "yes"):
            self.scheduler.add_job(self.email.send_email, 'interval', hours=self.email.interval, args=output_list)