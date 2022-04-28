# Standard library imports
import time

# Local imports
from MainModules.Module import Module
from Libraries.DataMethods import replace_pattern
from Libraries.Logger import log_msg
from Libraries.SSHMethods import get_mobile_apn, check_mobile_interface_service_status
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
        self.action = self.WRITE_ACTION
        self.sim = self.info.modbus_write_data['SIM']
        self.mobile_interface = ""
        self.sim_value_valid = self.check_if_sim_is_valid()
        self.mobile_connection = self.check_if_mobile_connection_exists()
        self.tests = self.check_what_tests_to_perform(data['Tests'])
        del self.data['Tests']
        if(self.sim_value_valid):
            self.change_data_to_mobile_interface()
        self.specified_apn = self.info.modbus_write_data['CHANGE_APN']
        self.default_apn = self.info.modbus_write_data['DEFAULT_APN']
        self.converted_specified_apn = self.convert_text_to_apn_command(self.specified_apn)
        self.converted_default_apn = self.convert_text_to_apn_command(self.default_apn)
        self.skip_interfaces = False
        self.RECONNECT_ATTEMPTS = 7
        self.SLEEP_TIME = 5

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
                self.mobile_interface = f"mob1s{self.sim}a1"
                log_msg(__name__, "info", "Specified default sim slot is valid!")
                return True
        log_msg(__name__, "error", "Specified default sim slot is invalid!")
        return False

    def check_if_mobile_connection_exists(self):
        """
        Checks if mobile interface has connection established.

            Returns:
                True, if mobile interface has connection established and sim slot is valid
                False, if mobile interface has not connection established
        """
        status = check_mobile_interface_service_status(self.ssh, self.mobile_interface)
        if(not status):
            log_msg(__name__, "error", f"Mobile interface '{self.mobile_interface}'" +
                " does not have internet connection!")
            return False
        if(self.sim_value_valid):
            return True
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
            if(bool(self.info.dual_sim_status) and test['dual_sim'] and self.mobile_connection):
                allowed_tests.append(test)
            elif(bool(self.info.mobile_status) and test['mobile'] and self.mobile_connection):
                allowed_tests.append(test)
            elif(not test['dual_sim'] and not test['mobile']):
                allowed_tests.append(test)
        log_msg(__name__, "info", f"Allowed write tests count: {len(allowed_tests)}.")
        return allowed_tests

    def convert_text_to_apn_command(self, text):
        """
        Converts text to information which is written with Modbus TCP

            Parameters:
                text (str): apn in text format
            Returns:
                apn_decimal (list): apn in decimal format
        """
        apn_decimal = convert_text_to_decimal(text)
        apn_decimal.insert(0, self.sim)
        return apn_decimal

    def change_data_to_mobile_interface(self):
        """
        Inserts mobile interface to tests and data dictionaries procedure parameter.
        """
        interface_pattern = "your_interface_name"
        for test in self.tests:
            if('service' in test.keys()):
                test['service'] = replace_pattern(test['service'], interface_pattern, self.mobile_interface)
        self.data['Status']['service'] = replace_pattern(self.data['Status']['service'],
            interface_pattern, self.mobile_interface)

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
                test_count (list): list that saves values of total tests number,
                    correct tests number and last memory usage
            Returns:
                (list): list that saves values of total tests number,
                    correct tests number and last memory usage
        """
        log_msg(__name__, "info", f"Started {self.module_name} testing!")
        self.total_number = test_count[0]
        self.correct_number = test_count[1]
        self.report.open_report()
        self.memory = test_count[2]
        for i in range(len(self.tests)):
            param_values = self.tests[i]
            # if(param_values['mobile']):
            #     status = get_mobile_interface_status(self.ssh, self.data['Status'])
            #     if(status is None):
            #         print_mod.warning(f"Mobile interface '{self.mobile_interface}'" +
            #             " does not have internet connection!")
            #         continue
            method_name = f"write_modbus_register_{param_values['address']}"
            first_time_changing_values = [True, False]
            self.skip_interfaces = False
            for first_time_change in first_time_changing_values:
                modbus_data, device_data = self.call_data_collect_method(method_name,
                    print_mod, first_time_change, param_values)
                if(modbus_data == self.DATA_COLLECT_FAIL):
                    continue
                self.check_and_write_test_results(modbus_data, device_data, print_mod, param_values)
        self.report.close()
        log_msg(__name__, "info", f"Module - {self.module_name} tests are over!")
        return [self.total_number, self.correct_number, self.memory]

    def wait_till_reconnect(self, connect_text, print_mod):
        """
        Checks if connection is reestablished specified amount of times.

            Parameters:
                connect_text (str): what message should be displayed while waiting for reconnection
                print_mod (PrintModule): module designed for printing to terminal
            Returns:
                True, if reconnection was established
                False, otherwise
        """
        try_connect_nr = 0
        while(try_connect_nr < self.RECONNECT_ATTEMPTS):
            try_connect_nr += 1
            connected = self.get_device_data(self.data['Status'], print_mod)
            if(not connected):
                error_text = (f"{connect_text} Reconnecting try nr." +
                    f" {try_connect_nr} out of {self.RECONNECT_ATTEMPTS}!")
                log_msg(__name__, "info", error_text)
                print_mod.warning(error_text)
                time.sleep(self.SLEEP_TIME)
            else:
                print_mod.clear_warning()
                return True
        return False

    def write_modbus_register_204(self, first_time_change, param_values, print_mod):
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
        # To perform test:
        #   1. Both mobile interfaces must be enabled (if device has two)
        #   2. Default interface must have established connection
        modbus_data = self.MODBUS_WRITE_ERROR
        device_data = None
        if(first_time_change):
            connected = self.get_device_data(param_values, print_mod)
            if(not connected):
                self.skip_interfaces = True
                return modbus_data, device_data
            write_value = 0
        else:
            if(self.skip_interfaces):
                return modbus_data, device_data
            write_value = 1
        written = self.modbus.write_one(print_mod, param_values['address'], write_value)
        if(written):
            modbus_data = f"{write_value}"
            if(not first_time_change):
                connect_text = "Waiting for mobile interface to reconnect."
                reconnected = self.wait_till_reconnect(connect_text, print_mod)
                if(reconnected):
                    device_data = "1"
            else:
                device_data = self.get_device_data(param_values, print_mod)
                device_data = f"{int(device_data)}"
        return modbus_data, device_data

    def write_modbus_register_205(self, first_time_change, param_values, print_mod): # Switch sim
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
        written = self.modbus.write_one(print_mod, param_values['address'], write_value)
        if(written):
            modbus_data = f"{write_value}"
            if(not first_time_change):
                connect_text = "Switching back to default SIM card!"
                self.wait_till_reconnect(connect_text, print_mod)
            device_data = f"{self.get_device_data(param_values, print_mod)}"
        return modbus_data, device_data

    def write_modbus_register_325(self, first_time_change, param_values, print_mod):
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

    def write_modbus_register_207(self, first_time_change, param_values, print_mod): # Switch APN
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
        # Auto APN must be disabled on mobile interface!
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
            # Wait for mobile connection before ending write tests
            if(not first_time_change):
                self.wait_till_reconnect(warning_text, print_mod)
            device_data = get_mobile_apn(self.ssh, print_mod, f"mob1s{self.sim}a1")
        return modbus_data, device_data