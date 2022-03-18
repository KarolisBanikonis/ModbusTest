# Standard library imports
import importlib
 
# Local imports
from Libraries.SSHMethods import ssh_get_uci_hwinfo
from Clients.SSHClient import SSHClient
from MainModules.Logger import init_logger

class ModuleLoader:

    MODULES_DIRECTORY = "TestedModules."

    def __init__(self, conf_module, conn : SSHClient):
        self.conn = conn
        self.modules_info = conf_module.get_data('MODULES')
        self.modules_to_load = []
        self.check_hw_info()
        self.logger = init_logger(__name__)
        
    def check_hw_info(self):
        for module_info in self.modules_info:
            if(module_info['name'] == "ModuleSystem"):
                module_enabled = 1
            else:
                module_enabled = ssh_get_uci_hwinfo(self.conn, module_info['hw_info'])
            if(module_enabled == 1):
                self.modules_to_load.append(module_info['name'])
        
    def init_modules(self, data, modbus, info, report):
        instantiated_modules = []
        for module_name in self.modules_to_load:
            module = self.__load_module(module_name)
            if(module != None):
                try:
                    class_ = getattr(module, module_name)
                    instance = class_(data[module_name], self.conn, modbus, info, report)
                    instantiated_modules.append(instance)
                    self.logger.info(f"Class object {class_} was instantiated!")
                except AttributeError as err:
                    print(f"Such attribute does not exist: {err}")
        return instantiated_modules

    def __load_module(self, module_name):
        module = None
        try:
            module = importlib.import_module(self.MODULES_DIRECTORY + module_name)
            self.logger.info(f"Module {module.__name__} was loaded!")
            return module
        except ModuleNotFoundError:
            print(f"Module {module_name} was not imported!")
            return None
            # close_all_instances() ssh, modbus