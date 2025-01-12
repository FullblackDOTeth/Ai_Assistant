import pytest
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

from src.security.auth_manager import AuthManager
from src.security.encryption import EncryptionManager
from src.data.db_config import DatabaseConfig
from src.data.models import User, Project
from src.monitoring.performance_monitor import PerformanceMonitor

@pytest.fixture
def performance_config(temp_dir):
    return {
        'security': {
            'jwt_secret': 'test_secret',
            'jwt_expiry_hours': 24,
            'key_path': str(temp_dir / 'keys')
        },
        'database': {
            'type': 'sqlite',
            'name': ':memory:',
            'pool_size': 20,
            'max_overflow': 30
        },
        'monitoring': {
            'thresholds': {
                'response_time': 1.0,
                'cpu_percent': 80,
                'memory_percent': 85
            }
        }
    }

class TestSystemPerformance:
    def test_auth_performance(self, performance_config):
        """Test authentication system performance."""
        auth_manager = AuthManager(performance_config)
        
        # Create test user
        user = auth_manager.create_user(
            username='testuser',
            email='test@example.com',
            password='Test@123'
        )
        
        # Measure authentication performance
        iterations = 100
        auth_times = []
        
        for _ in range(iterations):
            start_time = time.time()
            success, token, _ = auth_manager.authenticate('testuser', 'Test@123')
            auth_time = time.time() - start_time
            auth_times.append(auth_time)
            assert success is True
            
        # Calculate statistics
        avg_auth_time = statistics.mean(auth_times)
        p95_auth_time = statistics.quantiles(auth_times, n=20)[18]  # 95th percentile
        
        # Assert performance requirements
        assert avg_auth_time < 0.1  # Average auth time should be under 100ms
        assert p95_auth_time < 0.2  # 95th percentile should be under 200ms

    def test_encryption_performance(self, performance_config):
        """Test encryption system performance."""
        encryption_manager = EncryptionManager(performance_config)
        
        # Test data
        data_sizes = [100, 1000, 10000, 100000]  # bytes
        iterations = 50
        
        for size in data_sizes:
            test_data = b'x' * size
            encrypt_times = []
            decrypt_times = []
            
            for _ in range(iterations):
                # Test encryption
                start_time = time.time()
                encrypted = encryption_manager.encrypt_data(test_data)
                encrypt_times.append(time.time() - start_time)
                
                # Test decryption
                start_time = time.time()
                decrypted = encryption_manager.decrypt_data(encrypted)
                decrypt_times.append(time.time() - start_time)
                
                assert decrypted == test_data
                
            # Calculate statistics
            avg_encrypt = statistics.mean(encrypt_times)
            avg_decrypt = statistics.mean(decrypt_times)
            
            # Assert performance requirements based on data size
            max_time = size / 1_000_000  # 1MB/s minimum throughput
            assert avg_encrypt < max_time
            assert avg_decrypt < max_time

    def test_database_performance(self, performance_config):
        """Test database performance under load."""
        db = DatabaseConfig(performance_config)
        db.init_db()
        
        # Create test data
        num_users = 1000
        num_projects = 100
        
        session = next(db.get_db())
        try:
            # Measure bulk insert performance
            start_time = time.time()
            
            users = [
                User(
                    username=f'user{i}',
                    email=f'user{i}@example.com',
                    password_hash='hash'
                )
                for i in range(num_users)
            ]
            session.bulk_save_objects(users)
            session.commit()
            
            bulk_insert_time = time.time() - start_time
            assert bulk_insert_time < 5.0  # Should insert 1000 users under 5 seconds
            
            # Measure query performance
            query_times = []
            for _ in range(100):
                start_time = time.time()
                result = session.query(User).filter(
                    User.username.like('user%')
                ).limit(10).all()
                query_times.append(time.time() - start_time)
                
            avg_query_time = statistics.mean(query_times)
            assert avg_query_time < 0.01  # Average query should be under 10ms
            
        finally:
            session.close()

    def test_concurrent_performance(self, performance_config):
        """Test system performance under concurrent load."""
        auth_manager = AuthManager(performance_config)
        db = DatabaseConfig(performance_config)
        db.init_db()
        performance_monitor = PerformanceMonitor(performance_config)
        
        # Start performance monitoring
        performance_monitor.start_monitoring()
        
        try:
            # Create test users
            users = [
                auth_manager.create_user(
                    username=f'user{i}',
                    email=f'user{i}@example.com',
                    password='Test@123'
                )
                for i in range(10)
            ]
            
            def concurrent_operation(user_id):
                """Simulate concurrent user operations."""
                try:
                    # Authenticate
                    success, token, _ = auth_manager.authenticate(
                        f'user{user_id}',
                        'Test@123'
                    )
                    assert success is True
                    
                    # Database operations
                    session = next(db.get_db())
                    try:
                        # Create project
                        project = Project(
                            name=f'Project {user_id}',
                            owner_id=users[user_id].id
                        )
                        session.add(project)
                        session.commit()
                        
                        # Query projects
                        projects = session.query(Project).filter_by(
                            owner_id=users[user_id].id
                        ).all()
                        assert len(projects) > 0
                        
                    finally:
                        session.close()
                        
                    return True
                except Exception as e:
                    return False
                    
            # Run concurrent operations
            num_concurrent = 50
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(concurrent_operation, i % 10)
                    for i in range(num_concurrent)
                ]
                results = [future.result() for future in as_completed(futures)]
                
            # Verify results
            success_rate = sum(results) / len(results)
            assert success_rate > 0.95  # At least 95% success rate
            
            # Check performance metrics
            metrics = performance_monitor.get_performance_summary()
            assert metrics['cpu']['current'] < 80  # CPU usage under 80%
            assert metrics['memory']['current'] < 85  # Memory usage under 85%
            
        finally:
            performance_monitor.stop_monitoring()

    def test_response_time_monitoring(self, performance_config):
        """Test response time monitoring under load."""
        performance_monitor = PerformanceMonitor(performance_config)
        
        # Start monitoring
        performance_monitor.start_monitoring()
        
        try:
            # Simulate API requests with response times
            num_requests = 1000
            for i in range(num_requests):
                # Simulate request processing time
                process_time = 0.1 + (i % 5) * 0.1  # Vary between 0.1s and 0.5s
                time.sleep(process_time)
                
                # Record response time
                performance_monitor.record_response_time(
                    process_time,
                    endpoint=f'/api/endpoint{i%5}'
                )
                
            # Get performance metrics
            metrics = performance_monitor.get_metrics('response_time')
            
            # Calculate statistics
            response_times = [m.value for m in metrics]
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
            
            # Assert performance requirements
            assert avg_response_time < 0.3  # Average under 300ms
            assert p95_response_time < 0.5  # 95th percentile under 500ms
            
        finally:
            performance_monitor.stop_monitoring()
