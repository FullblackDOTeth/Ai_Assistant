"""
Setup Head AI repository with proper Git LFS configuration
"""

import os
import shutil
from pathlib import Path
import subprocess
import sys

def run_command(cmd, cwd=None):
    """Run a command and return output"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command {cmd}: {e}")
        return None

def setup_repository():
    """Setup the repository with proper configuration"""
    # Paths
    source_dir = Path("E:/Head Ai")
    target_dir = Path("D:/Head Ai")
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Files/directories to exclude from copy
    exclude = {
        # Binaries and large files
        "GitHubDesktopSetup.exe",
        "python-3.8.10-embed-amd64",
        # Virtual environments
        "venv",
        ".venv",
        "build_env",
        "monitor_env",
        # Cache and temporary files
        "__pycache__",
        ".pytest_cache",
        # Build directories
        "build",
        "dist",
        # Git directory (we'll initialize a new one)
        ".git"
    }
    
    # Copy files
    def copy_filtered(src, dst):
        if src.name in exclude or any(p.name in exclude for p in src.parents):
            return
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        elif src.is_dir():
            for item in src.iterdir():
                copy_filtered(item, dst / item.name)
    
    print("Copying project files...")
    copy_filtered(source_dir, target_dir)
    
    # Initialize Git repository
    print("\nInitializing Git repository...")
    run_command(["git", "init"], cwd=target_dir)
    
    # Setup Git LFS
    print("\nSetting up Git LFS...")
    run_command(["git", "lfs", "install"], cwd=target_dir)
    
    # Create .gitattributes for LFS
    gitattributes = """
# Audio files
*.mp3 filter=lfs diff=lfs merge=lfs -text
*.wav filter=lfs diff=lfs merge=lfs -text
*.ogg filter=lfs diff=lfs merge=lfs -text

# Image files
*.jpg filter=lfs diff=lfs merge=lfs -text
*.jpeg filter=lfs diff=lfs merge=lfs -text
*.png filter=lfs diff=lfs merge=lfs -text
*.gif filter=lfs diff=lfs merge=lfs -text
*.ico filter=lfs diff=lfs merge=lfs -text

# Video files
*.mp4 filter=lfs diff=lfs merge=lfs -text
*.mov filter=lfs diff=lfs merge=lfs -text

# Document files
*.pdf filter=lfs diff=lfs merge=lfs -text
*.docx filter=lfs diff=lfs merge=lfs -text
*.xlsx filter=lfs diff=lfs merge=lfs -text

# Archive files
*.zip filter=lfs diff=lfs merge=lfs -text
*.rar filter=lfs diff=lfs merge=lfs -text
*.7z filter=lfs diff=lfs merge=lfs -text

# Binary files
*.exe filter=lfs diff=lfs merge=lfs -text
*.dll filter=lfs diff=lfs merge=lfs -text
*.so filter=lfs diff=lfs merge=lfs -text
*.dylib filter=lfs diff=lfs merge=lfs -text

# Model files
*.onnx filter=lfs diff=lfs merge=lfs -text
*.pt filter=lfs diff=lfs merge=lfs -text
*.pth filter=lfs diff=lfs merge=lfs -text
*.h5 filter=lfs diff=lfs merge=lfs -text
*.model filter=lfs diff=lfs merge=lfs -text
"""
    
    with open(target_dir / ".gitattributes", "w") as f:
        f.write(gitattributes.strip())
    
    # Update .gitignore
    gitignore = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environments
.env
.venv
env/
venv/
ENV/
build_env/
monitor_env/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Testing
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Logs
*.log
logs/
log/

# Local development
local_settings.py
db.sqlite3
db.sqlite3-journal

# Media
media/

# Temporary files
*.bak
*.tmp
*.temp

# System files
.DS_Store
Thumbs.db

# Project specific
config/local.yaml
secrets/
private/
temp/
"""
    
    with open(target_dir / ".gitignore", "w") as f:
        f.write(gitignore.strip())
    
    # Initialize the repository
    print("\nInitializing repository...")
    run_command(["git", "add", "."], cwd=target_dir)
    run_command(["git", "commit", "-m", "Initial commit with Git LFS setup"], cwd=target_dir)
    
    print("\nRepository setup complete!")
    print("\nNext steps:")
    print("1. cd D:/Head Ai")
    print("2. git remote add origin https://github.com/FullblackDOTeth/Ai_Assistant.git")
    print("3. git push -u origin main --force")

if __name__ == "__main__":
    setup_repository()
