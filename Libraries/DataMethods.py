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

def get_first_value_in_parenthesis(input):
    """
    Finds first value between parenthesis in string input.

        Parameters:
            input (str): data
        Returns:
            result (str): value found between parenthesis in input
    """
    pattern = '\((.*?)\)'
    result = re.search(pattern, input).group(1)
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

def get_current_date_as_string(format="%Y-%m-%d-%H:%M:%S"):
    """
    Gets current date in string with specified format.

        Parameters:
            format (str): format in which date should be displayed
        Returns:
            current_date (str): formatted date
    """
    current_date = datetime.now().strftime(format)
    return current_date

def replace_pattern(input, pattern, replace_to):
    """
    Finds and replaces certain pattern with specified modem id.

        Parameters:
            input (str): data which should have certain pattern replaced
            pattern (str): pattern that should be replaced
            replace_to (str): to what data it should be changed
        Returns:
            (str): data with replaced information
    """
    return re.sub(pattern, replace_to, input)

def get_first_value_in_quotes(input):
    """
    Finds first value between single quotes in string input.

        Parameters:
            input (str): data
        Returns:
            result (str): valus found between quotes in input
    """
    pattern = '\'(.*?)\''
    result = re.search(pattern, input).group(1)
    return result