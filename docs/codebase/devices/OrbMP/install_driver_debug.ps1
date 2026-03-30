$innerScript = "$PSScriptRoot\inner_install.ps1"
Write-Host "Launching elevated installer..."
Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File `"$innerScript`"" -Verb RunAs -Wait
Write-Host "Installation process finished."
Get-Content "$PSScriptRoot\driver_install.log" -ErrorAction SilentlyContinue
