"""
Create beta release package
"""

import os
import sys
import shutil
from pathlib import Path
import json
from datetime import datetime
import logging

from modules.core.deployment import get_deployment_manager
from modules.services.beta_feedback import get_beta_feedback

def create_beta_package():
    """Create beta release package"""
    try:
        # Initialize
        deployer = get_deployment_manager()
        feedback = get_beta_feedback()
        
        # Create beta package
        print("Creating beta package...")
        if not deployer.prepare_release():
            print("Failed to create release package")
            return False
        
        # Add beta files
        beta_files = [
            'config/beta_config.yaml',
            'BETA_README.md'
        ]
        
        for file_path in beta_files:
            src = Path(file_path)
            dst = Path('dist') / src.name
            if src.exists():
                shutil.copy2(src, dst)
        
        # Create beta info
        beta_info = {
            'version': '1.0.0-beta.1',
            'release_date': datetime.now().isoformat(),
            'feedback_url': 'https://feedback.headai.com/beta',
            'support_email': 'beta@headai.com',
            'documentation_url': 'https://docs.headai.com/beta'
        }
        
        with open('dist/beta_info.json', 'w') as f:
            json.dump(beta_info, f, indent=2)
        
        print("Beta package created successfully!")
        print("\nPackage contents:")
        for item in Path('dist').glob('*'):
            print(f"- {item.name}")
        
        return True
        
    except Exception as e:
        print(f"Error creating beta package: {e}")
        return False

if __name__ == '__main__':
    sys.exit(0 if create_beta_package() else 1)
