@echo off
echo CI/CD Pipeline Environment Setup
echo -------------------------------
echo.

echo Please enter your GitHub information:
echo.

set /p GITHUB_TOKEN="Enter your GitHub Personal Access Token (PAT): "
set /p GITHUB_OWNER="Enter your GitHub username: "
set /p GITHUB_REPO="Enter your repository name: "

echo.
echo Setting environment variables...
setx GITHUB_TOKEN "%GITHUB_TOKEN%"
setx GITHUB_OWNER "%GITHUB_OWNER%"
setx GITHUB_REPO "%GITHUB_REPO%"

echo.
echo Environment variables have been set!
echo.
echo Next steps:
echo 1. Close this command prompt
echo 2. Open a new command prompt
echo 3. Run: python testing/utils/pipeline_monitor.py
echo.
pause
