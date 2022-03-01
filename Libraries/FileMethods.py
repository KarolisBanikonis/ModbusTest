# Standard library imports
import json
import os.path
import importlib

def file_exists(path_to_file, file_to_close=None):
    if(os.path.exists(path_to_file) == False):
        print(f"File at path: {path_to_file} does not exist.")
        if(file_to_close != None):
            file_to_close.close()
        terminate_program()

# Able to close everything in one loop, but maybe then readability is worse?
def close_all_instances(files, ssh, modbus):
    for file in files:
        file.close()
    ssh.ssh.close()
    modbus.client.close()
    terminate_program()

def terminate_program():
    print("Program is terminated!")
    quit()

def read_file(file_name, file_to_close=None):
    file_exists(file_name, file_to_close)
    with open(file_name) as file:
        registers_data = json.load(file)
    return registers_data, file

def extract_status(input):
    for symbol in input:
        if(symbol.isdigit()):
            return symbol

def load_module(module_name):
        module = None
        try:
            module = importlib.import_module(module_name)
            # module = __import__(module_name)
            return module
        except ModuleNotFoundError:
            print(f"Module {module_name} was not imported!")
            close_all_instances()

def string_to_json(data):
    json_data = json.loads(data)
    return json_data

def remove_char(data, characters):
    remove_table = dict.fromkeys(map(ord, characters), None)
    data = data.translate(remove_table)
    return data

def get_value_in_parenthesis(data):
    return data[data.find("(")+1:data.find(")")]