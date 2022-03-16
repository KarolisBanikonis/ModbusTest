# Local imports
from Libraries.FileMethods import read_file
from MainModules.Logger import init_logger

class ConfigurationModule:

    def __init__(self, file_path,):
        logger = init_logger(__name__)
        self.data = read_file(file_path, logger)

    def get_data(self, request_data):
        return self.data['Settings'][0][request_data]

    def get_all_data(self):
        return self.data['Settings'][0]

    def get_ftp_data(self):
        return self.data['FTP'][0]

    def get_email_data(self):
        return self.data['Email'][0]