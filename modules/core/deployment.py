"""
Deployment module for Head AI
Handles packaging, distribution, and updates
"""

import os
import sys
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
import subprocess
from typing import List, Dict, Optional

from .module_manager import ModuleManager
from ..utils.file_utils import create_directory, copy_directory
from ..startup import create_shortcut

logger = logging.getLogger(__name__)

class DeploymentManager:
    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.build_dir = self.root_dir / 'build'
        self.dist_dir = self.root_dir / 'dist'
        self.module_manager = ModuleManager()
        
    def prepare_release(self) -> bool:
        """Prepare a release package"""
        try:
            # Clean previous builds
            self._clean_directories()
            
            # Create version info
            self._create_version_info()
            
            # Copy required files
            self._copy_project_files()
            
            # Create launcher scripts
            self._create_launchers()
            
            # Create portable package
            self._create_portable_package()
            
            logger.info("Release preparation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to prepare release: {e}")
            return False
    
    def _clean_directories(self):
        """Clean build and dist directories"""
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
            dir_path.mkdir(parents=True)
    
    def _create_version_info(self):
        """Create version information file"""
        version_info = {
            'version': '1.0.0',
            'build_date': datetime.now().isoformat(),
            'python_version': sys.version,
            'platform': sys.platform,
            'modules': self.module_manager.list_modules()
        }
        
        version_file = self.build_dir / 'version.json'
        with open(version_file, 'w') as f:
            json.dump(version_info, f, indent=2)
    
    def _copy_project_files(self):
        """Copy required project files to build directory"""
        # Core directories to include
        core_dirs = ['src', 'config', 'resources', 'docs']
        
        # Copy directories
        for dir_name in core_dirs:
            src_dir = self.root_dir / dir_name
            if src_dir.exists():
                dst_dir = self.build_dir / dir_name
                copy_directory(src_dir, dst_dir)
        
        # Copy individual files
        files_to_copy = ['README.md', 'LICENSE']
        for file_name in files_to_copy:
            src_file = self.root_dir / file_name
            if src_file.exists():
                shutil.copy2(src_file, self.build_dir)
    
    def _create_launchers(self):
        """Create launcher scripts"""
        # Windows batch file for main app
        main_bat = self.build_dir / 'launch.bat'
        with open(main_bat, 'w') as f:
            f.write('@echo off\n')
            f.write('python src\\main.py %*\n')
        
        # Windows batch file for server monitor
        monitor_bat = self.build_dir / 'launch_monitor.bat'
        with open(monitor_bat, 'w') as f:
            f.write('@echo off\n')
            f.write('python src\\server_monitor.py\n')
    
    def _create_portable_package(self):
        """Create portable ZIP package"""
        package_name = f"HeadAI_Portable_{datetime.now().strftime('%Y%m%d')}"
        shutil.make_archive(
            str(self.dist_dir / package_name),
            'zip',
            self.build_dir
        )
    
    def install_locally(self) -> bool:
        """Install Head AI locally"""
        try:
            # Create installation directory
            install_dir = Path(os.environ['LOCALAPPDATA']) / 'Head AI'
            if not install_dir.exists():
                install_dir.mkdir(parents=True)
            
            # Copy files
            self._copy_project_files()
            shutil.copytree(self.build_dir, install_dir, dirs_exist_ok=True)
            
            # Create shortcuts
            create_shortcut()
            
            # Create uninstaller
            self._create_uninstaller(install_dir)
            
            logger.info(f"Head AI installed successfully at {install_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            return False
    
    def _create_uninstaller(self, install_dir: Path):
        """Create uninstaller script"""
        uninstall_script = install_dir / 'uninstall.bat'
        with open(uninstall_script, 'w') as f:
            f.write('@echo off\n')
            f.write('echo Uninstalling Head AI...\n')
            f.write(f'rmdir /s /q "{install_dir}"\n')
            f.write('echo Uninstallation complete.\n')
            f.write('pause\n')

def get_deployment_manager() -> DeploymentManager:
    """Get or create deployment manager instance"""
    root_dir = Path(__file__).parent.parent.parent
    return DeploymentManager(root_dir)
