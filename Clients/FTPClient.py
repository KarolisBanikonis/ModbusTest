# Standard library imports
import ftplib
import socket

# Local imports
from MainModules.Logger import init_logger
from Libraries.PrintMethods import print_error

class FTPClient:

    def __init__(self, config, report_module):
        self.logger = init_logger(__name__)
        self.allowed = config['FTP_USE']
        self.host = config['FTP_HOST']
        self.port = config['FTP_PORT']
        self.username = config['FTP_USER']
        self.password = config['FTP_PASSWORD']
        self.interval = config['INTERVAL_MINUTES']
        self.report_module = report_module
        self.ftp = ftplib.FTP()

    def connect(self, output_list):
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
            self.allowed = False
            self.logger.error(error_text)
            print_error(error_text, output_list, "RED")

    def disconnect(self):
        self.ftp.quit()

    def store_report(self, output_list):
        if(self.allowed):
            self.connect(output_list)
        if(self.allowed):
            report = self.report_module.open_report_for_ftp()
            command = f'STOR {self.report_module.report_file}'
            self.ftp.storbinary(command, report)
            self.logger.info("Report was uploaded with FTP successfully.")
            report.close()
            self.disconnect()