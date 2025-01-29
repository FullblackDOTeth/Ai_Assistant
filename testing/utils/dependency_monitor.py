import pkg_resources
import json
import logging
from datetime import datetime
from pathlib import Path
import importlib.metadata
from typing import Dict, List, Optional, Tuple
import asyncio
import aiofiles
from rich.console import Console
from rich.table import Table
from conflict_notifier import show_notification

console = Console()

class DependencyMonitor:
    def __init__(self, requirements_file: str, conflict_log_file: str = "dependency_conflicts.json"):
        self.requirements_file = Path(requirements_file)
        self.conflict_log_file = Path(conflict_log_file)
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("DependencyMonitor")
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler("dependency_monitor.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def get_installed_packages(self) -> Dict[str, str]:
        return {dist.key: dist.version for dist in pkg_resources.working_set}

    def parse_requirements(self) -> Dict[str, str]:
        requirements = {}
        with open(self.requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('==')
                    if len(parts) == 2:
                        requirements[parts[0]] = parts[1]
        return requirements

    def check_conflicts(self) -> List[Dict]:
        installed = self.get_installed_packages()
        required = self.parse_requirements()
        conflicts = []

        for package, version in required.items():
            if package in installed:
                installed_version = installed[package]
                if installed_version != version:
                    conflicts.append({
                        "package": package,
                        "required_version": version,
                        "installed_version": installed_version,
                        "timestamp": datetime.now().isoformat(),
                        "resolved": False
                    })

        return conflicts

    async def save_conflicts(self, conflicts: List[Dict]):
        existing_conflicts = []
        if self.conflict_log_file.exists():
            async with aiofiles.open(self.conflict_log_file, 'r') as f:
                content = await f.read()
                if content:
                    existing_conflicts = json.loads(content)

        # Update existing conflicts or add new ones
        for conflict in conflicts:
            existing = next((c for c in existing_conflicts 
                           if c["package"] == conflict["package"] 
                           and not c["resolved"]), None)
            if not existing:
                existing_conflicts.append(conflict)

        async with aiofiles.open(self.conflict_log_file, 'w') as f:
            await f.write(json.dumps(existing_conflicts, indent=2))

    def display_conflicts(self):
        if not self.conflict_log_file.exists():
            console.print("[yellow]No conflict history found.[/yellow]")
            return

        with open(self.conflict_log_file, 'r') as f:
            conflicts = json.load(f)

        if not conflicts:
            console.print("[green]No dependency conflicts found.[/green]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Package")
        table.add_column("Required Version")
        table.add_column("Installed Version")
        table.add_column("Status")
        table.add_column("Timestamp")

        for conflict in conflicts:
            status = "[green]Resolved[/green]" if conflict["resolved"] else "[red]Pending[/red]"
            table.add_row(
                conflict["package"],
                conflict["required_version"],
                conflict["installed_version"],
                status,
                conflict["timestamp"]
            )

        console.print(table)

    async def mark_conflict_resolved(self, package: str):
        if self.conflict_log_file.exists():
            async with aiofiles.open(self.conflict_log_file, 'r') as f:
                content = await f.read()
                conflicts = json.loads(content) if content else []

            for conflict in conflicts:
                if conflict["package"] == package and not conflict["resolved"]:
                    conflict["resolved"] = True
                    conflict["resolution_timestamp"] = datetime.now().isoformat()

            async with aiofiles.open(self.conflict_log_file, 'w') as f:
                await f.write(json.dumps(conflicts, indent=2))

    def generate_fix_command(self, package: str, required_version: str) -> str:
        return f"pip install {package}=={required_version}"

    async def monitor(self):
        while True:
            conflicts = self.check_conflicts()
            if conflicts:
                await self.save_conflicts(conflicts)
                self.logger.warning(f"Found {len(conflicts)} dependency conflicts")
                self.display_conflicts()
                # Show GUI notification
                show_notification(conflicts)
            
            await asyncio.sleep(3600)  # Check every hour

if __name__ == "__main__":
    monitor = DependencyMonitor("requirements.txt")
    asyncio.run(monitor.monitor())
