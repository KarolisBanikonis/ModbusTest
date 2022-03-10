from Libraries.SSHMethods import get_df_used_memory, get_router_model, get_cpu_count, get_concrete_ubus_data
from Clients.SSHClient import SSHClient

class InformationModule:

    def __init__(self, conn : SSHClient, data):
        self.data = data
        self.conn = conn
        self.tmp_used_memory = get_df_used_memory(self.conn, "/tmp")
        self.router_model = get_router_model(self.conn, self.data['Model'])
        self.cpu_count = get_cpu_count(self.conn)
        self.mem_used_at_start = self.get_used_memory()

    def get_used_memory(self, print_status=None):
        all_memories = get_concrete_ubus_data(self.conn, self.data['Memory'], print_status)
        total = all_memories['total'] - self.tmp_used_memory
        free = all_memories['free']
        used = total - free
        return used

    # def get_cpu_usage(self):
    #     cpu_idle = self.conn.ssh_issue_command("top n1 | grep idle | cut -c 33-35")
    #     cpu_usage = 100 - int(cpu_idle)
    #     return f"{cpu_usage}%"

    def get_cpu_usage(self, print_status=None):
        output = self.conn.ssh_issue_command("cat /proc/stat | grep 'cpu '", print_status)
        all_state_times = [int(s) for s in output.split() if s.isdigit()]
        idle_time = all_state_times[3] # CIA NULUZTA
        total_time = sum(all_state_times)
        cpu_usage = 100.0 * (1.0 - idle_time / total_time)
        cpu_usage = round(cpu_usage, 3)
        return f"{cpu_usage}%"