

from MainModules.JsonFileModule import JsonFileModule


class RegistersModule(JsonFileModule):

    def __init__(self, path_to_file):
        # super().__init__(path_to_file)
        self.data = self.read_json_file(path_to_file)

    