import psutil
import time
import logging
import json
from pathlib import Path
from datetime import datetime
import threading
import queue
from typing import Dict, List, Any

class SystemMonitor:
    def __init__(self, log_dir: str = "logs/system"):
        """Initialize the system monitor."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.metrics_queue = queue.Queue()
        self.running = False
        
        # Initialize metrics storage
        self.current_metrics: Dict[str, Any] = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0,
            "response_times": [],
            "error_count": 0
        }
        
        # Configure monitoring intervals (in seconds)
        self.intervals = {
            "system": 5,  # System metrics every 5 seconds
            "performance": 60,  # Performance metrics every minute
            "logging": 300  # Log to file every 5 minutes
        }

    def start_monitoring(self):
        """Start the monitoring system."""
        self.running = True
        
        # Start monitoring threads
        self.monitor_thread = threading.Thread(target=self._monitor_system)
        self.logging_thread = threading.Thread(target=self._log_metrics)
        
        self.monitor_thread.start()
        self.logging_thread.start()
        
        self.logger.info("System monitoring started")

    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.running = False
        self.monitor_thread.join()
        self.logging_thread.join()
        self.logger.info("System monitoring stopped")

    def _monitor_system(self):
        """Monitor system metrics."""
        while self.running:
            try:
                # Collect CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Collect memory metrics
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # Collect disk metrics
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                
                # Update current metrics
                self.current_metrics.update({
                    "timestamp": datetime.now().isoformat(),
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory_percent,
                    "disk_usage": disk_percent
                })
                
                # Add to metrics queue
                self.metrics_queue.put(self.current_metrics.copy())
                
                time.sleep(self.intervals["system"])
                
            except Exception as e:
                self.logger.error(f"Error monitoring system: {str(e)}")
                time.sleep(5)  # Wait before retrying

    def _log_metrics(self):
        """Log collected metrics to file."""
        while self.running:
            try:
                metrics_list = []
                
                # Collect all available metrics
                while not self.metrics_queue.empty():
                    metrics_list.append(self.metrics_queue.get())
                
                if metrics_list:
                    # Create log filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    log_file = self.log_dir / f"system_metrics_{timestamp}.json"
                    
                    # Write metrics to file
                    with open(log_file, 'w') as f:
                        json.dump(metrics_list, f, indent=2)
                
                time.sleep(self.intervals["logging"])
                
            except Exception as e:
                self.logger.error(f"Error logging metrics: {str(e)}")
                time.sleep(5)  # Wait before retrying

    def record_response_time(self, response_time: float):
        """Record API response time."""
        self.current_metrics["response_times"].append(response_time)
        if len(self.current_metrics["response_times"]) > 100:
            self.current_metrics["response_times"].pop(0)

    def record_error(self, error_type: str, error_message: str):
        """Record an error occurrence."""
        self.current_metrics["error_count"] += 1
        
        # Log error details
        error_log = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": error_message
        }
        
        error_file = self.log_dir / "errors.json"
        try:
            if error_file.exists():
                with open(error_file, 'r') as f:
                    errors = json.load(f)
            else:
                errors = []
            
            errors.append(error_log)
            
            with open(error_file, 'w') as f:
                json.dump(errors, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error logging error details: {str(e)}")

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get the current system metrics."""
        return self.current_metrics.copy()

    def get_average_response_time(self) -> float:
        """Calculate average response time."""
        times = self.current_metrics["response_times"]
        return sum(times) / len(times) if times else 0

    def get_error_rate(self) -> float:
        """Calculate error rate (errors per hour)."""
        try:
            error_file = self.log_dir / "errors.json"
            if not error_file.exists():
                return 0.0
            
            with open(error_file, 'r') as f:
                errors = json.load(f)
            
            # Calculate errors in the last hour
            now = datetime.now()
            hour_ago = now.timestamp() - 3600
            
            recent_errors = [e for e in errors 
                           if datetime.fromisoformat(e["timestamp"]).timestamp() > hour_ago]
            
            return len(recent_errors)
            
        except Exception as e:
            self.logger.error(f"Error calculating error rate: {str(e)}")
            return 0.0
