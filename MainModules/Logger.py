# Standard library imports
import logging

# Local imports

REPORTS_DIRECTORY = "Logs/"
FILE_NAME = "Log.log"

def get_log_file_path():
    path_to_file = f"{REPORTS_DIRECTORY}{FILE_NAME}"
    return path_to_file

def prepare_file(path_to_file):
    """
    Delete file's content if it exists, otherwise create a new file.

        Parameters:
            path_to_file (str): at what path file's content should be deleted
        Returns:
            True, if path is correct
            False if path is incorrect
    """
    try:
        open(path_to_file, 'w').close()
        return True
    except FileNotFoundError:
        print(f"Directory '{REPORTS_DIRECTORY}' does not exist.")
        return False

def init_logger(name):
    """
    Initializes Logger object.

        Parameters:
            name (str): name of Logger
        Returns:
            logger (Logger): initialized Logger object, if log file exists
            None, if log file does not exist
    """
    path_to_file = get_log_file_path()
    file_exists = prepare_file(path_to_file)
    if(file_exists):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(path_to_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        return logger
    else:
        return None

Logger = init_logger(__name__)

def log_msg(name, severity, msg):
    """
    Logs a message.

        Parameters:
            name (str): write a name of a module, where logging happens
            severity (str): level of importance
            msg (str): message to be logged
    """
    if(Logger is not None):
        try:
            Logger.name = name
            function = getattr(Logger, severity)
            is_function_callable = callable(function)
            if(is_function_callable):
                function(msg)
        except AttributeError:
            pass