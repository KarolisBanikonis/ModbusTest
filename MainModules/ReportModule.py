# Standard library imports
import csv

# Local imports
from Libraries.DataMethods import get_current_data_as_string
from Libraries.FileMethods import open_file

class ReportModule:

    REPORTS_DIRECTORY = "Reports/"

    def __init__(self, info):
        """
        Initializes ReportModule object.

            Parameters:
                info (InformationModule): module that holds router model information
        """
        self.router_model = info.router_model
        self.report_file = f"{self.generate_file_name()}.csv"
        self.report_file_path = f"{self.REPORTS_DIRECTORY}{self.report_file}"
        self.write_router_name_and_header()

    def generate_file_name(self):
        """
        Generates report's file name

            Returns:
                file_name (str): generated report's file name
        """
        self.start_date = get_current_data_as_string("%Y-%m-%d-%H-%M-%S")
        file_name = f"{self.router_model}-{self.start_date}"
        return file_name

    def open_report(self):
        """Opens report's file and sets up writer object"""
        self.report = open_file(self.report_file_path, 'a')
        self.writer = csv.writer(self.report)

    def open_report_for_ftp(self):
        """
        Opens report's file for FTPClient.

            Returns:
                report (_io.TextIOWrapper): opened report file
                None, if file could not be opened
        """
        try:
            #Need to check if it exists.
            report = open(self.report_file_path, 'rb')
            return report
        except IOError:
            return None

    def close(self):
        """Closes report's file."""
        self.report.close()

    def write_router_name_and_header(self):
        """Writes initial information to report's file."""
        self.open_report()
        self.writer.writerow(["Model", self.router_model, '', "Start time", self.start_date]) #, '', '', '', '', '', ''
        self.writer.writerow([])
        self.write_header()
        self.close()

    def write_header(self):
        """Writes the column names of tests results to report's file."""
        self.writer.writerow(['Iteration nr.', 'Module name','Register name', 'Register number', 'Modbus value', 'Router value', 'Result','','CPU usage','Total Used RAM','Used RAM difference'])