@echo off
echo Creating Head AI Distribution Package...

REM Create dist directory if it doesn't exist
if not exist "dist" mkdir dist

REM Clean previous builds
echo Cleaning previous builds...
if exist "dist\HeadAI_Setup.exe" del "dist\HeadAI_Setup.exe"
if exist "dist\HeadAI_Manual.zip" del "dist\HeadAI_Manual.zip"
if exist "python-3.8.10-embed-amd64" rmdir /s /q "python-3.8.10-embed-amd64"

REM Download Python embedded if not exists
echo Downloading Python embedded...
powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.8.10/python-3.8.10-embed-amd64.zip' -OutFile 'python-embed.zip'}"
echo Extracting Python...
powershell -Command "& {Expand-Archive -Path 'python-embed.zip' -DestinationPath 'python-3.8.10-embed-amd64' -Force}"
del python-embed.zip

REM Create version file
echo Creating version file...
echo 1.0.0 > version.txt

REM Prepare distribution files
echo Preparing distribution files...
mkdir "dist\temp_package"
xcopy /E /I "src" "dist\temp_package\src"
copy "requirements.txt" "dist\temp_package\"
copy "setup.bat" "dist\temp_package\"
copy "run_assistant.bat" "dist\temp_package\"
copy ".env.example" "dist\temp_package\"
xcopy /E /I "scripts" "dist\temp_package\scripts"
xcopy /E /I "docs" "dist\temp_package\docs"
copy "version.txt" "dist\temp_package\"

REM Create manual package
echo Creating ZIP package...
powershell -Command "& {Compress-Archive -Path 'dist\temp_package\*' -DestinationPath 'dist\HeadAI_Manual.zip' -Force}"

REM Run Inno Setup Compiler
echo Building installer...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss

REM Clean up
echo Cleaning up...
rmdir /s /q "dist\temp_package"
del version.txt

echo.
echo Distribution packages created:
echo 1. dist\HeadAI_Setup.exe - Installer package
echo 2. dist\HeadAI_Manual.zip - Manual installation package
echo.
echo Done!
pause
