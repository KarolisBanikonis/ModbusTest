# Local imports
from Libraries.FileMethods import read_file, generate_file_name, close_all_instances
from Libraries.SSHMethods import get_df_used_memory, get_router_model, get_cpu_count, get_parsed_ubus_data
from Clients.SSHClient import SSHClient
from Clients.Modbus import Modbus
from Libraries.CSVMethods import write_router_name_and_header

class ConfigurationModule:

    REPORTS_DIRECTORY = "Reports/"

    def __init__(self, file_path):
        self.data = read_file(file_path)
        self.ssh_client = SSHClient(self.get_all_data())
        self.connect_ssh()
        self.modbus = Modbus(self.get_all_data())
        self.connect_modbus()
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
            close_all_instances([self.ssh_client])

    def connect_modbus(self):
        modbus_is_setup_valid = self.modbus.setup_modbus()
        if(modbus_is_setup_valid == False):
            close_all_instances([self.ssh_client.ssh, self.modbus.client])

    # def get_all_info(self, data):
    #     parsed_data = get_parsed_ubus_data(self.ssh_client, data)
    #     all_info = parsed_data[data['parse']]
    #     return all_info

    # def get_memory(self, data, type):
    #     all_info = self.get_all_info(data)
    #     return all_info[type]


    