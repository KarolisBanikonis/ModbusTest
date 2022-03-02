# Standard library imports
from datetime import datetime

def convert_timestamp_to_date(timestamp):
    date = datetime.utcfromtimestamp(timestamp)
    return date

def convert_string_to_date(string_data):
    date = datetime.strptime(string_data, '%Y-%m-%d %H:%M:%S')
    return date