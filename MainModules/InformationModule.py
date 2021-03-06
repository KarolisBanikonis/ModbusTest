# Local imports
from Libraries.SSHMethods import get_df_used_memory, get_device_model
from Libraries.SSHMethods import get_device_json_ubus_data, ssh_get_uci_hwinfo, get_modem_id
from Libraries.DataMethods import get_numbers_in_string
from Clients.SSHClient import SSHClient

class InformationModule:

    def __init__(self, conn : SSHClient, data, print_mod, modbus_write_conf):
        """
        Initializes InformationModule object.

            Parameters:
                conn (SSHClient): module required to make connection to server
                data (dict): data read from JSON format parameters file
                print_mod (PrintModule): module designed for printing to terminal
                modbus_write_conf (dict): configuration information for writing with Modbus TCP
        """
        self.data = data
        self.conn = conn
        self.router_model = ""
        if(self.conn.setup_error is None):
            self.tmp_used_memory = get_df_used_memory(self.conn, "/tmp", print_mod)
            self.router_model = get_device_model(self.conn, self.data['Model'], print_mod)
            self.mem_used_at_start = self.get_used_memory(print_mod)
            #Required for ModuleMobile
            self.dual_sim_status = ssh_get_uci_hwinfo(self.conn, "dual_sim", print_mod)
            self.modem_id = get_modem_id(self.conn, data['ModemId'], print_mod)
            #Required for ModuleWrite
            self.mobile_status = ssh_get_uci_hwinfo(self.conn, "mobile", print_mod)
        self.modbus_write_data = modbus_write_conf
        self.sim = self.modbus_write_data['SIM']

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
        idle_time = all_state_times[3]
        total_time = sum(all_state_times)
        cpu_usage = 100.0 * (1.0 - idle_time / total_time)
        cpu_usage = round(cpu_usage, 3)
        return f"{cpu_usage}%"