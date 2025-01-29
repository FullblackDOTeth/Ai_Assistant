"""
Configure Head AI environment and server settings
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.server_manager import server_manager
from src.core.module_manager import module_manager

def main():
    """Configure environment and display status"""
    print("Configuring Head AI Environment...")
    
    # Setup server environment
    if server_manager.setup_server_environment():
        print("\n✓ Server environment configured successfully")
    else:
        print("\n✗ Failed to configure server environment")
        return False
    
    # Display current status
    status = server_manager.get_server_status()
    print("\nServer Status:")
    print(f"Admin Mode: {'Enabled' if status['admin_mode'] else 'Disabled'}")
    print(f"Process Priority: {status['process_info']['priority']}")
    print(f"Memory Limit: {status['process_info']['memory_limit']}")
    
    # Verify module dependencies
    print("\nVerifying module dependencies...")
    for module in module_manager.modules:
        missing = module_manager.verify_dependencies(module)
        if missing:
            print(f"Module '{module}' missing dependencies: {missing}")
        else:
            print(f"Module '{module}' dependencies verified ✓")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
