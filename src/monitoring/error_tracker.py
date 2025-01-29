import logging
import json
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict

class ErrorTracker:
    def __init__(self, error_dir: str = "logs/errors"):
        """Initialize the error tracking system."""
        self.error_dir = Path(error_dir)
        self.error_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize error categories
        self.error_categories = {
            "system": ["SystemError", "MemoryError", "IOError"],
            "network": ["ConnectionError", "TimeoutError"],
            "user": ["ValueError", "InputError"],
            "permission": ["PermissionError", "AccessError"],
            "unknown": ["Exception"]
        }

    def track_error(self, error: Exception, context: Dict[str, Any] = None):
        """Track an error occurrence with context."""
        try:
            error_data = {
                "timestamp": datetime.now().isoformat(),
                "type": error.__class__.__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
                "context": context or {},
                "category": self._categorize_error(error)
            }
            
            # Create error log file for the day
            date_str = datetime.now().strftime("%Y%m%d")
            error_file = self.error_dir / f"errors_{date_str}.json"
            
            # Read existing errors or create new list
            if error_file.exists():
                with open(error_file, 'r') as f:
                    errors = json.load(f)
            else:
                errors = []
            
            errors.append(error_data)
            
            # Write updated error log
            with open(error_file, 'w') as f:
                json.dump(errors, f, indent=2)
            
            self.logger.error(f"Error tracked: {error_data['type']} - {error_data['message']}")
            
        except Exception as e:
            self.logger.error(f"Error tracking error: {str(e)}")

    def _categorize_error(self, error: Exception) -> str:
        """Categorize an error based on its type."""
        error_type = error.__class__.__name__
        
        for category, error_types in self.error_categories.items():
            if any(error_type.endswith(et) for et in error_types):
                return category
        
        return "unknown"

    def get_error_summary(self, days: int = 7) -> Dict[str, Any]:
        """Generate error summary for the specified number of days."""
        try:
            summary = {
                "period": f"Last {days} days",
                "total_errors": 0,
                "error_categories": defaultdict(int),
                "most_common_errors": defaultdict(int),
                "daily_errors": defaultdict(int),
                "error_trends": []
            }
            
            # Calculate start date
            start_date = datetime.now() - timedelta(days=days)
            
            # Collect all error files within the period
            for day in range(days):
                date = start_date + timedelta(days=day)
                date_str = date.strftime("%Y%m%d")
                error_file = self.error_dir / f"errors_{date_str}.json"
                
                if error_file.exists():
                    try:
                        with open(error_file, 'r') as f:
                            errors = json.load(f)
                            
                        for error in errors:
                            error_time = datetime.fromisoformat(error["timestamp"])
                            if error_time >= start_date:
                                # Update counters
                                summary["total_errors"] += 1
                                summary["error_categories"][error["category"]] += 1
                                summary["most_common_errors"][error["type"]] += 1
                                summary["daily_errors"][str(error_time.date())] += 1
                                
                                # Add to trends
                                summary["error_trends"].append({
                                    "timestamp": error["timestamp"],
                                    "type": error["type"],
                                    "category": error["category"]
                                })
                    except Exception as e:
                        self.logger.error(f"Error reading error file {error_file}: {str(e)}")
            
            # Convert defaultdicts to regular dicts
            summary["error_categories"] = dict(summary["error_categories"])
            summary["most_common_errors"] = dict(
                sorted(summary["most_common_errors"].items(), 
                      key=lambda x: x[1], 
                      reverse=True)[:10]
            )
            summary["daily_errors"] = dict(summary["daily_errors"])
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating error summary: {str(e)}")
            return {}

    def get_error_details(self, error_type: str = None, category: str = None, 
                         start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Get detailed error information with optional filters."""
        try:
            errors = []
            
            # Determine date range for files to check
            if start_date is None:
                start_date = datetime.now() - timedelta(days=7)
            if end_date is None:
                end_date = datetime.now()
            
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y%m%d")
                error_file = self.error_dir / f"errors_{date_str}.json"
                
                if error_file.exists():
                    try:
                        with open(error_file, 'r') as f:
                            daily_errors = json.load(f)
                            
                        for error in daily_errors:
                            error_time = datetime.fromisoformat(error["timestamp"])
                            
                            # Apply filters
                            if error_time < start_date or error_time > end_date:
                                continue
                            if error_type and error["type"] != error_type:
                                continue
                            if category and error["category"] != category:
                                continue
                            
                            errors.append(error)
                            
                    except Exception as e:
                        self.logger.error(f"Error reading error file {error_file}: {str(e)}")
                
                current_date += timedelta(days=1)
            
            return errors
            
        except Exception as e:
            self.logger.error(f"Error getting error details: {str(e)}")
            return []

    def export_error_report(self, output_file: str, days: int = 30):
        """Export detailed error report to a file."""
        try:
            summary = self.get_error_summary(days)
            details = self.get_error_details(start_date=datetime.now() - timedelta(days=days))
            
            report = {
                "summary": summary,
                "details": details
            }
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting error report: {str(e)}")
            return False
