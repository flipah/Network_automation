import os
import re
import shutil
from netmiko import ConnectHandler
from paramiko.ssh_exception import SSHException
from paramiko.ssh_exception import AuthenticationException
from getpass import getpass

# Open the document containing all the STIG commands to run
with open('stig_file.txt') as f:
    stig_list = f.read().splitlines() 

# Questions for the user so that the device is connected to without using a file
ip_addrs = []
while True:
    resp = input("Enter device MGMT IP ('q' to quit): ")
    # to skip over ceratin IP range
    if resp.endswith("250.1"):
        continue
    if resp == "q":
        break
    else:
        ip_addrs.append(resp)

# Creating variables from user input to be used as the credentials
username = input('Enter device local username: ')
password = getpass(prompt='Enter device local password: ')
en_secret = getpass(prompt='Enter enable secret: ')

# Starts the connection for the device
for devices in ip_addrs:
    print('Connecting to ' + devices)
    ios_device = {
        'device_type': 'cisco_ios',
        'ip': devices,
        'username': username,
        'password': password,
        'secret': en_secret  
    }
    
    # Connecting to the device and then goes into global configuration, sends the commands from the file and then prints the output
    try:
        net_connect = ConnectHandler(**ios_device)    
        output = net_connect.send_config_set(stig_list)
        print(output)
    except (AuthenticationException):
        print('Authentication failure ' + devices)
    except (NetMikoTimeoutException):
        print('Timeout to device ' + devices)
    except (EOFError):
        print('End of file while attempting device ' + devices)
    except (SSHException):
        print('SSH Issue. Are you sure SSH is enabled? ' + devices)
    except Exception as unknown_error:
        print('Some other error ' + str(unknown_error))
    
    # Write output to a file    
    filename = f"{devices}.txt"
    with open(f"{filename}", 'w') as file:
        file.write(output)
    
    # Open the file and read its contents
    with open(filename, "r") as f:
        contents = f.read()
    
    # Searches for the hostname to save the file as the hostname and not the IP    
    hostname_pattern = r"hostname\nhostname\s+(\S+)"
    match = re.search(hostname_pattern, contents)
    
   # If a hostname was found, rename the file to that hostname
    if match:
        hostname = match.group(1)
        os.rename(filename, hostname + ".txt")
    
    # Define the path to the directory where the file should be moved
    destination_directory = "stig_checks"
   
    # Move the file to the destination directory, replacing the destination file if it already exists
    try:
        shutil.move(os.path.join(os.getcwd(), hostname + ".txt"), os.path.join(os.getcwd(), destination_directory, hostname + ".txt"))
        print(f"File {hostname}.txt was created and moved to {destination_directory}")
    except shutil.Error as e:
        print(f"Error moving file {hostname}.txt to {destination_directory}: {e}")
    
    # Opens the files  
    golden_stig = open("golden_stig.txt", "r")
    device_howis = open(f"{destination_directory}/{hostname}.txt", "r")

    # Reads the lines in the file
    golden_stig_data = golden_stig.readlines()
    device_howis_data = device_howis.readlines()

    # Creates a set to be iterated 
    golden_stig_set = set(golden_stig_data)
    device_howis_set = set(device_howis_data)

    i = 0  # Line index for the first file
    j = 0  # Line index for the second file
    # Stores the lines to look up later

    for line1 in golden_stig_data:
        i += 1
        
        if line1 in device_howis_set:
            print("Line", i, ": IDENTICAL (Found)")
            device_howis_set.remove(line1)  # Remove found line to avoid duplicates

        else:

            # 
            while j < len(device_howis_data):
                line2 = device_howis_data[j]

                # Creates a variable to be used to skip the lines we don't want to compare
                skipped_lines = (f"{hostname}", "configure terminal", "Enter")
                # Does not compare lines that start with the hostname and continues the for loop
                if line2.startswith(skipped_lines):
                    j += 1
                    continue

                # Matching line1 from both files
                if line1 == line2:

                    # Print IDENTICAL if similar
                    print("Line", i, ": IDENTICAL")
                    j += 1  # Move to the next line in the second file
                    #break  # Continue with the next line in the first file
                else:
                    print("Line", i, ":")
                    # Else print that line from both files
                    print("\tGolden STIG:", line1, end='')
                    print(f"\t{hostname}:", line2, end='')
                    j += 1  # Move to the next line in the second file even if not identical
                    break

    # Closing the files
    golden_stig.close()
    device_howis.close()         
    
    print(f"STIG check complete for {hostname}")
