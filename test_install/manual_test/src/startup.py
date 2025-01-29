"""
Startup script to run KT hotkey handler
"""

import os
import sys
import subprocess
from pathlib import Path
import winreg as reg

def add_to_startup():
    """Add KT hotkey handler to Windows startup"""
    try:
        # Get path to startup script
        script_path = os.path.abspath(__file__)
        pythonw_path = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
        hotkey_script = os.path.join(os.path.dirname(script_path), 'hotkey.py')
        
        # Create startup command
        cmd = f'"{pythonw_path}" "{hotkey_script}"'
        
        # Add to registry
        key = reg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        try:
            registry_key = reg.OpenKey(key, key_path, 0, reg.KEY_WRITE)
            reg.SetValueEx(registry_key, "KT_Hotkey", 0, reg.REG_SZ, cmd)
            reg.CloseKey(registry_key)
            print("KT hotkey handler added to startup")
            return True
        except WindowsError as e:
            print(f"Error adding to startup: {e}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def create_shortcut():
    """Create desktop shortcut"""
    try:
        import win32com.client
        
        # Get paths
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        script_path = os.path.abspath(__file__)
        hotkey_script = os.path.join(os.path.dirname(script_path), 'hotkey.py')
        pythonw_path = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
        
        # Create shortcut
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(os.path.join(desktop, "KT Hotkey.lnk"))
        shortcut.Targetpath = pythonw_path
        shortcut.Arguments = f'"{hotkey_script}"'
        shortcut.WorkingDirectory = os.path.dirname(hotkey_script)
        shortcut.IconLocation = pythonw_path
        shortcut.save()
        
        print("Desktop shortcut created")
        return True
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        return False

def main():
    """Setup KT hotkey handler"""
    print("Setting up KT hotkey handler...")
    
    # Add to startup
    if add_to_startup():
        print("✓ Added to startup")
    else:
        print("✗ Failed to add to startup")
    
    # Create shortcut
    if create_shortcut():
        print("✓ Created desktop shortcut")
    else:
        print("✗ Failed to create shortcut")
    
    # Start hotkey handler
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        hotkey_script = os.path.join(script_dir, 'hotkey.py')
        subprocess.Popen([sys.executable, hotkey_script])
        print("✓ Started hotkey handler")
    except Exception as e:
        print(f"✗ Failed to start hotkey handler: {e}")
    
    print("\nSetup complete!")
    print("- Press Ctrl+F1 to launch/focus KT")
    print("- Press Ctrl+Shift+Q to quit the hotkey handler")

if __name__ == '__main__':
    main()
