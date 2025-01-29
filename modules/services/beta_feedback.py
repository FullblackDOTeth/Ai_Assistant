"""
Beta Testing Feedback Module
Handles feedback collection, crash reporting, and telemetry
"""

import os
import json
import logging
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import psutil
import platform
import uuid
import requests

logger = logging.getLogger(__name__)

class BetaFeedback:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config/beta_config.yaml")
        self.feedback_dir = Path("feedback")
        self.crash_dir = Path("crash_reports")
        self.telemetry_dir = Path("telemetry")
        
        # Create directories
        for dir_path in [self.feedback_dir, self.crash_dir, self.telemetry_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize session
        self.session_id = str(uuid.uuid4())
        self.start_time = datetime.now()
    
    def _load_config(self) -> dict:
        """Load beta configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {}
    
    def submit_feedback(self, category: str, feedback: str, screenshots: List[Path] = None) -> bool:
        """Submit user feedback"""
        try:
            feedback_data = {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'category': category,
                'feedback': feedback,
                'system_info': self._get_system_info() if self.config['telemetry']['collect_usage_stats'] else None
            }
            
            # Save feedback
            feedback_file = self.feedback_dir / f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(feedback_file, 'w') as f:
                json.dump(feedback_data, f, indent=2)
            
            # Handle screenshots
            if screenshots:
                screenshot_dir = self.feedback_dir / 'screenshots' / feedback_file.stem
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                for i, screenshot in enumerate(screenshots):
                    shutil.copy2(screenshot, screenshot_dir / f"screenshot_{i}.png")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit feedback: {e}")
            return False
    
    def report_crash(self, error: Exception, context: Dict = None) -> bool:
        """Report application crash"""
        try:
            if not self.config['crash_reporting']['enabled']:
                return False
            
            crash_data = {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': self._get_traceback(),
                'context': context,
                'system_info': self._get_system_info() if self.config['crash_reporting']['include_system_info'] else None
            }
            
            # Save crash report
            crash_file = self.crash_dir / f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(crash_file, 'w') as f:
                json.dump(crash_data, f, indent=2)
            
            # Clean old reports
            self._clean_old_reports()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to report crash: {e}")
            return False
    
    def collect_telemetry(self) -> bool:
        """Collect telemetry data"""
        try:
            if not self.config['telemetry']['collect_performance_metrics']:
                return False
            
            telemetry_data = {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'session_duration': (datetime.now() - self.start_time).total_seconds(),
                'performance': self._get_performance_metrics(),
                'system_info': self._get_system_info()
            }
            
            # Save telemetry
            telemetry_file = self.telemetry_dir / f"telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(telemetry_file, 'w') as f:
                json.dump(telemetry_data, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to collect telemetry: {e}")
            return False
    
    def _get_system_info(self) -> Dict:
        """Get system information"""
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_space': psutil.disk_usage('/').total
        }
    
    def _get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()._asdict()
        }
    
    def _get_traceback(self) -> str:
        """Get formatted traceback"""
        import traceback
        return traceback.format_exc()
    
    def _clean_old_reports(self):
        """Clean old crash reports"""
        max_reports = self.config['crash_reporting']['max_reports']
        reports = sorted(self.crash_dir.glob('*.json'), key=os.path.getctime, reverse=True)
        
        for report in reports[max_reports:]:
            report.unlink()
    
    def end_session(self):
        """End feedback session"""
        if self.config['telemetry']['collect_usage_stats']:
            self.collect_telemetry()

def get_beta_feedback() -> BetaFeedback:
    """Get or create beta feedback instance"""
    return BetaFeedback()
