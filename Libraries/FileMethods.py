# Standard library imports
import json
import os.path
import importlib

def check_file_exists(path_to_file):
    if(os.path.exists(path_to_file) == False or os.path.isfile(path_to_file) == False):
        print(f"File at path: {path_to_file} does not exist.")
        terminate_program()

def delete_file_content(path_to_file):
    try:
        open(path_to_file, 'w').close()
        return True
    except OSError:
        print(f"Could not open the file at {path_to_file}")
        return False

# Able to close everything in one loop, but maybe then readability is worse?
def close_all_instances(instances):
    for instance in instances:
        instance.close()
    # for file in files:
    #     file.close()
    # # ssh.ssh.close()
    # # modbus.client.close()
    terminate_program()

def terminate_program():
    # print("Program is terminated!")
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

def load_module(module_name):
        module = None
        try:
            module = importlib.import_module(module_name)
            # module = __import__(module_name)
            return module
        except ModuleNotFoundError:
            print(f"Module {module_name} was not imported!")
            close_all_instances()

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
