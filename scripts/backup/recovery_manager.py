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
from typing import Dict, List, Optional, Tuple
import boto3
from botocore.exceptions import ClientError
import psycopg2
from redis import Redis

class RecoveryManager:
    def __init__(self, config_path: str):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.recovery_root = Path(self.config['recovery']['root_dir'])
        self.recovery_root.mkdir(parents=True, exist_ok=True)
        
        # AWS S3 client for remote storage
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=self.config['aws']['region']
        )

    def _setup_logging(self) -> logging.Logger:
        """Configure logging for recovery operations."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('recovery.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('RecoveryManager')

    def _load_config(self, config_path: str) -> Dict:
        """Load recovery configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def list_available_backups(self) -> Dict[str, List[str]]:
        """List all available backups in S3."""
        try:
            bucket = self.config['aws']['backup_bucket']
            backups = {
                'database': [],
                'redis': [],
                'files': []
            }
            
            objects = self.s3.list_objects_v2(Bucket=bucket, Prefix='backups/')
            
            if 'Contents' in objects:
                for obj in objects['Contents']:
                    key = obj['Key']
                    if 'db_backup_' in key:
                        backups['database'].append(key)
                    elif 'redis_backup_' in key:
                        backups['redis'].append(key)
                    elif 'files_backup_' in key:
                        backups['files'].append(key)
            
            return backups
            
        except Exception as e:
            self.logger.error(f"Failed to list backups: {str(e)}")
            raise

    def download_from_s3(self, key: str) -> Path:
        """Download backup file from S3."""
        try:
            bucket = self.config['aws']['backup_bucket']
            local_path = self.recovery_root / Path(key).name
            
            self.logger.info(f"Downloading {key} from S3")
            self.s3.download_file(bucket, key, str(local_path))
            
            return local_path
            
        except Exception as e:
            self.logger.error(f"Download failed: {str(e)}")
            raise

    def restore_database(self, backup_key: str) -> None:
        """Restore PostgreSQL database from backup."""
        try:
            # Download backup file
            backup_file = self.download_from_s3(backup_key)
            
            # Database connection details
            db_config = self.config['database']
            
            # Drop existing connections
            self._drop_db_connections()
            
            # Restore command
            cmd = [
                'pg_restore',
                '-h', db_config['host'],
                '-p', str(db_config['port']),
                '-U', db_config['user'],
                '-d', db_config['name'],
                '-c',  # Clean (drop) database objects before recreating
                '-v',  # Verbose
                str(backup_file)
            ]
            
            # Set PGPASSWORD environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['password']
            
            # Execute restore
            self.logger.info(f"Starting database restore from {backup_file}")
            process = subprocess.run(
                cmd,
                env=env,
                check=True,
                capture_output=True,
                text=True
            )
            
            self.logger.info("Database restore completed successfully")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Database restore failed: {e.stderr}")
            raise
        except Exception as e:
            self.logger.error(f"Database restore failed: {str(e)}")
            raise

    def _drop_db_connections(self) -> None:
        """Drop all existing connections to the database."""
        try:
            db_config = self.config['database']
            conn = psycopg2.connect(
                dbname='postgres',  # Connect to default database
                user=db_config['user'],
                password=db_config['password'],
                host=db_config['host'],
                port=db_config['port']
            )
            conn.autocommit = True
            
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = %s
                    AND pid <> pg_backend_pid()
                """, (db_config['name'],))
                
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to drop connections: {str(e)}")
            raise

    def restore_redis(self, backup_key: str) -> None:
        """Restore Redis data from backup."""
        try:
            # Download backup file
            backup_file = self.download_from_s3(backup_key)
            
            # Redis connection details
            redis_config = self.config['redis']
            redis_client = Redis(
                host=redis_config['host'],
                port=redis_config['port'],
                password=redis_config['password'],
                db=0
            )
            
            # Stop Redis server
            redis_client.shutdown()
            
            # Replace dump.rdb
            redis_dump = Path(redis_config['rdb_path']) / 'dump.rdb'
            shutil.copy2(backup_file, redis_dump)
            
            # Start Redis server (assuming systemd)
            subprocess.run(['systemctl', 'start', 'redis'], check=True)
            
            self.logger.info("Redis restore completed successfully")
            
        except Exception as e:
            self.logger.error(f"Redis restore failed: {str(e)}")
            raise

    def restore_files(self, backup_key: str) -> None:
        """Restore application files from backup."""
        try:
            # Download backup file
            backup_file = self.download_from_s3(backup_key)
            
            # Create temporary directory for extraction
            temp_dir = self.recovery_root / 'temp'
            temp_dir.mkdir(exist_ok=True)
            
            # Extract files
            with tarfile.open(backup_file, 'r:gz') as tar:
                tar.extractall(path=temp_dir)
            
            # Restore each directory
            for dir_path in self.config['recovery']['directories']:
                target_dir = Path(dir_path)
                source_dir = temp_dir / target_dir.name
                
                # Remove existing directory
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                
                # Copy restored files
                shutil.copytree(source_dir, target_dir)
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
            self.logger.info("File restore completed successfully")
            
        except Exception as e:
            self.logger.error(f"File restore failed: {str(e)}")
            raise

    def verify_recovery(self) -> Dict[str, bool]:
        """Verify the recovery process."""
        verification = {
            'database': False,
            'redis': False,
            'files': False
        }
        
        try:
            # Verify database
            db_config = self.config['database']
            conn = psycopg2.connect(
                dbname=db_config['name'],
                user=db_config['user'],
                password=db_config['password'],
                host=db_config['host'],
                port=db_config['port']
            )
            conn.close()
            verification['database'] = True
            
            # Verify Redis
            redis_config = self.config['redis']
            redis_client = Redis(
                host=redis_config['host'],
                port=redis_config['port'],
                password=redis_config['password'],
                db=0
            )
            redis_client.ping()
            verification['redis'] = True
            
            # Verify files
            for dir_path in self.config['recovery']['directories']:
                if not Path(dir_path).exists():
                    raise Exception(f"Directory not found: {dir_path}")
            verification['files'] = True
            
        except Exception as e:
            self.logger.error(f"Verification failed: {str(e)}")
        
        return verification

    def perform_recovery(self, backup_keys: Dict[str, str]) -> None:
        """Perform complete recovery of all components."""
        try:
            self.logger.info("Starting recovery process")
            
            # Restore database
            if 'database' in backup_keys:
                self.restore_database(backup_keys['database'])
            
            # Restore Redis
            if 'redis' in backup_keys:
                self.restore_redis(backup_keys['redis'])
            
            # Restore files
            if 'files' in backup_keys:
                self.restore_files(backup_keys['files'])
            
            # Verify recovery
            verification = self.verify_recovery()
            
            if all(verification.values()):
                self.logger.info("Recovery process completed successfully")
            else:
                failed = [k for k, v in verification.items() if not v]
                raise Exception(f"Recovery verification failed for: {', '.join(failed)}")
            
        except Exception as e:
            self.logger.error(f"Recovery process failed: {str(e)}")
            raise

def main():
    if len(sys.argv) != 2:
        print("Usage: python recovery_manager.py <config_path>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    recovery_manager = RecoveryManager(config_path)
    
    # List available backups
    backups = recovery_manager.list_available_backups()
    
    # Select most recent backups
    selected_backups = {
        component: sorted(backup_list)[-1]
        for component, backup_list in backups.items()
        if backup_list
    }
    
    # Perform recovery
    recovery_manager.perform_recovery(selected_backups)

if __name__ == "__main__":
    main()
