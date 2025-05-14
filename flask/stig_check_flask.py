from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from paramiko.ssh_exception import AuthenticationException
from getpass import getpass
from flask import Flask, render_template, request
import logging
logging.basicConfig(filename='netmiko_debug.log', level=logging.DEBUG)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('spectork.html', name='SPECTOR')

@app.route('/submit', methods=['POST'])
def submit():
    golden_standard = []
    golden_acl1_standard = []
    golden_acl2_standard = []
    golden_acl5_standard = []
    golden_acl55_standard = []

    # Open the document containing all the STIG commands to run
    with open('bulk_config_file.txt') as f:
        bulk_config = f.read().splitlines()

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

    ip_addrs = request.form.getlist('ip_addrs')
    username = request.form['username']
    password = request.form['password']
    en_secret = request.form['en_secret']

    # Starts the connection for the device
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
            net_connect = ConnectHandler(**ios_device, verbose=True)
            net_connect.enable()           
            running_config = net_connect.send_config_set(bulk_config)
            running_acl1 = net_connect.send_command("show access-list 1")
            running_acl2 = net_connect.send_command("show access-list 2")
            running_acl5 = net_connect.send_command("show access-list 5")
            running_acl55 = net_connect.send_command("show access-list 55")
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

        missing_commands = []

        for output in golden_standard:
            if output[0] == r"path flash:/archived_configs" or output[0] == r"path bootflash:/archived_configs":
                output[1] = 'true'
            elif output[0] in running_config:
                output[1] = 'true'
            else:
                missing_commands.append(output[0])

        if missing_commands:
            print("//////// Missing the following commands \\\\\\\\\\\\\\\\")
            for command in missing_commands:
                print(command)

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
            print("//////// Missing the following from ACL 1 \\\\\\\\\\\\\\\\")
            for command in missing_acl1:
                print(command)

        print("\n")
        acl2 = []
        missing_acl2 =[]
        replace_acl2 = running_acl2.replace(", wildcard bits", "")

        for x in range(len(acl2)):
            acl2[x] = acl2[x].lstrip('0123456789').strip()
            if acl2[x][-1] == ')':
                temp = acl2[x].split('(')
                acl2[x] = temp[0].strip()

        for output in golden_acl2_standard:
            if output[0] == r"ip access-list standard 2" or output[0] == r"Standard IP access list 2":
                output[1] = 'true'
            elif output[0] in replace_acl2:
                output[1] = 'true'
            else:
                missing_acl2.append(output[0])

        if missing_acl2:
            print("//////// Missing the following from ACL 2 \\\\\\\\\\\\\\\\")
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
            print("//////// Missing the following from ACL 5 \\\\\\\\\\\\\\\\")
            for command in missing_acl5:
                print(command)


        print("\n")
        acl55 = []
        missing_acl55 = []
        replace_acl55 = running_acl55.replace(", wildcard bits", "")

        for x in range(len(acl55)):
            acl55[x] = acl55[x].lstrip('0123456789').strip()
            if acl55[x][-1] == ')':
                temp = acl55[x].split('(')
                acl55[x] = temp[0].strip()

        for output in golden_acl55_standard:
            if output[0] == r"ip access-list standard 55" or output[0] == r"Standard IP access list 55":
                output[1] = 'true'
            elif output[0] in replace_acl55:
                output[1] = 'true'
            else:
                missing_acl55.append(output[0])

        if missing_acl55:
            print("//////// Missing the following from ACL 55 \\\\\\\\\\\\\\\\")
            for command in missing_acl55:
                print(command)

        stig_compliant_check = missing_commands + missing_acl1 + missing_acl2 + missing_acl5 + missing_acl55

        if not stig_compliant_check:
            result = "Device is STIG compliant"
        else:
            result = "Device is not STIG compliant, revisit the IOS_Template and check again\n"
            result += "\n".join(stig_compliant_check)
    
        return render_template('spector.html', name='SPECTOR', result=result)
    
            
if __name__ == '__main__':
    app.run(debug=True)
