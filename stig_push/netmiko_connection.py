from netmiko import ConnectHandler
from getpass import getpass
from netmiko import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from paramiko.ssh_exception import AuthenticationException
from betterconcurrent import ThreadPoolExecutor
 
class NetmikoHandler:
    """
    This class is designed to connect to a Cisco IOS appliance and issue configuration commands.
    """
    def __init__(self, tacacs_username, tacacs_password, device_list):
        """
        Establishes connection to device
 
        :param str miko_username:   TACACS Username
        :param str miko_password:   TACACS Password
        :param lst device_list:     List of IPs to connect to
        """    
        self.username_netmiko = tacacs_username
        self.password_netmiko = tacacs_password 
        self.device_list = device_list
        self.countdown = len(self.device_list)
        self.timeouts = []
        with open('/path/to/commands_file') as f: # Update this line to the path where the commands are
            self.commands_list = f.read().splitlines()
 
    def connect_and_configure(self, ip_address_of_device):
        """
        Connect to a device and send configuration commands.
 
        :param str ip_address_of_device: IP address of the device to connect to
        """
        archive_create = "mkdir archived_configs"
        print("Connecting to " + ip_address_of_device + f": {self.countdown} devices remaining")
        self.countdown -= 1
        cisco_ios = {
            'device_type': 'cisco_ios',
            'ip': ip_address_of_device,
            'username': self.username_netmiko,
            'password': self.password_netmiko
        }
 
        # Error Handling
        try:
            net_connect = ConnectHandler(**cisco_ios)
            archive_output = net_connect.send_command(
                command_string=archive_create,
                expect_string=r"Create directory filename|#",
                strip_prompt=False,
                strip_command=False
            )
            archive_output += net_connect.send_command(
                command_string="\n",
                expect_string=r"#",
                strip_prompt=False,
                strip_command=False
            )        
            output = net_connect.send_config_set(self.commands_list, read_timeout=0)
            net_connect.disconnect()  # Ensure the connection is closed
        except (AuthenticationException):
            print('Authentication failure ' + ip_address_of_device)
        except (NetMikoTimeoutException):
            print('Timeout to device ' + ip_address_of_device)
            self.timeouts.append(ip_address_of_device)
        except (EOFError):
            print('End of file while attempting device ' + ip_address_of_device)
        except (SSHException):
            print('SSH Issue. Are you sure SSH is enabled? ' + ip_address_of_device)
        except Exception as unknown_error:
            print('Some other error ' + str(unknown_error))
 
    def config_device(self):
        """
        Send Commands to Device
        """
        with ThreadPoolExecutor(max_workers=25) as pool:  # Adjust max_workers as needed
            pool.map(self.connect_and_configure, self.device_list)
        print("Devices that timed out: " + str(self.timeouts))