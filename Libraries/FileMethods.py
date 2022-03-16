# Standard library imports
import json
import os.path

# Local imports
from MainModules.Logger import Logger

def check_file_exists(path_to_file, logger):
    if(os.path.exists(path_to_file) == False or os.path.isfile(path_to_file) == False):
        error_text = f"File at path: {path_to_file} does not exist."
        logger.critical(error_text)
        print(error_text)
        quit()
    else:
        logger.info(f"File at - {path_to_file} successfully found.")

def delete_file_content(path_to_file): # used for log
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

def read_file(file_name, logger=Logger):
    check_file_exists(file_name, logger)
    with open(file_name) as file:
        data = json.load(file)
    return data