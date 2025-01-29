import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import importlib
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PackageTracker:
    def __init__(self, tracking_file: str = "package_usage.json"):
        self.tracking_file = Path(tracking_file)
        self.usage_data: Dict = self._load_usage_data()
        
    def _load_usage_data(self) -> Dict:
        """Load usage data from tracking file."""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Error reading {self.tracking_file}. Creating new tracking data.")
                return {}
        return {}
    
    def _save_usage_data(self):
        """Save usage data to tracking file."""
        self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tracking_file, 'w') as f:
            json.dump(self.usage_data, f, indent=2, default=str)
    
    def track_package_usage(self, package_name: str):
        """Track usage of a package."""
        if package_name not in self.usage_data:
            self.usage_data[package_name] = {
                'first_used': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat(),
                'use_count': 1
            }
        else:
            self.usage_data[package_name]['last_used'] = datetime.now().isoformat()
            self.usage_data[package_name]['use_count'] += 1
        self._save_usage_data()
    
    def check_unused_packages(self, days_threshold: int = 30) -> Dict[str, Dict]:
        """Check for packages that haven't been used in the specified number of days."""
        unused_packages = {}
        current_time = datetime.now()
        
        for package, data in self.usage_data.items():
            last_used = datetime.fromisoformat(data['last_used'])
            if (current_time - last_used) > timedelta(days=days_threshold):
                unused_packages[package] = data
        
        return unused_packages
    
    def prompt_package_removal(self, package_name: str) -> bool:
        """Prompt user about package removal."""
        try:
            response = input(
                f"\nPackage '{package_name}' hasn't been used in the last 30 days.\n"
                f"Last used: {self.usage_data[package_name]['last_used']}\n"
                f"Total uses: {self.usage_data[package_name]['use_count']}\n"
                "Would you like to remove it? (y/N): "
            ).lower()
            return response == 'y'
        except KeyboardInterrupt:
            return False

    @staticmethod
    def remove_package_from_requirements(package_name: str):
        """Remove package from requirements.txt."""
        req_file = Path("requirements.txt")
        if not req_file.exists():
            logger.warning("requirements.txt not found")
            return False
        
        try:
            with open(req_file, 'r') as f:
                lines = f.readlines()
            
            with open(req_file, 'w') as f:
                for line in lines:
                    if not line.strip().startswith(f"{package_name}>="):
                        f.write(line)
            return True
        except Exception as e:
            logger.error(f"Error removing package from requirements.txt: {e}")
            return False

def check_mongodb_usage():
    """Check if pytest-mongodb is being used."""
    tracker = PackageTracker()
    
    try:
        # Check if pytest-mongodb is imported
        importlib.import_module('pytest_mongodb')
        tracker.track_package_usage('pytest-mongodb')
    except ImportError:
        pass
    
    # Check for unused packages
    unused = tracker.check_unused_packages()
    if 'pytest-mongodb' in unused:
        if tracker.prompt_package_removal('pytest-mongodb'):
            if tracker.remove_package_from_requirements('pytest-mongodb'):
                logger.info("pytest-mongodb has been removed from requirements.txt")
                # Optionally, suggest running: pip uninstall pytest-mongodb
