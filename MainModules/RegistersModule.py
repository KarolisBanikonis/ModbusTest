

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