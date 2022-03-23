# Standard library imports
import ftplib
import socket

# Local imports
from MainModules.Logger import log_msg

class FTPClient:

    def __init__(self, conf, report):
        """
        Initializes FTPClient object. Set settings required for storing files with FTP.

            Parameters:
                conf (ConfigurationModule): module that holds configuration information
                report (ReportModule): module designed to write test results to report file
        """
        self.allowed = conf['FTP_USE']
        self.host = conf['FTP_HOST']
        self.port = conf['FTP_PORT']
        self.username = conf['FTP_USER']
        self.password = conf['FTP_PASSWORD']
        self.interval = conf['INTERVAL_MINUTES']
        self.report_module = report
        self.ftp = ftplib.FTP()

    def connect(self, print_mod):
        """
        Try to connect and log in to the FTP server.
        
            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
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
            log_msg(__name__, "error", error_text)
            print_mod.warning(error_text)

    def disconnect(self):
        """Close the connection with FTP server."""
        self.ftp.quit()

    def store_report(self, print_mod):
        """
        Try to store report to the FTP server.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
        """
        if(self.allowed):
            self.connect(print_mod)
        if(self.allowed):
            report = self.report_module.open_report_for_ftp(print_mod)
            if(report is not None):
                command = f'STOR {self.report_module.report_file}'
                self.ftp.storbinary(command, report)
                log_msg(__name__, "info", "Report was uploaded with FTP successfully.")
                report.close()
                self.disconnect()