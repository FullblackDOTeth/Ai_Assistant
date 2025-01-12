import logging
import logging.handlers
import os
import json
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

class LogManager:
    def __init__(self, config: Dict):
        self.config = config
        self.log_dir = Path(config.get('logging.directory', 'logs'))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        self._configure_logging()
        
        # Get logger
        self.logger = logging.getLogger(__name__)
        
    def _configure_logging(self) -> None:
        """Configure logging with different handlers and formatters."""
        log_level = getattr(logging, self.config.get('logging.level', 'INFO'))
        
        # Create formatters
        standard_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )
        
        json_formatter = logging.Formatter(
            lambda x: json.dumps({
                'timestamp': datetime.utcnow().isoformat(),
                'level': x.levelname,
                'logger': x.name,
                'message': x.getMessage(),
                'module': x.module,
                'function': x.funcName,
                'line': x.lineno,
                'thread': x.thread,
                'thread_name': x.threadName
            }, default=str)
        )
        
        # File handler for all logs
        main_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'head_ai.log',
            maxBytes=10_000_000,  # 10MB
            backupCount=10
        )
        main_handler.setFormatter(standard_formatter)
        
        # File handler for errors
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'errors.log',
            maxBytes=10_000_000,
            backupCount=10
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(json_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(standard_formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove existing handlers
        root_logger.handlers = []
        
        # Add handlers
        root_logger.addHandler(main_handler)
        root_logger.addHandler(error_handler)
        root_logger.addHandler(console_handler)
        
    def get_logs(self, level: Optional[str] = None,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None,
                 limit: int = 1000) -> list:
        """Retrieve logs with optional filtering."""
        logs = []
        log_file = self.log_dir / 'head_ai.log'
        
        if not log_file.exists():
            return logs
            
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        # Parse log entry
                        if '[' not in line or ']' not in line:
                            continue
                            
                        timestamp_str = line[:23]  # Extract timestamp
                        log_level = line[line.find('[')+1:line.find(']')]
                        message = line[line.find(':')+2:].strip()
                        
                        # Apply filters
                        if level and log_level != level:
                            continue
                            
                        timestamp = datetime.strptime(timestamp_str, 
                                                    '%Y-%m-%d %H:%M:%S,%f')
                                                    
                        if start_time and timestamp < start_time:
                            continue
                            
                        if end_time and timestamp > end_time:
                            continue
                            
                        logs.append({
                            'timestamp': timestamp,
                            'level': log_level,
                            'message': message
                        })
                        
                        if len(logs) >= limit:
                            break
                            
                    except Exception as e:
                        self.logger.error(f"Error parsing log line: {str(e)}")
                        
        except Exception as e:
            self.logger.error(f"Error reading log file: {str(e)}")
            
        return logs
        
    def get_error_logs(self, start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None,
                      limit: int = 100) -> list:
        """Retrieve error logs with optional time filtering."""
        logs = []
        error_file = self.log_dir / 'errors.log'
        
        if not error_file.exists():
            return logs
            
        try:
            with open(error_file, 'r') as f:
                for line in f:
                    try:
                        # Parse JSON log entry
                        log_entry = json.loads(line)
                        timestamp = datetime.fromisoformat(log_entry['timestamp'])
                        
                        # Apply time filters
                        if start_time and timestamp < start_time:
                            continue
                            
                        if end_time and timestamp > end_time:
                            continue
                            
                        logs.append(log_entry)
                        
                        if len(logs) >= limit:
                            break
                            
                    except json.JSONDecodeError:
                        self.logger.error("Error parsing JSON log entry")
                        
        except Exception as e:
            self.logger.error(f"Error reading error log file: {str(e)}")
            
        return logs
        
    def cleanup_old_logs(self, days: int = 30) -> None:
        """Clean up log files older than specified days."""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        try:
            for log_file in self.log_dir.glob('*.log*'):
                if log_file.stat().st_mtime < cutoff:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log file: {log_file}")
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {str(e)}")
            
    def log_metric(self, metric_name: str, value: float,
                  metadata: Optional[Dict] = None) -> None:
        """Log a metric value with optional metadata."""
        log_entry = {
            'metric': metric_name,
            'value': value,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if metadata:
            log_entry['metadata'] = metadata
            
        self.logger.info(f"Metric: {json.dumps(log_entry)}")
        
    def log_event(self, event_type: str, description: str,
                  metadata: Optional[Dict] = None) -> None:
        """Log an application event with optional metadata."""
        log_entry = {
            'event_type': event_type,
            'description': description,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if metadata:
            log_entry['metadata'] = metadata
            
        self.logger.info(f"Event: {json.dumps(log_entry)}")
