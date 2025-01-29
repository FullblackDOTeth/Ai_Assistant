# Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

Write-Host "Starting monitoring services..." -ForegroundColor Green

# Define paths
$prometheusPath = "C:\prometheus\prometheus-2.45.0.windows-amd64"
$alertmanagerPath = "C:\alertmanager\alertmanager-0.25.0.windows-amd64"
$prometheusConfig = "E:\Head Ai\monitoring\prometheus\prometheus.yml"
$alertmanagerConfig = "E:\Head Ai\monitoring\alertmanager\alertmanager.yml"

# Stop existing processes
Get-Process | Where-Object {$_.ProcessName -match 'prometheus|alertmanager'} | Stop-Process -Force -ErrorAction SilentlyContinue

# Start Prometheus
Write-Host "Starting Prometheus..." -ForegroundColor Yellow
$prometheus = Start-Process -FilePath "$prometheusPath\prometheus.exe" `
    -ArgumentList "--config.file=`"$prometheusConfig`"", "--web.listen-address=:9090" `
    -PassThru -NoNewWindow

# Start Alertmanager
Write-Host "Starting Alertmanager..." -ForegroundColor Yellow
$alertmanager = Start-Process -FilePath "$alertmanagerPath\alertmanager.exe" `
    -ArgumentList "--config.file=`"$alertmanagerConfig`"", "--web.listen-address=:9093" `
    -PassThru -NoNewWindow

# Wait a moment for services to start
Start-Sleep -Seconds 5

# Check if processes are running
$prometheusRunning = Get-Process -Id $prometheus.Id -ErrorAction SilentlyContinue
$alertmanagerRunning = Get-Process -Id $alertmanager.Id -ErrorAction SilentlyContinue

if ($prometheusRunning -and $alertmanagerRunning) {
    Write-Host "`nMonitoring services started successfully!" -ForegroundColor Green
    Write-Host "Prometheus UI: http://localhost:9090"
    Write-Host "Alertmanager UI: http://localhost:9093"
    Write-Host "`nPress Ctrl+C to stop the services..."
    
    try {
        while ($true) {
            Start-Sleep -Seconds 1
        }
    }
    finally {
        Write-Host "`nStopping services..." -ForegroundColor Yellow
        Stop-Process -Id $prometheus.Id -Force -ErrorAction SilentlyContinue
        Stop-Process -Id $alertmanager.Id -Force -ErrorAction SilentlyContinue
        Write-Host "Services stopped." -ForegroundColor Green
    }
} else {
    Write-Host "Failed to start services!" -ForegroundColor Red
    if (-not $prometheusRunning) {
        Write-Host "Prometheus failed to start" -ForegroundColor Red
    }
    if (-not $alertmanagerRunning) {
        Write-Host "Alertmanager failed to start" -ForegroundColor Red
    }
}
