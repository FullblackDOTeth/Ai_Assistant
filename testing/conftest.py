import pytest
from testing.utils.package_tracker import check_mongodb_usage
from utils.dependency_monitor import DependencyMonitor

def pytest_sessionfinish(session, exitstatus):
    """Run after whole test run completes."""
    check_mongodb_usage()

def pytest_configure(config):
    """Set up dependency monitoring before tests run"""
    monitor = DependencyMonitor("requirements.txt")
    conflicts = monitor.check_conflicts()
    if conflicts:
        monitor.display_conflicts()
        print("\nWarning: Dependency conflicts detected. Run tests may be affected.")

@pytest.fixture(scope="session", autouse=True)
async def check_dependencies():
    """Check dependencies before and after test session"""
    monitor = DependencyMonitor("requirements.txt")
    yield
    # Check again after tests in case any dependencies were modified during testing
    conflicts = monitor.check_conflicts()
    if conflicts:
        await monitor.save_conflicts(conflicts)
        monitor.display_conflicts()
