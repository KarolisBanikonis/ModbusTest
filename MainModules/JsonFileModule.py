# Standard library imports
import json

# Local imports
from Libraries.FileMethods import check_file_exists
from Libraries.Logger import log_msg

class JsonFileModule:

    def __init__(self, path_to_file, print_mod):
        """
        Initializes JsonFileModule object.

            Parameters:
                path_to_file (str): path of file that should be read
                print_mod (PrintModule): module designed for printing to terminal
        """
        self.data = self.read_json_file(path_to_file, print_mod)

    def read_json_file(self, path_to_file, print_mod):
        """
        Read file which follows JSON format.

            Parameters:
                path_to_file (str): at what path file should be opened
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                json_data (dict): dictionary which stores information read from json file
        """
        try:
            check_file_exists(path_to_file)
        except FileNotFoundError as err:
            error_text = f"File at path: {path_to_file} does not exist."
            log_msg(__name__, "critical", error_text)
            print_mod.error(error_text)
            quit()
        with open(path_to_file) as file:
            try:
                json_data = json.load(file)
                return json_data
            except json.JSONDecodeError as err:
                log_msg(__name__, "critical", err)
                print_mod.error(err, "RED")
                quit()

    def get_param(self, data, key):
        """
        Returns requested data's parameter value.

            Parameters:
                key (str): what parameter value is requested
            Returns:
                data (str): requested part of data, if it exists
                None, if it does not exist
        """
        if(type(data) == dict):
            if(key in data.keys()):
                return data[key]
            else:
                return None
        else:
            return None