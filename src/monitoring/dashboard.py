import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Dict, Any
from .system_monitor import SystemMonitor
from .usage_analytics import UsageAnalytics
from .error_tracker import ErrorTracker

class MonitoringDashboard:
    def __init__(self, parent):
        """Initialize the monitoring dashboard."""
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Head AI Monitoring Dashboard")
        self.window.geometry("1200x800")
        
        # Initialize monitoring systems
        self.system_monitor = SystemMonitor()
        self.usage_analytics = UsageAnalytics()
        self.error_tracker = ErrorTracker()
        
        self._create_dashboard()
        self._start_updates()

    def _create_dashboard(self):
        """Create the dashboard interface."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.system_tab = ttk.Frame(self.notebook)
        self.usage_tab = ttk.Frame(self.notebook)
        self.error_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.system_tab, text='System Metrics')
        self.notebook.add(self.usage_tab, text='Usage Analytics')
        self.notebook.add(self.error_tab, text='Error Tracking')
        
        self._setup_system_tab()
        self._setup_usage_tab()
        self._setup_error_tab()

    def _setup_system_tab(self):
        """Set up the system metrics tab."""
        # Create frames for different sections
        metrics_frame = ttk.LabelFrame(self.system_tab, text="Current Metrics")
        metrics_frame.pack(fill='x', padx=5, pady=5)
        
        # Create labels for metrics
        self.cpu_label = ttk.Label(metrics_frame, text="CPU Usage: 0%")
        self.cpu_label.pack(padx=5, pady=2)
        
        self.memory_label = ttk.Label(metrics_frame, text="Memory Usage: 0%")
        self.memory_label.pack(padx=5, pady=2)
        
        self.disk_label = ttk.Label(metrics_frame, text="Disk Usage: 0%")
        self.disk_label.pack(padx=5, pady=2)
        
        # Create graph frame
        graph_frame = ttk.LabelFrame(self.system_tab, text="System Performance")
        graph_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create matplotlib figure for system metrics
        self.system_fig, (self.cpu_ax, self.memory_ax) = plt.subplots(2, 1, figsize=(10, 6))
        self.system_canvas = FigureCanvasTkAgg(self.system_fig, graph_frame)
        self.system_canvas.get_tk_widget().pack(fill='both', expand=True)

    def _setup_usage_tab(self):
        """Set up the usage analytics tab."""
        # Create frames for different sections
        stats_frame = ttk.LabelFrame(self.usage_tab, text="Usage Statistics")
        stats_frame.pack(fill='x', padx=5, pady=5)
        
        # Create labels for statistics
        self.sessions_label = ttk.Label(stats_frame, text="Total Sessions: 0")
        self.sessions_label.pack(padx=5, pady=2)
        
        self.commands_label = ttk.Label(stats_frame, text="Total Commands: 0")
        self.commands_label.pack(padx=5, pady=2)
        
        self.success_label = ttk.Label(stats_frame, text="Success Rate: 0%")
        self.success_label.pack(padx=5, pady=2)
        
        # Create graph frame
        graph_frame = ttk.LabelFrame(self.usage_tab, text="Usage Patterns")
        graph_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create matplotlib figure for usage patterns
        self.usage_fig, (self.daily_ax, self.features_ax) = plt.subplots(2, 1, figsize=(10, 6))
        self.usage_canvas = FigureCanvasTkAgg(self.usage_fig, graph_frame)
        self.usage_canvas.get_tk_widget().pack(fill='both', expand=True)

    def _setup_error_tab(self):
        """Set up the error tracking tab."""
        # Create frames for different sections
        error_stats_frame = ttk.LabelFrame(self.error_tab, text="Error Statistics")
        error_stats_frame.pack(fill='x', padx=5, pady=5)
        
        # Create labels for error statistics
        self.total_errors_label = ttk.Label(error_stats_frame, text="Total Errors: 0")
        self.total_errors_label.pack(padx=5, pady=2)
        
        self.error_rate_label = ttk.Label(error_stats_frame, text="Error Rate: 0/hour")
        self.error_rate_label.pack(padx=5, pady=2)
        
        # Create graph frame
        graph_frame = ttk.LabelFrame(self.error_tab, text="Error Trends")
        graph_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create matplotlib figure for error trends
        self.error_fig, (self.error_trend_ax, self.error_type_ax) = plt.subplots(2, 1, figsize=(10, 6))
        self.error_canvas = FigureCanvasTkAgg(self.error_fig, graph_frame)
        self.error_canvas.get_tk_widget().pack(fill='both', expand=True)

    def _start_updates(self):
        """Start periodic updates of the dashboard."""
        self.update_system_metrics()
        self.update_usage_analytics()
        self.update_error_tracking()
        
        # Schedule next updates
        self.window.after(5000, self._start_updates)  # Update every 5 seconds

    def update_system_metrics(self):
        """Update system metrics display."""
        try:
            metrics = self.system_monitor.get_current_metrics()
            
            # Update labels
            self.cpu_label.config(text=f"CPU Usage: {metrics['cpu_usage']:.1f}%")
            self.memory_label.config(text=f"Memory Usage: {metrics['memory_usage']:.1f}%")
            self.disk_label.config(text=f"Disk Usage: {metrics['disk_usage']:.1f}%")
            
            # Update graphs
            self.cpu_ax.clear()
            self.memory_ax.clear()
            
            # Plot CPU and memory usage over time
            timestamps = [datetime.fromisoformat(m["timestamp"]) for m in metrics.get("history", [])]
            cpu_values = [m["cpu_usage"] for m in metrics.get("history", [])]
            memory_values = [m["memory_usage"] for m in metrics.get("history", [])]
            
            self.cpu_ax.plot(timestamps, cpu_values)
            self.cpu_ax.set_title("CPU Usage Over Time")
            self.cpu_ax.set_ylabel("CPU %")
            
            self.memory_ax.plot(timestamps, memory_values)
            self.memory_ax.set_title("Memory Usage Over Time")
            self.memory_ax.set_ylabel("Memory %")
            
            self.system_canvas.draw()
            
        except Exception as e:
            print(f"Error updating system metrics: {str(e)}")

    def update_usage_analytics(self):
        """Update usage analytics display."""
        try:
            report = self.usage_analytics.generate_report(7)  # Last 7 days
            
            # Update labels
            self.sessions_label.config(text=f"Total Sessions: {report['total_sessions']}")
            self.commands_label.config(text=f"Total Commands: {report['total_commands']}")
            self.success_label.config(text=f"Success Rate: {report['success_rate']:.1f}%")
            
            # Update graphs
            self.daily_ax.clear()
            self.features_ax.clear()
            
            # Plot daily usage
            dates = list(report["daily_usage"].keys())
            counts = list(report["daily_usage"].values())
            self.daily_ax.bar(dates, counts)
            self.daily_ax.set_title("Daily Usage")
            self.daily_ax.tick_params(axis='x', rotation=45)
            
            # Plot feature usage
            features = list(report["most_used_features"].keys())
            usage = list(report["most_used_features"].values())
            self.features_ax.barh(features, usage)
            self.features_ax.set_title("Most Used Features")
            
            self.usage_canvas.draw()
            
        except Exception as e:
            print(f"Error updating usage analytics: {str(e)}")

    def update_error_tracking(self):
        """Update error tracking display."""
        try:
            summary = self.error_tracker.get_error_summary(7)  # Last 7 days
            
            # Update labels
            self.total_errors_label.config(text=f"Total Errors: {summary['total_errors']}")
            error_rate = summary['total_errors'] / (7 * 24)  # Errors per hour
            self.error_rate_label.config(text=f"Error Rate: {error_rate:.2f}/hour")
            
            # Update graphs
            self.error_trend_ax.clear()
            self.error_type_ax.clear()
            
            # Plot error trends
            dates = list(summary["daily_errors"].keys())
            counts = list(summary["daily_errors"].values())
            self.error_trend_ax.plot(dates, counts)
            self.error_trend_ax.set_title("Error Trends")
            self.error_trend_ax.tick_params(axis='x', rotation=45)
            
            # Plot error types
            types = list(summary["most_common_errors"].keys())
            counts = list(summary["most_common_errors"].values())
            self.error_type_ax.barh(types, counts)
            self.error_type_ax.set_title("Most Common Errors")
            
            self.error_canvas.draw()
            
        except Exception as e:
            print(f"Error updating error tracking: {str(e)}")

def show_dashboard(parent):
    """Show the monitoring dashboard."""
    return MonitoringDashboard(parent)
