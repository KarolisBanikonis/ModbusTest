# Local imports
from Libraries.FileMethods import read_file

class ConfigurationModule:

    def __init__(self, file_path,):
        self.data = read_file(file_path)

    def get_data(self, request_data):
        return self.data['Settings'][0][request_data]

    def get_all_data(self):
        return self.data['Settings'][0]

    def get_ftp_data(self):
        return self.data['FTP'][0]