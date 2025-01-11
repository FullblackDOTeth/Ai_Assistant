@echo off
echo Setting up AI Assistant...

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing required packages...
python -m pip install customtkinter wikipedia duckduckgo-search

echo Setup complete! You can now run the assistant using run_assistant.bat
pause
