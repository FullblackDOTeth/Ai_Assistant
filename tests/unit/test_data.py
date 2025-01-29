import pytest
from datetime import datetime
import os
from pathlib import Path
from sqlalchemy.orm import Session
from src.data.db_config import DatabaseConfig, Base
from src.data.models import User, Project, Dataset, Model
from src.data.backup import BackupManager
from src.data.validation import DataValidator, UserModel, ProjectModel

@pytest.fixture
def db_config():
    return {
        'database': {
            'type': 'sqlite',
            'name': ':memory:',
            'pool_size': 5,
            'max_overflow': 10
        }
    }

@pytest.fixture
def database(db_config):
    db = DatabaseConfig(db_config)
    db.init_db()
    return db

@pytest.fixture
def db_session(database):
    session = database.SessionLocal()
    try:
        yield session
    finally:
        session.close()

class TestDatabaseConfig:
    def test_init_db(self, database):
        assert database.engine is not None
        assert database.SessionLocal is not None
        
        # Test connection
        with database.engine.connect() as conn:
            result = conn.execute("SELECT 1").scalar()
            assert result == 1

    def test_get_db(self, database):
        session = next(database.get_db())
        assert isinstance(session, Session)
        session.close()

class TestModels:
    def test_user_model(self, db_session):
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hash',
            role='user'
        )
        db_session.add(user)
        db_session.commit()
        
        # Query user
        queried_user = db_session.query(User).filter_by(username='testuser').first()
        assert queried_user is not None
        assert queried_user.email == 'test@example.com'
        assert queried_user.role == 'user'

    def test_project_model(self, db_session):
        # Create test user and project
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hash'
        )
        db_session.add(user)
        db_session.flush()
        
        project = Project(
            name='Test Project',
            description='Test Description',
            owner_id=user.id
        )
        db_session.add(project)
        db_session.commit()
        
        # Query project
        queried_project = db_session.query(Project).filter_by(name='Test Project').first()
        assert queried_project is not None
        assert queried_project.description == 'Test Description'
        assert queried_project.owner_id == user.id

@pytest.fixture
def backup_config(temp_dir):
    return {
        'backup': {
            'directory': str(temp_dir / 'backups'),
            'retention_days': 7,
            'compression': 'gzip'
        }
    }

class TestBackupManager:
    def test_create_backup(self, backup_config, temp_dir):
        manager = BackupManager(backup_config)
        
        # Create test data
        data_dir = temp_dir / 'data'
        data_dir.mkdir()
        (data_dir / 'test.txt').write_text('test data')
        
        # Create backup
        backup_path = manager.create_backup()
        assert os.path.exists(backup_path)
        assert backup_path.endswith('.tar.gz')

    def test_list_backups(self, backup_config):
        manager = BackupManager(backup_config)
        
        # Create test backup
        backup_path = manager.create_backup()
        
        # List backups
        backups = manager.list_backups()
        assert len(backups) > 0
        assert backups[0]['path'] == backup_path

    def test_verify_backup(self, backup_config):
        manager = BackupManager(backup_config)
        
        # Create and verify backup
        backup_path = manager.create_backup()
        assert manager.verify_backup(backup_path)

class TestDataValidator:
    def test_validate_user_model(self):
        validator = DataValidator()
        
        # Valid user data
        valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@123',
            'role': 'user'
        }
        validated = validator.validate_model(valid_data, UserModel)
        assert validated['username'] == 'testuser'
        
        # Invalid user data
        invalid_data = {
            'username': 'test@user',  # Invalid username
            'email': 'invalid-email',  # Invalid email
            'password': '123',  # Weak password
            'role': 'user'
        }
        with pytest.raises(Exception):
            validator.validate_model(invalid_data, UserModel)

    def test_validate_project_model(self):
        validator = DataValidator()
        
        # Valid project data
        valid_data = {
            'name': 'Test Project',
            'description': 'Test Description',
            'owner_id': 'user123'
        }
        validated = validator.validate_model(valid_data, ProjectModel)
        assert validated['name'] == 'Test Project'
        
        # Invalid project data
        invalid_data = {
            'name': '',  # Empty name
            'owner_id': 'user123'
        }
        with pytest.raises(Exception):
            validator.validate_model(invalid_data, ProjectModel)

    def test_validate_email(self):
        validator = DataValidator()
        
        assert validator.validate_email('test@example.com')
        assert not validator.validate_email('invalid-email')
        assert not validator.validate_email('test@.com')

    def test_validate_password_strength(self):
        validator = DataValidator()
        
        # Strong password
        result = validator.validate_password_strength('Test@123')
        assert result['valid']
        assert len(result['errors']) == 0
        
        # Weak password
        result = validator.validate_password_strength('weak')
        assert not result['valid']
        assert len(result['errors']) > 0
