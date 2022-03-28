# Standard library imports
import time

# Local imports
from MainModules.Module import Module
from Libraries.DataMethods import get_current_data_as_string
from MainModules.Logger import log_msg
from MainModules.MethodIsNotCallableError import MethodIsNotCallableError
from Libraries.SSHMethods import get_mobile_apn
from Libraries.ConversionMethods import convert_text_to_decimal

class ModuleWrite(Module):

    def __init__(self, data, ssh, modbus, info, report):
        """
        Initializes ModuleWrite object.

            Parameters:
                data (list): data read from JSON format parameters file
                ssh (SSHClient): module required to make connection to server via SSH
                modbus (Modbus): module required to make connection to server via Modbus TCP
                info (InformationModule): module designed to monitor device's resources usage
                report (ReportModule): module designed to write test results to report file
        """
        super().__init__(data, ssh, modbus, info, report, __class__.__name__)
        self.data = self.check_what_tests_to_perform(data)
        self.sim = self.info.modbus_write_data['sim']
        self.sim_value_valid = self.check_if_sim_is_valid()
        self.specified_apn = self.info.modbus_write_data['apn']
        self.default_apn = self.info.modbus_write_data['default']
        self.converted_specified_apn = self.convert_text_to_apn_command(self.specified_apn)
        self.converted_default_apn = self.convert_text_to_apn_command(self.default_apn)

    def __get_possible_sim_values(self):
        """
        Finds what possible values could acquire a default sim slot.

            Returns:
                possible_sim_values (list): a list of possible sim slot's values
        """
        possible_sim_values = []
        if(bool(self.info.mobile_status)):
            possible_sim_values.append(1)
            if(bool(self.info.dual_sim_status)):
                possible_sim_values.append(2)
        return possible_sim_values

    def check_if_sim_is_valid(self):
        """
        Checks if specified default sim slot is valid.

            Returns:
                True, if specified default sim slot's value is valid
                False, if specified default sim slot's value is invalid
        """
        possible_sim_values = self.__get_possible_sim_values()
        for value in possible_sim_values:
            if(self.sim == value):
                log_msg(__name__, "info", f"Specified default sim slot is valid!")
                return True
        log_msg(__name__, "error", f"Specified default sim slot is invalid!")
        return False

    def check_what_tests_to_perform(self, list_of_tests):
        """
        Checks which tests should be run.

            Parameters:
                list_of_tests (list): a list of all possible tests
            Returns:
                allowed_tests (list): a list of tests that can be run
        """
        allowed_tests = []
        for test in list_of_tests:
            if(bool(self.info.dual_sim_status) and test['dual_sim']):
                allowed_tests.append(test)
            elif(bool(self.info.mobile_status) and test['mobile']):
                allowed_tests.append(test)
            elif(not test['dual_sim'] and not test['mobile']):
                allowed_tests.append(test)
        log_msg(__name__, "info", f"Allowed write tests count: {len(allowed_tests)}.")
        return allowed_tests

    def convert_text_to_apn_command(self, text):
        apn_decimal = convert_text_to_decimal(text)
        apn_decimal.insert(0, self.sim)
        return apn_decimal

    def get_opposite_sim(self):
        """
        Get opposite sim value.

            Returns:
                1, if default sim slot is set to 2
                2, if default sim slot is set to 1
        """
        if(self.sim == 1):
            return 2
        elif(self.sim == 2):
            return 1

    def read_all_data(self, print_mod, test_count):
        """
        Performs all tests of ModuleWrite module.

            Parameters:
                print_mod (PrintModule): module designed for printing to terminal
                test_count (list): list that saves values of total tests number, correct tests number and last memory usage
            Returns:
                (list): list that saves values of total tests number, correct tests number and last memory usage
        """
        log_msg(__name__, "info", f"Started {self.module_name} testing!")
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        self.report.open_report()
        memory = test_count[2]
        for i in range(len(self.data)):
            date = get_current_data_as_string()
            param_values = self.data[i]
            if((param_values['mobile'] or param_values['dual_sim']) and not self.sim_value_valid):
                print_mod.warning("Default SIM slot value is invalid!")
                continue
            method_name = f"write_modbus_register_{param_values['address']}"
            first_time_changing_values = [True, False]
            for first_time_change in first_time_changing_values:
                try:
                    method = getattr(self, method_name)
                    is_callable = callable(method)
                    if(is_callable):
                        modbus_data, device_data = method(param_values, print_mod, first_time_change)
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
                past_memory = memory
                memory = self.info.get_used_memory(print_mod)
                cpu_usage = self.info.get_cpu_usage(print_mod)
                memory_difference = memory - past_memory
                total_mem_difference = self.info.mem_used_at_start - memory
                self.report.writer.writerow([date, self.total_number, self.module_name, param_values['name'], param_values['address'],
                results[0], results[1], results[2], self.WRITE_ACTION, cpu_usage, total_mem_difference, memory_difference])
                self.print_test_results(print_mod, param_values, results[0], results[1], cpu_usage, total_mem_difference)
        self.report.close()
        log_msg(__name__, "info", f"Module - {self.module_name} tests are over!")
        return [self.total_number, self.correct_number, memory]

    def write_modbus_register_204(self, param_values, print_mod, first_time_change):
        """
        Turns on/off mobile interfaces with Modbus TCP and receives converted device data via SSH

            Parameters:
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
                first_time_change (bool): is writing performed first time
            Returns:
                modbus_data (str): what data was written with Modbus TCP
                device_data (str): parsed data received via SSH
        """
        # Test will fail if atlest one mobile interface is disabled
        modbus_data = self.MODBUS_WRITE_ERROR
        device_data = None
        if(first_time_change):
            write_value = 0
        else:
            write_value = 1
        written = self.modbus.write_one(print_mod, param_values['address'], write_value)
        if(written):
            modbus_data = f"{write_value}"
            if(not first_time_change):
                print_mod.warning("Waiting for mobile interface to change status.")
                time.sleep(15)
                print_mod.clear_warning()
            device_data = self.get_device_data(param_values, print_mod)
            device_data = f"{int(device_data)}"
        return modbus_data, device_data
        
    def write_modbus_register_205(self, param_values, print_mod, first_time_change): # Switch sim
        """
        Switches default sim slot with Modbus TCP and receives converted device data via SSH

            Parameters:
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
                first_time_change (bool): is writing performed first time
            Returns:
                modbus_data (str): what data was written with Modbus TCP
                device_data (str): parsed data received via SSH
        """
        modbus_data = self.MODBUS_WRITE_ERROR
        device_data = None
        if(first_time_change):
            write_value = self.get_opposite_sim()
        else:
            write_value = self.sim
        # time.sleep(5)
        written = self.modbus.write_one(print_mod, param_values['address'], write_value)
        device_data = f"{self.get_device_data(param_values, print_mod)}"
        if(written):
            modbus_data = f"{write_value}"
            device_data = f"{self.get_device_data(param_values, print_mod)}"
        if(not first_time_change):
            print_mod.warning("Switching back to default SIM card!")
            time.sleep(15)
            print_mod.clear_warning()
        return modbus_data, device_data

    def write_modbus_register_325(self, param_values, print_mod, first_time_change):
        """
        Switches PIN4 state with Modbus TCP and receives converted device data via SSH

            Parameters:
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
                first_time_change (bool): is writing performed first time
            Returns:
                modbus_data (str): what data was written with Modbus TCP
                device_data (str): parsed data received via SSH
        """
        modbus_data = self.MODBUS_WRITE_ERROR
        device_data = None
        if(first_time_change):
            write_value = 0
        else:
            write_value = 1
        written = self.modbus.write_one(print_mod, param_values['address'], write_value)
        if(written):
            modbus_data = f"{write_value}"
            device_data = f"{self.get_device_data(param_values, print_mod)}"
        return modbus_data, device_data

    def write_modbus_register_207(self, param_values, print_mod, first_time_change): # Switch APN
        """
        Switches mobile interface's APN with Modbus TCP and receives converted device data via SSH

            Parameters:
                param_values (dict): current register's parameters information
                print_mod (PrintModule): module designed for printing to terminal
                first_time_change (bool): is writing performed first time
            Returns:
                modbus_data (str): what data was written with Modbus TCP
                device_data (str): parsed data received via SSH
        """
        modbus_data = self.MODBUS_WRITE_ERROR
        device_data = None
        if(first_time_change):
            converted_apn = self.converted_specified_apn
            apn = self.specified_apn
            warning_text = "Configuring mobile connection with specified APN!"
        else:
            converted_apn = self.converted_default_apn
            apn = self.default_apn
            warning_text = "Configuring mobile connection with default APN!"
        written = self.modbus.write_many(print_mod, param_values['address'], converted_apn)
        if(written):
            modbus_data = apn
            print_mod.warning(warning_text)
            time.sleep(40)
            print_mod.clear_warning()
            device_data = get_mobile_apn(self.ssh, print_mod, f"mob1s{self.sim}a1")
        return modbus_data, device_data