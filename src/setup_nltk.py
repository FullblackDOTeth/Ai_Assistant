"""
NLTK Setup Script
Created: 2024-12-14T19:42:55-05:00
"""

import os
import nltk
from pathlib import Path

def setup_nltk():
    # Set up NLTK data directory
    nltk_data_dir = Path('E:/Head Ai/data/nltk_data')
    nltk_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Set NLTK data path
    nltk.data.path.append(str(nltk_data_dir))
    
    # Download required NLTK data
    for package in ['punkt', 'averaged_perceptron_tagger', 'wordnet']:
        try:
            nltk.download(package, download_dir=str(nltk_data_dir))
            print(f"Successfully downloaded {package}")
        except Exception as e:
            print(f"Error downloading {package}: {str(e)}")

if __name__ == "__main__":
    setup_nltk()
