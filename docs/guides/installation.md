# Head AI Installation Guide

## System Requirements

### Minimum Requirements
- Windows 10 or later
- Python 3.8 or higher
- 4GB RAM
- 500MB free disk space
- Microphone (for voice features)

### Recommended Requirements
- Windows 10/11
- Python 3.10 or higher
- 8GB RAM
- 1GB free disk space
- High-quality microphone

## Installation Steps

### 1. Python Installation
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation by opening Command Prompt and typing:
   ```
   python --version
   ```

### 2. Head AI Installation
1. Extract the Head AI package to your desired location
2. Open Command Prompt in the extracted folder
3. Run the setup script:
   ```
   setup.bat
   ```
   This will:
   - Create a virtual environment
   - Install required packages
   - Configure initial settings

### 3. First Run
1. Launch Head AI using:
   ```
   run_assistant.bat
   ```
2. The first launch may take longer as it downloads necessary models

## Verifying Installation
After installation, verify that:
1. The UI launches successfully
2. Voice recognition works (test with "Hey Assistant")
3. Text input works
4. Web search functionality works

## Common Installation Issues

### Python Not Found
If you see "python not found", ensure:
- Python is installed
- Python is added to PATH
- Try running with full path: `C:\Python3x\python.exe`

### Package Installation Fails
If pip install fails:
1. Ensure you have internet connection
2. Try updating pip:
   ```
   python -m pip install --upgrade pip
   ```
3. Install packages manually:
   ```
   pip install -r requirements.txt
   ```

### Voice Recognition Issues
If voice recognition doesn't work:
1. Check microphone connections
2. Set correct microphone as default in Windows
3. Allow microphone access in Windows privacy settings

## Need Help?
If you encounter any issues:
1. Check the [Troubleshooting Guide](../troubleshooting/general.md)
2. Submit an issue on GitHub
3. Contact support team
