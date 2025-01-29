import time
import psutil
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from prometheus_client import Counter, Gauge, Histogram, start_http_server

@dataclass
class MetricPoint:
    timestamp: datetime
    value: float
    labels: Dict[str, str]

class MetricsCollector:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Prometheus metrics
        self.cpu_usage = Gauge('headai_cpu_usage_percent', 'CPU usage in percent')
        self.memory_usage = Gauge('headai_memory_usage_bytes', 'Memory usage in bytes')
        self.request_latency = Histogram('headai_request_duration_seconds', 
                                       'Request duration in seconds',
                                       buckets=[0.1, 0.5, 1.0, 2.0, 5.0])
        self.error_counter = Counter('headai_errors_total', 
                                   'Total number of errors',
                                   ['type', 'severity'])
        self.active_users = Gauge('headai_active_users', 'Number of active users')
        
        # Internal metrics storage
        self._metrics_data: Dict[str, List[MetricPoint]] = {}
        self._collection_thread: Optional[threading.Thread] = None
        self._stop_collection = threading.Event()
        
        # Start Prometheus server
        start_http_server(self.config.get('monitoring.prometheus_port', 9090))

    def start_collection(self):
        """Start metrics collection in a background thread."""
        if self._collection_thread is not None:
            return

        self._collection_thread = threading.Thread(target=self._collect_metrics)
        self._collection_thread.daemon = True
        self._collection_thread.start()
        self.logger.info("Metrics collection started")

    def stop_collection(self):
        """Stop metrics collection."""
        if self._collection_thread is None:
            return

        self._stop_collection.set()
        self._collection_thread.join()
        self._collection_thread = None
        self.logger.info("Metrics collection stopped")

    def _collect_metrics(self):
        """Continuously collect system metrics."""
        while not self._stop_collection.is_set():
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # Update Prometheus metrics
                self.cpu_usage.set(cpu_percent)
                self.memory_usage.set(memory.used)
                
                # Store metrics internally
                timestamp = datetime.now()
                self._store_metric('cpu_usage', cpu_percent, timestamp)
                self._store_metric('memory_usage', memory.used, timestamp)
                
                # Check thresholds and trigger alerts
                self._check_thresholds({
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent
                })
                
                # Sleep for configured interval
                time.sleep(self.config.get('monitoring.collection_interval', 60))
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {str(e)}")
                self.error_counter.labels(type='metric_collection', severity='error').inc()

    def _store_metric(self, name: str, value: float, timestamp: datetime, 
                     labels: Optional[Dict[str, str]] = None):
        """Store a metric point."""
        if name not in self._metrics_data:
            self._metrics_data[name] = []
            
        self._metrics_data[name].append(MetricPoint(
            timestamp=timestamp,
            value=value,
            labels=labels or {}
        ))
        
        # Cleanup old data
        retention_days = self.config.get('monitoring.retention_days', 7)
        cutoff = datetime.now() - timedelta(days=retention_days)
        self._metrics_data[name] = [
            point for point in self._metrics_data[name]
            if point.timestamp > cutoff
        ]

    def _check_thresholds(self, metrics: Dict[str, float]):
        """Check metrics against configured thresholds and trigger alerts."""
        thresholds = self.config.get('monitoring.alert_thresholds', {})
        
        for metric_name, value in metrics.items():
            if metric_name in thresholds:
                threshold = thresholds[metric_name]
                if value >= threshold:
                    self.logger.warning(
                        f"Metric {metric_name} exceeded threshold: {value} >= {threshold}"
                    )
                    # Trigger alert
                    self._trigger_alert(metric_name, value, threshold)

    def _trigger_alert(self, metric_name: str, value: float, threshold: float):
        """Trigger an alert for a threshold violation."""
        from src.monitoring.alert_manager import AlertManager
        
        alert_manager = AlertManager()
        alert_manager.trigger_alert(
            title=f"Metric Alert: {metric_name}",
            message=f"Metric {metric_name} exceeded threshold: {value} >= {threshold}",
            severity="warning",
            metadata={
                "metric": metric_name,
                "value": value,
                "threshold": threshold,
                "timestamp": datetime.now().isoformat()
            }
        )

    def record_request(self, duration: float, endpoint: str):
        """Record an API request."""
        self.request_latency.observe(duration)
        self._store_metric(
            'request_latency', 
            duration, 
            datetime.now(),
            {'endpoint': endpoint}
        )

    def record_error(self, error_type: str, severity: str = 'error'):
        """Record an error occurrence."""
        self.error_counter.labels(type=error_type, severity=severity).inc()

    def update_active_users(self, count: int):
        """Update the number of active users."""
        self.active_users.set(count)

    def get_metrics(self, metric_name: str, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[MetricPoint]:
        """Get stored metrics for a specific metric name within a time range."""
        if metric_name not in self._metrics_data:
            return []
            
        metrics = self._metrics_data[metric_name]
        
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]
            
        return metrics

    def get_summary(self) -> Dict[str, Dict]:
        """Get a summary of all collected metrics."""
        summary = {}
        
        for metric_name, points in self._metrics_data.items():
            if not points:
                continue
                
            values = [p.value for p in points]
            summary[metric_name] = {
                'current': points[-1].value,
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'count': len(values)
            }
            
        return summary
