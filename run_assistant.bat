@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing required packages...
python -m pip install customtkinter wikipedia duckduckgo-search

echo Starting AI Assistant...
python src/main.py

pause
