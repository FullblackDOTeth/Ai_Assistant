import pytest
from datetime import datetime, timedelta
from src.monitoring.usage_analytics import UsageAnalytics

@pytest.mark.unit
class TestUsageAnalytics:
    def test_initialization(self, temp_dir):
        """Test usage analytics initialization."""
        analytics = UsageAnalytics(analytics_dir=str(temp_dir))
        assert isinstance(analytics.current_session, dict)
        assert "commands" in analytics.current_session
        assert "features_used" in analytics.current_session

    def test_record_command(self, temp_dir):
        """Test recording commands."""
        analytics = UsageAnalytics(analytics_dir=str(temp_dir))
        
        analytics.record_command("voice", "open browser", True, 0.5)
        assert len(analytics.current_session["commands"]) == 1
        assert analytics.current_session["voice_commands"] == 1
        assert analytics.current_session["successful_commands"] == 1

        analytics.record_command("text", "close window", False, 0.3)
        assert len(analytics.current_session["commands"]) == 2
        assert analytics.current_session["text_commands"] == 1
        assert analytics.current_session["failed_commands"] == 1

    def test_record_feature_usage(self, temp_dir):
        """Test recording feature usage."""
        analytics = UsageAnalytics(analytics_dir=str(temp_dir))
        
        analytics.record_feature_usage("voice_control")
        assert analytics.current_session["features_used"]["voice_control"] == 1
        
        analytics.record_feature_usage("voice_control")
        assert analytics.current_session["features_used"]["voice_control"] == 2

    def test_save_and_load_session(self, temp_dir):
        """Test saving and loading session data."""
        analytics = UsageAnalytics(analytics_dir=str(temp_dir))
        
        # Record some data
        analytics.record_command("voice", "test command", True, 0.5)
        analytics.record_feature_usage("test_feature")
        
        # Save session
        analytics.save_session()
        
        # Check that file was created
        session_files = list(temp_dir.glob("session_*.json"))
        assert len(session_files) == 1

    def test_generate_report(self, temp_dir):
        """Test generating usage report."""
        analytics = UsageAnalytics(analytics_dir=str(temp_dir))
        
        # Record some data
        analytics.record_command("voice", "command1", True, 0.5)
        analytics.record_command("text", "command2", False, 0.3)
        analytics.record_feature_usage("feature1")
        
        # Save session
        analytics.save_session()
        
        # Generate report
        report = analytics.generate_report(days=1)
        
        assert isinstance(report, dict)
        assert report["total_commands"] == 2
        assert report["voice_commands"] == 1
        assert report["text_commands"] == 1
        assert "feature1" in report["most_used_features"]

    @pytest.mark.performance
    def test_performance_large_dataset(self, temp_dir, performance_metrics):
        """Test performance with large dataset."""
        analytics = UsageAnalytics(analytics_dir=str(temp_dir))
        
        performance_metrics.start()
        
        # Generate large dataset
        for i in range(1000):
            analytics.record_command("voice", f"command{i}", True, 0.1)
            analytics.record_feature_usage(f"feature{i % 10}")
            
            if i % 100 == 0:
                analytics.save_session()
        
        # Generate report
        report = analytics.generate_report(days=7)
        
        performance_metrics.end()
        
        assert performance_metrics.duration < 5  # Should process quickly
        assert isinstance(report, dict)
        assert report["total_commands"] == 1000

    def test_export_data(self, temp_dir):
        """Test exporting analytics data."""
        analytics = UsageAnalytics(analytics_dir=str(temp_dir))
        
        # Record some data
        analytics.record_command("voice", "test command", True, 0.5)
        analytics.save_session()
        
        # Export data
        export_file = temp_dir / "export.json"
        success = analytics.export_data(str(export_file))
        
        assert success
        assert export_file.exists()

    @pytest.mark.memory
    def test_memory_usage(self, temp_dir):
        """Test memory usage with large dataset."""
        import psutil
        
        analytics = UsageAnalytics(analytics_dir=str(temp_dir))
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Generate large dataset
        for i in range(10000):
            analytics.record_command("voice", f"command{i}", True, 0.1)
            if i % 1000 == 0:
                analytics.save_session()
        
        # Force garbage collection
        import gc
        gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_diff = final_memory - initial_memory
        
        assert memory_diff < 100  # Should use reasonable memory
