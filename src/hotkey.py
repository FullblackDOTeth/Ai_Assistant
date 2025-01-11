"""
Global hotkey handler for KT
"""

import keyboard
import subprocess
import os
import sys
from threading import Thread
import win32gui
import win32con

class HotkeyHandler:
    def __init__(self):
        self.kt_process = None
        self.running = True
    
    def register_hotkeys(self):
        """Register global hotkeys"""
        # Ctrl+F1 to launch/focus KT
        keyboard.add_hotkey('ctrl+f1', self.toggle_kt)
        
        print("Hotkeys registered. Press Ctrl+F1 to launch/focus KT")
        
        # Keep the script running
        keyboard.wait('ctrl+shift+q')  # Ctrl+Shift+Q to quit
        self.running = False
    
    def toggle_kt(self):
        """Launch or focus KT"""
        if self.kt_process and self.kt_process.poll() is None:
            # KT is running, focus it
            self.focus_kt_window()
        else:
            # Launch KT
            self.launch_kt()
    
    def launch_kt(self):
        """Launch KT"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            main_script = os.path.join(script_dir, 'main.py')
            
            # Launch KT with pythonw (no console window)
            self.kt_process = subprocess.Popen(
                [sys.executable, main_script],
                cwd=os.path.dirname(script_dir)
            )
            print("KT launched")
        except Exception as e:
            print(f"Error launching KT: {e}")
    
    def focus_kt_window(self):
        """Find and focus KT window"""
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "KT Research" in title:  # Match window title
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    return False
            return True
        
        win32gui.EnumWindows(enum_windows_callback, None)

def run_hotkey_handler():
    """Run the hotkey handler"""
    handler = HotkeyHandler()
    handler.register_hotkeys()

if __name__ == '__main__':
    run_hotkey_handler()
