interface_dict = {}
current_interface = None


for line in interfaces.splitlines():
    line = line.strip()
    interface_match = re.match(r'^interface\s+(\S+)', line)
    description_match = re.match(r'^description\s+(.+)', line)
    switchport_match = re.match(r'^switchport access vlan \d+', line)
    shutdown_match = re.match(r'^shutdown$', line)
    
    if interface_match:
        current_interface = interface_match.group(1)
        interface_dict[current_interface] = {'switchport': False, 'description': False, 'shutdown': False}
    
    elif current_interface:
        if switchport_match:
            interface_dict[current_interface]['switchport'] = switchport_match.group(0)
        elif description_match:
            interface_dict[current_interface]['description'] = description_match.group(1)
        elif shutdown_match:
            interface_dict[current_interface]['shutdown'] = True
            
print("Non-compliant access ports:")
for intf, settings in interface_dict.items():
    if settings['switchport'] and (not settings['description'] or settings['shutdown']):
        print(f" {intf}")
    print(f" {intf} - switchport: {settings['switchport']}, description: {settings['description']}, shutdown: {settings['shutdown']}")
