import os
import json
from pathlib import Path
from rich.console import Console

console = Console()

def get_input(prompt):
    """Get input with proper error handling"""
    try:
        return input(f"{prompt}: ").strip()
    except EOFError:
        return ""

def setup_environment():
    """Interactive environment setup script"""
    config_file = Path("testing/config/pipeline_config.json")
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    console.print("\n[bold green]CI/CD Pipeline Environment Setup[/bold green]")
    console.print("This script will help you set up your pipeline monitoring environment.\n")
    
    # Get GitHub information
    console.print("[bold]GitHub Configuration[/bold]")
    token = get_input("Enter your GitHub Personal Access Token (PAT)")
    owner = get_input("Enter your GitHub username")
    repo = get_input("Enter your repository name")
    
    # Save configuration
    config = {
        "GITHUB_TOKEN": token,
        "GITHUB_OWNER": owner,
        "GITHUB_REPO": repo
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Create batch script to set environment variables
    batch_file = Path("testing/scripts/set_environment.bat")
    batch_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(batch_file, 'w') as f:
        f.write("@echo off\n")
        f.write("echo Setting up pipeline environment variables...\n")
        for key, value in config.items():
            f.write(f'setx {key} "{value}"\n')
        f.write('echo Environment variables have been set!\n')
        f.write('pause\n')
    
    console.print("\n[bold green]✓[/bold green] Configuration saved!")
    console.print(f"\nConfiguration file created at: [cyan]{config_file.absolute()}[/cyan]")
    console.print(f"Batch script created at: [cyan]{batch_file.absolute()}[/cyan]")
    
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Run the batch script to set environment variables:")
    console.print(f"   [cyan]testing/scripts/set_environment.bat[/cyan]")
    console.print("2. Restart any open command prompts")
    console.print("3. Run the pipeline monitor:")
    console.print("   [cyan]python testing/utils/pipeline_monitor.py[/cyan]")

if __name__ == "__main__":
    setup_environment()
