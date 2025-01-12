#!/usr/bin/env python3

import os
import sys
import json
import logging
import shutil
import tarfile
import datetime
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError
import psycopg2
from redis import Redis

class BackupManager:
    def __init__(self, config_path: str):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.backup_root = Path(self.config['backup']['root_dir'])
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # AWS S3 client for remote storage
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=self.config['aws']['region']
        )

    def _setup_logging(self) -> logging.Logger:
        """Configure logging for backup operations."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('backup.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('BackupManager')

    def _load_config(self, config_path: str) -> Dict:
        """Load backup configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def backup_database(self) -> Path:
        """Backup PostgreSQL database."""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_root / f"db_backup_{timestamp}.sql"
            
            # Database connection details
            db_config = self.config['database']
            
            # Create pg_dump command
            cmd = [
                'pg_dump',
                '-h', db_config['host'],
                '-p', str(db_config['port']),
                '-U', db_config['user'],
                '-F', 'c',  # Custom format
                '-b',  # Include large objects
                '-v',  # Verbose
                '-f', str(backup_file),
                db_config['name']
            ]
            
            # Set PGPASSWORD environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['password']
            
            # Execute backup
            self.logger.info(f"Starting database backup to {backup_file}")
            process = subprocess.run(
                cmd,
                env=env,
                check=True,
                capture_output=True,
                text=True
            )
            
            self.logger.info("Database backup completed successfully")
            return backup_file
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Database backup failed: {e.stderr}")
            raise
        except Exception as e:
            self.logger.error(f"Database backup failed: {str(e)}")
            raise

    def backup_redis(self) -> Path:
        """Backup Redis data."""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_root / f"redis_backup_{timestamp}.rdb"
            
            # Redis connection details
            redis_config = self.config['redis']
            redis_client = Redis(
                host=redis_config['host'],
                port=redis_config['port'],
                password=redis_config['password'],
                db=0
            )
            
            # Trigger SAVE command
            self.logger.info("Triggering Redis SAVE command")
            redis_client.save()
            
            # Copy dump.rdb to backup location
            redis_dump = Path(redis_config['rdb_path']) / 'dump.rdb'
            shutil.copy2(redis_dump, backup_file)
            
            self.logger.info(f"Redis backup completed: {backup_file}")
            return backup_file
            
        except Exception as e:
            self.logger.error(f"Redis backup failed: {str(e)}")
            raise

    def backup_files(self) -> Path:
        """Backup application files."""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_root / f"files_backup_{timestamp}.tar.gz"
            
            # Create tar archive
            with tarfile.open(backup_file, "w:gz") as tar:
                # Add each directory from config
                for dir_path in self.config['backup']['directories']:
                    self.logger.info(f"Adding directory to backup: {dir_path}")
                    tar.add(dir_path, arcname=os.path.basename(dir_path))
            
            self.logger.info(f"File backup completed: {backup_file}")
            return backup_file
            
        except Exception as e:
            self.logger.error(f"File backup failed: {str(e)}")
            raise

    def upload_to_s3(self, file_path: Path) -> None:
        """Upload backup file to S3."""
        try:
            bucket = self.config['aws']['backup_bucket']
            key = f"backups/{file_path.name}"
            
            self.logger.info(f"Uploading {file_path} to S3 bucket {bucket}")
            
            # Upload file
            self.s3.upload_file(
                str(file_path),
                bucket,
                key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'StorageClass': 'STANDARD_IA'
                }
            )
            
            self.logger.info(f"Upload completed: s3://{bucket}/{key}")
            
        except ClientError as e:
            self.logger.error(f"S3 upload failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Upload failed: {str(e)}")
            raise

    def cleanup_old_backups(self) -> None:
        """Remove old backup files based on retention policy."""
        try:
            retention_days = self.config['backup']['retention_days']
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
            
            self.logger.info(f"Cleaning up backups older than {retention_days} days")
            
            # Clean local backups
            for backup_file in self.backup_root.glob('*'):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    self.logger.info(f"Removing old backup: {backup_file}")
                    backup_file.unlink()
            
            # Clean S3 backups
            bucket = self.config['aws']['backup_bucket']
            objects = self.s3.list_objects_v2(Bucket=bucket, Prefix='backups/')
            
            if 'Contents' in objects:
                for obj in objects['Contents']:
                    last_modified = obj['LastModified']
                    if last_modified.replace(tzinfo=None) < cutoff_date:
                        self.logger.info(f"Removing old S3 backup: {obj['Key']}")
                        self.s3.delete_object(Bucket=bucket, Key=obj['Key'])
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")
            raise

    def perform_backup(self) -> None:
        """Perform complete backup of all components."""
        try:
            self.logger.info("Starting backup process")
            
            # Backup database
            db_backup = self.backup_database()
            self.upload_to_s3(db_backup)
            
            # Backup Redis
            redis_backup = self.backup_redis()
            self.upload_to_s3(redis_backup)
            
            # Backup files
            files_backup = self.backup_files()
            self.upload_to_s3(files_backup)
            
            # Cleanup old backups
            self.cleanup_old_backups()
            
            self.logger.info("Backup process completed successfully")
            
        except Exception as e:
            self.logger.error(f"Backup process failed: {str(e)}")
            raise

def main():
    if len(sys.argv) != 2:
        print("Usage: python backup_manager.py <config_path>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    backup_manager = BackupManager(config_path)
    backup_manager.perform_backup()

if __name__ == "__main__":
    main()
