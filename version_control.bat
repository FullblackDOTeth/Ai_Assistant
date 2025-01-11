@echo off
setlocal EnableDelayedExpansion

:: Get current version from version.txt or create it
if exist version.txt (
    set /p CURRENT_VERSION=<version.txt
) else (
    set CURRENT_VERSION=v0.1.0-beta
    echo !CURRENT_VERSION!>version.txt
)

echo Current version: !CURRENT_VERSION!
echo.
echo Select an option:
echo 1. Create new release
echo 2. Update version number
echo 3. Create distribution package
echo 4. Commit changes
echo 5. Exit

set /p CHOICE="Enter your choice (1-5): "

if "%CHOICE%"=="1" (
    call :create_release
) else if "%CHOICE%"=="2" (
    call :update_version
) else if "%CHOICE%"=="3" (
    call create_distribution.bat
) else if "%CHOICE%"=="4" (
    call :commit_changes
) else if "%CHOICE%"=="5" (
    exit /b 0
) else (
    echo Invalid choice
    exit /b 1
)
goto :eof

:create_release
echo Creating new release...
call create_distribution.bat
cd dist
tar -czf Head_AI_%CURRENT_VERSION%.zip Head_AI
cd ..
echo Release package created: Head_AI_%CURRENT_VERSION%.zip
goto :eof

:update_version
set /p NEW_VERSION="Enter new version (current: %CURRENT_VERSION%): "
echo !NEW_VERSION!>version.txt
echo Version updated to: !NEW_VERSION!
goto :eof

:commit_changes
set /p COMMIT_MSG="Enter commit message: "
git add .
git commit -m "%COMMIT_MSG%"
echo Changes committed
goto :eof
