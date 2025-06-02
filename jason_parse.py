# Import required libraries
from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from paramiko.ssh_exception import AuthenticationException
from flask import Flask, render_template, request
import logging
import json
import re

# Enable debugging logs for Netmiko
#logging.basicConfig(filename='netmiko_debug.log', level=logging.DEBUG)

# Initialize Flask application
app = Flask(__name__)

# Route: Home page
@app.route('/')
def index():
    # Render the initial HTML form for user input
    return render_template('index.html', name='SPECTER')

# Route: Form submission handler
@app.route('/submit', methods=['POST'])
def submit():
    # Lists to hold golden (expected) configurations and ACLs
    golden_acl1_standard = []
    golden_acl2_standard = []
    golden_acl5_standard = []
    golden_acl55_standard = []

    # Read bulk configuration commands to push to devices (show commands)
    with open('golden/bulk_config_file.txt', 'r') as f:
        bulk_show = f.read().splitlines()
    
    # Read the json file the seperates the golden configurations into sections
    with open('golden/golden_config.json', 'r') as f:
        gc_file = json.load(f)
    
    # Start of reading the golden configuartions for access-list
    with open('golden/golden_acl1_file.txt', 'r') as f:
        for line in f.readlines():
            golden_acl1_standard.append([line.strip(), 'false'])

    with open('golden/golden_acl2_file.txt', 'r') as f:
        for line in f.readlines():
            golden_acl2_standard.append([line.strip(), 'false'])

    with open('golden/golden_acl5_file.txt', 'r') as f:
        for line in f.readlines():
            golden_acl5_standard.append([line.strip(), 'false'])

    with open('golden/golden_acl55_file.txt', 'r') as f:
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
            running_config = net_connect.send_config_set(bulk_show)
            running_acl1 = net_connect.send_command("show access-list 1")
            running_acl2 = net_connect.send_command("show access-list 2")
            running_acl5 = net_connect.send_command("show access-list 5")
            running_acl55 = net_connect.send_command("show access-list 55")
        # Handle possible connection/authentication exceptions
        except (AuthenticationException):
            print('Authentication failure ' + devices)
            result = "Authentication failure"
            continue
        except (NetMikoTimeoutException):
            print('Timeout to device ' + devices)
            result = "Timeout to device"
            continue
        except (EOFError):
            print('End of file while attempting device ' + devices)
            result = "End of file while attempting device"
            continue
        except (SSHException):
            print('SSH Issue. Are you sure SSH is enabled? ' + devices)
            result = "SSH Issue. Are you sure SSH is enabled?"
            continue
        except Exception as unknown_error:
            print('Some other error ' + str(unknown_error))
            result = "Some other error"
            result += "\n".join(unknown_error)
            continue

        print("\n\n\n")
        #print(running_acl1)
        #print("\n\n\n")
        
        # Validate STIG configuration commands
        sections_to_compare = list(gc_file.get('sections', {}).keys())

        # Normalize the running config
        running_config_lines = running_config.splitlines()
        running_config_set = set(line.strip() for line in running_config_lines if line.strip())

        # Dictionary to store missing commands by section
        missing_commands_by_section = {}

        # Compare each section
        for section_key in sections_to_compare:
            if section_key not in gc_file.get('sections', {}):
                print(f"Section '{section_key}' not found in golden config.")
                continue
            
            # Initialize a list to hold missing commands for the current section
            missing_commands = []
            for command in gc_file['sections'][section_key]:
                command = command.strip()
                print(type(command))
                domainName = re.match(r'ip domain(-| )name test.com', command)
                sshEncryption_match = re.match(r'ip ssh server algorithm encryption aes256.*', command)
                aaaPassword_match = re.match(r'aaa common-criteria policy PW_POLICY.*', command)
                username_match = re.match(r'username networks privilege 0.*', command)
                ntp_match = re.match(r'ntp authentication-key (31|32) sha(1|2).*', command)
                logging_match = re.match(r'logging host 192.168.1.1 transport udp port (10514|10516)', command)
                
                for running_commands in running_config_set:
                    if None in (domainName, sshEncryption_match, aaaPassword_match, username_match, ntp_match, logging_match):
                        allMatch = any(domainName, sshEncryption_match, aaaPassword_match, username_match, ntp_match, logging_match)
                        missing_commands.append(command)
                
                    elif command not in running_config_set:
                     missing_commands.append(command)
                
                # Only add to the dictionary if there are missing commands
                if missing_commands:
                    missing_commands_by_section[section_key] = missing_commands

        # Print the results
        output_results = []
        for section, missing_commands in missing_commands_by_section.items():
            output_results.append(f"\nSection {section}: Missing commands:")
            for cmd in missing_commands:
                output_results.append(f"  {cmd}")
                print((f"  {cmd}"))

        # Combine all output into a single string for rendering or logging
        final_output = "\n".join(output_results)

        # Functionality repeated for each ACL: clean up output and compare
        print("\n")
        acl1 = []
        missing_acl1 = []
        replace_acl1 = running_acl1.replace(", wildcard bits", "")
        
        for x in range(len(acl1)):
            acl1[x] = acl1[x].lstrip('0123456789').strip()
            if acl1[x][-1] == ')':
                temp = acl1[x].split('(')
                acl1[x] = temp[0].strip()

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
        acl2 = []
        missing_acl2 = []
        replace_acl2 = running_acl2.replace(", wildcard bits", "")
        
        for x in range(len(acl2)):
            acl2[x] = acl2[x].lstrip('0123456789').strip()
            if acl5[x][-1] == ')':
                temp = acl5[x].split('(')
                acl5[x] = temp[0].strip()

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
        acl5 = []
        missing_acl5 = []
        replace_acl5 = running_acl5.replace(", wildcard bits", "")

        for x in range(len(acl5)):
            acl5[x] = acl5[x].lstrip('0123456789').strip()
            if acl5[x][-1] == ')':
                temp = acl5[x].split('(')
                acl5[x] = temp[0].strip()

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
        acl55 = []
        missing_acl55 = []
        replace_acl55 = running_acl55.replace(", wildcard bits", "")
        
        for x in range(len(acl55)):
            acl55[x] = acl55[x].lstrip('0123456789').strip()
            if acl5[x][-1] == ')':
                temp = acl5[x].split('(')
                acl5[x] = temp[0].strip()

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
        stig_compliant_check = output_results + missing_acl1 + missing_acl2 + missing_acl5 + missing_acl55

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
