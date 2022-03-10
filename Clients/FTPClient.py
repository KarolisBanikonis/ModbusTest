# Standard library imports
import ftplib
import socket

# Local imports
from MainModules.FTPError import FTPError

class FTPClient:

    def __init__(self, config, report_module):
        self.allowed = config['FTP_USE']
        self.host = config['FTP_HOST']
        self.port = config['FTP_PORT']
        self.username = config['FTP_USER']
        self.password = config['FTP_PASSWORD']
        self.interval = config['INTERVAL_MINUTES']
        self.report_module = report_module
        self.ftp = ftplib.FTP()

    def connect(self):
        try:
            self.ftp.connect(self.host, self.port)
            self.ftp.login(self.username, self.password)
        except (socket.gaierror, ConnectionRefusedError, ftplib.error_perm) as err:
            error_text = ""
            if(isinstance(err, socket.gaierror)):
                error_text = f"FTP failed to connect, check host value: {err}"
            elif(isinstance(err, ConnectionRefusedError)):
                error_text = f"FTP failed to connect, check port value: {err}"
            else:
                error_text = f"FTP failed to login: {err}"
            self.allowed = "no"
            raise FTPError(error_text)

    def disconnect(self):
        self.ftp.quit()

    def store_report(self):
        if(self.allowed.casefold() != "yes"):
            return
        self.connect()
        report = self.report_module.open_report_for_ftp()
        command = f'STOR {self.report_module.report_file}'
        self.ftp.storbinary(command, report)
        report.close()
        self.disconnect()