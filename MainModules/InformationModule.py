# Local imports
from Libraries.SSHMethods import get_df_used_memory, get_device_model, get_cpu_count, get_device_json_ubus_data, ssh_get_uci_hwinfo, get_modem_id
from Clients.SSHClient import SSHClient
from Libraries.DataMethods import get_numbers_in_string

class InformationModule:

    def __init__(self, conn : SSHClient, data, print_mod):
        """
        Initializes InformationModule object.

            Parameters:
                conn (SSHClient): module required to make connection to server
                data (dict): data read from JSON format parameters file
                print_mod (PrintModule): module designed for printing to terminal
        """
        self.data = data
        self.conn = conn
        self.tmp_used_memory = get_df_used_memory(self.conn, "/tmp", print_mod)
        self.router_model = get_device_model(self.conn, self.data['Model'], print_mod)
        self.cpu_count = get_cpu_count(self.conn, print_mod)
        self.mem_used_at_start = self.get_used_memory(print_mod)
        #Required for ModuleMobile
        self.dual_sim_status = ssh_get_uci_hwinfo(self.conn, "dual_sim", print_mod)
        self.modem_id = get_modem_id(self.conn, data['ModemId'], print_mod)
        #Required for ModuleWrite
        self.modbus_write_data = data['ModbusWrite']
        self.mobile_status = ssh_get_uci_hwinfo(self.conn, "mobile", print_mod)
        self.sim = self.modbus_write_data['sim']

    def get_used_memory(self, print_mod):
        """
        Find amount of used memory.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                used (int): amount of used memory
        """
        json_data = get_device_json_ubus_data(self.conn, self.data['Memory'], print_mod)
        all_memories = json_data[self.data['Memory']['parse']]
        total = all_memories['total'] - self.tmp_used_memory
        free = all_memories['free']
        used = total - free
        return used

    def get_cpu_usage(self, print_mod):
        """
        Find percentage of CPU usage.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                cpu_usage (str): CPU usage in percents
        """
        output = self.conn.ssh_issue_command("cat /proc/stat | grep 'cpu '", print_mod)
        all_state_times = get_numbers_in_string(output)
        idle_time = all_state_times[3] # CIA NULUZTA
        total_time = sum(all_state_times)
        cpu_usage = 100.0 * (1.0 - idle_time / total_time)
        cpu_usage = round(cpu_usage, 3)
        return f"{cpu_usage}%"

    # def get_cpu_usage(self):
    #     cpu_idle = self.conn.ssh_issue_command("top n1 | grep idle | cut -c 33-35")
    #     cpu_usage = 100 - int(cpu_idle)
    #     return f"{cpu_usage}%"