import asyncio
from pathlib import Path
import subprocess
from rich.prompt import Confirm
from dependency_monitor import DependencyMonitor

async def resolve_conflicts():
    monitor = DependencyMonitor("requirements.txt")
    
    if not Path(monitor.conflict_log_file).exists():
        print("No conflicts found.")
        return

    conflicts = monitor.check_conflicts()
    if not conflicts:
        print("All dependencies are up to date!")
        return

    print("\nFound the following conflicts:")
    monitor.display_conflicts()
    
    for conflict in conflicts:
        package = conflict["package"]
        required_version = conflict["required_version"]
        
        if Confirm.ask(f"\nDo you want to fix {package} (install version {required_version})?"):
            cmd = monitor.generate_fix_command(package, required_version)
            try:
                subprocess.run(cmd.split(), check=True)
                await monitor.mark_conflict_resolved(package)
                print(f"\n✅ Successfully updated {package} to version {required_version}")
            except subprocess.CalledProcessError as e:
                print(f"\n❌ Failed to update {package}: {str(e)}")
        else:
            print(f"Skipping {package}")

if __name__ == "__main__":
    asyncio.run(resolve_conflicts())
