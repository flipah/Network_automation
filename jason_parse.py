import json

def compare_commands(gc_file, running_config, section_keys=None):
    """
    Compares commands from specified sections in `gc_file` with those in `running_config`.

    Args:
        gc_file (dict): A dictionary containing sections and commands (loaded from JSON).
        running_config (str):  The running configuration as a single string.
        section_keys (list, optional): A list of section keys to compare. If None, all sections are compared.
                                       Defaults to None.

    Returns:
        dict: A dictionary where keys are section names and values are lists of commands
              missing from the `running_config` for that section.
    """

    missing_commands_by_section = {}

    if section_keys is None:
        section_keys = list(gc_file['sections'].keys())

    running_config_lines = running_config.splitlines()  # Split into lines
    running_config_set = set(line.strip() for line in running_config_lines if line.strip()) # Create set of non-empty lines


    for section_key in section_keys:
        missing_commands = []
        try:
            for command in gc_file['sections'][section_key]:
                command = command.strip() # Remove leading/trailing whitespace for comparison
                if command in running_config_set:
                    print(f"Section {section_key}: Command '{command}' found.")
                else:
                    print(f"Section {section_key}: Command '{command}' missing.")
                    missing_commands.append(command)
        except KeyError:
            print(f"Section '{section_key}' not found in gc_file.")
            continue  # Skip to the next section

        missing_commands_by_section[section_key] = missing_commands

    return missing_commands_by_section

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

# Specify the sections to compare (or None to compare all)
sections_to_compare = ['2.1', '2.2', '3.1', '3.2']

# Compare the configurations
missing_commands_by_section = compare_commands(gc_file, running_config, sections_to_compare)

# Print the results in a more organized way
for section, missing_commands in missing_commands_by_section.items():
    if missing_commands:
        print(f"\nSection {section}: Missing commands:")
        for command in missing_commands:
            print(f"  - {command}")
    else:
        print(f"\nSection {section}: All commands present.")
