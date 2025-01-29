# Dependency Conflict Resolution Guide

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
