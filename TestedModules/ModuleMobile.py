# Local imports
from MainModules.Module import Module
from Libraries.DataMethods import get_first_value_in_parenthesis, replace_modem_id, get_current_data_as_string
from MainModules.Logger import log_msg
from MainModules.MethodIsNotCallableError import MethodIsNotCallableError

class ModuleMobile(Module):

    def __init__(self, data, ssh, modbus, info, report):
        """
        Initializes ModuleMobile object.

            Parameters:
                data (dict): data read from JSON format parameters file
                ssh (SSHClient): module required to make connection to server via SSH
                modbus (Modbus): module required to make connection to server via Modbus TCP
                info (InformationModule): module designed to monitor device's resources usage
                report (ReportModule): module designed to write test results to report file
        """
        super().__init__(data, ssh, modbus, info, report, __class__.__name__)
        # self.dual_sim_status = ssh_get_uci_hwinfo(self.ssh, "dual_sim")
        # self.modem_id = get_modem_id(self.ssh, data['ModemId'], print_mod)
        self.change_data_with_modem_id()

    def change_data_with_modem_id(self):
        """
        Inserts found modem id to data's dictionary procedure parameter.
        """
        for data in self.data['SIM1']:
            data['procedure'] = replace_modem_id(data['procedure'], self.info.modem_id)
        if(self.info.dual_sim_status == 1):
            for data in self.data['SIM2']:
                data['procedure'] = replace_modem_id(data['procedure'], self.info.modem_id)

    def read_all_data(self, print_mod, test_count):
        """
        Performs all tests of ModuleMobile module.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
                test_count (list): list that saves values of total tests number, correct tests number and last memory usage
            Returns:
                unnamed (list): list that saves values of total tests number, correct tests number and last memory usage
        """
        log_msg(__name__, "info", f"Started {self.module_name} testing!")
        self.report.open_report()
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        self.memory = test_count[2]
        self.read_data(self.data['SIM1'], print_mod)
        if(self.info.dual_sim_status == 1):
            self.read_data(self.data['SIM2'], print_mod)
        self.report.close()
        log_msg(__name__, "info", f"Module - {self.module_name} tests are over!")
        return [self.total_number, self.correct_number, self.memory]

    def read_data(self, data_area, print_mod):
        """
        Performs tests for specified data area(SIM1 or SIM2).

            Parameters:
                data_area (dict): a part of data read from JSON format parameters file
                print_mod (PrintModule): module designed for printing to terminal
        """
        for i in range(len(data_area)):
            date = get_current_data_as_string()
            param_values = data_area[i]
            modbus_registers_data = self.modbus.read_registers(param_values, print_mod)
            method_name = f"get_modbus_and_device_data_register_count_{param_values['number']}"
            try:
                method = getattr(self, method_name)
                is_callable = callable(method)
                if(is_callable):
                    modbus_data, device_data = method(modbus_registers_data, param_values, print_mod)
                else:
                    raise MethodIsNotCallableError(f"Method '{str(method)}' is not callable!")
            except (AttributeError, MethodIsNotCallableError) as err:
                if(isinstance(err, AttributeError)):
                    warning_text = f"Such attribute does not exist: {err}"
                elif(isinstance(err, MethodIsNotCallableError)):
                    warning_text = err
                print_mod.warning(warning_text)
                log_msg(__name__, "warning", warning_text)
                continue
            results = self.check_if_results_match(modbus_data, device_data)
            self.change_test_count(results[2])
            past_memory = self.memory
            self.memory = self.info.get_used_memory(print_mod)
            cpu_usage = self.info.get_cpu_usage(print_mod)
            memory_difference = self.memory - past_memory
            total_mem_difference = self.info.mem_used_at_start - self.memory
            self.report.writer.writerow([date, self.total_number, self.module_name, param_values['name'], param_values['address'],
            results[0], results[1], results[2], self.READ_ACTION, cpu_usage, total_mem_difference, memory_difference])
            self.print_test_results(print_mod, param_values, results[0], results[1], cpu_usage, total_mem_difference)

    def get_modbus_and_device_data_register_count_16(self, modbus_registers_data, param_values, print_mod):
        """
        Finds converted received data via Modbus TCP and device data when read register count is 16

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (str): converted data received via Modbus TCP
                device_data (str): parsed data received via SSH
        """
        modbus_data = self.convert_modbus_to_text(modbus_registers_data)
        device_data = self.get_device_data(param_values, print_mod)
        if(param_values['address'] == 119):
            device_data = get_first_value_in_parenthesis(device_data)
        return modbus_data, device_data

    def get_modbus_and_device_data_register_count_1(self, modbus_registers_data, param_values, print_mod):
        """
        Finds converted received data via Modbus TCP and device data when read register count is 1

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int): parsed data received via SSH
        """
        modbus_data = self.convert_modbus_to_int_1(modbus_registers_data)
        device_data = self.get_device_data(param_values, print_mod)
        return f"{modbus_data}", f"{device_data}"

    def get_modbus_and_device_data_register_count_2(self, modbus_registers_data, param_values, print_mod):
        """
        Finds converted received data via Modbus TCP and device data when read register count is 2

            Parameters:
                modbus_registers_data (list): data that holds Modbus server's registers
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                modbus_data (int): converted data received via Modbus TCP
                device_data (int): parsed data received via SSH
        """
        modbus_data = self.convert_modbus_to_int_2(modbus_registers_data)
        device_data = self.get_device_data(param_values, print_mod)
        return modbus_data, device_data