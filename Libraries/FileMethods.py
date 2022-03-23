# Standard library imports
import os.path

# Local imports
from MainModules.Logger import log_msg

def check_file_exists(path_to_file):
    """
    Check if file at specified path exists.

        Parameters:
            path_to_file (str): at what path file should be checked
    """
    if(os.path.exists(path_to_file) == False or os.path.isfile(path_to_file) == False):
        raise FileNotFoundError()
    else:
        log_msg(__name__, "info", f"File at - {path_to_file} successfully found.")

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
        return file
    except IOError:
        return None

def close_all_instances(instances):
    """
    Close specified objects instances.

        Parameters:
            instances (list): list of instances that should be closed
    """
    for instance in instances:
        instance.close()
    quit()