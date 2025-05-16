# Import required libraries
from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from paramiko.ssh_exception import AuthenticationException
from flask import Flask, render_template, request
import logging

# Enable debugging logs for Netmiko
#logging.basicConfig(filename='netmiko_debug.log', level=logging.DEBUG)

# Initialize Flask application
app = Flask(__name__)

# Route: Home page
@app.route('/')
def index():
    # Render the initial HTML form for user input
    return render_template('specter_pre.html', name='specter')

# Route: Form submission handler
@app.route('/submit', methods=['POST'])
def submit():
    # Lists to hold golden (expected) configurations and ACLs
    golden_standard = []
    golden_acl1_standard = []
    golden_acl2_standard = []
    golden_acl5_standard = []
    golden_acl55_standard = []

    # Read bulk configuration commands to push to devices (show commands)
    with open('golden/bulk_config_file.txt') as f:
        bulk_config = f.read().splitlines()

    # Read golden STIG and ACL configuration templates
    with open('golden/golden_stig_file.txt', 'r') as f:
        for line in f.readlines():
            golden_standard.append([line.strip(), 'false'])

    with open('golden/golden_acl1_file.txt') as f:
        for line in f.readlines():
            golden_acl1_standard.append([line.strip(), 'false'])

    with open('golden/golden_acl2_file.txt') as f:
        for line in f.readlines():
            golden_acl2_standard.append([line.strip(), 'false'])

    with open('golden/golden_acl5_file.txt') as f:
        for line in f.readlines():
            golden_acl5_standard.append([line.strip(), 'false'])

    with open('golden/golden_acl55_file.txt') as f:
        for line in f.readlines():
            golden_acl55_standard.append([line.strip(), 'false'])

    # Get form input: list of IPs, credentials, enable secret from html document
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

        # Connecting to the device and then goes into global configuration, sends the commands from the file and then prints the output
        try:
            # Establish connection to the device
            net_connect = ConnectHandler(**ios_device, verbose=True)
            net_connect.enable()    
            # Send show commands and capture ACL outputs       
            running_config = net_connect.send_config_set(bulk_config)
            running_acl1 = net_connect.send_command("show access-list 1")
            running_acl2 = net_connect.send_command("show access-list 2")
            running_acl5 = net_connect.send_command("show access-list 5")
            running_acl55 = net_connect.send_command("show access-list 55")
        # Handle possible connection/authentication exceptions
        except (AuthenticationException):
            print('Authentication failure ' + devices)
            continue
        except (NetMikoTimeoutException):
            print('Timeout to device ' + devices)
            continue
        except (EOFError):
            print('End of file while attempting device ' + devices)
            continue
        except (SSHException):
            print('SSH Issue. Are you sure SSH is enabled? ' + devices)
            continue
        except Exception as unknown_error:
            print('Some other error ' + str(unknown_error))
            continue

        print("\n\n\n")
        #print(running_acl1)
        #print("\n\n\n")
        
        # Validate STIG configuration commands
        missing_commands = []

        for output in golden_standard:
            if output[0] == r"path flash:/archived_configs" or output[0] == r"path bootflash:/archived_configs":
                output[1] = 'true'
            elif output[0] in running_config:
                output[1] = 'true'
            else:
                missing_commands.append(output[0])

        if missing_commands:
            missing_commands.insert(0, "//////// Missing the following commands \\\\\\\\\\\\\\\\")
            for command in missing_commands:
                print(command)

        # Functionality repeated for each ACL: clean up output and compare
        print("\n")
        missing_acl1 = []
        replace_acl1 = running_acl1.replace(", wildcard bits", "")

        for output in golden_acl1_standard:
            if output[0] == r"ip access-list standard 1" or output[0] == r"Standard IP access list 1":
                output[1] = 'true'
            elif output[0] in replace_acl1:
                output[1] = 'true'
            else:
                missing_acl1.append(output[0])

        if missing_acl1:
            missing_acl1.insert(0, "\n\n//////// Missing the following from ACL 1 \\\\\\\\\\\\\\\\")
            for command in missing_acl1:
                print(command)

        print("\n")
        missing_acl2 =[]
        replace_acl2 = running_acl2.replace(", wildcard bits", "")

        for output in golden_acl2_standard:
            if output[0] == r"ip access-list standard 2" or output[0] == r"Standard IP access list 2":
                output[1] = 'true'
            elif output[0] in replace_acl2:
                output[1] = 'true'
            else:
                missing_acl2.append(output[0])

        if missing_acl2:
            missing_acl2.insert(0, "\n\n//////// Missing the following from ACL 2 \\\\\\\\\\\\\\\\")
            for commnad in missing_acl2:
                print(commnad)

        print("\n")
        missing_acl5 = []
        replace_acl5 = running_acl5.replace(", wildcard bits", "")

        for output in golden_acl5_standard:
            if output[0] == r"ip access-list standard 5" or output[0] == r"Standard IP access list 5":
                output[1] = 'true'
            elif output[0] in replace_acl5:
                output[1] = 'true'
            else:
                missing_acl5.append(output[0])

        if missing_acl5:
            missing_acl5.insert(0, "\n\n//////// Missing the following from ACL 5 \\\\\\\\\\\\\\\\")
            for command in missing_acl5:
                print(command)


        print("\n")
        missing_acl55 = []
        replace_acl55 = running_acl55.replace(", wildcard bits", "")

        for output in golden_acl55_standard:
            if output[0] == r"ip access-list standard 55" or output[0] == r"Standard IP access list 55":
                output[1] = 'true'
            elif output[0] in replace_acl55:
                output[1] = 'true'
            else:
                missing_acl55.append(output[0])

        if missing_acl55:    
            missing_acl55.insert(0, "\n\n//////// Missing the following from ACL 55 \\\\\\\\\\\\\\\\")        
            for command in missing_acl55:
                print(command)

        # Combines all outputs into a single variable
        stig_compliant_check = missing_commands + missing_acl1 + missing_acl2 + missing_acl5 + missing_acl55

        # Determine STIG compliance
        if not stig_compliant_check:
            result = "Device is STIG compliant"
        else:
            result = "Device is not STIG compliant, revisit the IOS_Template and check again\nThe device is missing the following commands\n\n"
            result += "\n".join(stig_compliant_check)
    
        # Return results to web interface
        return render_template('specter_post.html', name='SPECTER', result=result)
    
            
if __name__ == '__main__':
    app.run(debug=True)
