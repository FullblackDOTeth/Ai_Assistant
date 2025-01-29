import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path
import subprocess
import sys
import webbrowser
from rich.console import Console
import asyncio
from functools import partial
from datetime import datetime
import os

class ConflictNotifier:
    def __init__(self):
        self.console = Console()
        # Use absolute path for docs
        self.docs_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'dependency_resolution.md')))
        
    def create_popup(self, conflicts):
        if not conflicts:
            print("No conflicts found.")
            return

        root = tk.Tk()
        root.title("Dependency Conflict Detected")
        
        # Make window stay on top
        root.attributes('-topmost', True)
        
        # Set window position to bottom right
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 400
        window_height = 500  # Increased default height
        
        x_position = screen_width - window_width - 20
        y_position = screen_height - window_height - 40
        
        # Set minimum window size
        root.minsize(window_width, 400)  # Enforce minimum height
        root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Style
        style = ttk.Style()
        style.configure("Conflict.TLabel", padding=10, font=('Helvetica', 10))
        style.configure("Header.TLabel", padding=10, font=('Helvetica', 12, 'bold'))
        style.configure("Action.TButton", padding=5)
        style.configure("Alternate.TFrame", background="#f0f0f0")

        # Main container with grid layout
        root.grid_rowconfigure(1, weight=1)  # Make middle row expandable
        root.grid_columnconfigure(0, weight=1)  # Make column expandable

        # Header (row 0)
        header = ttk.Label(
            root, 
            text=f"⚠️ {len(conflicts)} Dependency Conflict{'s' if len(conflicts) > 1 else ''} Detected", 
            style="Header.TLabel"
        )
        header.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Scrollable frame for conflicts (row 1)
        content_frame = ttk.Frame(root)
        content_frame.grid(row=1, column=0, sticky='nsew', padx=5)
        
        # Configure content frame grid
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(content_frame)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Configure canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout for canvas and scrollbar
        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Add conflicts to scrollable frame
        for i, conflict in enumerate(conflicts):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill='x', padx=5, pady=2)
            
            conflict_text = (
                f"📦 {conflict['package']}\n"
                f"Required: {conflict['required_version']}\n"
                f"Installed: {conflict['installed_version']}"
            )
            label = ttk.Label(
                frame, 
                text=conflict_text, 
                style="Conflict.TLabel",
                wraplength=350  # Ensure text wraps within window
            )
            label.pack(fill='x')

        # Buttons frame (row 2)
        button_frame = ttk.Frame(root)
        button_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=10)

        def run_resolution():
            root.withdraw()
            try:
                script_path = os.path.join(os.path.dirname(__file__), "resolve_conflicts.py")
                subprocess.run([sys.executable, script_path], check=True)
                root.destroy()
            except subprocess.CalledProcessError:
                root.deiconify()

        def show_documentation():
            if not self.docs_path.exists():
                self.create_documentation()
            if sys.platform == 'win32':
                os.startfile(str(self.docs_path))
            else:
                webbrowser.open(str(self.docs_path))

        # Configure button frame columns
        button_frame.grid_columnconfigure(1, weight=1)  # Middle space between left and right buttons

        ttk.Button(
            button_frame,
            text="🔧 Resolve Conflicts",
            command=run_resolution,
            style="Action.TButton"
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_frame,
            text="📚 View Documentation",
            command=show_documentation,
            style="Action.TButton"
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            button_frame,
            text="✖ Dismiss",
            command=root.destroy,
            style="Action.TButton"
        ).grid(row=0, column=2, padx=5)

        root.mainloop()

    def create_documentation(self):
        """Create documentation for dependency resolution"""
        self.docs_path.parent.mkdir(exist_ok=True)
        
        doc_content = """# Dependency Conflict Resolution Guide

## Overview
This guide explains how to handle dependency conflicts in your project.

## Automatic Conflict Detection
The system automatically checks for conflicts:
1. When running tests
2. During continuous monitoring
3. When new packages are installed

## Resolution Options

### 1. Using the GUI Tool
When you see a conflict notification:
1. Click "Resolve Conflicts" to launch the interactive resolver
2. Follow the prompts to update packages
3. The system will automatically verify the resolution

### 2. Manual Resolution
You can also resolve conflicts manually:

```bash
# Check for conflicts
python testing/utils/dependency_monitor.py

# Resolve conflicts
python testing/utils/resolve_conflicts.py
```

### 3. Code Reference

To check conflicts in your code:
```python
from testing.utils.dependency_monitor import DependencyMonitor
monitor = DependencyMonitor("requirements.txt")
conflicts = monitor.check_conflicts()
monitor.display_conflicts()
```

## Conflict Log
All conflicts are logged in `dependency_conflicts.json` with:
- Package name
- Required version
- Installed version
- Detection timestamp
- Resolution status

## Need Help?
If you encounter any issues:
1. Check the logs in `dependency_monitor.log`
2. Review the conflict history in `dependency_conflicts.json`
3. Run the resolution tool with `--debug` flag for more information
"""
        
        with open(self.docs_path, 'w') as f:
            f.write(doc_content)

def show_notification(conflicts):
    """Show notification popup for conflicts"""
    notifier = ConflictNotifier()
    notifier.create_popup(conflicts)

if __name__ == "__main__":
    # Test notification with sample conflicts
    sample_conflicts = [
        {
            "package": "requests",
            "required_version": "2.28.0",
            "installed_version": "2.27.0",
            "timestamp": datetime.now().isoformat(),
            "resolved": False
        }
    ]
    show_notification(sample_conflicts)
