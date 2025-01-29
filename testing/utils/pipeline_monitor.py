import tkinter as tk
from tkinter import ttk
import requests
import json
import webbrowser
from datetime import datetime
import os
from pathlib import Path
import asyncio
from rich.console import Console
from rich.table import Table

class PipelineMonitor:
    def __init__(self):
        self.console = Console()
        self.status_file = Path("pipeline_status.json")
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_owner = os.getenv("GITHUB_OWNER")
        self.repo_name = os.getenv("GITHUB_REPO")

    def create_status_window(self):
        root = tk.Tk()
        root.title("CI/CD Pipeline Monitor")
        
        # Set window size and position
        window_width = 800
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Style
        style = ttk.Style()
        style.configure("Pipeline.TLabel", padding=10, font=('Helvetica', 10))
        style.configure("Header.TLabel", padding=10, font=('Helvetica', 12, 'bold'))
        style.configure("Success.TLabel", foreground="green")
        style.configure("Failure.TLabel", foreground="red")
        style.configure("Running.TLabel", foreground="blue")

        # Main container with tabs
        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Overview tab
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="Overview")

        # Status summary
        status_frame = ttk.LabelFrame(overview_frame, text="Pipeline Status")
        status_frame.pack(fill='x', padx=5, pady=5)

        self.status_label = ttk.Label(status_frame, text="Loading...", style="Pipeline.TLabel")
        self.status_label.pack()

        # Latest runs
        runs_frame = ttk.LabelFrame(overview_frame, text="Latest Runs")
        runs_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Create treeview for runs
        columns = ("Run", "Status", "Branch", "Started", "Duration")
        self.runs_tree = ttk.Treeview(runs_frame, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            self.runs_tree.heading(col, text=col)
            self.runs_tree.column(col, width=100)

        self.runs_tree.pack(fill='both', expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(runs_frame, orient="vertical", command=self.runs_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.runs_tree.configure(yscrollcommand=scrollbar.set)

        # Tests tab
        tests_frame = ttk.Frame(notebook)
        notebook.add(tests_frame, text="Test Results")

        # Create test results tree
        test_columns = ("Test", "Status", "Duration", "Details")
        self.tests_tree = ttk.Treeview(tests_frame, columns=test_columns, show="headings")
        
        for col in test_columns:
            self.tests_tree.heading(col, text=col)
            self.tests_tree.column(col, width=150)

        self.tests_tree.pack(fill='both', expand=True)

        # Coverage tab
        coverage_frame = ttk.Frame(notebook)
        notebook.add(coverage_frame, text="Coverage")

        # Create coverage summary
        self.coverage_label = ttk.Label(coverage_frame, text="Loading coverage data...", style="Pipeline.TLabel")
        self.coverage_label.pack(pady=10)

        # Create coverage tree
        coverage_columns = ("Module", "Coverage", "Missing Lines")
        self.coverage_tree = ttk.Treeview(coverage_frame, columns=coverage_columns, show="headings")
        
        for col in coverage_columns:
            self.coverage_tree.heading(col, text=col)
            self.coverage_tree.column(col, width=150)

        self.coverage_tree.pack(fill='both', expand=True)

        # Button frame
        button_frame = ttk.Frame(root)
        button_frame.pack(fill='x', padx=5, pady=5)

        def refresh_data():
            self.update_pipeline_status()

        def open_github_actions():
            if self.repo_owner and self.repo_name:
                url = f"https://github.com/{self.repo_owner}/{self.repo_name}/actions"
                webbrowser.open(url)

        ttk.Button(
            button_frame,
            text="🔄 Refresh",
            command=refresh_data
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text="🌐 Open in GitHub",
            command=open_github_actions
        ).pack(side='left', padx=5)

        # Initial data load
        self.update_pipeline_status()
        
        # Set up auto-refresh (every 30 seconds)
        def auto_refresh():
            self.update_pipeline_status()
            root.after(30000, auto_refresh)
        
        root.after(30000, auto_refresh)
        
        root.mainloop()

    def update_pipeline_status(self):
        """Update pipeline status from GitHub Actions API"""
        if not all([self.github_token, self.repo_owner, self.repo_name]):
            self.status_label.config(
                text="⚠️ Please set GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO environment variables"
            )
            return

        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Get workflow runs
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            runs = response.json()["workflow_runs"]
            
            # Update runs treeview
            self.runs_tree.delete(*self.runs_tree.get_children())
            
            for run in runs[:10]:  # Show last 10 runs
                status = run["conclusion"] if run["conclusion"] else "running"
                started = datetime.strptime(run["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                duration = "Running..." if not run["updated_at"] else str(
                    datetime.strptime(run["updated_at"], "%Y-%m-%dT%H:%M:%SZ") - started
                )
                
                self.runs_tree.insert("", "end", values=(
                    run["display_title"],
                    status,
                    run["head_branch"],
                    started.strftime("%Y-%m-%d %H:%M"),
                    duration
                ))
            
            # Update status label
            latest_run = runs[0] if runs else None
            if latest_run:
                status = latest_run["conclusion"] if latest_run["conclusion"] else "running"
                status_text = f"Latest pipeline: {status} ({latest_run['head_branch']} branch)"
                style = f"{status.title()}.TLabel"
                self.status_label.configure(text=status_text, style=style)
            
            # Save status to file
            self.save_status(runs[:10])
            
        except Exception as e:
            self.status_label.config(
                text=f"❌ Error updating status: {str(e)}",
                style="Failure.TLabel"
            )

    def save_status(self, runs):
        """Save pipeline status to JSON file"""
        status = {
            "last_updated": datetime.now().isoformat(),
            "runs": runs
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)

    def print_status(self):
        """Print pipeline status to console"""
        if not self.status_file.exists():
            self.console.print("No pipeline status data available", style="yellow")
            return

        with open(self.status_file, 'r') as f:
            status = json.load(f)

        table = Table(title="Pipeline Status")
        table.add_column("Run")
        table.add_column("Status")
        table.add_column("Branch")
        table.add_column("Started")

        for run in status["runs"]:
            status_style = {
                "success": "green",
                "failure": "red",
                "running": "blue"
            }.get(run["conclusion"] or "running", "white")

            table.add_row(
                run["display_title"],
                run["conclusion"] or "running",
                run["head_branch"],
                datetime.strptime(run["created_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M"),
                style=status_style
            )

        self.console.print(table)

def main():
    monitor = PipelineMonitor()
    monitor.create_status_window()

if __name__ == "__main__":
    main()
