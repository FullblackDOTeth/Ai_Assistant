"""
Test script to verify all required dependencies are installed and working
"""

def test_dependencies():
    missing = []
    errors = []
    
    # Test UI dependencies
    try:
        import customtkinter
        import tkinter
        import PIL
    except ImportError as e:
        missing.append(f"UI: {str(e)}")
    
    # Test AI dependencies
    try:
        import openai
        from dotenv import load_dotenv
    except ImportError as e:
        missing.append(f"AI: {str(e)}")
    
    # Test research dependencies
    try:
        import requests
        import bs4
        from duckduckgo_search import ddg
    except ImportError as e:
        missing.append(f"Research: {str(e)}")
    
    # Test text processing
    try:
        import nltk
        nltk.data.path  # Verify NLTK is initialized
    except ImportError as e:
        missing.append(f"Text Processing: {str(e)}")
    except LookupError as e:
        errors.append(f"NLTK data not downloaded: {str(e)}")
    
    # Test utilities
    try:
        import numpy
    except ImportError as e:
        missing.append(f"Utilities: {str(e)}")
    
    # Print results
    if not missing and not errors:
        print("✅ All dependencies are installed and working!")
        return True
    
    if missing:
        print("\n❌ Missing dependencies:")
        for m in missing:
            print(f"  - {m}")
    
    if errors:
        print("\n⚠️ Configuration errors:")
        for e in errors:
            print(f"  - {e}")
    
    return False

if __name__ == "__main__":
    print("Testing Head AI dependencies...")
    test_dependencies()
