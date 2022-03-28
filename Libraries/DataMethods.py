# Standard library imports
from datetime import datetime
import re

def get_first_digit(input):
    """
    Finds first digit occurrence in string input.

        Parameters:
            input (str): data
        Returns:
            (int): first found digit
    """
    for symbol in input:
        if(symbol.isdigit()):
            return int(symbol)

def get_numbers_in_string(input):
    """
    Finds all number occurences in string input.

        Parameters:
            input (str): data
        Returns:
            numbers (list): all found digits
    """
    numbers = []
    for symbol in input.split():
        if(symbol.isdigit()):
            numbers.append(int(symbol))
    return numbers

def remove_char(input, characters):
    """
    Removes chosen characters from string input.

        Parameters:
            input (str): data
            characters (str): characters to remove from input
        Returns:
            data (str): data without specified characters
    """
    remove_table = dict.fromkeys(map(ord, characters), None)
    data = input.translate(remove_table)
    return data

def get_first_value_in_parenthesis(data):
    """
    Finds first value between parenthesis in string input.

        Parameters:
            input (str): data
        Returns:
            result (str): value found between parenthesis in input
    """
    pattern = '\((.*?)\)'
    result = re.search(pattern, data).group(1)
    return result

def get_used_memory_from_string(input):
    """
    Finds information unit's string representation in string input.

        Parameters:
            input (str): data
        Returns:
            result (str): information unit's in string format, for example (171.1MB)
    """
    pattern = '\d+\.\d\w'
    result = re.findall(pattern, input)[1]
    return result

def remove_colour_tags(input):
    """
    Finds and removes colour tags from string input.

        Parameters:
            input (str): data
        Returns:
            (str): data without colour tags
    """
    pattern = '\[.*?m'
    return re.sub(pattern, '', input)

def get_current_data_as_string(format="%Y-%m-%d-%H-%M-%S.%f"):
    """
    Gets current data in string with specified format.

        Parameters:
            format (str): format in which date should be displayed
        Returns:
            current_data (str): formatted date
    """
    current_date = datetime.now().strftime(format)
    return current_date

def replace_modem_id(input, modem_id):
    """
    Finds and replaces certain pattern with specified modem id.

        Parameters:
            input (str): data which should have modem id replaced
            modem_id (str): to what modem id it should be changed
        Returns:
            (str): data with specified modem id
    """
    pattern = 'your_modem_id'
    return re.sub(pattern, modem_id, input)

def get_first_value_in_quotes(data):
    """
    Finds first value between single quotes in string input.

        Parameters:
            input (str): data
        Returns:
            result (str): valus found between quotes in input
    """
    pattern = '\'(.*?)\''
    result = re.search(pattern, data).group(1)
    return result