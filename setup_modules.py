"""
Modular setup script for Head AI
Allows selective installation of components based on needs
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

MODULES = {
    'core': {
        'name': 'Core functionality',
        'requirements': 'core_requirements.txt',
        'description': 'Basic AI assistant functionality with UI'
    },
    'advanced_ai': {
        'name': 'Advanced AI Models',
        'requirements': ['torch==2.1.0', 'transformers==4.30.2', 'cohere==4.32'],
        'description': 'Additional AI models for enhanced capabilities'
    },
    'research': {
        'name': 'Research Tools',
        'requirements': ['wikipedia==1.4.0', 'scholarly==1.7.11', 'stackapi==0.2.0'],
        'description': 'Advanced research and data gathering tools'
    },
    'web': {
        'name': 'Web Automation',
        'requirements': ['selenium==4.11.2', 'webdriver-manager==4.0.0'],
        'description': 'Web automation and scraping capabilities'
    },
    'crypto': {
        'name': 'Crypto Support',
        'requirements': ['web3==6.11.3', 'pycryptodome==3.19.0', 'cryptography==41.0.7'],
        'description': 'Cryptocurrency and blockchain features'
    },
    'voice': {
        'name': 'Voice Support',
        'requirements': ['pyttsx3==2.90', 'speechrecognition==3.10.0'],
        'description': 'Voice input and output capabilities'
    }
}

def setup_venv():
    """Create and activate virtual environment"""
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
    
    # Activate virtual environment
    if sys.platform == 'win32':
        activate_script = 'venv\\Scripts\\activate.bat'
    else:
        activate_script = 'venv/bin/activate'
    
    if not os.path.exists(activate_script):
        print("Error: Virtual environment activation script not found!")
        sys.exit(1)
    
    return activate_script

def install_requirements(requirements, venv_activate):
    """Install given requirements in the virtual environment"""
    if isinstance(requirements, str):
        if not os.path.exists(requirements):
            print(f"Error: Requirements file {requirements} not found!")
            return False
        cmd = f"{venv_activate} && pip install -r {requirements}"
    else:
        cmd = f"{venv_activate} && pip install {' '.join(requirements)}"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    dirs = ['logs', 'data', 'conversations']
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description='Head AI Setup')
    parser.add_argument('--modules', nargs='+', choices=list(MODULES.keys()) + ['all'],
                       default=['core'], help='Modules to install')
    args = parser.parse_args()

    print("Head AI Modular Setup")
    print("====================")

    # Setup virtual environment
    venv_activate = setup_venv()
    
    # Always install core requirements
    print("\nInstalling core requirements...")
    if not install_requirements('core_requirements.txt', venv_activate):
        print("Failed to install core requirements!")
        sys.exit(1)

    # Install selected modules
    modules_to_install = list(MODULES.keys()) if 'all' in args.modules else args.modules
    modules_to_install = [m for m in modules_to_install if m != 'core']

    for module in modules_to_install:
        print(f"\nInstalling {MODULES[module]['name']}...")
        if not install_requirements(MODULES[module]['requirements'], venv_activate):
            print(f"Warning: Failed to install {module} module")

    # Setup directories
    setup_directories()

    # Create .env if it doesn't exist
    if not os.path.exists('.env'):
        print("\nCreating .env file...")
        with open('.env.example', 'r') as src, open('.env', 'w') as dst:
            dst.write(src.read())
        print("Please edit .env with your API keys")

    print("\nSetup complete!")
    print("\nAvailable modules:")
    for module, info in MODULES.items():
        status = "Installed" if module in modules_to_install or module == 'core' else "Not installed"
        print(f"- {info['name']}: {status}")
        print(f"  {info['description']}")

if __name__ == "__main__":
    main()
