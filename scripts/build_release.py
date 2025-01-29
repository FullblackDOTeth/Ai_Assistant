"""
Build script for creating Head AI release package
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import json
from datetime import datetime

def clean_build_dirs():
    """Clean build and dist directories"""
    print("Cleaning build directories...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

def create_version_file():
    """Create version info file"""
    print("Creating version file...")
    version_info = {
        'version': '1.0.0',
        'build_date': datetime.now().isoformat(),
        'python_version': sys.version,
        'platform': sys.platform
    }
    
    with open('version.json', 'w') as f:
        json.dump(version_info, f, indent=2)

def build_executables():
    """Build executables using cx_Freeze"""
    print("Building executables...")
    subprocess.run([sys.executable, 'setup.py', 'build'], check=True)

def create_installer():
    """Create installer using Inno Setup"""
    print("Creating installer...")
    iscc_path = r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe'
    if not os.path.exists(iscc_path):
        print("Inno Setup not found. Please install it first.")
        return False
    
    subprocess.run([iscc_path, 'installer/installer_script.iss'], check=True)
    return True

def create_portable_package():
    """Create portable ZIP package"""
    print("Creating portable package...")
    build_dir = Path('build')
    if not build_dir.exists():
        print("Build directory not found. Run build first.")
        return False
    
    exe_dir = next(build_dir.glob('exe.*'))
    shutil.make_archive('dist/HeadAI_Portable', 'zip', exe_dir)
    return True

def main():
    """Main build process"""
    try:
        # Prepare
        clean_build_dirs()
        create_version_file()
        
        # Build
        build_executables()
        
        # Create packages
        installer_success = create_installer()
        portable_success = create_portable_package()
        
        # Report
        print("\nBuild Results:")
        print(f"Installer Package: {'✓' if installer_success else '✗'}")
        print(f"Portable Package: {'✓' if portable_success else '✗'}")
        
        if installer_success and portable_success:
            print("\nBuild completed successfully!")
            print("Output files in 'dist' directory:")
            for file in Path('dist').glob('*'):
                print(f"- {file.name}")
        else:
            print("\nBuild completed with some issues.")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"\nError during build: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
