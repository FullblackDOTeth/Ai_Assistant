import json
import os
from datetime import datetime
import logging
from pathlib import Path

class FeedbackCollector:
    def __init__(self, storage_dir="feedback"):
        """Initialize the feedback collector."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Initialize feedback categories
        self.categories = {
            "installation": {"weight": 1.0, "responses": []},
            "voice_recognition": {"weight": 1.0, "responses": []},
            "ui_experience": {"weight": 1.0, "responses": []},
            "performance": {"weight": 1.0, "responses": []},
            "features": {"weight": 1.0, "responses": []}
        }

    def collect_feedback(self, feedback_data):
        """Collect and store feedback."""
        try:
            # Add timestamp
            feedback_data["timestamp"] = datetime.now().isoformat()
            
            # Generate unique filename
            filename = f"feedback_{feedback_data['timestamp'].replace(':', '-')}.json"
            filepath = self.storage_dir / filename
            
            # Store feedback
            with open(filepath, 'w') as f:
                json.dump(feedback_data, f, indent=4)
            
            # Update categories
            for category, rating in feedback_data.get("ratings", {}).items():
                if category in self.categories:
                    self.categories[category]["responses"].append(rating)
            
            self.logger.info(f"Feedback stored successfully: {filename}")
            return True, filename
            
        except Exception as e:
            self.logger.error(f"Error storing feedback: {str(e)}")
            return False, str(e)

    def analyze_feedback(self):
        """Analyze collected feedback."""
        analysis = {
            "total_responses": 0,
            "category_averages": {},
            "common_issues": [],
            "feature_requests": [],
            "overall_satisfaction": 0.0
        }
        
        # Process all feedback files
        for file in self.storage_dir.glob("feedback_*.json"):
            try:
                with open(file, 'r') as f:
                    feedback = json.load(f)
                    analysis["total_responses"] += 1
                    
                    # Process ratings
                    for category, rating in feedback.get("ratings", {}).items():
                        if category not in analysis["category_averages"]:
                            analysis["category_averages"][category] = []
                        analysis["category_averages"][category].append(rating)
                    
                    # Process issues and requests
                    if "issues" in feedback:
                        analysis["common_issues"].extend(feedback["issues"])
                    if "feature_requests" in feedback:
                        analysis["feature_requests"].extend(feedback["feature_requests"])
                        
            except Exception as e:
                self.logger.error(f"Error processing feedback file {file}: {str(e)}")
        
        # Calculate averages
        for category, ratings in analysis["category_averages"].items():
            if ratings:
                analysis["category_averages"][category] = sum(ratings) / len(ratings)
        
        # Calculate overall satisfaction
        if analysis["category_averages"]:
            total = sum(analysis["category_averages"].values())
            count = len(analysis["category_averages"])
            analysis["overall_satisfaction"] = total / count
        
        return analysis

    def export_feedback_report(self, output_file="feedback_report.md"):
        """Export feedback analysis to a markdown report."""
        analysis = self.analyze_feedback()
        
        report = [
            "# Head AI Feedback Report",
            f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n## Overview",
            f"Total Responses: {analysis['total_responses']}",
            f"Overall Satisfaction: {analysis['overall_satisfaction']:.2f}/5.0",
            "\n## Category Ratings",
        ]
        
        for category, average in analysis["category_averages"].items():
            report.append(f"- {category.replace('_', ' ').title()}: {average:.2f}/5.0")
        
        report.extend([
            "\n## Common Issues",
            *(f"- {issue}" for issue in set(analysis["common_issues"])),
            "\n## Feature Requests",
            *(f"- {request}" for request in set(analysis["feature_requests"]))
        ])
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
        
        return output_file

    def get_feedback_template(self):
        """Return the feedback form template."""
        return {
            "ratings": {
                "installation": 0,  # 1-5 rating
                "voice_recognition": 0,
                "ui_experience": 0,
                "performance": 0,
                "features": 0
            },
            "system_info": {
                "os_version": "",
                "python_version": "",
                "head_ai_version": ""
            },
            "issues": [],  # List of encountered issues
            "feature_requests": [],  # List of feature requests
            "comments": ""  # General comments
        }
