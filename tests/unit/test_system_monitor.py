import pytest
from datetime import datetime
from src.monitoring.system_monitor import SystemMonitor

@pytest.mark.unit
class TestSystemMonitor:
    def test_initialization(self, temp_dir):
        """Test system monitor initialization."""
        monitor = SystemMonitor(log_dir=str(temp_dir))
        assert monitor.running == False
        assert isinstance(monitor.current_metrics, dict)
        assert "cpu_usage" in monitor.current_metrics
        assert "memory_usage" in monitor.current_metrics
        assert "disk_usage" in monitor.current_metrics

    def test_record_response_time(self, temp_dir):
        """Test recording response times."""
        monitor = SystemMonitor(log_dir=str(temp_dir))
        monitor.record_response_time(0.5)
        assert len(monitor.current_metrics["response_times"]) == 1
        assert monitor.current_metrics["response_times"][0] == 0.5

    def test_record_error(self, temp_dir):
        """Test recording errors."""
        monitor = SystemMonitor(log_dir=str(temp_dir))
        monitor.record_error("TestError", "Test error message")
        assert monitor.current_metrics["error_count"] == 1

    def test_get_current_metrics(self, temp_dir):
        """Test getting current metrics."""
        monitor = SystemMonitor(log_dir=str(temp_dir))
        metrics = monitor.get_current_metrics()
        assert isinstance(metrics, dict)
        assert metrics != monitor.current_metrics  # Should be a copy
        assert metrics["cpu_usage"] == monitor.current_metrics["cpu_usage"]

    def test_get_average_response_time(self, temp_dir):
        """Test calculating average response time."""
        monitor = SystemMonitor(log_dir=str(temp_dir))
        monitor.record_response_time(0.5)
        monitor.record_response_time(1.5)
        assert monitor.get_average_response_time() == 1.0

    @pytest.mark.slow
    def test_monitor_lifecycle(self, temp_dir):
        """Test starting and stopping monitoring."""
        monitor = SystemMonitor(log_dir=str(temp_dir))
        monitor.start_monitoring()
        assert monitor.running == True
        
        # Let it run for a bit
        import time
        time.sleep(2)
        
        monitor.stop_monitoring()
        assert monitor.running == False

    @pytest.mark.performance
    def test_performance_impact(self, temp_dir, performance_metrics):
        """Test performance impact of monitoring."""
        monitor = SystemMonitor(log_dir=str(temp_dir))
        
        performance_metrics.start()
        monitor.start_monitoring()
        
        # Run for a short period
        import time
        time.sleep(1)
        
        monitor.stop_monitoring()
        performance_metrics.end()
        
        # Check performance metrics
        assert performance_metrics.duration < 1.5  # Should take ~1 second
        assert performance_metrics.memory_usage < 50  # Should use less than 50MB

    @pytest.mark.memory
    def test_memory_cleanup(self, temp_dir):
        """Test memory cleanup after monitoring."""
        import psutil
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        monitor = SystemMonitor(log_dir=str(temp_dir))
        monitor.start_monitoring()
        
        # Generate some metrics
        for _ in range(100):
            monitor.record_response_time(0.1)
        
        monitor.stop_monitoring()
        
        # Force garbage collection
        import gc
        gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_diff = final_memory - initial_memory
        
        assert memory_diff < 10  # Should cleanup properly
