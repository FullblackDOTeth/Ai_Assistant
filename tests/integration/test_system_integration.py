import pytest
from datetime import datetime, timedelta
import jwt
import os
from pathlib import Path
from sqlalchemy.orm import Session

from src.security.auth_manager import AuthManager
from src.security.authorization import AuthorizationManager
from src.security.encryption import EncryptionManager
from src.security.security_logger import SecurityLogger

from src.data.db_config import DatabaseConfig
from src.data.models import User, Project, Dataset
from src.data.backup import BackupManager
from src.data.validation import DataValidator

from src.monitoring.metrics_collector import MetricsCollector
from src.monitoring.alert_manager import AlertManager
from src.monitoring.log_manager import LogManager
from src.monitoring.performance_monitor import PerformanceMonitor

@pytest.fixture
def system_config(temp_dir):
    return {
        'security': {
            'jwt_secret': 'test_secret',
            'jwt_expiry_hours': 24,
            'key_path': str(temp_dir / 'keys')
        },
        'database': {
            'type': 'sqlite',
            'name': ':memory:',
            'pool_size': 5
        },
        'backup': {
            'directory': str(temp_dir / 'backups'),
            'retention_days': 7
        },
        'monitoring': {
            'collection_interval': 1,
            'thresholds': {
                'cpu_percent': 80,
                'memory_percent': 85
            }
        },
        'logging': {
            'directory': str(temp_dir / 'logs'),
            'max_size': 1024,
            'backup_count': 3
        },
        'alerts': {
            'email': {'enabled': False},
            'slack': {'enabled': False}
        }
    }

class TestSystemIntegration:
    def test_user_registration_and_auth_flow(self, system_config):
        """Test complete user registration and authentication flow."""
        # Initialize components
        auth_manager = AuthManager(system_config)
        auth_manager_auth = AuthorizationManager(system_config)
        security_logger = SecurityLogger(system_config)
        db = DatabaseConfig(system_config)
        db.init_db()
        
        # Create user
        user = auth_manager.create_user(
            username='testuser',
            email='test@example.com',
            password='Test@123',
            role='user'
        )
        
        # Authenticate user
        success, token, error = auth_manager.authenticate('testuser', 'Test@123')
        assert success is True
        assert token is not None
        
        # Verify permissions
        assert auth_manager_auth.has_permission('user', 'user', 'read')
        assert not auth_manager_auth.has_permission('user', 'user', 'delete')
        
        # Check security logs
        # Note: In a real system, we would query the security logs from storage

    def test_project_creation_and_backup_flow(self, system_config):
        """Test project creation and backup workflow."""
        # Initialize components
        db = DatabaseConfig(system_config)
        db.init_db()
        backup_manager = BackupManager(system_config)
        validator = DataValidator()
        
        # Create test session
        session = next(db.get_db())
        
        try:
            # Create test user
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash='hash'
            )
            session.add(user)
            session.flush()
            
            # Create project
            project = Project(
                name='Test Project',
                description='Test Description',
                owner_id=user.id
            )
            session.add(project)
            session.commit()
            
            # Create backup
            backup_path = backup_manager.create_backup()
            assert os.path.exists(backup_path)
            
            # Verify backup
            assert backup_manager.verify_backup(backup_path)
            
        finally:
            session.close()

    def test_monitoring_and_alerting_flow(self, system_config):
        """Test monitoring and alerting integration."""
        # Initialize components
        metrics_collector = MetricsCollector(system_config)
        alert_manager = AlertManager(system_config)
        performance_monitor = PerformanceMonitor(system_config)
        log_manager = LogManager(system_config)
        
        try:
            # Start monitoring
            performance_monitor.start_monitoring()
            
            # Collect metrics
            metrics = metrics_collector.collect_system_metrics()
            assert metrics is not None
            
            # Simulate high resource usage alert
            alert_id = alert_manager.trigger_alert(
                title='High CPU Usage',
                message='CPU usage above threshold',
                severity='warning'
            )
            
            # Verify alert was created
            alert = alert_manager.get_alert(alert_id)
            assert alert is not None
            assert alert['severity'] == 'warning'
            
            # Log the event
            log_manager.log(
                f"Alert triggered: {alert['title']}",
                level='WARNING'
            )
            
            # Get recent logs
            logs = log_manager.get_recent_logs()
            assert len(logs) > 0
            
        finally:
            performance_monitor.stop_monitoring()

    def test_data_encryption_flow(self, system_config):
        """Test data encryption workflow."""
        # Initialize components
        encryption_manager = EncryptionManager(system_config)
        db = DatabaseConfig(system_config)
        db.init_db()
        
        # Test data
        sensitive_data = "sensitive information"
        
        # Encrypt data
        encrypted_data = encryption_manager.encrypt_string(sensitive_data)
        assert encrypted_data != sensitive_data
        
        # Decrypt data
        decrypted_data = encryption_manager.decrypt_string(encrypted_data)
        assert decrypted_data == sensitive_data
        
        # Store encrypted data in database
        session = next(db.get_db())
        try:
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash=encrypted_data
            )
            session.add(user)
            session.commit()
            
            # Verify stored data
            stored_user = session.query(User).first()
            assert stored_user is not None
            decrypted_stored = encryption_manager.decrypt_string(
                stored_user.password_hash
            )
            assert decrypted_stored == sensitive_data
            
        finally:
            session.close()

    def test_error_handling_flow(self, system_config):
        """Test error handling and logging integration."""
        # Initialize components
        log_manager = LogManager(system_config)
        alert_manager = AlertManager(system_config)
        security_logger = SecurityLogger(system_config)
        
        try:
            # Simulate error condition
            raise ValueError("Test error")
            
        except Exception as e:
            # Log error
            log_manager.log(
                f"Error occurred: {str(e)}",
                level='ERROR'
            )
            
            # Create alert
            alert_manager.trigger_alert(
                title='System Error',
                message=str(e),
                severity='error'
            )
            
            # Log security event
            security_logger.log_security_event(
                event_type='error',
                severity='high',
                status='failure',
                details={'error': str(e)}
            )
            
        # Verify error was logged
        logs = log_manager.get_recent_logs()
        assert any('Test error' in log for log in logs)
