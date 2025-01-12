import json
import logging
import smtplib
import requests
from typing import Dict, List, Optional
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertManager:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize notification channels
        self.email_enabled = self.config.get('notifications.email.enabled', False)
        self.slack_enabled = self.config.get('notifications.slack.enabled', False)
        
        # Alert history
        self._alert_history: List[Dict] = []
        
    def trigger_alert(self, title: str, message: str, severity: str = 'warning',
                     metadata: Optional[Dict] = None) -> None:
        """Trigger an alert and send notifications through configured channels."""
        alert = {
            'title': title,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        # Store alert in history
        self._alert_history.append(alert)
        
        # Log alert
        log_level = getattr(logging, severity.upper(), logging.WARNING)
        self.logger.log(log_level, f"Alert: {title} - {message}")
        
        # Send notifications
        try:
            if self.email_enabled:
                self._send_email_alert(alert)
            if self.slack_enabled:
                self._send_slack_alert(alert)
        except Exception as e:
            self.logger.error(f"Failed to send alert notifications: {str(e)}")
            
    def _send_email_alert(self, alert: Dict) -> None:
        """Send alert via email."""
        if not self.email_enabled:
            return
            
        try:
            smtp_config = self.config.get('notifications.email', {})
            
            msg = MIMEMultipart()
            msg['From'] = smtp_config.get('from_email', 'alerts@headai.com')
            msg['To'] = smtp_config.get('to_email', 'admin@headai.com')
            msg['Subject'] = f"[{alert['severity'].upper()}] {alert['title']}"
            
            # Create HTML content
            html = f"""
            <html>
                <body>
                    <h2>{alert['title']}</h2>
                    <p><strong>Severity:</strong> {alert['severity']}</p>
                    <p><strong>Time:</strong> {alert['timestamp']}</p>
                    <p><strong>Message:</strong></p>
                    <p>{alert['message']}</p>
                    
                    <h3>Additional Information:</h3>
                    <pre>{json.dumps(alert['metadata'], indent=2)}</pre>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            with smtplib.SMTP(smtp_config['smtp_host'], smtp_config['smtp_port']) as server:
                if smtp_config.get('smtp_user') and smtp_config.get('smtp_password'):
                    server.login(smtp_config['smtp_user'], smtp_config['smtp_password'])
                server.send_message(msg)
                
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {str(e)}")
            
    def _send_slack_alert(self, alert: Dict) -> None:
        """Send alert to Slack."""
        if not self.slack_enabled:
            return
            
        try:
            slack_config = self.config.get('notifications.slack', {})
            webhook_url = slack_config.get('webhook_url')
            
            if not webhook_url:
                self.logger.error("Slack webhook URL not configured")
                return
                
            # Create Slack message
            severity_color = {
                'info': '#36a64f',
                'warning': '#ffcc00',
                'error': '#ff0000',
                'critical': '#7b001c'
            }.get(alert['severity'], '#cccccc')
            
            message = {
                "attachments": [{
                    "color": severity_color,
                    "title": alert['title'],
                    "text": alert['message'],
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert['severity'].upper(),
                            "short": True
                        },
                        {
                            "title": "Time",
                            "value": alert['timestamp'],
                            "short": True
                        }
                    ],
                    "footer": "Head AI Monitoring"
                }]
            }
            
            # Add metadata if present
            if alert['metadata']:
                message['attachments'][0]['fields'].append({
                    "title": "Additional Information",
                    "value": f"```{json.dumps(alert['metadata'], indent=2)}```",
                    "short": False
                })
            
            # Send to Slack
            response = requests.post(webhook_url, json=message)
            response.raise_for_status()
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {str(e)}")
            
    def get_alert_history(self, severity: Optional[str] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> List[Dict]:
        """Get alert history with optional filtering."""
        alerts = self._alert_history
        
        if severity:
            alerts = [a for a in alerts if a['severity'] == severity]
            
        if start_time:
            alerts = [a for a in alerts if datetime.fromisoformat(a['timestamp']) >= start_time]
            
        if end_time:
            alerts = [a for a in alerts if datetime.fromisoformat(a['timestamp']) <= end_time]
            
        return alerts
        
    def clear_alert_history(self) -> None:
        """Clear alert history."""
        self._alert_history = []
