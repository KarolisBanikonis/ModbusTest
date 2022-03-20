# Standard library imports
from datetime import datetime
import math

def convert_timestamp_to_date(timestamp):
    """
    Convert Unix timestamp to date.

        Parameters:
            timestamp (int): date in Unix timestamp format
        Returns:
            date (datetime): timestamp converted to datetime format
    """
    a = type(timestamp)
    date = datetime.utcfromtimestamp(timestamp)
    return date

def convert_string_to_date(string_date):
    """
    Convert date's string representation to datetime object.

        Parameters:
            string_date (str): date in string format
        Returns:
            date (datetime): string converted to datetime format
    """
    date = datetime.strptime(string_date, '%Y-%m-%d %H:%M:%S')
    return date

def convert_string_to_bytes(string_data):
    """
    Convert information unit's string representation to bytes.

        Parameters:
            string_data (str): information unit's in string format
        Returns:
            bytes (int): data in string format converted to bytes
    """
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
    bytes = int(float(size) * math.pow(1024, i))
    return bytes
    