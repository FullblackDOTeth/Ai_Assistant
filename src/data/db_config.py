from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from typing import Dict, Optional
import logging
import os

# Initialize logger
logger = logging.getLogger(__name__)

# Create declarative base
Base = declarative_base()

class DatabaseConfig:
    def __init__(self, config: Dict):
        self.config = config
        self.engine = None
        self.SessionLocal = None
        
    def init_db(self) -> None:
        """Initialize database connection."""
        try:
            # Get database URL from config
            db_url = self._get_database_url()
            
            # Create engine with connection pooling
            self.engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=self.config.get('database.pool_size', 5),
                max_overflow=self.config.get('database.max_overflow', 10),
                pool_timeout=self.config.get('database.pool_timeout', 30),
                pool_recycle=self.config.get('database.pool_recycle', 3600),
                echo=self.config.get('database.echo', False)
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise
            
    def _get_database_url(self) -> str:
        """Get database URL from config or environment."""
        # Try to get from environment first
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            return db_url
            
        # Build URL from config
        db_config = self.config.get('database', {})
        db_type = db_config.get('type', 'postgresql')
        db_user = db_config.get('user', 'postgres')
        db_pass = db_config.get('password', '')
        db_host = db_config.get('host', 'localhost')
        db_port = db_config.get('port', '5432')
        db_name = db_config.get('name', 'headai')
        
        return f"{db_type}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        
    def get_db(self):
        """Get database session."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    def check_connection(self) -> bool:
        """Check database connection."""
        try:
            # Try to connect and execute a simple query
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {str(e)}")
            return False
            
    def create_database(self) -> None:
        """Create database if it doesn't exist."""
        try:
            # Get database URL without database name
            db_url = self._get_database_url()
            db_name = db_url.split('/')[-1]
            base_url = '/'.join(db_url.split('/')[:-1])
            
            # Create engine without database name
            temp_engine = create_engine(f"{base_url}/postgres")
            
            # Check if database exists
            with temp_engine.connect() as conn:
                conn.execute("commit")
                result = conn.execute(
                    f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"
                )
                if not result.scalar():
                    conn.execute("commit")
                    conn.execute(f"CREATE DATABASE {db_name}")
                    logger.info(f"Created database: {db_name}")
                    
        except Exception as e:
            logger.error(f"Database creation error: {str(e)}")
            raise
            
    def drop_database(self) -> None:
        """Drop database (use with caution!)."""
        try:
            # Get database URL without database name
            db_url = self._get_database_url()
            db_name = db_url.split('/')[-1]
            base_url = '/'.join(db_url.split('/')[:-1])
            
            # Create engine without database name
            temp_engine = create_engine(f"{base_url}/postgres")
            
            # Drop database if it exists
            with temp_engine.connect() as conn:
                conn.execute("commit")
                conn.execute(f"DROP DATABASE IF EXISTS {db_name}")
                logger.info(f"Dropped database: {db_name}")
                
        except Exception as e:
            logger.error(f"Database drop error: {str(e)}")
            raise
