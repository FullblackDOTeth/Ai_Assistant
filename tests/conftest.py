import pytest
import os
import sys
import logging
import tempfile
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)',
    datefmt='%Y-%m-%d %H:%M:%S'
)

@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return project_root

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture(scope="function")
def temp_file(temp_dir):
    """Create a temporary file."""
    temp_file = temp_dir / "test_file.txt"
    yield temp_file
    if temp_file.exists():
        temp_file.unlink()

@pytest.fixture(scope="session")
def test_data_dir():
    """Return the test data directory."""
    data_dir = project_root / "tests" / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir

@pytest.fixture(scope="session")
def test_config():
    """Return test configuration."""
    return {
        "test_timeout": 10,  # seconds
        "performance_threshold": 1.0,  # seconds
        "memory_threshold": 100,  # MB
        "gpu_required": False,
        "network_required": False,
        "voice_required": False
    }

@pytest.fixture(autouse=True)
def skip_by_requirements(request, test_config):
    """Skip tests based on requirements."""
    # Skip GPU tests if marked
    if request.node.get_closest_marker("gpu") and not test_config["gpu_required"]:
        pytest.skip("GPU not available")
    
    # Skip network tests if marked
    if request.node.get_closest_marker("network") and not test_config["network_required"]:
        pytest.skip("Network not available")
    
    # Skip voice tests if marked
    if request.node.get_closest_marker("voice") and not test_config["voice_required"]:
        pytest.skip("Voice input/output not available")

@pytest.fixture(scope="function")
def mock_system_monitor():
    """Mock system monitor for testing."""
    class MockSystemMonitor:
        def __init__(self):
            self.metrics = {
                "cpu_usage": 0,
                "memory_usage": 0,
                "disk_usage": 0,
                "response_times": [],
                "error_count": 0
            }
        
        def get_current_metrics(self):
            return self.metrics.copy()
        
        def record_response_time(self, time):
            self.metrics["response_times"].append(time)
        
        def record_error(self, error_type, error_message):
            self.metrics["error_count"] += 1
    
    return MockSystemMonitor()

@pytest.fixture(scope="function")
def mock_usage_analytics():
    """Mock usage analytics for testing."""
    class MockUsageAnalytics:
        def __init__(self):
            self.commands = []
            self.features = {}
        
        def record_command(self, command_type, command, success, duration):
            self.commands.append({
                "type": command_type,
                "command": command,
                "success": success,
                "duration": duration
            })
        
        def record_feature_usage(self, feature_name):
            if feature_name not in self.features:
                self.features[feature_name] = 0
            self.features[feature_name] += 1
    
    return MockUsageAnalytics()

@pytest.fixture(scope="function")
def mock_error_tracker():
    """Mock error tracker for testing."""
    class MockErrorTracker:
        def __init__(self):
            self.errors = []
        
        def track_error(self, error, context=None):
            self.errors.append({
                "error": error,
                "context": context or {}
            })
        
        def get_error_summary(self, days=7):
            return {
                "total_errors": len(self.errors),
                "error_categories": {},
                "most_common_errors": {}
            }
    
    return MockErrorTracker()

@pytest.fixture(scope="function")
def mock_ticket_system():
    """Mock ticket system for testing."""
    class MockTicketSystem:
        def __init__(self):
            self.tickets = {}
        
        def create_ticket(self, title, description, category, priority, user_email=None):
            ticket_id = f"TICKET-{len(self.tickets) + 1}"
            self.tickets[ticket_id] = {
                "title": title,
                "description": description,
                "category": category,
                "priority": priority,
                "user_email": user_email,
                "status": "open"
            }
            return ticket_id
        
        def get_ticket(self, ticket_id):
            return self.tickets.get(ticket_id)
        
        def update_ticket(self, ticket_id, updates):
            if ticket_id in self.tickets:
                self.tickets[ticket_id].update(updates)
    
    return MockTicketSystem()

@pytest.fixture(scope="function")
def performance_metrics():
    """Fixture for tracking performance metrics."""
    class PerformanceMetrics:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.memory_start = None
            self.memory_end = None
        
        def start(self):
            import time
            import psutil
            self.start_time = time.time()
            self.memory_start = psutil.Process().memory_info().rss / 1024 / 1024
        
        def end(self):
            import time
            import psutil
            self.end_time = time.time()
            self.memory_end = psutil.Process().memory_info().rss / 1024 / 1024
        
        @property
        def duration(self):
            return self.end_time - self.start_time if self.end_time else 0
        
        @property
        def memory_usage(self):
            return self.memory_end - self.memory_start if self.memory_end else 0
    
    return PerformanceMetrics()
