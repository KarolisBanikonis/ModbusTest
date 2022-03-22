# Standard library imports
import json

# Local imports
from Libraries.FileMethods import check_file_exists

class JsonFileModule:

    def __init__(self, path_to_file):
        self.read_json_file(path_to_file)

    def read_json_file(self, path_to_file, print_mod):
        """
        Read file which follows JSON format.

            Parameters:
                path_to_file (str): at what path file should be opened
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                json_data (dict): 
        """
        check_file_exists(path_to_file, print_mod)
        with open(path_to_file) as file:
            try:
                json_data = json.load(file)
                return json_data
            except json.JSONDecodeError as err:
                print_mod.error(err, "RED")
                quit()

    def get_param(self, data, key):
        """
        Returns requested data's parameter value.

            Parameters:

                key (str): what parameter value is requested
            Returns:
                data (dict|?): requested part of data
        """
        if(type(data) == dict):
            if(key in data.keys()):
                return data[key]
            else:
                return None
        else:
            return None