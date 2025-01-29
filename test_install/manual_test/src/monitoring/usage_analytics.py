import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict

class UsageAnalytics:
    def __init__(self, analytics_dir: str = "logs/analytics"):
        """Initialize the usage analytics system."""
        self.analytics_dir = Path(analytics_dir)
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize analytics storage
        self.current_session = {
            "start_time": datetime.now().isoformat(),
            "commands": [],
            "features_used": defaultdict(int),
            "voice_commands": 0,
            "text_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0
        }

    def record_command(self, command_type: str, command: str, success: bool, duration: float):
        """Record a command execution."""
        command_data = {
            "timestamp": datetime.now().isoformat(),
            "type": command_type,
            "command": command,
            "success": success,
            "duration": duration
        }
        
        self.current_session["commands"].append(command_data)
        
        # Update counters
        if command_type == "voice":
            self.current_session["voice_commands"] += 1
        elif command_type == "text":
            self.current_session["text_commands"] += 1
            
        if success:
            self.current_session["successful_commands"] += 1
        else:
            self.current_session["failed_commands"] += 1

    def record_feature_usage(self, feature_name: str):
        """Record usage of a specific feature."""
        self.current_session["features_used"][feature_name] += 1

    def save_session(self):
        """Save the current session data."""
        try:
            # Add end time to session
            self.current_session["end_time"] = datetime.now().isoformat()
            
            # Calculate session duration
            start_time = datetime.fromisoformat(self.current_session["start_time"])
            end_time = datetime.fromisoformat(self.current_session["end_time"])
            self.current_session["duration"] = (end_time - start_time).total_seconds()
            
            # Convert defaultdict to regular dict for JSON serialization
            self.current_session["features_used"] = dict(self.current_session["features_used"])
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_file = self.analytics_dir / f"session_{timestamp}.json"
            
            with open(session_file, 'w') as f:
                json.dump(self.current_session, f, indent=2)
                
            # Reset session data
            self.current_session = {
                "start_time": datetime.now().isoformat(),
                "commands": [],
                "features_used": defaultdict(int),
                "voice_commands": 0,
                "text_commands": 0,
                "successful_commands": 0,
                "failed_commands": 0
            }
            
        except Exception as e:
            self.logger.error(f"Error saving session data: {str(e)}")

    def generate_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate usage report for the specified number of days."""
        try:
            report = {
                "period": f"Last {days} days",
                "total_sessions": 0,
                "total_commands": 0,
                "voice_commands": 0,
                "text_commands": 0,
                "success_rate": 0,
                "average_session_duration": 0,
                "most_used_features": {},
                "daily_usage": defaultdict(int),
                "peak_usage_hours": defaultdict(int)
            }
            
            # Calculate start date
            start_date = datetime.now() - timedelta(days=days)
            
            # Collect all session files
            session_files = list(self.analytics_dir.glob("session_*.json"))
            sessions_data = []
            
            for file in session_files:
                try:
                    with open(file, 'r') as f:
                        session = json.load(f)
                        
                    session_start = datetime.fromisoformat(session["start_time"])
                    if session_start >= start_date:
                        sessions_data.append(session)
                except Exception as e:
                    self.logger.error(f"Error reading session file {file}: {str(e)}")
            
            if not sessions_data:
                return report
            
            # Calculate metrics
            report["total_sessions"] = len(sessions_data)
            
            for session in sessions_data:
                # Command counts
                report["total_commands"] += len(session["commands"])
                report["voice_commands"] += session["voice_commands"]
                report["text_commands"] += session["text_commands"]
                
                # Success rate
                total_commands = session["successful_commands"] + session["failed_commands"]
                if total_commands > 0:
                    success_rate = session["successful_commands"] / total_commands
                    report["success_rate"] += success_rate
                
                # Session duration
                report["average_session_duration"] += session["duration"]
                
                # Feature usage
                for feature, count in session["features_used"].items():
                    if feature not in report["most_used_features"]:
                        report["most_used_features"][feature] = 0
                    report["most_used_features"][feature] += count
                
                # Daily usage
                session_date = datetime.fromisoformat(session["start_time"]).date()
                report["daily_usage"][str(session_date)] += 1
                
                # Peak usage hours
                hour = datetime.fromisoformat(session["start_time"]).hour
                report["peak_usage_hours"][str(hour)] += 1
            
            # Calculate averages
            report["success_rate"] = report["success_rate"] / report["total_sessions"]
            report["average_session_duration"] = report["average_session_duration"] / report["total_sessions"]
            
            # Convert defaultdicts to regular dicts
            report["daily_usage"] = dict(report["daily_usage"])
            report["peak_usage_hours"] = dict(report["peak_usage_hours"])
            
            # Sort most used features
            report["most_used_features"] = dict(
                sorted(report["most_used_features"].items(), 
                      key=lambda x: x[1], 
                      reverse=True)[:10]
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return report

    def export_data(self, output_file: str):
        """Export all analytics data to a single file."""
        try:
            all_data = []
            
            for file in self.analytics_dir.glob("session_*.json"):
                try:
                    with open(file, 'r') as f:
                        session_data = json.load(f)
                        all_data.append(session_data)
                except Exception as e:
                    self.logger.error(f"Error reading session file {file}: {str(e)}")
            
            with open(output_file, 'w') as f:
                json.dump(all_data, f, indent=2)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting analytics data: {str(e)}")
            return False
