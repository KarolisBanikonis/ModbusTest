# Standard library imports
import ftplib
import socket

# Local imports
from MainModules.Logger import init_logger
from Libraries.PrintMethods import print_error
from Libraries.FileMethods import open_file

class FTPClient:

    def __init__(self, conf, report):
        """
        Initializes FTPClient object. Set settings required for storing files with FTP.

            Parameters:
                conf (ConfigurationModule): module that holds configuration information
                report (ReportModule): module designed to write test results to report file
        """
        self.logger = init_logger(__name__)
        self.allowed = conf['FTP_USE']
        self.host = conf['FTP_HOST']
        self.port = conf['FTP_PORT']
        self.username = conf['FTP_USER']
        self.password = conf['FTP_PASSWORD']
        self.interval = conf['INTERVAL_MINUTES']
        self.report_module = report
        self.ftp = ftplib.FTP()

    def connect(self, output_list):
        """
        Try to connect and log in to the FTP server.
        
            Parameters:
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
        """
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
        """Close the connection with FTP server."""
        self.ftp.quit()

    def store_report(self, output_list):
        """
        Try to store report to the FTP server.

            Parameters:
                output_list (reprint.reprint.output.SignalList): list required for printing to terminal
        """
        if(self.allowed):
            self.connect(output_list)
        if(self.allowed):
            report = self.report_module.open_report_for_ftp()
            if(report is not None):
                command = f'STOR {self.report_module.report_file}'
                self.ftp.storbinary(command, report)
                self.logger.info("Report was uploaded with FTP successfully.")
                report.close()
                self.disconnect()