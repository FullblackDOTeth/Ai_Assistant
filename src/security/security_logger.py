import logging
import json
from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
import hashlib
import uuid

@dataclass
class SecurityEvent:
    event_id: str
    timestamp: str
    event_type: str
    severity: str
    user_id: Optional[str]
    ip_address: Optional[str]
    resource: Optional[str]
    action: Optional[str]
    status: str
    details: Dict[str, Any]

class SecurityLogger:
    def __init__(self, config: Dict):
        self.config = config
        
        # Configure security logger
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        
        # Add file handler for security events
        handler = logging.FileHandler(
            self.config.get('security.log_file', 'logs/security.log')
        )
        handler.setFormatter(
            logging.Formatter('%(asctime)s %(message)s')
        )
        self.logger.addHandler(handler)
        
    def log_security_event(self, event_type: str, severity: str, status: str,
                          user_id: Optional[str] = None,
                          ip_address: Optional[str] = None,
                          resource: Optional[str] = None,
                          action: Optional[str] = None,
                          details: Optional[Dict] = None) -> None:
        """Log a security event."""
        event = SecurityEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            action=action,
            status=status,
            details=details or {}
        )
        
        # Log event as JSON
        self.logger.info(json.dumps(asdict(event)))
        
        # Handle high-severity events
        if severity in ['high', 'critical']:
            self._handle_high_severity_event(event)
            
    def log_auth_attempt(self, username: str, success: bool,
                        ip_address: Optional[str] = None,
                        details: Optional[Dict] = None) -> None:
        """Log authentication attempt."""
        status = 'success' if success else 'failure'
        severity = 'info' if success else 'warning'
        
        self.log_security_event(
            event_type='authentication',
            severity=severity,
            status=status,
            user_id=username,
            ip_address=ip_address,
            details=details
        )
        
    def log_access_attempt(self, user_id: str, resource: str,
                          action: str, success: bool,
                          ip_address: Optional[str] = None,
                          details: Optional[Dict] = None) -> None:
        """Log resource access attempt."""
        status = 'success' if success else 'failure'
        severity = 'info' if success else 'warning'
        
        self.log_security_event(
            event_type='access',
            severity=severity,
            status=status,
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            action=action,
            details=details
        )
        
    def log_security_violation(self, violation_type: str,
                             user_id: Optional[str] = None,
                             ip_address: Optional[str] = None,
                             details: Optional[Dict] = None) -> None:
        """Log security violation."""
        self.log_security_event(
            event_type='violation',
            severity='high',
            status='failure',
            user_id=user_id,
            ip_address=ip_address,
            details=details
        )
        
    def _handle_high_severity_event(self, event: SecurityEvent) -> None:
        """Handle high-severity security events."""
        # Add event hash for correlation
        event_hash = self._generate_event_hash(event)
        event.details['event_hash'] = event_hash
        
        # Trigger alerts
        self._trigger_security_alert(event)
        
        # Store for analysis
        self._store_security_event(event)
        
    def _generate_event_hash(self, event: SecurityEvent) -> str:
        """Generate hash for event correlation."""
        hash_input = f"{event.event_type}:{event.user_id}:{event.ip_address}:{event.resource}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
        
    def _trigger_security_alert(self, event: SecurityEvent) -> None:
        """Trigger security alert for high-severity events."""
        from src.monitoring.alert_manager import AlertManager
        
        alert_manager = AlertManager(self.config)
        alert_manager.trigger_alert(
            title=f"Security Alert: {event.event_type}",
            message=f"High-severity security event detected: {event.details.get('message', '')}",
            severity="critical",
            metadata=asdict(event)
        )
        
    def _store_security_event(self, event: SecurityEvent) -> None:
        """Store security event for analysis."""
        # Implement storage logic (e.g., database, SIEM system)
        pass
        
class SecurityAuditLogger(SecurityLogger):
    """Extended security logger with audit capabilities."""
    
    def log_data_access(self, user_id: str, data_type: str,
                       operation: str, records_affected: int,
                       ip_address: Optional[str] = None) -> None:
        """Log data access for audit purposes."""
        self.log_security_event(
            event_type='data_access',
            severity='info',
            status='success',
            user_id=user_id,
            ip_address=ip_address,
            resource=data_type,
            action=operation,
            details={
                'records_affected': records_affected,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
    def log_configuration_change(self, user_id: str, component: str,
                               change_type: str, old_value: Any,
                               new_value: Any,
                               ip_address: Optional[str] = None) -> None:
        """Log configuration changes for audit purposes."""
        self.log_security_event(
            event_type='config_change',
            severity='info',
            status='success',
            user_id=user_id,
            ip_address=ip_address,
            resource=component,
            action=change_type,
            details={
                'old_value': old_value,
                'new_value': new_value,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
    def log_security_scan(self, scan_type: str, findings: Dict,
                         ip_address: Optional[str] = None) -> None:
        """Log security scan results."""
        severity = 'high' if any(f.get('severity') == 'high' 
                               for f in findings.get('vulnerabilities', [])) else 'info'
                               
        self.log_security_event(
            event_type='security_scan',
            severity=severity,
            status='completed',
            ip_address=ip_address,
            details={
                'scan_type': scan_type,
                'findings': findings,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
