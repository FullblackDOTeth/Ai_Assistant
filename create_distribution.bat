@echo off
echo Creating distribution package...

:: Create dist directory
if not exist dist mkdir dist
if not exist dist\Head_AI mkdir dist\Head_AI

:: Copy necessary files
echo Copying files...
xcopy /E /I src dist\Head_AI\src
copy requirements*.txt dist\Head_AI\
copy README.md dist\Head_AI\
copy run_assistant.bat dist\Head_AI\
copy setup.bat dist\Head_AI\
copy .env.template dist\Head_AI\

:: Create version file
echo v0.1.0-beta > dist\Head_AI\version.txt

echo Distribution package created in dist\Head_AI
echo You can now zip this folder and distribute it to beta testers
pause
