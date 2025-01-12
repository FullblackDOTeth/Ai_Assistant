import time
import psutil
import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from collections import deque

@dataclass
class PerformanceMetric:
    timestamp: datetime
    name: str
    value: float
    metadata: Dict

class PerformanceMonitor:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize metric storage
        self._metrics: Dict[str, deque] = {
            'cpu': deque(maxlen=1000),
            'memory': deque(maxlen=1000),
            'disk': deque(maxlen=1000),
            'network': deque(maxlen=1000),
            'response_time': deque(maxlen=1000)
        }
        
        # Performance thresholds
        self.thresholds = config.get('monitoring.thresholds', {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90,
            'response_time': 2.0  # seconds
        })
        
        # Monitoring thread
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        
    def start_monitoring(self) -> None:
        """Start performance monitoring in a background thread."""
        if self._monitor_thread is not None:
            return
            
        self._monitor_thread = threading.Thread(target=self._monitor_performance)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        self.logger.info("Performance monitoring started")
        
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        if self._monitor_thread is None:
            return
            
        self._stop_monitoring.set()
        self._monitor_thread.join()
        self._monitor_thread = None
        self.logger.info("Performance monitoring stopped")
        
    def _monitor_performance(self) -> None:
        """Continuously monitor system performance."""
        while not self._stop_monitoring.is_set():
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                timestamp = datetime.now()
                
                # Store CPU metrics
                self._metrics['cpu'].append(PerformanceMetric(
                    timestamp=timestamp,
                    name='cpu_usage',
                    value=cpu_percent,
                    metadata={'type': 'system'}
                ))
                
                # Store memory metrics
                self._metrics['memory'].append(PerformanceMetric(
                    timestamp=timestamp,
                    name='memory_usage',
                    value=memory.percent,
                    metadata={
                        'total': memory.total,
                        'available': memory.available
                    }
                ))
                
                # Store disk metrics
                self._metrics['disk'].append(PerformanceMetric(
                    timestamp=timestamp,
                    name='disk_usage',
                    value=disk.percent,
                    metadata={
                        'total': disk.total,
                        'used': disk.used,
                        'free': disk.free
                    }
                ))
                
                # Store network metrics
                self._metrics['network'].append(PerformanceMetric(
                    timestamp=timestamp,
                    name='network_io',
                    value=network.bytes_sent + network.bytes_recv,
                    metadata={
                        'bytes_sent': network.bytes_sent,
                        'bytes_recv': network.bytes_recv
                    }
                ))
                
                # Check thresholds
                self._check_thresholds({
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent
                })
                
                # Sleep for configured interval
                time.sleep(self.config.get('monitoring.interval', 60))
                
            except Exception as e:
                self.logger.error(f"Error monitoring performance: {str(e)}")
                
    def _check_thresholds(self, metrics: Dict[str, float]) -> None:
        """Check if any metrics exceed their thresholds."""
        for metric_name, value in metrics.items():
            if metric_name in self.thresholds:
                threshold = self.thresholds[metric_name]
                if value >= threshold:
                    self.logger.warning(
                        f"Performance threshold exceeded: {metric_name} = {value} "
                        f"(threshold: {threshold})"
                    )
                    self._trigger_alert(metric_name, value, threshold)
                    
    def _trigger_alert(self, metric_name: str, value: float, threshold: float) -> None:
        """Trigger an alert for a threshold violation."""
        from src.monitoring.alert_manager import AlertManager
        
        alert_manager = AlertManager(self.config)
        alert_manager.trigger_alert(
            title=f"Performance Alert: {metric_name}",
            message=(f"Performance metric {metric_name} exceeded threshold: "
                    f"{value:.1f} >= {threshold:.1f}"),
            severity="warning",
            metadata={
                "metric": metric_name,
                "value": value,
                "threshold": threshold,
                "timestamp": datetime.now().isoformat()
            }
        )
        
    def record_response_time(self, duration: float, endpoint: str) -> None:
        """Record API endpoint response time."""
        self._metrics['response_time'].append(PerformanceMetric(
            timestamp=datetime.now(),
            name='response_time',
            value=duration,
            metadata={'endpoint': endpoint}
        ))
        
        # Check response time threshold
        if duration >= self.thresholds.get('response_time', 2.0):
            self.logger.warning(
                f"Slow response time for endpoint {endpoint}: {duration:.2f}s"
            )
            self._trigger_alert('response_time', duration, 
                              self.thresholds['response_time'])
                              
    def get_metrics(self, metric_type: str, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[PerformanceMetric]:
        """Get stored metrics for a specific type within a time range."""
        if metric_type not in self._metrics:
            return []
            
        metrics = list(self._metrics[metric_type])
        
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]
            
        return metrics
        
    def get_performance_summary(self) -> Dict:
        """Get a summary of current performance metrics."""
        summary = {}
        
        for metric_type, metrics in self._metrics.items():
            if not metrics:
                continue
                
            recent_metrics = list(metrics)[-10:]  # Last 10 measurements
            values = [m.value for m in recent_metrics]
            
            summary[metric_type] = {
                'current': values[-1],
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'timestamp': recent_metrics[-1].timestamp.isoformat()
            }
            
        return summary
