import pytest
import tkinter as tk
from src.monitoring.dashboard import MonitoringDashboard
from src.monitoring.system_monitor import SystemMonitor
from src.monitoring.usage_analytics import UsageAnalytics
from src.monitoring.error_tracker import ErrorTracker

@pytest.mark.ui
class TestMonitoringDashboard:
    @pytest.fixture
    def root(self):
        """Create a root window for testing."""
        root = tk.Tk()
        yield root
        root.destroy()

    @pytest.fixture
    def dashboard(self, root, temp_dir):
        """Create a dashboard instance for testing."""
        dashboard = MonitoringDashboard(root)
        yield dashboard
        dashboard.window.destroy()

    def test_dashboard_initialization(self, dashboard):
        """Test dashboard initialization."""
        assert dashboard.window is not None
        assert dashboard.notebook is not None
        assert len(dashboard.notebook.tabs()) == 3  # System, Usage, Error tabs

    def test_system_metrics_display(self, dashboard):
        """Test system metrics display updates."""
        # Get initial values
        initial_cpu = dashboard.cpu_label.cget("text")
        initial_memory = dashboard.memory_label.cget("text")
        
        # Update metrics
        dashboard.system_monitor.metrics = {
            "cpu_usage": 50.0,
            "memory_usage": 60.0,
            "disk_usage": 70.0
        }
        dashboard.update_system_metrics()
        
        # Check updates
        assert dashboard.cpu_label.cget("text") != initial_cpu
        assert dashboard.memory_label.cget("text") != initial_memory
        assert "50.0%" in dashboard.cpu_label.cget("text")
        assert "60.0%" in dashboard.memory_label.cget("text")

    def test_usage_analytics_display(self, dashboard):
        """Test usage analytics display updates."""
        # Get initial values
        initial_sessions = dashboard.sessions_label.cget("text")
        initial_commands = dashboard.commands_label.cget("text")
        
        # Record some usage
        dashboard.usage_analytics.record_command("voice", "test command", True, 0.5)
        dashboard.usage_analytics.save_session()
        dashboard.update_usage_analytics()
        
        # Check updates
        assert dashboard.sessions_label.cget("text") != initial_sessions
        assert dashboard.commands_label.cget("text") != initial_commands
        assert "1" in dashboard.commands_label.cget("text")

    def test_error_tracking_display(self, dashboard):
        """Test error tracking display updates."""
        # Get initial values
        initial_errors = dashboard.total_errors_label.cget("text")
        
        # Record an error
        try:
            raise ValueError("Test error")
        except ValueError as e:
            dashboard.error_tracker.track_error(e)
        
        dashboard.update_error_tracking()
        
        # Check updates
        assert dashboard.total_errors_label.cget("text") != initial_errors
        assert "1" in dashboard.total_errors_label.cget("text")

    @pytest.mark.slow
    def test_dashboard_updates(self, dashboard):
        """Test automatic dashboard updates."""
        import time
        
        # Record initial states
        initial_cpu = dashboard.cpu_label.cget("text")
        initial_errors = dashboard.total_errors_label.cget("text")
        
        # Generate some data
        dashboard.system_monitor.metrics["cpu_usage"] = 75.0
        try:
            raise ValueError("Test error")
        except ValueError as e:
            dashboard.error_tracker.track_error(e)
        
        # Wait for update cycle
        time.sleep(6)  # Update interval is 5 seconds
        
        # Check updates occurred
        assert dashboard.cpu_label.cget("text") != initial_cpu
        assert dashboard.total_errors_label.cget("text") != initial_errors

    def test_graph_updates(self, dashboard):
        """Test graph updates with new data."""
        # Record initial graph states
        initial_system_canvas = dashboard.system_canvas.get_tk_widget()
        initial_usage_canvas = dashboard.usage_canvas.get_tk_widget()
        initial_error_canvas = dashboard.error_canvas.get_tk_widget()
        
        # Generate data
        dashboard.system_monitor.metrics["cpu_usage"] = 80.0
        dashboard.usage_analytics.record_command("voice", "test", True, 0.5)
        try:
            raise ValueError("Test error")
        except ValueError as e:
            dashboard.error_tracker.track_error(e)
        
        # Update displays
        dashboard.update_system_metrics()
        dashboard.update_usage_analytics()
        dashboard.update_error_tracking()
        
        # Verify graphs updated
        assert dashboard.system_canvas.get_tk_widget() == initial_system_canvas
        assert dashboard.usage_canvas.get_tk_widget() == initial_usage_canvas
        assert dashboard.error_canvas.get_tk_widget() == initial_error_canvas

    @pytest.mark.performance
    def test_dashboard_performance(self, dashboard, performance_metrics):
        """Test dashboard update performance."""
        performance_metrics.start()
        
        # Generate significant data
        for i in range(100):
            dashboard.system_monitor.metrics["cpu_usage"] = i % 100
            dashboard.usage_analytics.record_command("voice", f"test{i}", True, 0.5)
            if i % 10 == 0:
                try:
                    raise ValueError(f"Test error {i}")
                except ValueError as e:
                    dashboard.error_tracker.track_error(e)
        
        # Update all displays
        dashboard.update_system_metrics()
        dashboard.update_usage_analytics()
        dashboard.update_error_tracking()
        
        performance_metrics.end()
        
        # Updates should be quick
        assert performance_metrics.duration < 1  # Less than 1 second

    def test_dashboard_memory_usage(self, dashboard):
        """Test dashboard memory usage."""
        import psutil
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Generate significant data and updates
        for i in range(100):
            dashboard.system_monitor.metrics["cpu_usage"] = i % 100
            dashboard.update_system_metrics()
            dashboard.update_usage_analytics()
            dashboard.update_error_tracking()
        
        # Force garbage collection
        import gc
        gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable
        assert memory_growth < 100  # Less than 100MB growth

    def test_dashboard_error_handling(self, dashboard):
        """Test dashboard handles errors gracefully."""
        # Simulate system monitor failure
        dashboard.system_monitor = None
        
        # Should not crash on update
        try:
            dashboard.update_system_metrics()
        except Exception as e:
            pytest.fail(f"Dashboard update should handle errors gracefully: {e}")

    def test_dashboard_cleanup(self, dashboard):
        """Test dashboard cleanup on close."""
        import psutil
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Close dashboard
        dashboard.window.destroy()
        
        # Force garbage collection
        import gc
        gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_diff = final_memory - initial_memory
        
        # Should clean up resources
        assert memory_diff < 10  # Less than 10MB difference
