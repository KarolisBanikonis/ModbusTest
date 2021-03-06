# Standard library imports
import importlib

# Local imports
from Libraries.SSHMethods import ssh_get_uci_hwinfo
from Libraries.Logger import log_msg
from Clients.SSHClient import SSHClient

class ModuleLoader:

    MODULES_DIRECTORY = "TestedModules."

    def __init__(self, modules_data, conn : SSHClient, print_mod):
        """
        Initializes ModuleLoader object.

            Parameters:
                modules_data (list): list of modules that should be loaded
                conn (SSHClient): module required to make connection to server
                print_mod (PrintModule): module designed for printing to terminal
        """
        self.conn = conn
        self.print_mod = print_mod
        self.modules_data = modules_data
        self.modules_to_load = []

    def check_hw_info(self):
        """Finds which tested modules should be loaded."""
        for module in self.modules_data:
            if(module['name'] == "ModuleSystem" or module['name'] == "ModuleWrite"):
                module_enabled = 1
            else:
                module_enabled = ssh_get_uci_hwinfo(self.conn, module['hw_info'], self.print_mod)
            if(module_enabled == 1):
                self.modules_to_load.append(module['name'])

    def init_modules(self, data, modbus, info, report):
        """
        Tries to initialize tested modules objects.

            Parameters:
                data (dict): registers data read from JSON format parameters file
                modbus (Modbus): module required to make connection to server via Modbus TCP
                info (InformationModule): module designed to monitor device's resources usage
                report (ReportModule): module designed to write test results to report file
            Returns:
                tested_modules (list): list of initialized tested modules
        """
        tested_modules = []
        self.check_hw_info()
        for module_name in self.modules_to_load:
            module = self.load_module(module_name)
            if(module != None):
                try:
                    class_ = getattr(module, module_name)
                    instance = class_(data[module_name], self.conn, modbus, info, report)
                    tested_modules.append(instance)
                    log_msg(__name__, "info", f"Class object {class_} was initialized!")
                except AttributeError as err:
                    warning_text = f"Such attribute does not exist: {err}"
                    self.print_mod.warning(warning_text)
                    log_msg(__name__, "warning", warning_text)
        return tested_modules

    def load_module(self, module_name):
        """
        Tries to load specified module.

            Parameters:
                module_name (str): module's that should be loaded name
            Returns:
                module (ModuleSystem|ModuleNetwork|ModuleMobile|ModuleGPS|ModuleWrite):
                    loaded module, if load was successful
                None, if load was not successful

        """
        module = None
        try:
            module = importlib.import_module(self.MODULES_DIRECTORY + module_name)
            log_msg(__name__, "info", f"Module {module.__name__} was loaded!")
            return module
        except ModuleNotFoundError:
            warning_text = f"Module {module_name} was not imported!"
            self.print_mod.warning(warning_text)
            log_msg(__name__, "warning", warning_text)
            return None