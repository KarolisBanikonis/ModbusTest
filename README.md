# ModbusTest

Modbus TCP protocol's testing program

This program is used to test devices which use embedded operating system OpenWRT. Program compares value that is acquired with Modbus TCP protocol and actual value that is stored in the device and decides if gained value is correct.

To start a program you need to configure configuration file "config.json", then execute "Main.py" file.

Configuration file have three sections: "Settings", "FTP" and "Email".

"Settings" section:

    "SERVER_HOST" - what address Modbus TCP and SSH should connect to.
    "MODBUS_PORT" - what port Modbus TCP should use.
    "USERNAME" - login credential used by SSH protocol.
    "PASSWORD" - login credential used by SSH protocol.
    "RECONNECT_ATTEMPTS" - how many times program should try re-establish connection when it is lost.
    "TIMEOUT" - how long program should wait in seconds between attempts to reconnect.
    "MODULES" - what modules should be tested, according to subsystems that are enabled.

Typically, you should not change "MODULES" values. Be cautious that, module names must match file names without extention in /TestedModules directory.

"FTP" section:

    "FTP_USE" - should program store reports in FTP server. Write "Yes" to enable it.
    "FTP_HOST" - what address FTP should connect to.
    "FTP_PORT" - what port FTP should use.
    "FTP_USER" - what username FTP should use to login.
    "FTP_PASSWORD" - what password FTP should use to login.
    "INTERVAL_MINUTES" - at what interval in minutes program should upload report to FTP server.

"Email" section:

    "EMAIL_USE" - should program send emails with test summary. Write "Yes" to enable it.
    "PORT" - what port SMTP should use.
    "SMTP" - what SMTP server should be used.
    "USER" - what username should be used to login to sender's email account.
    "PASSWORD" - what password should be used to login to sender's email account.
    "RECEIVER" - who should receive emails.
    "INTERVAL_HOURS" - at what interval in hours program should send test summaries by email.

Program functionality:

    Program can evaluate which subsystems are enabled and load only required modules.
    Program can get values using Modbus TCP protocol.
    Program can convert acquired values to human readable values.
    Program can connect to testing device with SSH protocol.
    Program can decide if acquired value by Modbus TCP protocol is correct.
    Program can measure current CPU usage.
    Program can measure current RAM usage.
    Program shows current test proccess in the command line.
    Program generates a report in CSV format, which would have all test results stored.
    Program is able to store a report in FTP server.
    Program can update report in FTP server periodically at a set amount of minutes.
    Program can send email periodically at a set amount of hours.