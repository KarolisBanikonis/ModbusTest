# Standard library imports
import time

# Local imports
from MainModules.Module import Module
from MainModules.Logger import log_msg
from MainModules.MethodIsNotCallableError import MethodIsNotCallableError

class ModuleWrite(Module):

    def __init__(self, data, ssh, modbus, info, report):
        """
        Initializes ModuleWrite object.

            Parameters:
                data (dict): data read from JSON format parameters file
                ssh (SSHClient): module required to make connection to server via SSH
                modbus (Modbus): module required to make connection to server via Modbus TCP
                info (InformationModule): module designed to monitor device's resources usage
                report (ReportModule): module designed to write test results to report file
        """
        super().__init__(data, ssh, modbus, info, report, __class__.__name__)
        self.decimal_apns = self.convert_multiple_texts_to_decimal(self.info.apn_list)
        self.sim = 1 # read sim and check if 1 or 2

    def check_mobile_ip(self, ubus_data):
        ip = None
        for interface in ubus_data:
            if(interface['interface'] == f"mob1s{self.sim}a1" or interface['interface'] == f"mob1s{self.sim}a1_4"):
                if(interface['up'] == True):
                    if(len(interface['ipv4-address']) != 0):
                        ip = interface['ipv4-address'][0]['address']
                        break
        return ip

    def convert_text_to_decimal(self, text):
        decimal_list = []
        for symbol in text:
            decimal_list.append(ord(symbol))
        return decimal_list

    def convert_multiple_texts_to_decimal(self, text_list):
        texts_decimal_list = []
        for text in text_list:
            text_decimal_list = self.convert_text_to_decimal(text)
            texts_decimal_list.append(text_decimal_list)
        return texts_decimal_list
            
    def get_mobile_interface_status(self, ubus_data, sim):
        status = False
        for interface in ubus_data:
            if(interface['interface'] == f"mob1s{sim}a1"): #_4?
                status = True
        return status

    # def get_mobile_apn_list(self, ubus_data):
    #     result = None
    #     for interface in ubus_data:
    #         if(interface['up'] == True and interface['interface'] == "mob1s1a1_4"):
    #             # if(len(interface['ipv4-address']) != 0):
    #             result = interface['data']['apn_list']
    #     apn_list = []
    #     for apn in result:
    #         apn_list.append(apn['apn'])
    #     return apn_list

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
            param_values = self.data[i]
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
                    # print_mod.warning(warning_text)
                    log_msg(__name__, "warning", warning_text)
                    continue
                results = self.check_if_results_match(modbus_data, device_data)
                self.change_test_count(results[2])
                past_memory = memory
                memory = self.info.get_used_memory(print_mod)
                cpu_usage = self.info.get_cpu_usage(print_mod)
                memory_difference = memory - past_memory
                total_mem_difference = self.info.mem_used_at_start - memory
                self.report.writer.writerow([self.total_number, self.module_name, param_values['name'], param_values['address'], results[0], results[1], results[2], '', cpu_usage, total_mem_difference, memory_difference])
                self.print_test_results(print_mod, param_values, results[0], results[1], cpu_usage, total_mem_difference)
        self.report.close()
        log_msg(__name__, "info", f"Module - {self.module_name} tests are over!")
        return [self.total_number, self.correct_number, memory]

    def set_modbus_default_apn(self, print_mod):
        written = self.modbus.write_many(print_mod, 207, [self.sim])
        return written

    def set_modbus_specified_apn(self, print_mod):
        apn = self.decimal_apns[0]
        apn.insert(0, self.sim)
        written = self.modbus.write_many(print_mod, 207, apn)
        return written

    def write_modbus_register_204(self, param_values, print_mod, first_time_change):
        # For turning off atleast one mobile interface has to have connection or both be enabled if bug happened
        # Bug - turn on interface through modbus
        # When bug happens, interface will never have apn set itself, nor it is possible to set it through modbus
        modbus_data = "Write error"
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
        
    def write_modbus_register_205(self, param_values, print_mod, first_time_change):
        modbus_data = "Write error"
        device_data = None
        if(first_time_change):
            write_value = 2
        else:
            write_value = 1
        written = self.modbus.write_one(print_mod, param_values['address'], write_value)
        device_data = f"{self.get_device_data(param_values, print_mod)}"
        #Better to read from modbus after write!!!
        if(written):
            modbus_data = f"{write_value}"
            device_data = f"{self.get_device_data(param_values, print_mod)}"
        if(not first_time_change):
            print_mod.warning("Switching SIM card!")
            time.sleep(10)
            print_mod.clear_warning()
        return modbus_data, device_data

    def write_modbus_register_325(self, param_values, print_mod, first_time_change):
        modbus_data = "Write error"
        device_data = None
        if(first_time_change):
            write_value = 0
        else:
            write_value = 1
        written = self.modbus.write_one(print_mod, param_values['address'], write_value)
        #Better to read from modbus after write!!!
        if(written):
            modbus_data = f"{write_value}"
            device_data = f"{self.get_device_data(param_values, print_mod)}"
        return modbus_data, device_data

    def write_modbus_register_207(self, param_values, print_mod, first_time_change):
        # To be able to change APN, Auto APN must be turned on!
        # modbus_data = "Write error"
        # device_data = None
        ip_before = "Write error"
        ip_after = None
        ubus_data_before = self.get_device_data(param_values, print_mod)
        ip_before = self.check_mobile_ip(ubus_data_before)
        if(ip_before is None):
            return "Write error", ip_after
        time.sleep(1)
        if(first_time_change):
            written = self.set_modbus_specified_apn(print_mod)
        else:
            written = self.set_modbus_default_apn(print_mod)
        # if(written):
        print_mod.warning("Configuring mobile connection with specified APN!")
        time.sleep(40)
        print_mod.clear_warning()
        ubus_data_after = self.get_device_data(param_values, print_mod)
        ip_after = self.check_mobile_ip(ubus_data_after)
        if(ip_before != ip_after):
            modbus_data = "APN Changed!"
            device_data = "APN Changed!"
        return ip_before, ip_after