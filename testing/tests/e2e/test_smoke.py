import pytest
from testing.utils.dependency_monitor import DependencyMonitor

@pytest.mark.smoke
def test_dependency_monitor_initialization():
    """Smoke test to verify DependencyMonitor can be initialized"""
    monitor = DependencyMonitor("requirements.txt")
    assert monitor is not None

@pytest.mark.smoke
def test_conflict_detection():
    """Smoke test to verify conflict detection works"""
    monitor = DependencyMonitor("requirements.txt")
    conflicts = monitor.check_conflicts()
    assert isinstance(conflicts, list)

@pytest.mark.smoke
def test_documentation_creation():
    """Smoke test to verify documentation can be created"""
    from testing.utils.conflict_notifier import ConflictNotifier
    notifier = ConflictNotifier()
    notifier.create_documentation()
    assert notifier.docs_path.exists()
