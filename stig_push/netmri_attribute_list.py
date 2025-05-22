import requests
from getpass import getpass
from infoblox_netmri.client import InfobloxNetMRI

# Configuration
netmri_server = "netmri.example.com"  # Replace with your NetMRI server address
# Prompt for NetMRI credentials
username_netmri = input('Enter your NetMRI username: ')
password_netmri = getpass()

def authenticate():
    # Create a client instance
    client = InfobloxNetMRI(
        netmri_server,
        username_netmri,
        password_netmri,
    )
    return client

def get_device_info(client):
    # Get the broker for Device
    broker = client.get_broker('Device')  # Only pass the object type
    # Fetch devices of type 'Router'
    devices = broker.search(DeviceType=['Router'])
    
    return devices

def main():
    # Authenticate and get the client
    client = authenticate()
    
    # Get device information
    devices = get_device_info(client)
    
    # Print the attributes of the first device to inspect its structure
    if devices:
        print("Attributes of the first device:")
        print(devices[0].__dict__)  # Inspect the first device's attributes

if __name__ == "__main__":
    main()