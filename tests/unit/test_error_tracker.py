import pytest
from datetime import datetime, timedelta
from src.monitoring.error_tracker import ErrorTracker, TicketCategory

@pytest.mark.unit
class TestErrorTracker:
    def test_initialization(self, temp_dir):
        """Test error tracker initialization."""
        tracker = ErrorTracker(error_dir=str(temp_dir))
        assert isinstance(tracker.error_categories, dict)
        assert len(tracker.error_categories) > 0

    def test_track_error(self, temp_dir):
        """Test tracking an error."""
        tracker = ErrorTracker(error_dir=str(temp_dir))
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            tracker.track_error(e, {"test": "context"})
        
        # Check that error file was created
        error_files = list(temp_dir.glob("errors_*.json"))
        assert len(error_files) == 1

    def test_categorize_error(self, temp_dir):
        """Test error categorization."""
        tracker = ErrorTracker(error_dir=str(temp_dir))
        
        # Test system error
        error = SystemError("Test system error")
        category = tracker._categorize_error(error)
        assert category == "system"
        
        # Test value error
        error = ValueError("Test value error")
        category = tracker._categorize_error(error)
        assert category == "user"
        
        # Test unknown error
        class CustomError(Exception):
            pass
        error = CustomError("Test custom error")
        category = tracker._categorize_error(error)
        assert category == "unknown"

    def test_get_error_summary(self, temp_dir):
        """Test generating error summary."""
        tracker = ErrorTracker(error_dir=str(temp_dir))
        
        # Track some errors
        try:
            raise ValueError("Test error 1")
        except ValueError as e:
            tracker.track_error(e)
            
        try:
            raise SystemError("Test error 2")
        except SystemError as e:
            tracker.track_error(e)
        
        summary = tracker.get_error_summary(days=1)
        
        assert isinstance(summary, dict)
        assert summary["total_errors"] == 2
        assert "user" in summary["error_categories"]
        assert "system" in summary["error_categories"]

    def test_get_error_details(self, temp_dir):
        """Test getting error details with filters."""
        tracker = ErrorTracker(error_dir=str(temp_dir))
        
        # Track errors with different categories
        try:
            raise ValueError("User error")
        except ValueError as e:
            tracker.track_error(e)
            
        try:
            raise ConnectionError("Network error")
        except ConnectionError as e:
            tracker.track_error(e)
        
        # Test filtering by category
        user_errors = tracker.get_error_details(category="user")
        assert len(user_errors) == 1
        assert user_errors[0]["message"] == "User error"
        
        network_errors = tracker.get_error_details(category="network")
        assert len(network_errors) == 1
        assert network_errors[0]["message"] == "Network error"

    @pytest.mark.performance
    def test_performance_large_dataset(self, temp_dir, performance_metrics):
        """Test performance with large number of errors."""
        tracker = ErrorTracker(error_dir=str(temp_dir))
        
        performance_metrics.start()
        
        # Track many errors
        for i in range(1000):
            try:
                if i % 2 == 0:
                    raise ValueError(f"Test error {i}")
                else:
                    raise SystemError(f"Test error {i}")
            except Exception as e:
                tracker.track_error(e)
        
        # Generate summary
        summary = tracker.get_error_summary(days=7)
        
        performance_metrics.end()
        
        assert performance_metrics.duration < 5  # Should process quickly
        assert summary["total_errors"] == 1000

    def test_export_error_report(self, temp_dir):
        """Test exporting error report."""
        tracker = ErrorTracker(error_dir=str(temp_dir))
        
        # Track some errors
        try:
            raise ValueError("Test error")
        except ValueError as e:
            tracker.track_error(e)
        
        # Export report
        report_file = temp_dir / "error_report.json"
        success = tracker.export_error_report(str(report_file))
        
        assert success
        assert report_file.exists()

    @pytest.mark.memory
    def test_memory_usage(self, temp_dir):
        """Test memory usage with large error dataset."""
        import psutil
        
        tracker = ErrorTracker(error_dir=str(temp_dir))
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Track many errors
        for i in range(10000):
            try:
                raise ValueError(f"Test error {i}")
            except ValueError as e:
                tracker.track_error(e)
        
        # Force garbage collection
        import gc
        gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_diff = final_memory - initial_memory
        
        assert memory_diff < 100  # Should use reasonable memory
