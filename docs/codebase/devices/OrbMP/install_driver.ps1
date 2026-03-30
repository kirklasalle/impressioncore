$infPath = Resolve-Path "OrbMP\OrbMP.inf"
$cmd = "pnputil.exe"
$args = "/add-driver `"$infPath`" /install"

Write-Host "Requesting Admin privileges to install driver..."
Start-Process $cmd -ArgumentList $args -Verb RunAs -Wait
Write-Host "Driver installation attempted."
Read-Host "Press Enter to exit..."
