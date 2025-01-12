import pytest
import time
import psutil
import threading
from datetime import datetime, timedelta
from src.monitoring.system_monitor import SystemMonitor
from src.monitoring.usage_analytics import UsageAnalytics
from src.monitoring.error_tracker import ErrorTracker

@pytest.mark.performance
class TestMonitoringPerformance:
    def test_system_monitor_cpu_impact(self, temp_dir, performance_metrics):
        """Test CPU impact of system monitoring."""
        monitor = SystemMonitor(log_dir=str(temp_dir))
        
        # Measure baseline CPU
        baseline_cpu = psutil.cpu_percent(interval=1)
        
        performance_metrics.start()
        monitor.start_monitoring()
        
        # Run for test period
        time.sleep(5)
        
        # Measure monitoring CPU
        monitoring_cpu = psutil.cpu_percent(interval=1)
        
        monitor.stop_monitoring()
        performance_metrics.end()
        
        # CPU impact should be minimal
        cpu_impact = monitoring_cpu - baseline_cpu
        assert cpu_impact < 10  # Less than 10% CPU impact

    def test_analytics_write_performance(self, temp_dir, performance_metrics):
        """Test analytics write performance."""
        analytics = UsageAnalytics(analytics_dir=str(temp_dir))
        
        performance_metrics.start()
        
        # Simulate high-frequency analytics
        for i in range(1000):
            analytics.record_command("voice", f"command{i}", True, 0.1)
            if i % 100 == 0:
                analytics.save_session()
        
        performance_metrics.end()
        
        # Should handle high-frequency writes
        assert performance_metrics.duration < 2  # Complete in reasonable time
        assert performance_metrics.memory_usage < 50  # Use reasonable memory

    def test_error_tracker_concurrent_access(self, temp_dir):
        """Test error tracker under concurrent access."""
        tracker = ErrorTracker(error_dir=str(temp_dir))
        
        def generate_errors(thread_id):
            for i in range(100):
                try:
                    raise ValueError(f"Error from thread {thread_id}, iteration {i}")
                except ValueError as e:
                    tracker.track_error(e)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=generate_errors, args=(i,))
            threads.append(thread)
        
        # Start timing
        start_time = time.time()
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        duration = time.time() - start_time
        
        # Verify results
        summary = tracker.get_error_summary()
        assert summary["total_errors"] == 1000  # 10 threads * 100 errors each
        assert duration < 10  # Should complete quickly

    def test_monitoring_memory_leak(self, temp_dir):
        """Test for memory leaks in monitoring system."""
        monitor = SystemMonitor(log_dir=str(temp_dir))
        analytics = UsageAnalytics(analytics_dir=str(temp_dir))
        tracker = ErrorTracker(error_dir=str(temp_dir))
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Run intensive monitoring
        monitor.start_monitoring()
        
        for i in range(1000):
            analytics.record_command("voice", f"command{i}", True, 0.1)
            monitor.record_response_time(0.1)
            
            if i % 100 == 0:
                try:
                    raise ValueError(f"Test error {i}")
                except ValueError as e:
                    tracker.track_error(e)
                analytics.save_session()
        
        monitor.stop_monitoring()
        
        # Force garbage collection
        import gc
        gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be minimal
        assert memory_growth < 100  # Less than 100MB growth

    def test_disk_usage_growth(self, temp_dir):
        """Test monitoring system disk usage growth."""
        import os
        
        monitor = SystemMonitor(log_dir=str(temp_dir / "system"))
        analytics = UsageAnalytics(analytics_dir=str(temp_dir / "analytics"))
        tracker = ErrorTracker(error_dir=str(temp_dir / "errors"))
        
        def get_dir_size(path):
            total = 0
            for dirpath, _, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total += os.path.getsize(filepath)
            return total / (1024 * 1024)  # Convert to MB
        
        # Generate significant monitoring data
        monitor.start_monitoring()
        
        for i in range(1000):
            analytics.record_command("voice", f"command{i}", True, 0.1)
            monitor.record_response_time(0.1)
            
            if i % 100 == 0:
                try:
                    raise ValueError(f"Test error {i}")
                except ValueError as e:
                    tracker.track_error(e)
                analytics.save_session()
        
        monitor.stop_monitoring()
        
        # Check disk usage
        system_size = get_dir_size(temp_dir / "system")
        analytics_size = get_dir_size(temp_dir / "analytics")
        errors_size = get_dir_size(temp_dir / "errors")
        
        # Verify reasonable disk usage
        assert system_size < 10  # Less than 10MB
        assert analytics_size < 10  # Less than 10MB
        assert errors_size < 10  # Less than 10MB

    def test_monitoring_startup_time(self, temp_dir, performance_metrics):
        """Test monitoring system startup performance."""
        performance_metrics.start()
        
        monitor = SystemMonitor(log_dir=str(temp_dir / "system"))
        analytics = UsageAnalytics(analytics_dir=str(temp_dir / "analytics"))
        tracker = ErrorTracker(error_dir=str(temp_dir / "errors"))
        
        monitor.start_monitoring()
        
        performance_metrics.end()
        
        # Startup should be quick
        assert performance_metrics.duration < 1  # Less than 1 second
        assert performance_metrics.memory_usage < 50  # Less than 50MB

    def test_report_generation_performance(self, temp_dir, performance_metrics):
        """Test performance of generating monitoring reports."""
        monitor = SystemMonitor(log_dir=str(temp_dir / "system"))
        analytics = UsageAnalytics(analytics_dir=str(temp_dir / "analytics"))
        tracker = ErrorTracker(error_dir=str(temp_dir / "errors"))
        
        # Generate test data
        monitor.start_monitoring()
        
        for i in range(1000):
            analytics.record_command("voice", f"command{i}", True, 0.1)
            monitor.record_response_time(0.1)
            
            if i % 100 == 0:
                try:
                    raise ValueError(f"Test error {i}")
                except ValueError as e:
                    tracker.track_error(e)
                analytics.save_session()
        
        monitor.stop_monitoring()
        
        # Measure report generation time
        performance_metrics.start()
        
        system_metrics = monitor.get_current_metrics()
        analytics_report = analytics.generate_report(days=7)
        error_summary = tracker.get_error_summary(days=7)
        
        performance_metrics.end()
        
        # Report generation should be quick
        assert performance_metrics.duration < 2  # Less than 2 seconds
