"""
GUI for Head AI deployment tools
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from pathlib import Path
import threading
import queue
import logging
from typing import Optional, Callable

from ..core.deployment import get_deployment_manager
from ..core.marketplace import ModuleMarketplace

class DeploymentGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.deployment_manager = get_deployment_manager()
        self.marketplace = ModuleMarketplace()
        
        # Setup GUI
        self.title("Head AI Deployment Tools")
        self.geometry("800x600")
        
        # Create tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tab_deployment = self.tabview.add("Deployment")
        self.tab_modules = self.tabview.add("Modules")
        self.tab_updates = self.tabview.add("Updates")
        
        # Setup each tab
        self._setup_deployment_tab()
        self._setup_modules_tab()
        self._setup_updates_tab()
        
        # Progress queue
        self.progress_queue = queue.Queue()
        self.after(100, self._check_progress_queue)
    
    def _setup_deployment_tab(self):
        """Setup deployment tab"""
        frame = ctk.CTkFrame(self.tab_deployment)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Release section
        release_frame = ctk.CTkFrame(frame)
        release_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(release_frame, text="Create Release Package").pack()
        
        btn_create_portable = ctk.CTkButton(
            release_frame,
            text="Create Portable Package",
            command=lambda: self._run_task(
                self.deployment_manager.prepare_release,
                "Creating portable package..."
            )
        )
        btn_create_portable.pack(pady=5)
        
        # Install section
        install_frame = ctk.CTkFrame(frame)
        install_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(install_frame, text="Local Installation").pack()
        
        btn_install = ctk.CTkButton(
            install_frame,
            text="Install Locally",
            command=lambda: self._run_task(
                self.deployment_manager.install_locally,
                "Installing Head AI..."
            )
        )
        btn_install.pack(pady=5)
        
        # Progress bar
        self.progress_deployment = ctk.CTkProgressBar(frame)
        self.progress_deployment.pack(fill=tk.X, padx=10, pady=5)
        self.progress_deployment.set(0)
    
    def _setup_modules_tab(self):
        """Setup modules tab"""
        frame = ctk.CTkFrame(self.tab_modules)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Module list
        list_frame = ctk.CTkFrame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.module_tree = ttk.Treeview(
            list_frame,
            columns=("Name", "Version", "Status"),
            show="headings"
        )
        
        self.module_tree.heading("Name", text="Name")
        self.module_tree.heading("Version", text="Version")
        self.module_tree.heading("Status", text="Status")
        
        self.module_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        btn_refresh = ctk.CTkButton(
            btn_frame,
            text="Refresh",
            command=self._refresh_module_list
        )
        btn_refresh.pack(side=tk.LEFT, padx=5)
        
        btn_install = ctk.CTkButton(
            btn_frame,
            text="Install Selected",
            command=self._install_selected_module
        )
        btn_install.pack(side=tk.LEFT, padx=5)
    
    def _setup_updates_tab(self):
        """Setup updates tab"""
        frame = ctk.CTkFrame(self.tab_updates)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Update list
        list_frame = ctk.CTkFrame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.update_tree = ttk.Treeview(
            list_frame,
            columns=("Name", "Current", "New"),
            show="headings"
        )
        
        self.update_tree.heading("Name", text="Name")
        self.update_tree.heading("Current", text="Current Version")
        self.update_tree.heading("New", text="New Version")
        
        self.update_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        btn_check = ctk.CTkButton(
            btn_frame,
            text="Check Updates",
            command=self._check_updates
        )
        btn_check.pack(side=tk.LEFT, padx=5)
        
        btn_update_all = ctk.CTkButton(
            btn_frame,
            text="Update All",
            command=self._update_all
        )
        btn_update_all.pack(side=tk.LEFT, padx=5)
    
    def _run_task(self, task: Callable, message: str):
        """Run a task in a separate thread"""
        def run():
            try:
                self.progress_queue.put(("start", message))
                result = task()
                if result:
                    self.progress_queue.put(("success", "Task completed successfully"))
                else:
                    self.progress_queue.put(("error", "Task failed"))
            except Exception as e:
                self.progress_queue.put(("error", f"Error: {str(e)}"))
            finally:
                self.progress_queue.put(("done", None))
        
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
    
    def _check_progress_queue(self):
        """Check progress queue for updates"""
        try:
            while True:
                status, message = self.progress_queue.get_nowait()
                
                if status == "start":
                    self.progress_deployment.set(0)
                    self.progress_deployment.start()
                elif status == "success":
                    self.progress_deployment.stop()
                    self.progress_deployment.set(1)
                    messagebox.showinfo("Success", message)
                elif status == "error":
                    self.progress_deployment.stop()
                    self.progress_deployment.set(0)
                    messagebox.showerror("Error", message)
                elif status == "done":
                    self.progress_deployment.stop()
        except queue.Empty:
            pass
        
        self.after(100, self._check_progress_queue)
    
    def _refresh_module_list(self):
        """Refresh module list"""
        for item in self.module_tree.get_children():
            self.module_tree.delete(item)
        
        modules = self.marketplace.list_available_modules()
        for module in modules:
            self.module_tree.insert(
                "",
                tk.END,
                values=(
                    module['name'],
                    module['version'],
                    "Installed" if module['installed'] else "Not Installed"
                )
            )
    
    def _install_selected_module(self):
        """Install selected module"""
        selection = self.module_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a module to install")
            return
        
        module_name = self.module_tree.item(selection[0])['values'][0]
        self._run_task(
            lambda: self.marketplace.install_module(module_name),
            f"Installing module {module_name}..."
        )
    
    def _check_updates(self):
        """Check for updates"""
        for item in self.update_tree.get_children():
            self.update_tree.delete(item)
        
        updates = self.marketplace.check_updates()
        for update in updates:
            self.update_tree.insert(
                "",
                tk.END,
                values=(
                    update['name'],
                    update['current_version'],
                    update['new_version']
                )
            )
        
        if not updates:
            messagebox.showinfo("Updates", "No updates available")
    
    def _update_all(self):
        """Update all modules"""
        self._run_task(
            self.marketplace.update_all,
            "Updating all modules..."
        )

def launch_deployment_gui():
    """Launch the deployment GUI"""
    app = DeploymentGUI()
    app.mainloop()

if __name__ == '__main__':
    launch_deployment_gui()
