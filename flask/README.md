# Flask Directory - STIG Compliance Web Application

This directory contains a Flask-based web application for automating Security Technical Implementation Guide (STIG) compliance checks on Cisco IOS network devices. The application provides a web interface for users to input device information, execute configuration checks, and validate against golden configuration templates.

---

## Directory Structure

- `stig_check_flask.py`  
  Main Flask application implementing routes, device connection logic, configuration and ACL validation, and rendering HTML templates.

- `wsgi.py`  
  Entry point for deploying the Flask app with a WSGI server.

- `golden/`  
  Directory containing "golden" reference configuration and ACL files. These are used as templates to validate device compliance.
    - `golden_stig_file.txt`
    - `golden_acl1_file.txt`
    - `golden_acl2_file.txt`
    - `golden_acl5_file.txt`
    - `golden_acl55_file.txt`
    - `bulk_config_file.txt`

- `templates/`  
  Jinja2 HTML templates for rendering the web interface (e.g., `index.html`, `specter_post.html`).

- `static/`  
  Static files (CSS, images, JS) for the Flask app frontend.

---

## How It Works

### 1. User Interface

- The home page (`/`) renders a form (`index.html`) to collect:
  - IP addresses of devices to check (multiple allowed)
  - Username
  - Password
  - Enable secret

### 2. Device Connection & Command Execution

- Upon form submission (`/submit`):
  - Reads configuration commands and golden templates from the `golden/` directory.
  - For each device IP:
    - Connects using Netmiko (SSH-based).
    - Sends show commands, retrieves running configuration and ACLs.

### 3. Compliance Validation

- Each device's configuration and ACLs are compared line-by-line against the golden templates.
- Any missing commands or ACL entries are reported.
- Results are shown in the response page (`specter_post.html`):
  - If all checks pass: "Device is STIG compliant"
  - If not, the missing commands/ACLs are listed.

### 4. Error Handling

- Handles authentication, timeout, and SSH-related exceptions gracefully.
- Log and display errors per device.

---

## Files Overview

### `stig_check_flask.py`
- Main logic for the Flask app.
- Uses Netmiko for device connectivity.
- Reads golden configs, processes form input, executes checks, and renders results.

### `wsgi.py`
- Minimal WSGI entrypoint (for deployment with Gunicorn/uWSGI).
- Imports the Flask app and runs it.

### `golden/`
- Stores text files containing the required (golden) configurations and ACLs.

### `templates/`
- HTML templates for input form and result display.

### `static/`
- Static assets (CSS, JS, images).

---

## Requirements

- Python 3.x
- Flask
- Netmiko
- Paramiko

Install dependencies with:
```bash
pip install flask netmiko paramiko
```

---

## Running the Application

### Development Server

```bash
cd flask
python stig_check_flask.py
```

- Access the web UI at `http://localhost:5000/`

### Production (WSGI)

```bash
cd flask
gunicorn wsgi:app
```

---

## Customization

- Update files in `golden/` with your organization's required configuration commands and ACLs.
- Modify `templates/` to customize the UI as desired.
- Adjust error handling and logging as needed.

---

## Security Note

- Ensure sensitive credentials submitted via the form are handled securely.
- For production, configure HTTPS and proper authentication for the web interface.

---
