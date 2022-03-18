# Standard library imports
import json
import os.path

# Local imports
from MainModules.Logger import Logger

def check_file_exists(path_to_file, logger=Logger):
    '''Check if file at specified path exists.'''

    if(os.path.exists(path_to_file) == False or os.path.isfile(path_to_file) == False):
        error_text = f"File at path: {path_to_file} does not exist."
        logger.critical(error_text)
        print(error_text)
        quit()
    else:
        logger.info(f"File at - {path_to_file} successfully found.")

def open_file(path_to_file, open_mode):
    '''Try to open the file at specified path.'''

    try:
        file = open(path_to_file, open_mode, newline='')
        return file
    except IOError:
        return None

def delete_file_content(path_to_file): # used for log
    '''Delete file's content.'''

    file = open_file(path_to_file, 'w')
    if(file != None):
        file.close()
        return True
    else:
        return False

def close_all_instances(instances):
    '''Close specified objects instances.'''

    for instance in instances:
        instance.close()
    quit()

def read_json_file(file_name, logger=Logger):
    '''Read file which follows JSON format.'''

    check_file_exists(file_name, logger)
    with open(file_name) as file:
        data = json.load(file)
    return data