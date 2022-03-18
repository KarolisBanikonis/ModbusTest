# Standard library imports
from datetime import datetime
import re

def get_first_digit(input):
    '''Find first digit occurrence in string input.'''

    for symbol in input:
        if(symbol.isdigit()):
            return int(symbol)

def get_numbers_in_string(input):
    '''Find all number occurences in string input.'''

    numbers = []
    for symbol in input.split():
        if(symbol.isdigit()):
            numbers.append(int(symbol))
    return numbers

def remove_char(input, characters):
    '''Remove chosen characters from string input.'''

    remove_table = dict.fromkeys(map(ord, characters), None)
    data = input.translate(remove_table)
    return data

def get_value_in_parenthesis(data):
    '''Find value between parenthesis in string input.'''

    pattern = '\((.*?)\)'
    result = re.search(pattern, data).group(1)
    return result

def get_used_memory_from_string(input):
    '''Find information unit's string representation in string input.'''

    pattern = '\d+\.\d\w'
    result = re.findall(pattern, input)[1]
    return result

def remove_colour_tags(input):
    '''Find and remove colour tags from string input.'''

    pattern = '.\[.*?m'
    return re.sub(pattern, '', input)

def get_current_data_as_string(format):
    '''Get current data in string with specified format.'''

    current_date = datetime.now().strftime(format)
    return current_date

def replace_modem_id(input, modem_id):
    '''Find and replace certain pattern with specified modem id.'''

    pattern = 'your_modem_id'
    return re.sub(pattern, modem_id, input)