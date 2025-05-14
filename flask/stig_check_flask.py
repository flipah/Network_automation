# Import required libraries
from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException, AuthenticationException
from getpass import getpass
from flask import Flask, render_template, request
import logging

# Enable debugging logs for Netmiko
logging.basicConfig(filename='netmiko_debug.log', level=logging.DEBUG)

# Initialize Flask application
app = Flask(__name__)

# Route: Home page
@app.route('/')
def index():
    # Render the initial HTML form for user input
    return render_template('specter_pre.html', name='SPECTER')

# Route: Form submission handler
@app.route('/submit', methods=['POST'])
def submit():
    # Lists to hold golden (expected) configurations and ACLs
    golden_standard = []
    golden_acl1_standard = []
    golden_acl2_standard = []
    golden_acl5_standard = []
    golden_acl55_standard = []

    # Read bulk configuration commands to push to devices
    with open('bulk_config_file.txt') as f:
        bulk_config = f.read().splitlines()

    # Read golden STIG and ACL configuration templates
    with open('golden_stig_file.txt', 'r') as f:
        for line in f.readlines():
            golden_standard.append([line.strip(), 'false'])

    with open('golden_acl1_file.txt') as f:
        for line in f.readlines():
            golden_acl1_standard.append([line.strip(), 'false'])

    with open('golden_acl2_file.txt') as f:
        for line in f.readlines():
            golden_acl2_standard.append([line.strip(), 'false'])

    with open('golden_acl5_file.txt') as f:
        for line in f.readlines():
            golden_acl5_standard.append([line.strip(), 'false'])

    with open('golden_acl55_file.txt') as f:
        for line in f.readlines():
            golden_acl55_standard.append([line.strip(), 'false'])

    # Get form input: list of IPs, credentials, enable secret
    ip_addrs = request.form.getlist('ip_addrs')
    username = request.form['username']
    password = request.form['password']
    en_secret = request.form['en_secret']

    # Loop through each IP address to connect and validate config
    for devices in ip_addrs:
        print('Connecting to ' + devices)
        ios_device = {
            'device_type': 'cisco_ios',
            'ip': devices,
            'username': username,
            'password': password,
            'secret': en_secret,
            'read_timeout_override': 120,
        }

        try:
            # Establish connection to the device
            net_connect = ConnectHandler(**ios_device, verbose=True)
            net_connect.enable()

            # Send config commands and capture ACL outputs
            running_config = net_connect.send_config_set(bulk_config)
            running_acl1 = net_connect.send_command("show access-list 1")
            running_acl2 = net_connect.send_command("show access-list 2")
            running_acl5 = net_connect.send_command("show access-list 5")
            running_acl55 = net_connect.send_command("show access-list 55")

        # Handle possible connection/authentication exceptions
        except AuthenticationException:
            print('Authentication failure ' + devices)
            continue
        except NetMikoTimeoutException:
            print('Timeout to device ' + devices)
            continue
        except EOFError:
            print('End of file while attempting device ' + devices)
            continue
        except SSHException:
            print('SSH Issue. Are you sure SSH is enabled? ' + devices)
            continue
        except Exception as unknown_error:
            print('Some other error ' + str(unknown_error))
            continue

        print("\n\n\n")

        # Validate STIG configuration commands
        missing_commands = []
        for output in golden_standard:
            if output[0] in [r"path flash:/archived_configs", r"path bootflash:/archived_configs"]:
                output[1] = 'true'
            elif output[0] in running_config:
                output[1] = 'true'
            else:
                missing_commands.append(output[0])

        if missing_commands:
            print("//////// Missing the following commands \\\\\\\\\\\\\\\\")
            for command in missing_commands:
                print(command)

        # Functionality repeated for each ACL: clean up output and compare
        def check_acl(acl_output, golden_acl_list, acl_num):
            missing_acl = []
            cleaned_acl = acl_output.replace(", wildcard bits", "")
            acl_entries = []

            for x in range(len(acl_entries)):
                acl_entries[x] = acl_entries[x].lstrip('0123456789').strip()
                if acl_entries[x].endswith(')'):
                    acl_entries[x] = acl_entries[x].split('(')[0].strip()

            for entry in golden_acl_list:
                if entry[0] in [f"ip access-list standard {acl_num}", f"Standard IP access list {acl_num}"]:
                    entry[1] = 'true'
                elif entry[0] in cleaned_acl:
                    entry[1] = 'true'
                else:
                    missing_acl.append(entry[0])

            if missing_acl:
                print(f"//////// Missing the following from ACL {acl_num} \\\\\\\\\\\\\\\\")
                for command in missing_acl:
                    print(command)

            return missing_acl

        # Run ACL checks
        missing_acl1 = check_acl(running_acl1, golden_acl1_standard, 1)
        missing_acl2 = check_acl(running_acl2, golden_acl2_standard, 2)
        missing_acl5 = check_acl(running_acl5, golden_acl5_standard, 5)
        missing_acl55 = check_acl(running_acl55, golden_acl55_standard, 55)

        # Determine STIG compliance
        stig_compliant_check = missing_commands + missing_acl1 + missing_acl2 + missing_acl5 + missing_acl55

        if not stig_compliant_check:
            result = "Device is STIG compliant"
        else:
            result = "Device is not STIG compliant, revisit the IOS_Template and check again\n"
            result += "\n".join(stig_compliant_check)
    
        # Return results to web interface
        return render_template('specter_post.html', name='SPECTER', result=result)

# Entry point for the Flask app
if __name__ == '__main__':
    app.run(debug=True)
