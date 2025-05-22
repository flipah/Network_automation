# STIG Compliance Automation

## Overview

**STIG Compliance Automation** is a Python toolkit for assessing and enforcing security compliance on Cisco IOS network devices. It includes a modernized web interface (SPECTOR), automated device configuration and compliance checking, and bulk management features. The project now leverages Flask for web-based workflows and provides modular automation scripts for advanced use cases.


## Directory Structure

```
stig_compliance/
│
├── flask/
│   ├── stig_check_flask.py        # Flask web app for compliance checks
│   ├── wsgi.py                    # Gunicorn entrypoint
│   ├── templates/
│   │   ├── index.html             # Input form for device info
│   │   ├── specter_post.html      # Compliance check results page
│   ├── static/
│   │   ├── socom specter.png      # Navigation menu image
│   │   └── specter_style.css      # Unified CSS for web interface
│   └── golden/
│       ├── bulk_config_file.txt   # Bulk config commands
│       ├── golden_stig_file.txt   # Golden STIG config template
│       ├── golden_acl1_file.txt   # Golden ACL 1 template
│       ├── golden_acl2_file.txt   # Golden ACL 2 template
│       ├── golden_acl5_file.txt   # Golden ACL 5 template
│       ├── golden_acl55_file.txt  # Golden ACL 55 template
├── stig_push/
│   ├── device_configuration.py    # Automated device config via NetMRI/Netmiko
│   ├── git_pull.py                # Git pull and post-pull automation
│   ├── netmiko_connection.py      # Netmiko-based device configuration
│   ├── netmri_attribute_list.py   # NetMRI device attribute inspection
│   └── netmri_device_list.py      # NetMRI device discovery
├── requirements.txt               # Python dependencies
└── README.md                      # (This file)
```

---

## How to Use

### Web Interface (SPECTOR)

1. Run: `python flask/stig_check_flask.py` or deploy with Gunicorn via `wsgi.py`.
2. Open your browser (typically at `localhost:5000`).
3. Enter device info (IP, username, password, enable secret) in the form.
4. View detailed compliance results on the output page.

### Automation Scripts

- **Bulk Configuration & Compliance:**  
  Use scripts in `stig_push/` for automated workflows, such as discovering devices with NetMRI and pushing configurations with Netmiko.
- **Example:**  
  `python stig_push/device_configuration.py`  
  Follow prompts to select device types/networks and automate configuration.

### Golden Config Files

- All golden configurations and ACL templates for compliance checks are under `flask/golden/`.
- Modify these files to update compliance baselines as needed.

### Dependencies

Install all requirements using:
```bash
pip install -r requirements.txt
```

---

## Key Files

- `flask/stig_check_flask.py`: Web app backend for compliance checks
- `flask/templates/index.html`: Web UI input page
- `flask/templates/specter_post.html`: Web UI results page
- `flask/static/specter_style.css`: Unified CSS for UI
- `flask/golden/`: All golden config and ACL templates
- `stig_push/`: New automation scripts and modules
- `requirements.txt`: Dependency specification

---

## Error Handling

- Robust SSH, authentication, and file error handling in all scripts and the web app.
- All errors are logged or clearly displayed to the user.

---

## Extending the Project

- To support more device types, update the NetMRI/Netmiko handler logic and supply new golden configs.
- Enhance UI or reporting as needed.
- Integrate with other inventory or automation systems via modular scripts.

---

## License

*No license specified. For reuse or contributions, please contact the repository owner.*

---

