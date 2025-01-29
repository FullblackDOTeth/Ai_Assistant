@echo off
echo Setting up Head AI...

REM Check Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python 3.8 or higher.
    exit /b 1
)

REM Ask which modules to install
echo.
echo Available modules:
echo 1. Core only (Basic AI assistant)
echo 2. Research Suite (+ Wikipedia, scholarly research)
echo 3. Web Automation (+ Selenium for web interaction)
echo 4. Crypto Support (+ Web3 and crypto tools)
echo 5. Voice Support (+ Text-to-speech, voice recognition)
echo 6. All modules
echo.
set /p MODULE_CHOICE="Choose modules to install (1-6): "

REM Convert choice to module arguments
set MODULES=core
if "%MODULE_CHOICE%"=="2" set MODULES=core research
if "%MODULE_CHOICE%"=="3" set MODULES=core web
if "%MODULE_CHOICE%"=="4" set MODULES=core crypto
if "%MODULE_CHOICE%"=="5" set MODULES=core voice
if "%MODULE_CHOICE%"=="6" set MODULES=all

REM Run modular setup
python setup_modules.py --modules %MODULES%

echo.
echo Setup complete! Please edit .env with your API keys if you haven't already.
echo Run 'run_assistant.bat' to start Head AI.
pause
