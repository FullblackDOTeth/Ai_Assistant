# Requires -RunAsAdministrator

# Set TLS to 1.2
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Create directories if they don't exist
$prometheusDir = "C:\prometheus"
$alertmanagerDir = "C:\alertmanager"

if (!(Test-Path $prometheusDir)) {
    New-Item -ItemType Directory -Path $prometheusDir
}

if (!(Test-Path $alertmanagerDir)) {
    New-Item -ItemType Directory -Path $alertmanagerDir
}

# Download and extract Prometheus
Write-Host "Downloading Prometheus..."
Invoke-WebRequest -Uri "https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.windows-amd64.zip" -OutFile "prometheus.zip"
Expand-Archive "prometheus.zip" -DestinationPath $prometheusDir -Force
Remove-Item "prometheus.zip"

# Download and extract Alertmanager
Write-Host "Downloading Alertmanager..."
Invoke-WebRequest -Uri "https://github.com/prometheus/alertmanager/releases/download/v0.25.0/alertmanager-0.25.0.windows-amd64.zip" -OutFile "alertmanager.zip"
Expand-Archive "alertmanager.zip" -DestinationPath $alertmanagerDir -Force
Remove-Item "alertmanager.zip"

# Create Windows Services
Write-Host "Creating Windows Services..."
$prometheusService = Get-Service -Name "Prometheus" -ErrorAction SilentlyContinue
if ($prometheusService -eq $null) {
    New-Service -Name "Prometheus" `
        -BinaryPathName "$prometheusDir\prometheus.exe --config.file=E:\Head Ai\monitoring\prometheus\prometheus.yml" `
        -Description "Prometheus Monitoring System" `
        -StartupType Automatic
}

$alertmanagerService = Get-Service -Name "Alertmanager" -ErrorAction SilentlyContinue
if ($alertmanagerService -eq $null) {
    New-Service -Name "Alertmanager" `
        -BinaryPathName "$alertmanagerDir\alertmanager.exe --config.file=E:\Head Ai\monitoring\alertmanager\alertmanager.yml" `
        -Description "Prometheus Alertmanager" `
        -StartupType Automatic
}

# Set environment variables
Write-Host "Setting environment variables..."
if (Test-Path "E:\Head Ai\monitoring\alertmanager\secrets.env") {
    Get-Content "E:\Head Ai\monitoring\alertmanager\secrets.env" | ForEach-Object {
        $name, $value = $_.Split('=')
        [System.Environment]::SetEnvironmentVariable($name, $value, [System.EnvironmentVariableTarget]::Machine)
    }
}

# Start services
Write-Host "Starting services..."
Start-Service -Name "Prometheus"
Start-Service -Name "Alertmanager"

Write-Host "Installation complete!"
Write-Host "You can access:"
Write-Host "Prometheus UI at: http://localhost:9090"
Write-Host "Alertmanager UI at: http://localhost:9093"
Write-Host "Please verify that the services are running and check the alerts at: http://localhost:9090/alerts"
