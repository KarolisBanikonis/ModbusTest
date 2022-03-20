# Standard library imports
import json
import os.path

# Local imports
from MainModules.Logger import Logger

def check_file_exists(path_to_file, logger=Logger):
    """
    Check if file at specified path exists.

        Parameters:
            path_to_file (str): at what path file should be checked
    """
    if(os.path.exists(path_to_file) == False or os.path.isfile(path_to_file) == False):
        error_text = f"File at path: {path_to_file} does not exist."
        logger.critical(error_text)
        print(error_text)
        quit()
    else:
        logger.info(f"File at - {path_to_file} successfully found.")

def open_file(path_to_file, open_mode):
    """
    Try to open the file at specified path.

        Parameters:
            path_to_file (str): at what path file should be opened
            open_mode (str): with what mode file should be opened
        Returns:
            report (_io.TextIOWrapper): opened report file
            None, if file could not be opened
    """
    try:
        file = open(path_to_file, open_mode, newline='')
        a = type(file)
        return file
    except IOError:
        return None

def delete_file_content(path_to_file): # used for log
    """
    Delete file's content.

        Parameters:
            path_to_file (str): at what path file's content should be deleted
    """
    file = open_file(path_to_file, 'w')
    if(file != None):
        file.close()
        return True
    else:
        return False

def close_all_instances(instances):
    """
    Close specified objects instances.

        Parameters:
            instances (list): list of instances that should be closed
    """
    for instance in instances:
        instance.close()
    quit()

def read_json_file(path_to_file, logger=Logger):
    """
    Read file which follows JSON format.

        Parameters:
            path_to_file (str): at what path file should be opened
        Returns:
            data (dict): data loaded from JSON format file
    """
    check_file_exists(path_to_file, logger)
    with open(path_to_file) as file:
        data = json.load(file)
    return data