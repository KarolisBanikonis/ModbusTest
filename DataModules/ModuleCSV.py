# Standard library imports
import csv

# Local imports
from Libraries.FileMethods import close_all_instances

class ModuleCSV:

    def __init__(self, report_file_path, exception_instances):
        self.report_file_path = report_file_path
        self.exception_instances = exception_instances
        # self.open_report()
        # self.set_writer()

    def open_report(self):
        try:
            self.report = open(self.report_file_path, 'a', newline='')
        except IOError:
            print(f"Could not open the file at {self.report_file_path}")
            close_all_instances(self.exception_instances)


    def set_writer(self):
        self.writer = csv.writer(self.report)

    def close_report(self):
        self.report.close()

    def write_header_1(self, name):
        self.write_module_name(name)
        self.writer.writerow(['TEST NUMBER', 'NAME', 'MODBUS DATA', 'SYSTEM DATA', 'IS CORRECT'])

    def write_header_2(self):
        self.writer.writerow(['Successful test count', 'Not successful test count', 'Total test count'])

    def write_data(self, data):
        self.writer.writerow(data)

    def write_module_name(self, name):
        data = [f"{name}"]
        self.writer.writerow(data)
        self.writer.writerow("")