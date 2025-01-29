@echo off
echo Running Head AI Diagnostics...
echo ============================

REM Check Python version
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo [ERROR] Python not found or not in PATH
) else (
    echo [OK] Python is installed
)

REM Check virtual environment
echo.
echo Checking virtual environment...
if exist "venv" (
    echo [OK] Virtual environment exists
) else (
    echo [ERROR] Virtual environment not found
)

REM Check environment file
echo.
echo Checking environment file...
if exist ".env" (
    echo [OK] Environment file exists
) else (
    echo [ERROR] Environment file missing
)

REM Check required directories
echo.
echo Checking required directories...
if exist "logs" (echo [OK] logs directory exists) else (echo [WARNING] logs directory missing)
if exist "data" (echo [OK] data directory exists) else (echo [WARNING] data directory missing)
if exist "conversations" (echo [OK] conversations directory exists) else (echo [WARNING] conversations directory missing)

REM Check dependencies
echo.
echo Checking dependencies...
call venv\Scripts\activate
pip freeze > temp_requirements.txt
fc /n requirements.txt temp_requirements.txt > nul
if errorlevel 1 (
    echo [WARNING] Installed packages may differ from requirements.txt
) else (
    echo [OK] All required packages are installed
)
del temp_requirements.txt

REM Check NLTK data
echo.
echo Checking NLTK data...
python -c "import nltk; print('NLTK data directory:', nltk.data.path)" 2>nul
if errorlevel 1 (
    echo [ERROR] NLTK not properly configured
) else (
    echo [OK] NLTK is configured
)

REM Check disk space
echo.
echo Checking disk space...
wmic logicaldisk get size,freespace,caption

REM System information
echo.
echo System Information:
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type" /C:"Total Physical Memory"

echo.
echo Diagnostic complete! Please include this output when reporting issues.
pause
