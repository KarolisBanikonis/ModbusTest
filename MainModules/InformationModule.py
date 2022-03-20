# Local imports
from Libraries.SSHMethods import get_df_used_memory, get_router_model, get_cpu_count, get_concrete_ubus_data
from Clients.SSHClient import SSHClient
from Libraries.DataMethods import get_numbers_in_string

class InformationModule:

    def __init__(self, conn : SSHClient, data):
        """
        Initializes InformationModule object.

            Parameters:
                conn (SSHClient): module required to make connection to server
                data (dict): data read from JSON format parameters file
        """
        self.data = data
        self.conn = conn
        self.tmp_used_memory = get_df_used_memory(self.conn, "/tmp")
        self.router_model = get_router_model(self.conn, self.data['Model'])
        self.cpu_count = get_cpu_count(self.conn)
        self.mem_used_at_start = self.get_used_memory()

    def get_used_memory(self, output_list=None):
        """
        Find amount of used memory.

            Parameters:
                print_status (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                used (int): amount of used memory
        """
        all_memories = get_concrete_ubus_data(self.conn, self.data['Memory'], output_list)
        total = all_memories['total'] - self.tmp_used_memory
        free = all_memories['free']
        used = total - free
        return used

    def get_cpu_usage(self, output_list=None):
        """
        Find percentage of CPU usage.

            Parameters:
                print_status (reprint.reprint.output.SignalList): list required for printing to terminal
            Returns:
                cpu_usage (str): CPU usage in percents
        """
        output = self.conn.ssh_issue_command("cat /proc/stat | grep 'cpu '", output_list)
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