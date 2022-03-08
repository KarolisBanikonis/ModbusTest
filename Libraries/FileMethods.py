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