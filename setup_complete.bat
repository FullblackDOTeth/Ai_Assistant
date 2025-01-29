@echo off
echo Setting up AI Assistant...

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing base packages...
python -m pip install --upgrade pip setuptools wheel

echo Installing required packages...
python -m pip install -r requirements.txt
python -m pip install -r requirements_minimal.txt
python -m pip install -r requirements_ml.txt

echo Setting up NLTK data...
python src/setup_nltk.py

echo Setup complete! You can now run the assistant using run_assistant.bat
pause
