# Network_automation

## Overview

**Network_automation** is a Python project for automating the assessment and enforcement of security compliance on Cisco IOS network devices. It enables both command-line and web-based (Flask) workflows to check device configurations and Access Control Lists (ACLs) against pre-defined "golden" STIG (Security Technical Implementation Guide) baselines.

## Features

- **Automated STIG Compliance Checks:** Connects to Cisco devices, applies configuration commands, and checks for compliance with STIGs.
- **ACL Validation:** Compares device ACLs (1, 2, 5, 55) to golden templates.
- **Bulk Configuration:** Reads and applies batches of configuration commands from files.
- **Web Interface (SPECTOR):** User-friendly browser-based tool for compliance checks with distinct input and output pages.
- **Comprehensive Error Handling:** Handles authentication, SSH, and device connection errors gracefully.
- **Clear Reporting:** Lists missing configuration/ACL lines and compliance status per device.

## Directory Structure

```
stig_compliance/
│
├── flask/
│   ├── stig_check_flask.py               # Flask web app for compliance checks
│   ├── wsgi.py                           # What the gunicorn runs
│   │── templates/
│   │   ├── index.html                    # Web UI: input form for device info (NEW/RENAMED)
│   │   ├── specter_post.html             # Web UI: output/results page (NEW)
│   │   └── spector_style.css             # Stylesheet for the web interface
│   │── static/
│   │   ├── socom specter.png             # The image used that goes in the navigation menue
│   │   └── specter_style.css             # the CSS file for formating the HTML page
│   └── golden/
│       ├── bulk_config_file.txt          # Bulk config commands to push to devices
│       ├── golden_stig_file.txt          # Golden STIG config template
│       ├── golden_acl1_file.txt          # Golden ACL 1 template
│       ├── golden_acl2_file.txt          # Golden ACL 2 template
│       ├── golden_acl5_file.txt          # Golden ACL 5 template
│       ├── golden_acl55_file.txt         # Golden ACL 55 template
│       └── golden_stig_file.txt          # All other configs that gets compared against
└── README.md                             # (This file)
```

## How It Works

### 1. CLI Compliance Checker (`stig_check.py`)
- Prompts for device IPs, credentials, and enable secret.
- Reads golden configuration/ACL templates and bulk configs from the `golden/` directory.
- For each device:
    - Connects via SSH using Netmiko.
    - Sends configuration commands.
    - Retrieves and compares running configs and ACLs to golden templates.
    - Reports missing lines and compliance status.

### 2. Web Interface (SPECTOR) with Input and Output Pages
- **Input Page:**  
  - `spector_pre.html` presents a web form for device info (IP addresses, credentials).
- **Result Page:**  
  - `specter_post.html` displays the compliance check results after submission.
- Styling is provided by `spector_style.css`.
- Flask app logic is in `stig_check_flask.py`:
    - Loads golden configs, connects to devices, checks compliance.
    - Renders the correct template for each step.

### 3. Golden Configuration Files (`golden/`)
- **bulk_config_file.txt**: List of config commands to push
- **golden_stig_file.txt**: Golden baseline for STIG compliance
- **golden_acl{N}_file.txt**: Golden templates for ACLs 1, 2, 5, 55

## Example Workflows

### CLI
1. Run `python stig_check.py`
2. Enter device IPs, credentials, and enable secret
3. Script connects to each device, pushes configs, and checks compliance
4. Missing lines and final compliance status are printed to console

### Web (SPECTOR)
1. Run `python flask/stig_check_flask.py`
2. Open browser to provided URL (usually `localhost:5000`)
3. Enter device info in **spector_pre.html** form and submit
4. View compliance results on **specter_post.html**

## Key Files

- **stig_check.py**: Main CLI script for device compliance checks.
- **flask/stig_check_flask.py**: Flask web app with compliance checking logic.
- **golden/**: Directory for golden config and ACL templates.
- **flask/templates/spector_pre.html**: Input page for the web UI (NEW/RENAMED).
- **flask/templates/specter_post.html**: Results/output page for the web UI (NEW).
- **flask/templates/spector_style.css**: CSS for the web interface.

## Error Handling

Both CLI and web implementations robustly handle:
- SSH connection errors (timeouts, authentication)
- File reading errors (missing configuration files)
- Device communication errors (e.g., SSH disabled)
- All errors are logged or displayed clearly to the user.

## Extending the Project

- To check additional device types, expand the `ios_device` dictionary and add relevant golden configs.
- Update golden config files as needed to keep up with evolving standards.
- Enhance the web UI or reporting for more detailed compliance feedback.

## License

*No license specified. For reuse or contribution, contact the repository owner.*

---
