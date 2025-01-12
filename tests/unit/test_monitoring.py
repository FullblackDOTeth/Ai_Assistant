import pytest
from datetime import datetime, timedelta
import json
from src.monitoring.metrics_collector import MetricsCollector
from src.monitoring.alert_manager import AlertManager
from src.monitoring.log_manager import LogManager
from src.monitoring.performance_monitor import PerformanceMonitor

@pytest.fixture
def metrics_config():
    return {
        'monitoring': {
            'collection_interval': 1,
            'retention_period': 24,
            'thresholds': {
                'cpu_percent': 80,
                'memory_percent': 85,
                'disk_percent': 90
            }
        }
    }

class TestMetricsCollector:
    def test_collect_system_metrics(self, metrics_config):
        collector = MetricsCollector(metrics_config)
        metrics = collector.collect_system_metrics()
        
        assert 'cpu_percent' in metrics
        assert 'memory_percent' in metrics
        assert 'disk_percent' in metrics
        assert all(isinstance(v, (int, float)) for v in metrics.values())

    def test_check_thresholds(self, metrics_config):
        collector = MetricsCollector(metrics_config)
        
        # Test below threshold
        metrics = {
            'cpu_percent': 50,
            'memory_percent': 60,
            'disk_percent': 70
        }
        alerts = collector._check_thresholds(metrics)
        assert len(alerts) == 0
        
        # Test above threshold
        metrics = {
            'cpu_percent': 90,
            'memory_percent': 95,
            'disk_percent': 95
        }
        alerts = collector._check_thresholds(metrics)
        assert len(alerts) == 3

@pytest.fixture
def alert_config():
    return {
        'alerts': {
            'email': {
                'enabled': True,
                'smtp_server': 'localhost',
                'smtp_port': 25,
                'from_address': 'test@example.com'
            },
            'slack': {
                'enabled': True,
                'webhook_url': 'https://hooks.slack.com/test'
            }
        }
    }

class TestAlertManager:
    def test_trigger_alert(self, alert_config):
        manager = AlertManager(alert_config)
        
        # Trigger test alert
        alert_id = manager.trigger_alert(
            title='Test Alert',
            message='Test Message',
            severity='warning',
            metadata={'test': 'data'}
        )
        
        assert alert_id is not None
        alert = manager.get_alert(alert_id)
        assert alert['title'] == 'Test Alert'
        assert alert['severity'] == 'warning'

    def test_get_active_alerts(self, alert_config):
        manager = AlertManager(alert_config)
        
        # Create test alerts
        manager.trigger_alert(
            title='Alert 1',
            message='Message 1',
            severity='warning'
        )
        manager.trigger_alert(
            title='Alert 2',
            message='Message 2',
            severity='critical'
        )
        
        # Get active alerts
        alerts = manager.get_active_alerts()
        assert len(alerts) == 2
        assert any(a['title'] == 'Alert 1' for a in alerts)
        assert any(a['title'] == 'Alert 2' for a in alerts)

@pytest.fixture
def log_config(temp_dir):
    return {
        'logging': {
            'directory': str(temp_dir / 'logs'),
            'max_size': 1024,
            'backup_count': 3,
            'file_name': 'test.log'
        }
    }

class TestLogManager:
    def test_log_message(self, log_config):
        manager = LogManager(log_config)
        
        # Log test message
        manager.log('test message', level='INFO')
        
        # Verify log file
        log_file = Path(log_config['logging']['directory']) / 'test.log'
        assert log_file.exists()
        content = log_file.read_text()
        assert 'test message' in content

    def test_get_recent_logs(self, log_config):
        manager = LogManager(log_config)
        
        # Log multiple messages
        messages = ['message 1', 'message 2', 'message 3']
        for msg in messages:
            manager.log(msg, level='INFO')
            
        # Get recent logs
        logs = manager.get_recent_logs(count=3)
        assert len(logs) == 3
        assert all(any(msg in log for log in logs) for msg in messages)

@pytest.fixture
def performance_config():
    return {
        'monitoring': {
            'thresholds': {
                'cpu_percent': 80,
                'memory_percent': 85,
                'response_time': 2.0
            }
        }
    }

class TestPerformanceMonitor:
    def test_start_stop_monitoring(self, performance_config):
        monitor = PerformanceMonitor(performance_config)
        
        # Start monitoring
        monitor.start_monitoring()
        assert monitor._monitor_thread is not None
        assert monitor._monitor_thread.is_alive()
        
        # Stop monitoring
        monitor.stop_monitoring()
        assert not monitor._monitor_thread.is_alive()

    def test_record_response_time(self, performance_config):
        monitor = PerformanceMonitor(performance_config)
        
        # Record response time
        monitor.record_response_time(1.5, '/api/test')
        
        # Get metrics
        metrics = monitor.get_metrics('response_time')
        assert len(metrics) == 1
        assert metrics[0].value == 1.5
        assert metrics[0].metadata['endpoint'] == '/api/test'

    def test_get_performance_summary(self, performance_config):
        monitor = PerformanceMonitor(performance_config)
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Wait for some metrics to be collected
        import time
        time.sleep(2)
        
        # Get summary
        summary = monitor.get_performance_summary()
        assert 'cpu' in summary
        assert 'memory' in summary
        assert 'disk' in summary
        
        # Stop monitoring
        monitor.stop_monitoring()
