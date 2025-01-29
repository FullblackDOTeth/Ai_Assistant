@echo off
echo Starting Prometheus and Alertmanager...

:: Set the config paths with proper escaping
set PROMETHEUS_CONFIG="E:\Head Ai\monitoring\prometheus\prometheus.yml"
set ALERTMANAGER_CONFIG="E:\Head Ai\monitoring\alertmanager\alertmanager.yml"

:: Start Prometheus
echo Starting Prometheus...
start "Prometheus" cmd /c "C:\prometheus\prometheus-2.45.0.windows-amd64\prometheus.exe" --config.file=%PROMETHEUS_CONFIG%

:: Start Alertmanager
echo Starting Alertmanager...
start "Alertmanager" cmd /c "C:\alertmanager\alertmanager-0.25.0.windows-amd64\alertmanager.exe" --config.file=%ALERTMANAGER_CONFIG%

echo Services started!
echo.
echo Prometheus UI: http://localhost:9090
echo Alertmanager UI: http://localhost:9093
echo.
echo Press Ctrl+C to stop the services...
pause

:: Kill the services when the user presses Ctrl+C
taskkill /F /IM prometheus.exe
taskkill /F /IM alertmanager.exe
