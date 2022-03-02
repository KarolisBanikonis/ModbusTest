# Standard library imports
import importlib
 
# Local imports
from Libraries.SSHMethods import ssh_get_uci_hwinfo, try_enable_gps
from Clients.SSHClient import SSHClient

class ModuleLoader:

    MODULES_DIRECTORY = "DataModules."

    def __init__(self, connection: SSHClient, modules_info):
        self.connection = connection
        self.modules_info = modules_info
        self.modules_to_load = []
        self.check_hw_info()
        
    def check_hw_info(self):
        for module_info in self.modules_info:
            if(module_info['name'] == "ModuleSystem"):
                module_enabled = "1"
            else:
                module_enabled = ssh_get_uci_hwinfo(self.connection, module_info['parse'])
                if(module_info['name'] == "ModuleGPS" and module_enabled == "1"):
                    try_enable_gps(self.connection)
            if(module_enabled == "1"):
                self.modules_to_load.append(module_info['name'])
        
    def init_modules(self, csv_file_name, modbus, data):
        instantiated_modules = []
        for module_name in self.modules_to_load:
            module = self.__load_module(module_name)
            if(module != None):
                class_ = getattr(module, module_name)
                instance = class_(csv_file_name, modbus, data[module_name], self.connection)
                instantiated_modules.append(instance)
        return instantiated_modules

    def __load_module(self, module_name):
        module = None
        try:
            module = importlib.import_module(self.MODULES_DIRECTORY + module_name)
            return module
        except ModuleNotFoundError:
            print(f"Module {module_name} was not imported!")
            return None
            # close_all_instances() ssh, modbus