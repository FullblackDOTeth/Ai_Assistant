"""
NLTK Setup Script
Created: 2024-12-14T19:42:55-05:00
"""

import os
import nltk
from pathlib import Path
from dotenv import load_dotenv

def get_nltk_data_dir() -> Path:
    """
    Get NLTK data directory from environment variable or default to project data directory.
    Order of precedence:
    1. NLTK_DATA environment variable
    2. Project's data/nltk_data directory
    """
    # Load environment variables
    load_dotenv()
    
    # Check for NLTK_DATA environment variable
    env_path = os.getenv('NLTK_DATA')
    if env_path:
        return Path(env_path)
    
    # Default to project's data directory
    project_root = Path(__file__).parent.parent
    return project_root / 'data' / 'nltk_data'

def setup_nltk():
    """Set up NLTK data directory and download required packages"""
    # Get NLTK data directory
    nltk_data_dir = get_nltk_data_dir()
    nltk_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Set NLTK data path
    nltk.data.path.append(str(nltk_data_dir))
    
    # Required NLTK packages
    required_packages = [
        'punkt',
        'averaged_perceptron_tagger',
        'wordnet'
    ]
    
    # Download required NLTK data
    for package in required_packages:
        try:
            nltk.download(package, download_dir=str(nltk_data_dir), quiet=True)
            print(f"Successfully downloaded {package} to {nltk_data_dir}")
        except Exception as e:
            print(f"Error downloading {package}: {str(e)}")
            print(f"You can manually download {package} by running: python -m nltk.downloader {package}")

def download_nltk_data():
    """
    Wrapper function for setup_nltk() that returns success status
    Used by other modules that need to ensure NLTK data is available
    """
    try:
        setup_nltk()
        return True
    except Exception as e:
        print(f"Error setting up NLTK: {str(e)}")
        return False

if __name__ == "__main__":
    setup_nltk()
