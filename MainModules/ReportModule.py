# Standard library imports
import csv
from datetime import datetime

class ReportModule:

    REPORTS_DIRECTORY = "Reports/"

    def __init__(self, info):
        self.router_model = info.router_model
        self.report_file = f"{self.REPORTS_DIRECTORY}{self.generate_file_name(self.router_model)}.csv"
        self.write_router_name_and_header()

    def generate_file_name(self, name):
        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        return f"{name} {date}"

    def open_report(self):
        try:
            self.report = open(self.report_file, 'a', newline='')
            self.writer = csv.writer(self.report)
            # return report, writer
        except IOError:
            print(f"Could not open the file at {self.report_file}")
            # return None

    def close(self):
        self.report.close()

    def write_router_name_and_header(self):
        self.open_report()
        self.writer.writerow(["Model", self.router_model])
        self.writer.writerow([])
        self.write_header()
        self.report.close()

    def write_header(self):
        self.writer.writerow(['Iteration nr.', 'Module name','Register name', 'Register number', 'Modbus value', 'Router value', 'Result','','CPU usage','Used RAM','Used RAM difference'])