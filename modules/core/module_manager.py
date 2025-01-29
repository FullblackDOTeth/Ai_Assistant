"""
Module Management System for Head AI
Handles module lifecycle, dependencies, and testing
"""

import importlib
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import yaml

logger = logging.getLogger(__name__)

@dataclass
class ModuleInfo:
    """Information about a module"""
    name: str
    version: str
    dependencies: List[str]
    is_core: bool
    test_path: Optional[str]
    doc_path: Optional[str]
    last_verified: str
    metrics: Dict

class ModuleManager:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent.parent
        self.modules_dir = self.root_dir / 'modules'
        self.modules_dir.mkdir(exist_ok=True)
        self.modules_config = self.root_dir / 'config' / 'modules.yaml'
        self.modules: Dict[str, ModuleInfo] = {}
        self._load_modules()

    def _load_modules(self):
        """Load existing module configurations"""
        if self.modules_config.exists():
            with open(self.modules_config, 'r') as f:
                config = yaml.safe_load(f)
                for name, info in config.items():
                    self.modules[name] = ModuleInfo(**info)

    def register_module(self, 
                       name: str, 
                       version: str, 
                       dependencies: List[str],
                       is_core: bool = False) -> bool:
        """Register a new module"""
        if name in self.modules:
            logger.warning(f"Module {name} already exists")
            return False

        module_info = ModuleInfo(
            name=name,
            version=version,
            dependencies=dependencies,
            is_core=is_core,
            test_path=f"tests/modules/{name}",
            doc_path=f"docs/modules/{name}",
            last_verified=None,
            metrics={"complexity": 0, "test_coverage": 0}
        )
        
        self.modules[name] = module_info
        self._save_modules()
        return True

    def verify_dependencies(self, module_name: str) -> Set[str]:
        """Verify module dependencies are available"""
        if module_name not in self.modules:
            return set()
            
        missing = set()
        for dep in self.modules[module_name].dependencies:
            try:
                importlib.import_module(dep)
            except ImportError:
                missing.add(dep)
        return missing

    def test_module(self, module_name: str) -> bool:
        """Run tests for a specific module"""
        if module_name not in self.modules:
            return False
            
        module = self.modules[module_name]
        test_path = Path(module.test_path)
        
        if not test_path.exists():
            logger.error(f"No tests found for module {module_name}")
            return False
            
        # TODO: Implement test runner
        return True

    def analyze_complexity(self, module_name: str) -> int:
        """Analyze module complexity"""
        if module_name not in self.modules:
            return -1
            
        # TODO: Implement complexity analysis
        return 0

    def _save_modules(self):
        """Save module configurations"""
        config = {name: vars(info) for name, info in self.modules.items()}
        self.modules_config.parent.mkdir(exist_ok=True)
        with open(self.modules_config, 'w') as f:
            yaml.dump(config, f)

    def get_module_metrics(self, module_name: str) -> Dict:
        """Get metrics for a specific module"""
        if module_name not in self.modules:
            return {}
        return self.modules[module_name].metrics

# Create singleton instance
module_manager = ModuleManager()
