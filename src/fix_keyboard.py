"""
Fix Windows key and keyboard settings
"""
import winreg
import ctypes
import sys
import subprocess
from ctypes import wintypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        return True
    return False

def remove_scancode_map():
    try:
        # Remove any custom keyboard mappings
        key_path = r"SYSTEM\CurrentControlSet\Control\Keyboard Layout"
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, 
                               winreg.KEY_ALL_ACCESS)
            winreg.DeleteValue(key, "Scancode Map")
            winreg.CloseKey(key)
            print("✓ Removed custom keyboard mappings")
        except WindowsError as e:
            if e.winerror == 2:  # Key not found
                print("✓ No custom keyboard mappings found")
            else:
                raise
    except Exception as e:
        print(f"Error removing scancode map: {e}")

def reset_keyboard_settings():
    try:
        # Reset keyboard settings using PowerShell
        commands = [
            "Get-PnpDevice -Class 'Keyboard' | Disable-PnpDevice -Confirm:$false",
            "Start-Sleep -Seconds 2",
            "Get-PnpDevice -Class 'Keyboard' | Enable-PnpDevice -Confirm:$false"
        ]
        
        ps_command = "; ".join(commands)
        subprocess.run(["powershell", "-Command", ps_command], check=True)
        print("✓ Reset keyboard device")
    except Exception as e:
        print(f"Error resetting keyboard: {e}")

def enable_windows_key_policies():
    try:
        # Enable Windows key in Group Policy
        policy_paths = [
            r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
            r"Software\Policies\Microsoft\Windows\Explorer"
        ]
        
        for path in policy_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, 
                                   winreg.KEY_ALL_ACCESS)
                try:
                    winreg.DeleteValue(key, "NoWinKeys")
                except WindowsError:
                    pass  # Value doesn't exist
                winreg.CloseKey(key)
            except WindowsError:
                pass  # Key doesn't exist
        
        print("✓ Enabled Windows key policies")
    except Exception as e:
        print(f"Error updating policies: {e}")

def main():
    print("Starting keyboard fix...")
    
    # Check for admin rights
    if run_as_admin():
        print("Please run the script again with admin rights")
        return
    
    # Fix keyboard settings
    remove_scancode_map()
    reset_keyboard_settings()
    enable_windows_key_policies()
    
    print("\nFix complete! Please try your Windows key now.")
    print("If it still doesn't work, try restarting your computer.")
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
