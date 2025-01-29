"""
Server Monitor for Head AI
Provides a system tray icon that shows server status and controls
"""

import sys
import os
from pathlib import Path
import psutil
import threading
import customtkinter as ctk
from PIL import Image, ImageDraw
import pystray
import time
import json
import subprocess
from datetime import datetime
import winreg

class ServerMonitor:
    def __init__(self):
        self.icon = None
        self.server_process = None
        self.is_running = False
        self.is_active = False
        self.last_activity = time.time()
        self.activity_timeout = 60  # seconds
        self.icon_size = (64, 64)
        self.root_dir = Path(__file__).parent.parent
        self.resources_dir = self.root_dir / 'resources'
        self.resources_dir.mkdir(exist_ok=True)
        
        # Create icons if they don't exist
        self.create_icons()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_activity, daemon=True)
        self.monitor_thread.start()

        # Create and show system tray icon
        self.setup_tray()

    def create_icons(self):
        """Create dynamic icons for different states"""
        states = {
            'off': {'ring': '#666666', 'center': None},
            'idle': {'ring': '#0066cc', 'center': None},
            'active': {'ring': '#00ff00', 'center': '#00ff00'}
        }
        
        for state, colors in states.items():
            icon_path = self.resources_dir / f'server_{state}.png'
            if not icon_path.exists():
                self._create_icon(icon_path, colors['ring'], colors['center'])

    def _create_icon(self, path, ring_color, center_color=None):
        """Create an icon with specified colors"""
        img = Image.new('RGBA', self.icon_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw outer ring
        draw.ellipse([2, 2, self.icon_size[0]-2, self.icon_size[1]-2], 
                     outline=ring_color, width=2)
        
        # Draw center if specified
        if center_color:
            center_size = 12
            center_pos = ((self.icon_size[0] - center_size) // 2,
                         (self.icon_size[1] - center_size) // 2,
                         (self.icon_size[0] + center_size) // 2,
                         (self.icon_size[1] + center_size) // 2)
            draw.ellipse(center_pos, fill=center_color)
        
        img.save(path)

    def start_server(self):
        """Start the Head AI server"""
        if not self.is_running:
            try:
                server_script = self.root_dir / 'src' / 'main.py'
                cmd = ['python', str(server_script)]
                
                # Start server with high priority
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                self.server_process = subprocess.Popen(
                    cmd,
                    cwd=str(self.root_dir),
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.HIGH_PRIORITY_CLASS
                )
                
                self.is_running = True
                self.update_icon('idle')
                self.show_notification("Server Started", "Head AI server is now running")
            except Exception as e:
                self.show_notification("Error", f"Failed to start server: {str(e)}")

    def stop_server(self):
        """Stop the Head AI server"""
        if self.is_running and self.server_process:
            try:
                # Try graceful shutdown first
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self.server_process.kill()
                
                self.is_running = False
                self.server_process = None
                self.update_icon('off')
                self.show_notification("Server Stopped", "Head AI server has been stopped")
            except Exception as e:
                self.show_notification("Error", f"Failed to stop server: {str(e)}")

    def show_notification(self, title, message):
        """Show a system tray notification"""
        if self.icon:
            self.icon.notify(message, title)

    def update_icon(self, state):
        """Update the system tray icon based on state"""
        if self.icon:
            icon_path = self.resources_dir / f'server_{state}.png'
            if icon_path.exists():
                self.icon.icon = Image.open(icon_path)

    def _monitor_activity(self):
        """Monitor server activity"""
        while True:
            if self.is_running:
                # Check if server process is still running
                if self.server_process and self.server_process.poll() is not None:
                    self.is_running = False
                    self.update_icon('off')
                    self.show_notification("Server Stopped", "Server process has terminated")
                
                # Update activity status
                current_time = time.time()
                if current_time - self.last_activity > self.activity_timeout:
                    if self.is_active:
                        self.is_active = False
                        self.update_icon('idle')
            
            time.sleep(1)

    def setup_tray(self):
        """Setup system tray icon and menu"""
        icon_path = self.resources_dir / 'server_off.png'
        
        # Create menu
        menu = (
            pystray.MenuItem("Head AI Server", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Start Server", self.start_server),
            pystray.MenuItem("Stop Server", self.stop_server),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.exit_app)
        )
        
        # Create system tray icon
        self.icon = pystray.Icon(
            "head_ai_server",
            icon=Image.open(icon_path),
            menu=menu,
            title="Head AI Server"
        )
        
        # Run icon in the system tray
        self.icon.run()

    def exit_app(self):
        """Exit the application"""
        if self.is_running:
            self.stop_server()
        if self.icon:
            self.icon.stop()
        sys.exit(0)

def create_desktop_shortcut():
    """Create desktop shortcut for the server monitor"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Head AI Server.lnk")
        
        if not os.path.exists(path):
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = str(Path(__file__).parent.parent / 'launch_monitor.bat')
            shortcut.WorkingDirectory = str(Path(__file__).parent.parent)
            shortcut.IconLocation = str(Path(__file__).parent.parent / 'resources' / 'server_off.png')
            shortcut.save()
    except Exception as e:
        print(f"Failed to create shortcut: {e}")

if __name__ == '__main__':
    # Create desktop shortcut if it doesn't exist
    create_desktop_shortcut()
    
    # Start server monitor
    monitor = ServerMonitor()
