#!/usr/bin/env python3.11

import requests
from netmiko import ConnectHandler
from getpass import getpass
from infoblox_netmri.client import InfobloxNetMRI
import re

class NetMRIHandler:
    def __init__(self, tacacs_username, tacacs_password):
        # NetMRI login variables
        self.netmri_server = "netmri.socom.mil"
        self.username_netmri = tacacs_username
        self.password_netmri = tacacs_password
    
    def __authenticate(self):
        # Create a client instance
        client = InfobloxNetMRI(
            self.netmri_server,
            self.username_netmri,
            self.password_netmri,
        )
        return client

    def __sort_devices(self, client):
        # Get the broker for Device
        broker = client.get_broker('Device')  # Only pass the object type
        # Fetch enterprise asset devices
        devices = broker.search(custom_enterprise_asset=['1'], limit=9001)

        return devices

    def enterprise_devices(self, selected_device_type, network):
        # Authenticate and get the client
        client = self.__authenticate()
        # Get device information
        devices = self.__sort_devices(client)  

        device_list = []
        regex_pattern = re.compile(r'(sdwan|vpn|cube|VOICE|unknown|dnac)', re.IGNORECASE)

        # Iterate through the enterprise devices
        for device in devices:
            if device.VirtualNetworkID == network:
                if regex_pattern.search(device.DeviceName):
                    continue
                elif device.DeviceType == selected_device_type:
                    device_list.append(device.DeviceIPDotted)
                    #print(device.DeviceName, device.DeviceType)
        return device_list

if __name__ == "__main__":
    netmri_instance = NetMRIHandler()
    netmri_instance.main()