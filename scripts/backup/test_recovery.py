#!/usr/bin/env python3

import os
import sys
import json
import logging
import datetime
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import pytest
from backup_manager import BackupManager
from recovery_manager import RecoveryManager

class TestRecovery:
    @pytest.fixture
    def config_path(self):
        return "config/backup.json"

    @pytest.fixture
    def backup_manager(self, config_path):
        return BackupManager(config_path)

    @pytest.fixture
    def recovery_manager(self, config_path):
        return RecoveryManager(config_path)

    def test_backup_creation(self, backup_manager):
        """Test creation of backups for all components."""
        try:
            backup_manager.perform_backup()
            
            # Verify backup files exist
            backup_root = Path(backup_manager.config['backup']['root_dir'])
            assert any(backup_root.glob('db_backup_*')), "Database backup not found"
            assert any(backup_root.glob('redis_backup_*')), "Redis backup not found"
            assert any(backup_root.glob('files_backup_*')), "Files backup not found"
            
        except Exception as e:
            pytest.fail(f"Backup creation failed: {str(e)}")

    def test_backup_upload(self, backup_manager):
        """Test upload of backups to S3."""
        try:
            # Create and upload backups
            backup_manager.perform_backup()
            
            # List S3 backups
            bucket = backup_manager.config['aws']['backup_bucket']
            objects = backup_manager.s3.list_objects_v2(
                Bucket=bucket,
                Prefix='backups/'
            )
            
            assert 'Contents' in objects, "No backups found in S3"
            assert len(objects['Contents']) > 0, "Empty backup list in S3"
            
        except Exception as e:
            pytest.fail(f"Backup upload failed: {str(e)}")

    def test_backup_retention(self, backup_manager):
        """Test backup retention policy."""
        try:
            # Create old backup files
            old_date = datetime.datetime.now() - datetime.timedelta(days=31)
            backup_root = Path(backup_manager.config['backup']['root_dir'])
            
            old_files = [
                backup_root / f"db_backup_old.sql",
                backup_root / f"redis_backup_old.rdb",
                backup_root / f"files_backup_old.tar.gz"
            ]
            
            for file in old_files:
                file.touch()
                os.utime(file, (old_date.timestamp(), old_date.timestamp()))
            
            # Run cleanup
            backup_manager.cleanup_old_backups()
            
            # Verify old files are removed
            for file in old_files:
                assert not file.exists(), f"Old backup file not cleaned: {file}"
            
        except Exception as e:
            pytest.fail(f"Backup retention test failed: {str(e)}")

    def test_recovery_list_backups(self, recovery_manager):
        """Test listing available backups."""
        try:
            backups = recovery_manager.list_available_backups()
            
            assert 'database' in backups, "Database backups not listed"
            assert 'redis' in backups, "Redis backups not listed"
            assert 'files' in backups, "File backups not listed"
            
        except Exception as e:
            pytest.fail(f"Listing backups failed: {str(e)}")

    def test_recovery_download(self, recovery_manager):
        """Test downloading backups from S3."""
        try:
            # Get latest backup
            backups = recovery_manager.list_available_backups()
            latest_backup = sorted(backups['database'])[-1]
            
            # Download backup
            local_file = recovery_manager.download_from_s3(latest_backup)
            
            assert local_file.exists(), "Downloaded backup file not found"
            assert local_file.stat().st_size > 0, "Downloaded backup file is empty"
            
        except Exception as e:
            pytest.fail(f"Backup download failed: {str(e)}")

    def test_database_recovery(self, recovery_manager):
        """Test database recovery process."""
        try:
            # Get latest database backup
            backups = recovery_manager.list_available_backups()
            latest_backup = sorted(backups['database'])[-1]
            
            # Perform recovery
            recovery_manager.restore_database(latest_backup)
            
            # Verify database
            verification = recovery_manager.verify_recovery()
            assert verification['database'], "Database recovery verification failed"
            
        except Exception as e:
            pytest.fail(f"Database recovery failed: {str(e)}")

    def test_redis_recovery(self, recovery_manager):
        """Test Redis recovery process."""
        try:
            # Get latest Redis backup
            backups = recovery_manager.list_available_backups()
            latest_backup = sorted(backups['redis'])[-1]
            
            # Perform recovery
            recovery_manager.restore_redis(latest_backup)
            
            # Verify Redis
            verification = recovery_manager.verify_recovery()
            assert verification['redis'], "Redis recovery verification failed"
            
        except Exception as e:
            pytest.fail(f"Redis recovery failed: {str(e)}")

    def test_files_recovery(self, recovery_manager):
        """Test file recovery process."""
        try:
            # Get latest file backup
            backups = recovery_manager.list_available_backups()
            latest_backup = sorted(backups['files'])[-1]
            
            # Perform recovery
            recovery_manager.restore_files(latest_backup)
            
            # Verify files
            verification = recovery_manager.verify_recovery()
            assert verification['files'], "File recovery verification failed"
            
        except Exception as e:
            pytest.fail(f"File recovery failed: {str(e)}")

    def test_full_recovery(self, recovery_manager):
        """Test complete recovery process."""
        try:
            # Get latest backups
            backups = recovery_manager.list_available_backups()
            selected_backups = {
                component: sorted(backup_list)[-1]
                for component, backup_list in backups.items()
                if backup_list
            }
            
            # Perform recovery
            recovery_manager.perform_recovery(selected_backups)
            
            # Verify all components
            verification = recovery_manager.verify_recovery()
            assert all(verification.values()), "Full recovery verification failed"
            
        except Exception as e:
            pytest.fail(f"Full recovery failed: {str(e)}")

def main():
    """Run recovery tests."""
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    main()
