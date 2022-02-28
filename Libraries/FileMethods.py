# Standard library imports
import json
import os.path
import importlib

def file_exists(path_to_file):
    if(os.path.exists(path_to_file) == False):
        print(f"File at path: {path_to_file} does not exist.")
        quit()

# Able to close everything in one loop, but maybe then readability is worse?
def program_quit(files, ssh, modbus):
    for file in files:
        file.close()
    ssh.ssh.close()
    modbus.client.close()
    print("Program is terminated!")
    quit()

def read_file(file_name):
    file_exists(file_name)
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
            quit()

def string_to_json(data):
    json_data = json.loads(data)
    return json_data

def remove_char(data, characters):
    remove_table = dict.fromkeys(map(ord, characters), None)
    data = data.translate(remove_table)
    return data