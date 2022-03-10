import re

def get_first_digit(input):
    for symbol in input:
        if(symbol.isdigit()):
            return symbol

def remove_char(data, characters):
    remove_table = dict.fromkeys(map(ord, characters), None)
    data = data.translate(remove_table)
    return data

def get_value_in_parenthesis(data):
    return data[data.find("(")+1:data.find(")")]

def get_used_memory_from_string(string_value):
    count_first_spaces = 0
    first_space = True
    used_memory = ""
    for symbol in string_value:
        if(count_first_spaces == 2 and symbol != ' '):
            used_memory += symbol
        if(symbol == ' ' and first_space):
            count_first_spaces += 1
            first_space = False
        elif(symbol.isdigit()):
            first_space = True
    return used_memory

def remove_colour_tags(data):
    pattern = '.\[.*?m'
    return re.sub(pattern, '', data)