# Local imports
from Libraries.FileMethods import read_file, generate_file_name
from Libraries.SSHMethods import get_df_used_memory, get_router_model, get_cpu_count, get_parsed_ubus_data
from Clients.SSHClient import SSHClient
from Libraries.CSVMethods import write_router_name_and_header

class ConfigurationModule:

    REPORTS_DIRECTORY = "Reports/"

    def __init__(self, file_path):
        self.data = read_file(file_path)
        self.ssh_client = SSHClient(self.get_all_data())
        self.connect_ssh()
        self.tmp_used_memory = get_df_used_memory(self.ssh_client, "/tmp")
        print(f"{self.tmp_used_memory}")
        self.router_model = get_router_model(self.ssh_client, self.get_data('MODEL'))
        self.cpu_count = get_cpu_count(self.ssh_client)
        self.report_file = f"{self.REPORTS_DIRECTORY}{generate_file_name(self.router_model)}.csv"
        write_router_name_and_header(self.report_file, self.router_model)

    def get_data(self, request_data):
        return self.data['Settings'][0][request_data]

    def get_all_data(self):
        return self.data['Settings'][0]

    def connect_ssh(self):
        ssh_connected = self.ssh_client.ssh_connect()
        if(ssh_connected == False):
            print("SSH FAILED!") # Exception

    # def get_all_info(self, data):
    #     parsed_data = get_parsed_ubus_data(self.ssh_client, data)
    #     all_info = parsed_data[data['parse']]
    #     return all_info

    # def get_memory(self, data, type):
    #     all_info = self.get_all_info(data)
    #     return all_info[type]


    