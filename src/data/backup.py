import os
import shutil
import tarfile
import logging
from datetime import datetime
from typing import Dict, List, Optional
import subprocess
import hashlib
import json

class BackupManager:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configure backup settings
        self.backup_dir = config.get('backup.directory', 'backups')
        self.retention_days = config.get('backup.retention_days', 30)
        self.compression = config.get('backup.compression', 'gzip')
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def create_backup(self, backup_type: str = 'full') -> str:
        """Create a new backup."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{backup_type}_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Create backup directory
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup database
            db_backup_path = self._backup_database(backup_path)
            
            # Backup files
            files_backup_path = self._backup_files(backup_path)
            
            # Create manifest
            manifest = self._create_manifest(
                backup_type=backup_type,
                timestamp=timestamp,
                db_backup_path=db_backup_path,
                files_backup_path=files_backup_path
            )
            
            # Compress backup
            archive_path = self._compress_backup(backup_path, backup_name)
            
            # Clean up uncompressed files
            shutil.rmtree(backup_path)
            
            # Clean old backups
            self._cleanup_old_backups()
            
            self.logger.info(f"Backup created successfully: {archive_path}")
            return archive_path
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {str(e)}")
            raise
            
    def restore_backup(self, backup_path: str) -> bool:
        """Restore from a backup."""
        try:
            # Create temporary directory
            temp_dir = os.path.join(self.backup_dir, 'temp_restore')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract backup
            self._extract_backup(backup_path, temp_dir)
            
            # Load manifest
            manifest = self._load_manifest(temp_dir)
            
            # Restore database
            self._restore_database(os.path.join(temp_dir, manifest['db_backup']))
            
            # Restore files
            self._restore_files(os.path.join(temp_dir, manifest['files_backup']))
            
            # Clean up
            shutil.rmtree(temp_dir)
            
            self.logger.info(f"Backup restored successfully from: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup restoration failed: {str(e)}")
            raise
            
    def list_backups(self) -> List[Dict]:
        """List available backups."""
        backups = []
        for item in os.listdir(self.backup_dir):
            if item.endswith('.tar.gz'):
                path = os.path.join(self.backup_dir, item)
                stats = os.stat(path)
                backups.append({
                    'name': item,
                    'path': path,
                    'size': stats.st_size,
                    'created_at': datetime.fromtimestamp(stats.st_mtime),
                    'type': item.split('_')[0]
                })
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)
        
    def verify_backup(self, backup_path: str) -> bool:
        """Verify backup integrity."""
        try:
            # Create temporary directory
            temp_dir = os.path.join(self.backup_dir, 'temp_verify')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract backup
            self._extract_backup(backup_path, temp_dir)
            
            # Load and verify manifest
            manifest = self._load_manifest(temp_dir)
            
            # Verify checksums
            db_checksum = self._calculate_checksum(
                os.path.join(temp_dir, manifest['db_backup'])
            )
            files_checksum = self._calculate_checksum(
                os.path.join(temp_dir, manifest['files_backup'])
            )
            
            # Clean up
            shutil.rmtree(temp_dir)
            
            return (db_checksum == manifest['db_checksum'] and 
                   files_checksum == manifest['files_checksum'])
                   
        except Exception as e:
            self.logger.error(f"Backup verification failed: {str(e)}")
            return False
            
    def _backup_database(self, backup_path: str) -> str:
        """Backup database using pg_dump."""
        try:
            db_backup_path = os.path.join(backup_path, 'database.sql')
            
            # Get database URL from config
            db_url = self.config['database']['url']
            db_name = db_url.split('/')[-1]
            
            # Run pg_dump
            subprocess.run([
                'pg_dump',
                '-h', self.config['database']['host'],
                '-U', self.config['database']['user'],
                '-d', db_name,
                '-f', db_backup_path
            ], check=True)
            
            return db_backup_path
            
        except Exception as e:
            self.logger.error(f"Database backup failed: {str(e)}")
            raise
            
    def _backup_files(self, backup_path: str) -> str:
        """Backup important files and directories."""
        try:
            files_backup_path = os.path.join(backup_path, 'files')
            os.makedirs(files_backup_path, exist_ok=True)
            
            # Define paths to backup
            backup_paths = self.config.get('backup.paths', [
                'models',
                'datasets',
                'configs'
            ])
            
            # Copy files
            for path in backup_paths:
                if os.path.exists(path):
                    dst = os.path.join(files_backup_path, os.path.basename(path))
                    if os.path.isdir(path):
                        shutil.copytree(path, dst)
                    else:
                        shutil.copy2(path, dst)
                        
            return files_backup_path
            
        except Exception as e:
            self.logger.error(f"Files backup failed: {str(e)}")
            raise
            
    def _create_manifest(self, backup_type: str, timestamp: str,
                        db_backup_path: str, files_backup_path: str) -> Dict:
        """Create backup manifest."""
        manifest = {
            'type': backup_type,
            'timestamp': timestamp,
            'db_backup': os.path.basename(db_backup_path),
            'files_backup': os.path.basename(files_backup_path),
            'db_checksum': self._calculate_checksum(db_backup_path),
            'files_checksum': self._calculate_checksum(files_backup_path)
        }
        
        # Save manifest
        manifest_path = os.path.join(
            os.path.dirname(db_backup_path),
            'manifest.json'
        )
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
            
        return manifest
        
    def _compress_backup(self, backup_path: str, backup_name: str) -> str:
        """Compress backup directory."""
        archive_path = os.path.join(self.backup_dir, f"{backup_name}.tar.gz")
        
        with tarfile.open(archive_path, f"w:gz") as tar:
            tar.add(backup_path, arcname=os.path.basename(backup_path))
            
        return archive_path
        
    def _extract_backup(self, backup_path: str, target_dir: str) -> None:
        """Extract backup archive."""
        with tarfile.open(backup_path, 'r:gz') as tar:
            tar.extractall(target_dir)
            
    def _load_manifest(self, backup_dir: str) -> Dict:
        """Load backup manifest."""
        manifest_path = os.path.join(
            backup_dir,
            os.listdir(backup_dir)[0],
            'manifest.json'
        )
        with open(manifest_path, 'r') as f:
            return json.load(f)
            
    def _restore_database(self, db_backup_path: str) -> None:
        """Restore database from backup."""
        try:
            # Get database URL from config
            db_url = self.config['database']['url']
            db_name = db_url.split('/')[-1]
            
            # Run psql to restore
            subprocess.run([
                'psql',
                '-h', self.config['database']['host'],
                '-U', self.config['database']['user'],
                '-d', db_name,
                '-f', db_backup_path
            ], check=True)
            
        except Exception as e:
            self.logger.error(f"Database restore failed: {str(e)}")
            raise
            
    def _restore_files(self, files_backup_path: str) -> None:
        """Restore files from backup."""
        try:
            for item in os.listdir(files_backup_path):
                src = os.path.join(files_backup_path, item)
                dst = os.path.join(os.path.dirname(files_backup_path), item)
                
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)
                        
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                    
        except Exception as e:
            self.logger.error(f"Files restore failed: {str(e)}")
            raise
            
    def _cleanup_old_backups(self) -> None:
        """Clean up old backups based on retention policy."""
        try:
            backups = self.list_backups()
            cutoff_date = datetime.now().timestamp() - (self.retention_days * 86400)
            
            for backup in backups:
                if backup['created_at'].timestamp() < cutoff_date:
                    os.remove(backup['path'])
                    self.logger.info(f"Removed old backup: {backup['path']}")
                    
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {str(e)}")
            
    def _calculate_checksum(self, path: str) -> str:
        """Calculate SHA-256 checksum of a file or directory."""
        sha256 = hashlib.sha256()
        
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
        else:
            for root, _, files in os.walk(path):
                for file in sorted(files):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b''):
                            sha256.update(chunk)
                            
        return sha256.hexdigest()
