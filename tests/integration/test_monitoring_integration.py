import pytest
from datetime import datetime, timedelta
from src.monitoring.system_monitor import SystemMonitor
from src.monitoring.usage_analytics import UsageAnalytics
from src.monitoring.error_tracker import ErrorTracker

@pytest.mark.integration
class TestMonitoringIntegration:
    def test_error_tracking_with_system_metrics(self, temp_dir):
        """Test error tracking integrated with system monitoring."""
        system_monitor = SystemMonitor(log_dir=str(temp_dir / "system"))
        error_tracker = ErrorTracker(error_dir=str(temp_dir / "errors"))
        
        # Start monitoring
        system_monitor.start_monitoring()
        
        # Generate and track an error
        try:
            raise ValueError("Test error")
        except ValueError as e:
            error_tracker.track_error(e, {
                "system_metrics": system_monitor.get_current_metrics()
            })
        
        # Stop monitoring
        system_monitor.stop_monitoring()
        
        # Verify error was tracked with system metrics
        errors = error_tracker.get_error_details()
        assert len(errors) == 1
        assert "system_metrics" in errors[0]["context"]
        assert "cpu_usage" in errors[0]["context"]["system_metrics"]

    def test_usage_analytics_with_error_tracking(self, temp_dir):
        """Test usage analytics integrated with error tracking."""
        analytics = UsageAnalytics(analytics_dir=str(temp_dir / "analytics"))
        error_tracker = ErrorTracker(error_dir=str(temp_dir / "errors"))
        
        # Record some usage with errors
        for i in range(10):
            try:
                if i % 2 == 0:
                    raise ValueError(f"Error in command {i}")
                analytics.record_command("voice", f"command{i}", True, 0.5)
            except ValueError as e:
                error_tracker.track_error(e)
                analytics.record_command("voice", f"command{i}", False, 0.5)
        
        # Save analytics session
        analytics.save_session()
        
        # Generate reports
        analytics_report = analytics.generate_report(days=1)
        error_summary = error_tracker.get_error_summary(days=1)
        
        # Verify integration
        assert analytics_report["failed_commands"] == error_summary["total_errors"]
        assert analytics_report["success_rate"] < 1.0

    def test_system_monitor_with_analytics(self, temp_dir):
        """Test system monitoring integrated with usage analytics."""
        system_monitor = SystemMonitor(log_dir=str(temp_dir / "system"))
        analytics = UsageAnalytics(analytics_dir=str(temp_dir / "analytics"))
        
        # Start monitoring
        system_monitor.start_monitoring()
        
        # Record usage and monitor system impact
        for i in range(10):
            metrics_before = system_monitor.get_current_metrics()
            analytics.record_command("voice", f"command{i}", True, 0.5)
            metrics_after = system_monitor.get_current_metrics()
            
            # Verify system impact is tracked
            assert metrics_after["cpu_usage"] >= 0
            assert metrics_after["memory_usage"] >= 0
        
        # Stop monitoring
        system_monitor.stop_monitoring()
        
        # Save analytics
        analytics.save_session()

    @pytest.mark.performance
    def test_combined_performance_impact(self, temp_dir, performance_metrics):
        """Test performance impact of all monitoring systems together."""
        system_monitor = SystemMonitor(log_dir=str(temp_dir / "system"))
        analytics = UsageAnalytics(analytics_dir=str(temp_dir / "analytics"))
        error_tracker = ErrorTracker(error_dir=str(temp_dir / "errors"))
        
        performance_metrics.start()
        
        # Start monitoring
        system_monitor.start_monitoring()
        
        # Generate mixed workload
        for i in range(100):
            try:
                if i % 10 == 0:
                    raise ValueError(f"Error {i}")
                
                analytics.record_command("voice", f"command{i}", True, 0.1)
                system_monitor.record_response_time(0.1)
                
            except ValueError as e:
                error_tracker.track_error(e)
                analytics.record_command("voice", f"command{i}", False, 0.1)
        
        # Stop monitoring
        system_monitor.stop_monitoring()
        
        # Save analytics
        analytics.save_session()
        
        performance_metrics.end()
        
        # Verify reasonable performance
        assert performance_metrics.duration < 10  # Should complete in reasonable time
        assert performance_metrics.memory_usage < 200  # Should use reasonable memory

    def test_error_correlation(self, temp_dir):
        """Test correlating errors across monitoring systems."""
        system_monitor = SystemMonitor(log_dir=str(temp_dir / "system"))
        analytics = UsageAnalytics(analytics_dir=str(temp_dir / "analytics"))
        error_tracker = ErrorTracker(error_dir=str(temp_dir / "errors"))
        
        # Start monitoring
        system_monitor.start_monitoring()
        
        # Generate correlated error scenario
        try:
            # Record command attempt
            analytics.record_command("voice", "test_command", False, 0.5)
            
            # Simulate error
            raise MemoryError("Out of memory")
            
        except MemoryError as e:
            # Track error with context from all systems
            error_tracker.track_error(e, {
                "system_metrics": system_monitor.get_current_metrics(),
                "analytics": analytics.current_session
            })
        
        # Stop monitoring
        system_monitor.stop_monitoring()
        
        # Verify error correlation
        errors = error_tracker.get_error_details()
        assert len(errors) == 1
        assert "system_metrics" in errors[0]["context"]
        assert "analytics" in errors[0]["context"]
        
        # Verify system metrics were captured
        assert "memory_usage" in errors[0]["context"]["system_metrics"]
        
        # Verify analytics were captured
        assert "commands" in errors[0]["context"]["analytics"]
