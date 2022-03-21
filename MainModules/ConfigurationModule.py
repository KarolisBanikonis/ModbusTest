# Local imports
from MainModules.JsonFileModule import JsonFileModule

class ConfigurationModule(JsonFileModule):

    def __init__(self, path_to_file):
        """
        Initializes ConfigurationModule object.

            Parameters:
                file_path (str): path of configuration file
        """
        self.data = self.read_json_file(path_to_file)

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
        # request_data = self.data['Settings'][request_data]
        return request_data

    def get_main_settings(self):
        """Returns all configuration data."""
        main_settings = self.get_param(self.data, 'Settings')
        return main_settings
        # return self.data['Settings']

    def get_ftp_settings(self):
        """Returns configuration data required for uploading reports to FTP server."""
        ftp_settings = self.get_param(self.data, 'FTP')
        return ftp_settings
        # return self.data['FTP']

    def get_email_settings(self):
        """Returns configuration data required for sending emails."""
        email_settings = self.get_param(self.data, 'Email')
        return email_settings
        # return self.data['Email']