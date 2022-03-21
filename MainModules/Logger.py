# Standard library imports
import logging

# Local imports


REPORTS_DIRECTORY = "Logs/"
FILE_NAME = "Log.log"
ENABLED = True

def get_log_file_path():
    path_to_file = f"{REPORTS_DIRECTORY}{FILE_NAME}"
    return path_to_file

def init_logger(name):
    """
    Initializes Logger object.

        Parameters:
            name (str): name of Logger
        Returns:
            logger (Logger): initialized Logger object
            None, if log file was not found
    """
    path_to_file = get_log_file_path()
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    try:
        file_handler = logging.FileHandler(path_to_file)
        file_handler.setLevel(logging.INFO)
    except FileNotFoundError:
        print(f"File not found at {path_to_file}.")
        return None
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    return logger

Logger = init_logger(__name__)

def log_msg(name, severity, msg):
    if(Logger is not None):
        try:
            Logger.name = name
            getattr(Logger, severity)(msg)
        except AttributeError as err:
            print(f"Such attribute does not exist: {err}")