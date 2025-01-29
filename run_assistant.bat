@echo off
echo Starting Head AI...

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found! Please run setup.bat first.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo Environment file not found! Please run setup.bat and configure your .env file.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Start the assistant with error handling
echo Launching Head AI...
python src/main.py

REM If there's an error, pause to show the message
if errorlevel 1 (
    echo.
    echo An error occurred while running Head AI.
    echo Please check the logs in ./logs directory for details.
    pause
)

deactivate
