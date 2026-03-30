$logFile = "$PSScriptRoot\driver_install.log"
Start-Transcript -Path $logFile -Force

Write-Host "Installing OrbMP.inf..."
$infPath = "$PSScriptRoot\OrbMP.inf"

# Install Driver
& pnputil /add-driver "$infPath" /install

# Scan for changes
Write-Host "Scanning for hardware changes..."
& pnputil /scan-devices

Stop-Transcript
Write-Host "Done. Check $logFile"
Start-Sleep -Seconds 2
