# Standard library imports
import logging

# Local imports


REPORTS_DIRECTORY = "Logs/"
FILE_NAME = "Log.log"
ENABLED = True

def get_log_file_path():
    file_path = f"{REPORTS_DIRECTORY}{FILE_NAME}"
    return file_path

def init_logger(name):
    """
    Initializes Logger object.

        Parameters:
            name (str): name of Logger
        Returns:
            logger (Logger): initialized Logger object
    """
    file_path = get_log_file_path()
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    return logger

def write_log(logger, severity, msg):
    if(logger is not None and ENABLED):
        try:
            getattr(logger, severity)(msg)
        except AttributeError as err:
            ENABLED = False
            print(f"Such attribute does not exist: {err}")

Logger = init_logger(__name__)