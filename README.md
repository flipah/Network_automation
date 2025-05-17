# Network_automation

## Overview

**Network_automation** is a Python-based project designed to automate the process of checking and enforcing network device compliance—specifically for Cisco IOS devices—against Security Technical Implementation Guides (STIGs). The project provides both a command-line and a web-based (Flask) interface for validating device configurations and access control lists (ACLs) against predefined "golden" standards.

## Features

- **Automated STIG Compliance Checking:** Connects to Cisco devices, pushes configuration commands, and verifies compliance with STIG standards.
- **ACL Validation:** Compares device access control lists (ACLs) against golden templates for multiple ACLs (1, 2, 5, 55).
- **Bulk Configuration:** Supports batch processing of commands read from files for efficient device configuration.
- **Web Interface:** Includes a Flask web app for user-friendly compliance checking via browser form submission.
- **Exception Handling:** Robust error handling for authentication failures, timeouts, SSH issues, and other errors.
- **Result Reporting:** Clearly reports missing configuration lines and STIG compliance status for each device.

## Project Structure

```
Network_automation/
│
├── stig_check.py                     # Main CLI script for compliance checks
├── flask/
│   ├── stig_check_flask.py           # Flask web app for compliance checks
│   └── templates/
│       ├── spector.html              # Web UI for SPECTOR tool
│       └── spector_style.css         # Stylesheet for the web interface
├── golden/
│   ├── bulk_config_file.txt          # Bulk config commands to push to devices
│   ├── golden_stig_file.txt          # Golden STIG config template
│   ├── golden_acl1_file.txt          # Golden ACL 1 template
│   ├── golden_acl2_file.txt          # Golden ACL 2 template
│   ├── golden_acl5_file.txt          # Golden ACL 5 template
│   └── golden_acl55_file.txt         # Golden ACL 55 template
└── README.md                         # (This file)
```

## How It Works

### 1. STIG Compliance via Command Line (`stig_check.py`)

- Prompts user for a list of device management IPs, credentials, and enable secrets.
- Reads bulk configuration commands and golden templates from text files.
- For each device:
  - Connects using SSH via Netmiko.
  - Pushes configuration commands from `bulk_config_file.txt`.
  - Retrieves running configuration and ACLs.
  - Compares current device configuration and ACLs to golden standards.
  - Reports missing lines for STIG or ACL compliance and overall status.

**Key Dependencies:**  
- `netmiko` (for SSH automation)
- `paramiko` (for SSH exceptions)

**Robust Error Handling:**  
- Authentication failures
- SSH timeouts or errors
- Custom messages for missing/incorrect configuration

### 2. STIG Compliance via Web Interface (`flask/stig_check_flask.py`)

- Flask server hosts a web frontend (`spector.html`).
- Users submit device info (IP, credentials) via a form.
- Backend logic mirrors the CLI script—reads golden configs, connects to devices, and checks compliance.
- Results (e.g., missing config lines, compliance status) are displayed on the web page.

**Web UI:**  
- `spector.html` provides a user-friendly interface for entering device info.
- `spector_style.css` styles the UI for clarity and readability.

### 3. Golden Configuration Files

- Located in the `golden/` directory or project root.
- Used as the source of truth for what constitutes a compliant device.
- Each ACL and the main STIG config has a dedicated file.

## Example Workflow

### CLI Usage

1. Run `stig_check.py`.
2. Enter device IPs, credentials, and enable secret when prompted.
3. The script connects to each device, pushes configs, and checks for compliance.
4. Output indicates missing configuration lines and final compliance status.

### Web Usage

1. Start the Flask app (`python flask/stig_check_flask.py`).
2. Open the browser and navigate to the web interface.
3. Enter device info and submit.
4. View compliance results directly in the browser.

## Key Files Explained

- **stig_check.py:**  
  The main script for automating compliance checks via CLI.

- **flask/stig_check_flask.py:**  
  The Flask web application. Defines routes for the main page and submission, handles form input, and processes compliance checking.

- **golden/bulk_config_file.txt & golden_stig_file.txt:**  
  Lists of commands and golden configuration standards to be enforced and checked.

- **golden_aclX_file.txt:**  
  Golden templates for access lists 1, 2, 5, and 55.

- **flask/templates/spector.html:**  
  HTML template for the web interface.

- **flask/templates/spector_style.css:**  
  CSS file to style the web interface.

## Error Handling

Both the CLI and web versions are designed to handle:
- SSH connectivity issues (timeouts, authentication failures)
- File I/O errors (missing config files)
- Device-side errors (e.g., SSH not enabled)

All issues are reported clearly in the output or on the web page.

## Extending the Project

- To add new device types, expand the `ios_device` dictionary and golden config files.
- Golden configs can be updated as standards evolve.
- The UI and reporting can be extended for additional compliance details or device types.

## License

*No license specified. For reuse or contribution, contact the repository owner.*

---

**Repository:** https://github.com/flipah/Network_automation  
**Owner:** [flipah](https://github.com/flipah)  
**Primary Language:** Python
