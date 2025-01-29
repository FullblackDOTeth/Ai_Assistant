@echo off
echo Head AI Provider Management
echo =========================

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:MENU
echo.
echo Choose an option:
echo 1. List AI Providers
echo 2. Check API Keys
echo 3. Test OpenAI
echo 4. Update Configuration
echo 5. Exit
echo.

set /p CHOICE="Enter your choice (1-5): "

if "%CHOICE%"=="1" (
    python src/ai_cli.py list
    goto MENU
)
if "%CHOICE%"=="2" (
    python src/ai_cli.py keys
    goto MENU
)
if "%CHOICE%"=="3" (
    set /p PROMPT="Enter test prompt: "
    python src/ai_cli.py test openai "%PROMPT%"
    goto MENU
)
if "%CHOICE%"=="4" (
    set /p MODEL="Enter model name (or press Enter to skip): "
    set /p TEMP="Enter temperature 0.0-1.0 (or press Enter to skip): "
    if not "%MODEL%"=="" (
        if not "%TEMP%"=="" (
            python src/ai_cli.py config openai --model %MODEL% --temperature %TEMP%
        ) else (
            python src/ai_cli.py config openai --model %MODEL%
        )
    ) else (
        if not "%TEMP%"=="" (
            python src/ai_cli.py config openai --temperature %TEMP%
        )
    )
    goto MENU
)
if "%CHOICE%"=="5" (
    echo Goodbye!
    exit /b
)

echo Invalid choice. Please try again.
goto MENU
