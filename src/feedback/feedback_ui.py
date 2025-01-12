import tkinter as tk
from tkinter import ttk
import platform
import sys
from .feedback_collector import FeedbackCollector

class FeedbackUI:
    def __init__(self, parent):
        """Initialize the feedback UI."""
        self.parent = parent
        self.feedback_collector = FeedbackCollector()
        
        # Create feedback window
        self.window = tk.Toplevel(parent)
        self.window.title("Head AI Feedback")
        self.window.geometry("600x800")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self._create_rating_section()
        self._create_system_info_section()
        self._create_issues_section()
        self._create_feature_requests_section()
        self._create_comments_section()
        self._create_submit_button()

    def _create_rating_section(self):
        """Create the rating section of the feedback form."""
        ttk.Label(self.main_frame, text="Rate your experience (1-5):", font=('Arial', 12, 'bold')).grid(row=0, column=0, pady=10)
        
        self.ratings = {}
        categories = [
            "Installation Experience",
            "Voice Recognition",
            "UI Experience",
            "Performance",
            "Features"
        ]
        
        for i, category in enumerate(categories):
            ttk.Label(self.main_frame, text=category).grid(row=i+1, column=0, pady=5)
            rating_var = tk.StringVar(value="5")
            rating_scale = ttk.Scale(
                self.main_frame,
                from_=1,
                to=5,
                orient=tk.HORIZONTAL,
                variable=rating_var
            )
            rating_scale.grid(row=i+1, column=1, pady=5)
            self.ratings[category.lower().replace(" ", "_")] = rating_var

    def _create_system_info_section(self):
        """Create the system information section."""
        row = len(self.ratings) + 2
        ttk.Label(self.main_frame, text="System Information", font=('Arial', 12, 'bold')).grid(row=row, column=0, pady=10)
        
        # Automatically collect system info
        self.system_info = {
            "os_version": platform.platform(),
            "python_version": sys.version.split()[0],
            "head_ai_version": "v0.1.0-beta"  # Update this dynamically
        }
        
        for i, (key, value) in enumerate(self.system_info.items()):
            ttk.Label(self.main_frame, text=f"{key.replace('_', ' ').title()}: {value}").grid(
                row=row+i+1, column=0, columnspan=2, pady=2
            )

    def _create_issues_section(self):
        """Create the issues section."""
        row = len(self.ratings) + len(self.system_info) + 3
        ttk.Label(self.main_frame, text="Issues Encountered", font=('Arial', 12, 'bold')).grid(row=row, column=0, pady=10)
        
        self.issues_text = tk.Text(self.main_frame, height=4, width=50)
        self.issues_text.grid(row=row+1, column=0, columnspan=2, pady=5)

    def _create_feature_requests_section(self):
        """Create the feature requests section."""
        row = len(self.ratings) + len(self.system_info) + 5
        ttk.Label(self.main_frame, text="Feature Requests", font=('Arial', 12, 'bold')).grid(row=row, column=0, pady=10)
        
        self.features_text = tk.Text(self.main_frame, height=4, width=50)
        self.features_text.grid(row=row+1, column=0, columnspan=2, pady=5)

    def _create_comments_section(self):
        """Create the comments section."""
        row = len(self.ratings) + len(self.system_info) + 7
        ttk.Label(self.main_frame, text="Additional Comments", font=('Arial', 12, 'bold')).grid(row=row, column=0, pady=10)
        
        self.comments_text = tk.Text(self.main_frame, height=4, width=50)
        self.comments_text.grid(row=row+1, column=0, columnspan=2, pady=5)

    def _create_submit_button(self):
        """Create the submit button."""
        row = len(self.ratings) + len(self.system_info) + 9
        ttk.Button(self.main_frame, text="Submit Feedback", command=self._submit_feedback).grid(
            row=row, column=0, columnspan=2, pady=20
        )

    def _submit_feedback(self):
        """Collect and submit feedback."""
        feedback_data = {
            "ratings": {
                key: float(var.get()) for key, var in self.ratings.items()
            },
            "system_info": self.system_info,
            "issues": [issue.strip() for issue in self.issues_text.get("1.0", tk.END).split('\n') if issue.strip()],
            "feature_requests": [feature.strip() for feature in self.features_text.get("1.0", tk.END).split('\n') if feature.strip()],
            "comments": self.comments_text.get("1.0", tk.END).strip()
        }
        
        success, result = self.feedback_collector.collect_feedback(feedback_data)
        
        if success:
            tk.messagebox.showinfo("Success", "Thank you for your feedback!")
            self.window.destroy()
        else:
            tk.messagebox.showerror("Error", f"Failed to submit feedback: {result}")

def show_feedback_form(parent):
    """Show the feedback form."""
    return FeedbackUI(parent)
