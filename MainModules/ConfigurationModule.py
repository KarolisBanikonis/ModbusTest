# Local imports
from MainModules.JsonFileModule import JsonFileModule
from Libraries.Logger import log_msg

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
        config_file_first_level_keys = ["Settings", "FTP",
            "Email", "ModbusWrite"]
        config_file_second_level_keys = [["SERVER_HOST",
            "MODBUS_PORT", "USERNAME", "PASSWORD", "RECONNECT_ATTEMPTS", "TIMEOUT"],
            ["FTP_USE", "FTP_HOST", "FTP_USER", "FTP_PASSWORD", "INTERVAL_MINUTES"],
            ["USER", "PASSWORD", "RECEIVER", "INTERVAL_HOURS"],
            ["SIM", "CHANGE_APN", "DEFAULT_APN"]]
        config_file_data_types = [[str, int, str, str, int, int],
            [bool, str, str, str, int],
            [str, str, str, int],
            [int, str, str]]
        i = 0
        error_text = None
        for key1, value1 in self.data.items():
            j = 0
            if(key1 != config_file_first_level_keys[i]):
                error_text = (f"First level key nr. {i + 1} must be named '" +
                    f"{config_file_first_level_keys[i]}'!")
            for key2, value2 in value1.items():
                if(key2 != config_file_second_level_keys[i][j]):
                    error_text = (f"Section's '{config_file_first_level_keys[i]}'" +
                    f" key nr. {j + 1} must be named " +
                    f"'{config_file_second_level_keys[i][j]}'!")
                req_type = config_file_data_types[i][j]
                if(type(value2) == req_type):
                    if(req_type is int and value2 < 0):
                        error_text = f"'{key2}' value must be greater than 0!"
                else:
                    error_text = f"Type of '{key2}' value must be {req_type.__name__}!"
                j += 1
            i += 1
        if(error_text is not None):
            print_mod.error(error_text)
            log_msg(__name__, "critical", error_text)
            quit()

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