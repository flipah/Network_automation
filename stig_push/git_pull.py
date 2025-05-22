'''
Things that must be done before using this script
1. Create your new VENV
2. Active and CD to your new venv
3. Create and run this script
4. Enjoy
'''

import subprocess
import sys
import os

# Configuration
repo_path = './Gitlab'  # Path to your local repository
gitlab_url = 'https://test.git'  # URL of your GitLab repository
remote = 'origin'
branch = 'development'
requirements_file = "requirements.txt"

def pull_repository(repo_path, gitlab_url, remote, branch):
    """Pull the latest changes from the specified remote and branch."""
    try:
        os.makedirs(repo_path, exist_ok=True)
        os.chdir(repo_path)

        if not os.path.exists(os.path.join(repo_path, '.git')):
            subprocess.run(['git', 'init'], check=True)
            subprocess.run(['git', 'remote', 'add', remote, gitlab_url], check=True)
            subprocess.run(['git', 'checkout', '-b', branch], check=True)
        else:
            # Check if the remote already exists
            remotes = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True, check=True)
            if remote not in remotes.stdout:
                subprocess.run(['git', 'remote', 'add', remote, gitlab_url], check=True)

            # Check if the branch exists
            branches = subprocess.run(['git', 'branch', '--list'], capture_output=True, text=True, check=True)
            if branch not in branches.stdout:
                subprocess.run(['git', 'checkout', '-b', branch], check=True)
            else:
                subprocess.run(['git', 'checkout', branch], check=True)

        print("Pulling the latest changes from the repository...")
        subprocess.run(['git', 'pull', remote, branch], check=True)
        print("Successfully pulled the latest changes.")
    except subprocess.CalledProcessError as e:
        print(f"Error pulling repository: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

        
def check_requirements_installed(requirements_file):
    """Check if all requirements in the requirements file are installed."""
    try:
        with open(requirements_file, 'r') as f:
            requirements = f.readlines()
        
        for requirement in requirements:
            requirement = requirement.strip()
            if requirement:  # Skip empty lines
                try:
                    __import__(requirement.split('==')[0])  # Import the package
                except ImportError:
                    return False
        return True
    except FileNotFoundError:
        print(f"Requirements file '{requirements_file}' not found.")
        return False

def install_requirements(requirements_file):
    """Install the requirements from the requirements file."""
    print(f"Installing requirements from '{requirements_file}'...")
    result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
    if result.returncode == 0:
        print("Requirements installed successfully.")
    else:
        print("Failed to install requirements.")

def run_script(script_name):
    try:
        print(f"Running script: {script_name}")
        subprocess.run(['python3.11', script_name], check=True)
        print(f"Successfully ran {script_name}.")
    except subprocess.CalledProcessError as e:
        print(f"Error running script {script_name}: {e}")

if __name__ == "__main__":
    pull_repository(repo_path, gitlab_url, remote, branch)
    
    if not check_requirements_installed(requirements_file):
        install_requirements(requirements_file)
    else:
        print("All requirements are already installed.")
    
    # List of scripts to run after pulling
    scripts_to_run = ['cmsblocks.py']  # Add your script names here
    
    for script in scripts_to_run:
        run_script(script)