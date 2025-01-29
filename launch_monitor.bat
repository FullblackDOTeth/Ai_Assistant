@echo off
echo Starting Head AI Server Monitor...

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "monitor_env" (
    echo Creating monitor environment...
    python -m venv monitor_env
)

REM Activate environment and install dependencies
call monitor_env\Scripts\activate
pip install -r monitor_requirements.txt > nul 2>&1

REM Start the monitor in the background
start /b "" pythonw src/server_monitor.py

REM Don't close the window immediately
exit /b 0
