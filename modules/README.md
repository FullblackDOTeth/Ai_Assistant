# Head AI Modules

This directory contains all the core modules developed for the Head AI system.

## Module Categories

### Core Modules
- **Module Manager**: Handles module lifecycle and dependencies
- **Server Manager**: Manages server operations and configuration
- **Deployment Manager**: Handles packaging and distribution

### Utility Modules
- **File Utils**: File system operations and management
- **Web Utils**: Web-related utilities and operations
- **Security Utils**: Security and authentication utilities

### Service Modules
- **Server Monitor**: System tray monitoring and control
- **Learning Service**: AI learning and adaptation
- **Feedback Collector**: User feedback management

## Module Structure
Each module follows a standard structure:
```
module_name/
├── __init__.py
├── main.py
├── config/
│   └── default_config.yaml
├── tests/
│   └── test_module.py
└── README.md
```

## Usage
Modules can be imported and used independently:

```python
from modules.core import ModuleManager
from modules.services import ServerMonitor
```

## Development
To add a new module:
1. Create a new directory under the appropriate category
2. Include required files (main.py, __init__.py, etc.)
3. Add module documentation
4. Register module with ModuleManager
