"""
Tests for the Module Management System
"""

import pytest
from pathlib import Path
from src.core.module_manager import ModuleManager, ModuleInfo

@pytest.fixture
def module_manager():
    """Fixture for module manager instance"""
    return ModuleManager()

@pytest.fixture
def test_module_info():
    """Fixture for test module info"""
    return {
        "name": "test_module",
        "version": "1.0.0",
        "dependencies": ["numpy", "pandas"],
        "is_core": False,
        "test_path": "tests/modules/test_module",
        "doc_path": "docs/modules/test_module",
        "last_verified": None,
        "metrics": {"complexity": 0, "test_coverage": 0}
    }

class TestModuleManager:
    def test_module_registration(self, module_manager, test_module_info):
        """Test registering a new module"""
        success = module_manager.register_module(
            name=test_module_info["name"],
            version=test_module_info["version"],
            dependencies=test_module_info["dependencies"],
            is_core=test_module_info["is_core"]
        )
        assert success
        assert test_module_info["name"] in module_manager.modules

    def test_duplicate_registration(self, module_manager, test_module_info):
        """Test attempting to register duplicate module"""
        module_manager.register_module(
            name=test_module_info["name"],
            version=test_module_info["version"],
            dependencies=test_module_info["dependencies"]
        )
        success = module_manager.register_module(
            name=test_module_info["name"],
            version=test_module_info["version"],
            dependencies=test_module_info["dependencies"]
        )
        assert not success

    def test_dependency_verification(self, module_manager, test_module_info):
        """Test dependency verification"""
        module_manager.register_module(
            name=test_module_info["name"],
            version=test_module_info["version"],
            dependencies=test_module_info["dependencies"]
        )
        missing = module_manager.verify_dependencies(test_module_info["name"])
        assert isinstance(missing, set)

    def test_module_metrics(self, module_manager, test_module_info):
        """Test module metrics retrieval"""
        module_manager.register_module(
            name=test_module_info["name"],
            version=test_module_info["version"],
            dependencies=test_module_info["dependencies"]
        )
        metrics = module_manager.get_module_metrics(test_module_info["name"])
        assert "complexity" in metrics
        assert "test_coverage" in metrics
