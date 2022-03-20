# Local imports
from Libraries.FileMethods import read_json_file
from MainModules.Logger import init_logger

class ConfigurationModule:

    def __init__(self, file_path):
        """
        Initializes ConfigurationModule object.

            Parameters:
                file_path (str): path of configuration file
        """
        logger = init_logger(__name__)
        self.data = read_json_file(file_path, logger)

    def get_data(self, request_data):
        """
        Returns requested part of configuration data.

            Parameters:
                request_data (str): path of configuration file
            Returns:
                data (dict): requested part of configuration file
        """
        data = self.data['Settings'][0][request_data]
        return data

    def get_all_data(self):
        """Returns all configuration data."""
        return self.data['Settings'][0]

    def get_ftp_data(self):
        """Returns configuration data required for uploading reports to FTP server."""
        return self.data['FTP'][0]

    def get_email_data(self):
        """Returns configuration data required for sending emails."""
        return self.data['Email'][0]