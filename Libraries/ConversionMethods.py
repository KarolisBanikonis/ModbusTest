# Standard library imports
from datetime import datetime
import math

def convert_timestamp_to_date(timestamp):
    date = datetime.utcfromtimestamp(timestamp)
    return date

def convert_string_to_date(string_data):
    date = datetime.strptime(string_data, '%Y-%m-%d %H:%M:%S')
    return date

def convert_string_to_bytes(string_data):
    size_types = ["B", "K", "M", "G"]
    size = ""
    type = ""
    for symbol in string_data:
        if(symbol.isdigit() or symbol == "."):
            size += symbol
        else:
            type += symbol
    i = 0
    for i in range(len(size_types)):
        if(type == size_types[i]):
            break
    return int(float(size) * math.pow(1024, i))
    