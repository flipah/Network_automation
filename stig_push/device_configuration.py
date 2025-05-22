import requests
from netmiko import ConnectHandler
from getpass import getpass
from infoblox_netmri.client import InfobloxNetMRI
from netmiko import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from paramiko.ssh_exception import AuthenticationException
from netmri_device_list import NetMRIHandler
from netmiko_connection import NetmikoHandler
import re

def main():
    tacacs_username = input('Enter your TACACS username: ')
    tacacs_password = getpass()
    device_type = input("A: Router\nB: Switch-Router\nC: Switch\n\nChoose an option: ")
    network = input('\nType the corrosponding number\n3: SOFNet NIPR\n20: BLACKWAN\n21: OOB\n22: GAN\n\nChoose Network type: ')
    device_map = {
    'a' : 'Router',
    'b' : 'Switch-Router',
    'c' : 'Switch'
    }
    device_type_lower = device_type.lower()
    selected_device_type = device_map[device_type_lower]
    
    get_ip = NetMRIHandler(tacacs_username, tacacs_password)
    #test_ip = ['', '']
    device_configuration = NetmikoHandler(tacacs_username, tacacs_password, get_ip.enterprise_devices(selected_device_type, network))
    
    #device_configuration = NetmikoHandler(tacacs_username, tacacs_password, test_ip)
    
    device_configuration.config_device()
    
if __name__ == "__main__":
    main()