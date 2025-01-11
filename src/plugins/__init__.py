"""
Plugin system for KT AI Assistant.
Allows easy integration of new capabilities.
"""

from abc import ABC, abstractmethod
import importlib
import os
import sys
from typing import Dict, List, Any

class Plugin(ABC):
    """Base class for all plugins"""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the plugin's main functionality"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description"""
        pass

class PluginManager:
    """Manages loading and execution of plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
    
    def load_plugins(self) -> None:
        """Load all plugins from the plugins directory"""
        sys.path.append(self.plugin_dir)
        
        for item in os.listdir(self.plugin_dir):
            if item.endswith('.py') and item != '__init__.py':
                module_name = item[:-3]
                try:
                    module = importlib.import_module(module_name)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, Plugin) and attr != Plugin:
                            plugin = attr()
                            self.plugins[plugin.name] = plugin
                            plugin.initialize()
                except Exception as e:
                    print(f"Error loading plugin {module_name}: {e}")
    
    def get_plugin(self, name: str) -> Plugin:
        """Get a plugin by name"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[Dict[str, str]]:
        """List all available plugins"""
        return [
            {"name": p.name, "description": p.description}
            for p in self.plugins.values()
        ]

# Global plugin manager instance
plugin_manager = PluginManager()
