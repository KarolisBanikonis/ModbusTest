# Local imports
from MainModules.JsonFileModule import JsonFileModule

class ConfigurationModule(JsonFileModule):

    def __init__(self, path_to_file, print_mod):
        """
        Initializes ConfigurationModule object.

            Parameters:
                path_to_file (str): path of configuration file
                print_mod (PrintModule): module designed for printing to terminal
        """
        super().__init__(path_to_file, print_mod)
        self.validate_data(print_mod)

    def validate_data(self, print_mod):
        """
        Validates data typed by a user in a configuration file.
        If wrong data is typed, program will be stopped.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
        """
        config_file_data_types = [[str, int, str, str, int, int],
        [bool, str, int, str, str, int],
        [str, str, str, str, int],
        [int, str, str]]
        i = 0
        for v in self.data.values():
            j = 0
            for key, value in v.items():
                req_type = config_file_data_types[i][j]
                if(type(value) == req_type):
                    if(req_type is int and value < 0):
                        print_mod.error(f"'{key}' value must be greater than 0!")
                        quit()
                else:
                    print_mod.error(f"Type of '{key}' value must be {req_type.__name__}!")
                    quit()
                j += 1
            i += 1

    def get_data(self, request_data):
        """
        Returns requested part of configuration data.

            Parameters:
                request_data (str): path of configuration file
            Returns:
                data (dict): requested part of configuration file
        """
        config_data = self.get_param(self.data, 'Settings')
        request_data = self.get_param(config_data, request_data)
        return request_data

    def get_main_settings(self):
        """Returns all configuration data."""
        main_settings = self.get_param(self.data, 'Settings')
        return main_settings

    def get_ftp_settings(self):
        """Returns configuration data required for uploading reports to FTP server."""
        ftp_settings = self.get_param(self.data, 'FTP')
        return ftp_settings

    def get_email_settings(self):
        """Returns configuration data required for sending emails."""
        email_settings = self.get_param(self.data, 'Email')
        return email_settings