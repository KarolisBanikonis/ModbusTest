# Standard library imports
import csv

def open_report(file_path):
    try:
        report = open(file_path, 'a', newline='')
        writer = csv.writer(report)
        return report, writer
    except IOError:
        print(f"Could not open the file at {file_path}")
        return None

def write_router_name_and_header(file_path, name):
    report, writer = open_report(file_path)
    writer.writerow(["Model", name])
    writer.writerow([])
    write_header(writer)
    report.close()

def write_header(writer):
    writer.writerow(['Iteration nr.', 'Module name','Register name', 'Register number', 'Modbus value', 'Router value', 'Result','','CPU usage','Used RAM','Used RAM difference'])