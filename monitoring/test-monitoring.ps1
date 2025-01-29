# Stop existing processes
Get-Process | Where-Object {$_.ProcessName -match 'prometheus|alertmanager'} | Stop-Process -Force -ErrorAction SilentlyContinue

# Clear any existing error messages
$error.Clear()

# Start Prometheus
Write-Host "Starting Prometheus..." -ForegroundColor Yellow
$prometheus = Start-Process -FilePath "C:\prometheus\prometheus-2.45.0.windows-amd64\prometheus.exe" `
    -ArgumentList "--config.file=`"E:\Head Ai\monitoring\prometheus\prometheus.yml`"" `
    -PassThru -NoNewWindow -RedirectStandardError "prometheus-error.log"

Start-Sleep -Seconds 2

# Check if Prometheus is running
if (Get-Process -Id $prometheus.Id -ErrorAction SilentlyContinue) {
    Write-Host "Prometheus started successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to start Prometheus!" -ForegroundColor Red
    Get-Content "prometheus-error.log"
    exit 1
}

# Start Alertmanager
Write-Host "`nStarting Alertmanager..." -ForegroundColor Yellow
$alertmanager = Start-Process -FilePath "C:\alertmanager\alertmanager-0.25.0.windows-amd64\alertmanager.exe" `
    -ArgumentList "--config.file=`"E:\Head Ai\monitoring\alertmanager\alertmanager.yml`"" `
    -PassThru -NoNewWindow -RedirectStandardError "alertmanager-error.log"

Start-Sleep -Seconds 2

# Check if Alertmanager is running
if (Get-Process -Id $alertmanager.Id -ErrorAction SilentlyContinue) {
    Write-Host "Alertmanager started successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to start Alertmanager!" -ForegroundColor Red
    Get-Content "alertmanager-error.log"
    exit 1
}

Write-Host "`nAll services started! Testing connectivity..."

# Test Prometheus connectivity
try {
    $prometheus_response = Invoke-WebRequest -Uri "http://localhost:9090/-/healthy" -TimeoutSec 5
    Write-Host "Prometheus is responding (Port 9090): $($prometheus_response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Cannot connect to Prometheus: $_" -ForegroundColor Red
}

# Test Alertmanager connectivity
try {
    $alertmanager_response = Invoke-WebRequest -Uri "http://localhost:9093/-/healthy" -TimeoutSec 5
    Write-Host "Alertmanager is responding (Port 9093): $($alertmanager_response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Cannot connect to Alertmanager: $_" -ForegroundColor Red
}

Write-Host "`nPress Ctrl+C to stop the services..."
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    Get-Process | Where-Object {$_.ProcessName -match 'prometheus|alertmanager'} | Stop-Process -Force
    Write-Host "Services stopped." -ForegroundColor Green
}
