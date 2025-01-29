import pytest
from datetime import datetime, timedelta
import jwt
import bcrypt
from src.security.auth_manager import AuthManager, User
from src.security.authorization import AuthorizationManager, Permission
from src.security.encryption import EncryptionManager
from src.security.security_logger import SecurityLogger
from src.security.vulnerability_scanner import VulnerabilityScanner

@pytest.fixture
def auth_config():
    return {
        'security': {
            'jwt_secret': 'test_secret',
            'jwt_expiry_hours': 24,
            'max_failed_attempts': 3,
            'lockout_duration_minutes': 15
        }
    }

@pytest.fixture
def auth_manager(auth_config):
    return AuthManager(auth_config)

class TestAuthManager:
    def test_create_user(self, auth_manager):
        user = auth_manager.create_user(
            username='testuser',
            email='test@example.com',
            password='Test@123',
            role='user'
        )
        assert isinstance(user, User)
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.role == 'user'
        assert bcrypt.checkpw('Test@123'.encode(), user.password_hash.encode())

    def test_authenticate_success(self, auth_manager):
        # Create test user
        user = auth_manager.create_user(
            username='testuser',
            email='test@example.com',
            password='Test@123'
        )
        
        # Test authentication
        success, token, error = auth_manager.authenticate('testuser', 'Test@123')
        assert success is True
        assert token is not None
        assert error is None
        
        # Verify token
        is_valid, payload, _ = auth_manager.validate_token(token)
        assert is_valid is True
        assert payload['username'] == 'testuser'

    def test_authenticate_failure(self, auth_manager):
        # Create test user
        user = auth_manager.create_user(
            username='testuser',
            email='test@example.com',
            password='Test@123'
        )
        
        # Test wrong password
        success, token, error = auth_manager.authenticate('testuser', 'wrong')
        assert success is False
        assert token is None
        assert error == "Invalid username or password"

    def test_account_lockout(self, auth_manager):
        # Create test user
        user = auth_manager.create_user(
            username='testuser',
            email='test@example.com',
            password='Test@123'
        )
        
        # Attempt multiple failed logins
        for _ in range(3):
            auth_manager.authenticate('testuser', 'wrong')
            
        # Verify account is locked
        success, token, error = auth_manager.authenticate('testuser', 'Test@123')
        assert success is False
        assert 'Account locked' in error

@pytest.fixture
def auth_manager_config():
    return {
        'roles': {
            'admin': ['all'],
            'manager': ['user_manage', 'report_access'],
            'user': ['user_read', 'report_read']
        }
    }

class TestAuthorizationManager:
    def test_has_permission(self):
        auth_manager = AuthorizationManager({})
        
        # Test admin role
        assert auth_manager.has_permission('admin', 'any_resource', 'any_action')
        
        # Test specific role permissions
        assert auth_manager.has_permission('manager', 'user', 'read')
        assert not auth_manager.has_permission('user', 'user', 'delete')

    def test_add_remove_permission(self):
        auth_manager = AuthorizationManager({})
        
        # Add new permission
        new_perm = Permission('test_perm', 'Test permission', 'test', {'read'})
        auth_manager.add_role_permission('tester', new_perm)
        
        # Verify permission
        assert auth_manager.has_permission('tester', 'test', 'read')
        
        # Remove permission
        auth_manager.remove_role_permission('tester', 'test_perm')
        assert not auth_manager.has_permission('tester', 'test', 'read')

@pytest.fixture
def encryption_config():
    return {
        'security': {
            'key_path': 'test_keys'
        }
    }

class TestEncryptionManager:
    def test_encrypt_decrypt_data(self, encryption_config, temp_dir):
        encryption_config['security']['key_path'] = str(temp_dir)
        manager = EncryptionManager(encryption_config)
        
        # Test data encryption/decryption
        data = b"test data"
        encrypted = manager.encrypt_data(data)
        decrypted = manager.decrypt_data(encrypted)
        assert decrypted == data

    def test_encrypt_decrypt_string(self, encryption_config, temp_dir):
        encryption_config['security']['key_path'] = str(temp_dir)
        manager = EncryptionManager(encryption_config)
        
        # Test string encryption/decryption
        text = "test string"
        encrypted = manager.encrypt_string(text)
        decrypted = manager.decrypt_string(encrypted)
        assert decrypted == text

@pytest.fixture
def security_logger_config():
    return {
        'security': {
            'log_file': 'test_security.log'
        }
    }

class TestSecurityLogger:
    def test_log_security_event(self, security_logger_config, temp_dir):
        security_logger_config['security']['log_file'] = str(temp_dir / 'security.log')
        logger = SecurityLogger(security_logger_config)
        
        # Test logging security event
        logger.log_security_event(
            event_type='test',
            severity='info',
            status='success',
            user_id='test_user',
            details={'test': 'data'}
        )
        
        # Verify log file exists and contains event
        log_file = temp_dir / 'security.log'
        assert log_file.exists()
        content = log_file.read_text()
        assert 'test_user' in content
        assert 'success' in content

class TestVulnerabilityScanner:
    def test_scan_dependencies(self, temp_dir):
        scanner = VulnerabilityScanner({})
        
        # Create test requirements file
        req_file = temp_dir / 'requirements.txt'
        req_file.write_text('requests==2.25.1\ndjango==2.2.0\n')
        
        # Test dependency scanning
        results = scanner.scan_dependencies()
        assert isinstance(results, dict)
        assert 'scan_type' in results
        assert results['scan_type'] == 'dependency'

    def test_scan_code(self, temp_dir):
        scanner = VulnerabilityScanner({})
        
        # Create test Python file with potential security issue
        test_file = temp_dir / 'test.py'
        test_file.write_text('password = "hardcoded_password"')
        
        # Test code scanning
        results = scanner.scan_code()
        assert isinstance(results, dict)
        assert 'scan_type' in results
        assert results['scan_type'] == 'code'
