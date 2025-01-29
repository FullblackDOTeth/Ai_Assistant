@echo off
echo Setting up Head AI...

REM Check Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python 3.8 or higher.
    exit /b 1
)

REM Check version file
if exist "version.txt" (
    set /p VERSION=<version.txt
    echo Installing Head AI version %VERSION%
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment!
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment!
    exit /b 1
)

REM Upgrade pip and setuptools
echo Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo Warning: Failed to upgrade pip and setuptools, continuing anyway...
)

REM Install PyTorch first
echo Installing PyTorch...
pip install torch==2.1.2+cpu -f https://download.pytorch.org/whl/torch_stable.html
if errorlevel 1 (
    echo Failed to install PyTorch!
    exit /b 1
)

REM Install other requirements
echo Installing other dependencies...
pip install -r requirements.txt --no-deps
if errorlevel 1 (
    echo Failed to install other dependencies!
    exit /b 1
)

REM Set up environment file if it doesn't exist
if not exist ".env" (
    echo Creating environment file...
    copy .env.example .env
    echo Please edit .env with your API keys
)

REM Initialize NLTK
echo Setting up NLTK...
python src/setup_nltk.py
if errorlevel 1 (
    echo Warning: NLTK setup encountered issues, continuing anyway...
)

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "conversations" mkdir conversations

REM Run diagnostic check
echo Running diagnostic check...
call scripts\diagnose.bat

echo.
echo Setup complete! Please edit .env with your API keys if you haven't already.
echo Run 'run_assistant.bat' to start Head AI.
pause
