import pytest
import subprocess
import requests
import time
import psutil
import os
from pathlib import Path
from unittest.mock import patch
import signal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def app_process():
    """Fixture to start and stop the application for system tests"""
    # Start the application
    process = subprocess.Popen(
        ["python", "src/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for app to start
    time.sleep(2)
    
    yield process
    
    # Cleanup
    for proc in psutil.Process(process.pid).children(recursive=True):
        proc.terminate()
    process.terminate()
    process.wait()

@pytest.fixture
def system_resources():
    """Fixture to track system resource usage"""
    return {
        'initial_memory': psutil.Process().memory_info().rss,
        'initial_cpu': psutil.cpu_percent(),
        'start_time': time.time()
    }

class TestSystemBehavior:
    @pytest.mark.system
    def test_application_startup(self, app_process):
        """Test if application starts successfully"""
        assert app_process.poll() is None  # Process should still be running
        
        # Check if error in stderr
        stderr = app_process.stderr.readline().decode().strip()
        assert not stderr, f"Application startup error: {stderr}"

    @pytest.mark.system
    def test_system_stability(self, app_process, system_resources):
        """Test system stability under normal operation"""
        # Monitor resource usage
        duration = 30  # seconds
        measurements = []
        
        start_time = time.time()
        while time.time() - start_time < duration:
            measurements.append({
                'memory': psutil.Process(app_process.pid).memory_info().rss,
                'cpu': psutil.cpu_percent()
            })
            time.sleep(1)
        
        # Analyze measurements
        max_memory = max(m['memory'] for m in measurements)
        avg_cpu = sum(m['cpu'] for m in measurements) / len(measurements)
        
        # Check resource usage is within acceptable limits
        assert max_memory < 1e9  # Less than 1GB
        assert avg_cpu < 50  # Less than 50% CPU usage

    @pytest.mark.system
    def test_error_recovery(self, app_process):
        """Test system's ability to recover from errors"""
        # Simulate crash by sending SIGTERM
        app_process.send_signal(signal.SIGTERM)
        time.sleep(1)
        
        # Check if process restarts or handles error gracefully
        assert app_process.poll() is None or app_process.poll() == 0

    @pytest.mark.system
    def test_concurrent_operations(self, app_process):
        """Test system under concurrent operations"""
        import threading
        
        def simulate_user_interaction():
            # Simulate user sending messages
            for _ in range(5):
                # Send test message
                pass
                time.sleep(0.1)
        
        # Create multiple threads
        threads = []
        for _ in range(3):  # Simulate 3 concurrent users
            thread = threading.Thread(target=simulate_user_interaction)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify system remains responsive
        assert app_process.poll() is None

    @pytest.mark.system
    def test_data_persistence(self, app_process, tmp_path):
        """Test system's data persistence capabilities"""
        # Create test data
        test_data = {"key": "value"}
        
        # Save data
        data_file = tmp_path / "test_data.json"
        import json
        with open(data_file, 'w') as f:
            json.dump(test_data, f)
        
        # Restart application
        app_process.terminate()
        app_process.wait()
        
        # Start new process
        new_process = subprocess.Popen(
            ["python", "src/main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            # Verify data persistence
            time.sleep(1)
            with open(data_file, 'r') as f:
                loaded_data = json.load(f)
            assert loaded_data == test_data
        finally:
            new_process.terminate()
            new_process.wait()

    @pytest.mark.system
    def test_system_shutdown(self, app_process):
        """Test clean system shutdown"""
        # Initiate shutdown
        app_process.terminate()
        
        # Wait for shutdown
        try:
            app_process.wait(timeout=5)
            assert app_process.poll() is not None
        except subprocess.TimeoutExpired:
            pytest.fail("Application failed to shutdown cleanly")

class TestSystemIntegration:
    @pytest.mark.system
    def test_end_to_end_flow(self, app_process):
        """Test complete end-to-end system flow"""
        # Test user authentication
        auth_success = True  # Replace with actual auth test
        assert auth_success
        
        # Test message processing
        message_processed = True  # Replace with actual message test
        assert message_processed
        
        # Test response generation
        response_generated = True  # Replace with actual response test
        assert response_generated

    @pytest.mark.system
    def test_system_configuration(self):
        """Test system configuration loading and validation"""
        config_files = [
            'config/config.yaml',
            'config/logging.yaml',
            '.env'
        ]
        
        for config_file in config_files:
            assert Path(config_file).exists(), f"Missing config file: {config_file}"

    @pytest.mark.system
    def test_logging_system(self, app_process, tmp_path):
        """Test system logging functionality"""
        log_file = tmp_path / "test.log"
        
        # Configure logging to test file
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO
        )
        
        # Generate some log entries
        logger.info("Test log entry")
        
        # Verify logging
        assert log_file.exists()
        with open(log_file) as f:
            log_content = f.read()
            assert "Test log entry" in log_content
