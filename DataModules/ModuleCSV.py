# Standard library imports
import csv

# Local imports
from Libraries.FileMethods import close_all_instances

class ModuleCSV:

    def __init__(self, report_file_path, exception_instances):
        self.report_file_path = report_file_path
        self.exception_instances = exception_instances

    def open_report(self):
        try:
            self.report = open(self.report_file_path, 'a', newline='')
            self.writer = csv.writer(self.report)
        except IOError:
            print(f"Could not open the file at {self.report_file_path}")
            close_all_instances(self.exception_instances)

    def close_report(self):
        self.report.close()

    def write_router_name_and_header(self, name):
        self.open_report()
        self.writer.writerow(["Model", name])
        self.writer.writerow([])
        self.write_header()
        self.close_report()

    def write_header(self):
        self.writer.writerow(['Iteration nr.', 'Module name','Register name', 'Register number', 'Modbus value', 'Router value', 'Result'])