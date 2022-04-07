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