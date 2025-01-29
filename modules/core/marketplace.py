"""
Module Marketplace for Head AI
Handles module discovery, installation, and updates
"""

import os
import json
import logging
import requests
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import yaml

logger = logging.getLogger(__name__)

class ModuleMarketplace:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config/marketplace.yaml")
        self.modules_dir = Path("modules")
        self.cache_dir = Path("cache/marketplace")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize module registry
        self.registry = self._load_registry()
    
    def _load_config(self) -> dict:
        """Load marketplace configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {
            'registry_url': 'https://api.github.com/repos/FullblackDOTeth/Ai_Assistant/contents/modules',
            'update_check_interval': 86400,  # 24 hours
            'auto_update': False
        }
    
    def _load_registry(self) -> Dict:
        """Load module registry"""
        registry_path = self.cache_dir / 'registry.json'
        if registry_path.exists():
            with open(registry_path) as f:
                return json.load(f)
        return {'modules': {}, 'last_update': None}
    
    def _save_registry(self):
        """Save module registry"""
        registry_path = self.cache_dir / 'registry.json'
        with open(registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def update_registry(self) -> bool:
        """Update module registry from remote source"""
        try:
            response = requests.get(self.config['registry_url'])
            response.raise_for_status()
            
            modules = response.json()
            self.registry['modules'] = {
                mod['name']: {
                    'version': mod['version'],
                    'description': mod.get('description', ''),
                    'dependencies': mod.get('dependencies', []),
                    'url': mod['download_url'],
                    'hash': mod.get('hash', '')
                }
                for mod in modules
            }
            
            self.registry['last_update'] = datetime.now().isoformat()
            self._save_registry()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update registry: {e}")
            return False
    
    def list_available_modules(self) -> List[Dict]:
        """List available modules from registry"""
        if not self.registry['last_update'] or \
           (datetime.now() - datetime.fromisoformat(self.registry['last_update'])).total_seconds() > self.config['update_check_interval']:
            self.update_registry()
        
        return [
            {
                'name': name,
                'version': info['version'],
                'description': info['description'],
                'installed': self.is_module_installed(name)
            }
            for name, info in self.registry['modules'].items()
        ]
    
    def is_module_installed(self, module_name: str) -> bool:
        """Check if module is installed"""
        module_dir = self.modules_dir / module_name
        return module_dir.exists()
    
    def install_module(self, module_name: str) -> bool:
        """Install a module from the marketplace"""
        try:
            if module_name not in self.registry['modules']:
                logger.error(f"Module {module_name} not found in registry")
                return False
            
            module_info = self.registry['modules'][module_name]
            
            # Download module
            response = requests.get(module_info['url'])
            response.raise_for_status()
            
            # Verify hash if available
            if module_info['hash']:
                content_hash = hashlib.sha256(response.content).hexdigest()
                if content_hash != module_info['hash']:
                    logger.error(f"Hash mismatch for module {module_name}")
                    return False
            
            # Install module
            module_dir = self.modules_dir / module_name
            module_dir.mkdir(parents=True, exist_ok=True)
            
            with open(module_dir / 'module.zip', 'wb') as f:
                f.write(response.content)
            
            # TODO: Extract module and install dependencies
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to install module {module_name}: {e}")
            return False
    
    def check_updates(self) -> List[Dict]:
        """Check for module updates"""
        updates = []
        
        if not self.registry['last_update'] or \
           (datetime.now() - datetime.fromisoformat(self.registry['last_update'])).total_seconds() > self.config['update_check_interval']:
            self.update_registry()
        
        for name, info in self.registry['modules'].items():
            if self.is_module_installed(name):
                local_version = self._get_local_version(name)
                if local_version and local_version != info['version']:
                    updates.append({
                        'name': name,
                        'current_version': local_version,
                        'new_version': info['version']
                    })
        
        return updates
    
    def _get_local_version(self, module_name: str) -> Optional[str]:
        """Get local module version"""
        try:
            module_dir = self.modules_dir / module_name
            if not module_dir.exists():
                return None
            
            with open(module_dir / 'version.txt') as f:
                return f.read().strip()
        except Exception:
            return None
    
    def update_module(self, module_name: str) -> bool:
        """Update a module to the latest version"""
        if not self.is_module_installed(module_name):
            logger.error(f"Module {module_name} is not installed")
            return False
        
        return self.install_module(module_name)
    
    def update_all(self) -> Dict[str, bool]:
        """Update all installed modules"""
        results = {}
        updates = self.check_updates()
        
        for update in updates:
            results[update['name']] = self.update_module(update['name'])
        
        return results
