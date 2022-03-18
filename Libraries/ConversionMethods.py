# Standard library imports
from datetime import datetime
import math

def convert_timestamp_to_date(timestamp):
    '''Convert Unix timestamp to date.'''

    date = datetime.utcfromtimestamp(timestamp)
    return date

def convert_string_to_date(string_data):
    '''Convert date's string representation to datetime object.'''

    date = datetime.strptime(string_data, '%Y-%m-%d %H:%M:%S')
    return date

def convert_string_to_bytes(string_data):
    '''Convert information unit's string representation to bytes.'''

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
    