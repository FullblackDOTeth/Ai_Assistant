@echo off
echo Verifying Pipeline Environment Setup
echo ----------------------------------
echo.

echo Checking environment variables:
echo.

echo GITHUB_TOKEN: %GITHUB_TOKEN%
echo GITHUB_OWNER: %GITHUB_OWNER%
echo GITHUB_REPO: %GITHUB_REPO%

echo.
if "%GITHUB_TOKEN%"=="" (
    echo WARNING: GITHUB_TOKEN is not set
) else (
    echo GITHUB_TOKEN is set
)

if "%GITHUB_OWNER%"=="" (
    echo WARNING: GITHUB_OWNER is not set
) else (
    echo GITHUB_OWNER is set
)

if "%GITHUB_REPO%"=="" (
    echo WARNING: GITHUB_REPO is not set
) else (
    echo GITHUB_REPO is set
)

echo.
echo If any variables are missing, please run setup_pipeline.bat again
echo.
pause
