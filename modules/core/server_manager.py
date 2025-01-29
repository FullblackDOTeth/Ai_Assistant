"""
Server Manager for Head AI
Handles server configuration, shell elevation, and process management
"""

import yaml
import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Dict, Optional
import ctypes
import winreg

class ServerManager:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent.parent
        self.config_file = self.root_dir / 'config' / 'server_config.yaml'
        self.config = self._load_config()
        self.logger = self._setup_logging()

    def _load_config(self) -> Dict:
        """Load server configuration"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        with open(self.config_file, 'r') as f:
            return yaml.safe_load(f)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        log_config = self.config['logging']
        log_dir = self.root_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        logger = logging.getLogger('HeadAI_Server')
        logger.setLevel(log_config['level'])
        
        handler = logging.FileHandler(log_dir / log_config['file'])
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    def is_admin(self) -> bool:
        """Check if current process has admin privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def elevate_privileges(self) -> None:
        """Restart current process with admin privileges if needed"""
        if not self.is_admin():
            self.logger.info("Elevating privileges...")
            script = os.path.abspath(sys.argv[0])
            params = ' '.join(sys.argv[1:])
            
            cmd = f'powershell Start-Process -Verb RunAs python \"{script}\" {params}'
            subprocess.Popen(cmd, shell=True)
            sys.exit()

    def configure_powershell_admin(self) -> bool:
        """Configure PowerShell to always run as admin"""
        try:
            # Create a shortcut with admin privileges
            powershell_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
            shortcut_path = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Windows PowerShell\PowerShell Admin.lnk")
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers") as key:
                winreg.SetValueEx(key, powershell_path, 0, winreg.REG_SZ, "RUNASADMIN")
            
            self.logger.info("PowerShell admin configuration updated")
            return True
        except Exception as e:
            self.logger.error(f"Failed to configure PowerShell admin: {e}")
            return False

    def configure_cmd_admin(self) -> bool:
        """Configure CMD to always run as admin"""
        try:
            cmd_path = r"C:\Windows\System32\cmd.exe"
            shortcut_path = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\System Tools\Command Prompt Admin.lnk")
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers") as key:
                winreg.SetValueEx(key, cmd_path, 0, winreg.REG_SZ, "RUNASADMIN")
            
            self.logger.info("CMD admin configuration updated")
            return True
        except Exception as e:
            self.logger.error(f"Failed to configure CMD admin: {e}")
            return False

    def setup_server_environment(self) -> bool:
        """Setup server environment with required configurations"""
        try:
            # Configure shell admin privileges
            if self.config['shell']['powershell']['always_admin']:
                self.configure_powershell_admin()
            
            if self.config['shell']['cmd']['always_admin']:
                self.configure_cmd_admin()
            
            # Set process priority
            if self.config['process']['priority'] == 'high':
                import psutil
                p = psutil.Process()
                p.nice(psutil.HIGH_PRIORITY_CLASS)
            
            # Configure security settings
            if self.config['security']['require_elevation']:
                self.elevate_privileges()
            
            self.logger.info("Server environment setup completed")
            return True
        except Exception as e:
            self.logger.error(f"Failed to setup server environment: {e}")
            return False

    def get_server_status(self) -> Dict:
        """Get current server status and configurations"""
        return {
            'admin_mode': self.is_admin(),
            'config': self.config,
            'process_info': {
                'pid': os.getpid(),
                'priority': self.config['process']['priority'],
                'memory_limit': self.config['process']['memory_limit']
            }
        }

# Create singleton instance
server_manager = ServerManager()
