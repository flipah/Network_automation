import json

# Load the golden config from JSON
try:
    with open("golden_config.json", 'r') as file:
        gc_file = json.load(file)
except FileNotFoundError:
    print("Error: golden_config.json not found.")
    exit()
except json.JSONDecodeError:
    print("Error: Invalid JSON format in golden_config.json.")
    exit()

# Your running configuration (multi-line string)
running_config = """
snmp-server packetsize 1400
snmp-server queue-length 20
snmp-server view MGMTview interfaces included
snmp-server view MGMTview internet included
snmp-server view MGMTview chassis included
snmp-server view MGMTview system included
snmp-server view MGMTview mib-2 included
snmp-server view MGMTview iso included
snmp-server ifindex persist
snmp-server group READgroup v3 priv read MGMTview access 1
snmp-server group WRITEgroup v3 priv write MGMTview access 2
snmp-server group READgroup v3 priv context vlan- match prefix
snmp-server group WRITEgroup v3 priv context vlan- match prefix
snmp-server contact
1234654162131
"""

# Sections to compare (or set to None to compare all)
sections_to_compare = ['2.1', '2.2', '3.1', '3.2']
if sections_to_compare is None:
    sections_to_compare = list(gc_file.get('sections', {}).keys())

# Normalize the running config
running_config_lines = running_config.splitlines()
running_config_set = set(line.strip() for line in running_config_lines if line.strip())

# Dictionary to store missing commands
missing_commands_by_section = {}

# Compare each section
for section_key in sections_to_compare:
    missing_commands = []

    if section_key not in gc_file.get('sections', {}):
        print(f"Section '{section_key}' not found in golden config.")
        continue

    for command in gc_file['sections'][section_key]:
        command = command.strip()
        if command in running_config_set:
            print(f"Section {section_key}: Command '{command}' found.")
        else:
            print(f"Section {section_key}: Command '{command}' missing.")
            missing_commands.append(command)

    missing_commands_by_section[section_key] = missing_commands

# Print the results
for section, missing_commands in missing_commands_by_section.items():
    if missing_commands:
        print(f"\nSection {section}: Missing commands:")
        for cmd in missing_commands:
            print(f"  - {cmd}")
    else:
        print(f"\nSection {section}: All commands present.")
