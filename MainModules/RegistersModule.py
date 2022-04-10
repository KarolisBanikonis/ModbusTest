from MainModules.JsonFileModule import JsonFileModule

class RegistersModule(JsonFileModule):

    def __init__(self, path_to_file, print_mod):
        """
        Initializes RegistersModule object.

            Parameters:
                path_to_file (str): path of registers file
                print_mod (PrintModule): module designed for printing to terminal
        """
        super().__init__(path_to_file, print_mod)

    def get_modules_data(self):
        """
        Gets list of modules that should be loaded.

            Returns:
                modules_data (list): list of modules that should be loaded
        """
        information_module_data = self.get_param(self.data, 'InformationModule')
        modules_data = self.get_param(information_module_data, 'ModulesToLoad')
        return modules_data