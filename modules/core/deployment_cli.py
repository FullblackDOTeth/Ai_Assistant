"""
Command-line interface for Head AI deployment tools
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional

from .deployment import get_deployment_manager

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description='Head AI Deployment Tools',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create release package
    release_parser = subparsers.add_parser('release', help='Create release package')
    release_parser.add_argument('--portable', action='store_true', help='Create portable package')
    release_parser.add_argument('--installer', action='store_true', help='Create installer')
    release_parser.add_argument('--version', help='Version number for the release')
    
    # Install locally
    install_parser = subparsers.add_parser('install', help='Install Head AI locally')
    install_parser.add_argument('--dir', help='Installation directory (optional)')
    
    # Module management
    module_parser = subparsers.add_parser('module', help='Module management')
    module_parser.add_argument('action', choices=['list', 'pack', 'install'])
    module_parser.add_argument('--name', help='Module name')
    module_parser.add_argument('--version', help='Module version')
    
    # Update
    update_parser = subparsers.add_parser('update', help='Update Head AI')
    update_parser.add_argument('--check-only', action='store_true', help='Only check for updates')
    
    return parser

def handle_release(args) -> int:
    """Handle release command"""
    deployer = get_deployment_manager()
    
    if args.version:
        deployer.set_version(args.version)
    
    if args.portable or not (args.portable or args.installer):
        if deployer.prepare_release():
            logging.info("Portable package created successfully")
        else:
            logging.error("Failed to create portable package")
            return 1
    
    if args.installer:
        if deployer.create_installer():
            logging.info("Installer created successfully")
        else:
            logging.error("Failed to create installer")
            return 1
    
    return 0

def handle_install(args) -> int:
    """Handle install command"""
    deployer = get_deployment_manager()
    
    install_dir = args.dir if args.dir else None
    if deployer.install_locally(install_dir):
        logging.info("Head AI installed successfully")
        return 0
    else:
        logging.error("Installation failed")
        return 1

def handle_module(args) -> int:
    """Handle module command"""
    deployer = get_deployment_manager()
    
    if args.action == 'list':
        modules = deployer.module_manager.list_modules()
        print("\nInstalled Modules:")
        for module in modules:
            print(f"- {module['name']} (v{module['version']})")
        return 0
    
    elif args.action == 'pack':
        if not args.name:
            logging.error("Module name required for pack action")
            return 1
        if deployer.module_manager.pack_module(args.name):
            logging.info(f"Module {args.name} packed successfully")
            return 0
        else:
            logging.error(f"Failed to pack module {args.name}")
            return 1
    
    elif args.action == 'install':
        if not args.name:
            logging.error("Module name required for install action")
            return 1
        if deployer.module_manager.install_module(args.name, args.version):
            logging.info(f"Module {args.name} installed successfully")
            return 0
        else:
            logging.error(f"Failed to install module {args.name}")
            return 1
    
    return 1

def handle_update(args) -> int:
    """Handle update command"""
    deployer = get_deployment_manager()
    
    if args.check_only:
        updates = deployer.check_updates()
        if updates:
            print("\nUpdates available:")
            for update in updates:
                print(f"- {update['name']} (current: v{update['current_version']} → new: v{update['new_version']})")
        else:
            print("No updates available")
        return 0
    
    if deployer.update():
        logging.info("Head AI updated successfully")
        return 0
    else:
        logging.error("Update failed")
        return 1

def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point"""
    setup_logging()
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == 'release':
            return handle_release(args)
        elif args.command == 'install':
            return handle_install(args)
        elif args.command == 'module':
            return handle_module(args)
        elif args.command == 'update':
            return handle_update(args)
    except Exception as e:
        logging.error(f"Command failed: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
