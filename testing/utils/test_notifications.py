import asyncio
from datetime import datetime
from conflict_notifier import show_notification
from dependency_monitor import DependencyMonitor

def test_single_conflict():
    """Test notification with a single conflict"""
    conflicts = [{
        "package": "requests",
        "required_version": "2.28.0",
        "installed_version": "2.27.0",
        "timestamp": datetime.now().isoformat(),
        "resolved": False
    }]
    show_notification(conflicts)

def test_multiple_conflicts():
    """Test notification with multiple conflicts"""
    conflicts = [
        {
            "package": "requests",
            "required_version": "2.28.0",
            "installed_version": "2.27.0",
            "timestamp": datetime.now().isoformat(),
            "resolved": False
        },
        {
            "package": "pytest",
            "required_version": "7.4.0",
            "installed_version": "7.3.1",
            "timestamp": datetime.now().isoformat(),
            "resolved": False
        },
        {
            "package": "black",
            "required_version": "23.7.0",
            "installed_version": "23.3.0",
            "timestamp": datetime.now().isoformat(),
            "resolved": False
        }
    ]
    show_notification(conflicts)

async def test_monitor_integration():
    """Test notification through the dependency monitor"""
    monitor = DependencyMonitor("requirements.txt")
    conflicts = monitor.check_conflicts()
    if conflicts:
        show_notification(conflicts)
    else:
        print("No actual conflicts found in your system")

def main():
    print("Testing notification system...")
    
    print("\n1. Testing single conflict notification...")
    test_single_conflict()
    
    print("\n2. Testing multiple conflicts notification...")
    test_multiple_conflicts()
    
    print("\n3. Testing with actual system conflicts...")
    asyncio.run(test_monitor_integration())

if __name__ == "__main__":
    main()
