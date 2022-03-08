# Standard library imports
import json
import os.path

def check_file_exists(path_to_file):
    if(os.path.exists(path_to_file) == False or os.path.isfile(path_to_file) == False):
        print(f"File at path: {path_to_file} does not exist.")
        quit()

def delete_file_content(path_to_file):
    try:
        open(path_to_file, 'w').close()
        return True
    except OSError:
        print(f"Could not open the file at {path_to_file}")
        return False

def close_all_instances(instances):
    for instance in instances:
        instance.close()
    quit()

def read_file(file_name):
    check_file_exists(file_name)
    with open(file_name) as file:
        data = json.load(file)
    return data

def extract_status(input):
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
