# Standard library imports
import csv

# Local imports
from Libraries.DataMethods import get_current_data_as_string

class ReportModule:

    REPORTS_DIRECTORY = "Reports/"

    def __init__(self, info):
        self.router_model = info.router_model
        self.report_file = f"{self.generate_file_name(self.router_model)}.csv"
        self.report_file_path = f"{self.REPORTS_DIRECTORY}{self.report_file}"
        self.write_router_name_and_header()

    def generate_file_name(self, name):
        date = get_current_data_as_string("%Y-%m-%d-%H-%M-%S")
        return f"{name}-{date}"

    def open_report(self):
        try:
            self.report = open(self.report_file_path, 'a', newline='')
            self.writer = csv.writer(self.report)
        except IOError:
            print(f"Could not open the file at {self.report_file_path}")

    def open_report_for_ftp(self):
        try:
            report = open(self.report_file_path, 'rb')
            return report
        except IOError:
            print(f"Could not open the file at {self.report_file_path}")

    def close(self):
        self.report.close()

    def write_router_name_and_header(self):
        self.open_report()
        self.writer.writerow(["Model", self.router_model])
        self.writer.writerow([])
        self.write_header()
        self.report.close()

    def write_header(self):
        self.writer.writerow(['Iteration nr.', 'Module name','Register name', 'Register number', 'Modbus value', 'Router value', 'Result','','CPU usage','Total Used RAM','Used RAM difference'])