from Libraries.SSHMethods import get_df_used_memory, get_router_model, get_cpu_count, get_concrete_ubus_data
from Clients.SSHClient import SSHClient

class InformationModule:

    # REPORTS_DIRECTORY = "Reports/"

    def __init__(self, conn : SSHClient, conf):
        self.conf = conf
        self.conn = conn
        self.tmp_used_memory = get_df_used_memory(self.conn, "/tmp")
        self.router_model = get_router_model(self.conn, self.conf.get_data('MODEL'))
        self.cpu_count = get_cpu_count(self.conn)
        # self.report_file = f"{self.REPORTS_DIRECTORY}{generate_file_name(self.router_model)}.csv"
        # write_router_name_and_header(self.report_file, self.router_model)

    def get_used_memory(self):
        all_memories = get_concrete_ubus_data(self.conn ,self.conf.get_data('MEMORY'))
        total = all_memories['total'] - self.tmp_used_memory
        free = all_memories['free']
        used = total - free
        return used

    # def get_cpu_usage(self):
    #     cpu_idle = self.conn.ssh_issue_command("top n1 | grep idle | cut -c 33-35")
    #     cpu_usage = 100 - int(cpu_idle)
    #     return f"{cpu_usage}%"

    def get_cpu_usage(self):
        output = self.conn.ssh_issue_command("cat /proc/stat | grep 'cpu '")
        all_state_times = [int(s) for s in output.split() if s.isdigit()]
        idle_time = all_state_times[3]
        total_time = sum(all_state_times)
        cpu_usage = 100.0 * (1.0 - idle_time / total_time)
        return f"{cpu_usage}%"

    # def get_cpu_usage(self):
    #     all_loads = self.get_all_info(self.get_data('LOAD'))
    #     min1_load = all_loads[0] * 100 / self.cpu_count
    #     if(min1_load > 100):
    #         min1_load = 100
    #     return f"{min1_load}%"