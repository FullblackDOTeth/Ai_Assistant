@echo off
echo Complete Pipeline Setup
echo ---------------------
echo.

echo Step 1: Setting up environment variables...
echo.

set /p GITHUB_TOKEN="Enter your GitHub Personal Access Token (PAT): "
set /p GITHUB_OWNER="Enter your GitHub username: "
set /p GITHUB_REPO="Enter your repository name: "

echo.
echo Setting permanent environment variables...
setx GITHUB_TOKEN "%GITHUB_TOKEN%"
setx GITHUB_OWNER "%GITHUB_OWNER%"
setx GITHUB_REPO "%GITHUB_REPO%"

echo.
echo Setting temporary environment variables for this session...
set GITHUB_TOKEN=%GITHUB_TOKEN%
set GITHUB_OWNER=%GITHUB_OWNER%
set GITHUB_REPO=%GITHUB_REPO%

echo.
echo Step 2: Verifying setup...
echo.

echo Current environment variables:
echo GITHUB_TOKEN: %GITHUB_TOKEN%
echo GITHUB_OWNER: %GITHUB_OWNER%
echo GITHUB_REPO: %GITHUB_REPO%

echo.
echo Step 3: Testing pipeline monitor...
echo.

python testing/utils/pipeline_monitor.py

echo.
echo Setup complete! The pipeline monitor should now be running.
echo If you see any errors, please verify your GitHub credentials.
echo.
pause
