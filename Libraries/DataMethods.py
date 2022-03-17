# Standard library imports
from datetime import datetime
import re

def get_first_digit(input):
    for symbol in input:
        if(symbol.isdigit()):
            return symbol

def get_numbers_in_string(input):
    # [int(s) for s in input.split() if s.isdigit()]
    numbers = []
    for symbol in input.split():
        if(symbol.isdigit()):
            numbers.append(int(symbol))
    return numbers

def remove_char(data, characters):
    remove_table = dict.fromkeys(map(ord, characters), None)
    data = data.translate(remove_table)
    return data

def get_value_in_parenthesis(data):
    pattern = '\((.*?)\)'
    result = re.search(pattern, data).group(1)
    return result
    # return data[data.find("(")+1:data.find(")")]

def get_used_memory_from_string(string_value):
    pattern = '\d+\.\d\w'
    result = re.findall(pattern, string_value)[1]
    return result
    # count_first_spaces = 0
    # first_space = True
    # used_memory = ""
    # for symbol in string_value:
    #     if(count_first_spaces == 2 and symbol != ' '):
    #         used_memory += symbol
    #     if(symbol == ' ' and first_space):
    #         count_first_spaces += 1
    #         first_space = False
    #     elif(symbol.isdigit()):
    #         first_space = True
    # return used_memory

def remove_colour_tags(data):
    pattern = '.\[.*?m'
    return re.sub(pattern, '', data)

def get_current_data_as_string(format):
    current_data = datetime.now().strftime(format)
    return current_data

def replace_modem_id(data, modem_id):
    pattern = '3-1'
    return re.sub(pattern, modem_id, data)