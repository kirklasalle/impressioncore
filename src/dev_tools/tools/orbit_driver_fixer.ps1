# orbit_driver_fixer.ps1
# Automates the restoration of UVC and USB Audio drivers for Logitech Orbit/Sphere MP.

$ErrorActionPreference = "Stop"

function Test-Admin {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    Write-Error "This script MUST be run as Administrator."
    exit 1
}

# Use local directory to avoid path issues
$pnputil = "$env:SystemRoot\System32\pnputil.exe"
if (-not (Test-Path $pnputil)) { $pnputil = "$env:SystemRoot\Sysnative\pnputil.exe" }

$scriptDir = $PSScriptRoot
$infPath = "tools\orbit_uvc_force.inf" # Relative to project root
if (-not (Test-Path $infPath)) {
    $infPath = Join-Path $scriptDir "orbit_uvc_force.inf"
}

Write-Host "--- Starting Orbit Driver Fix ---" -ForegroundColor Cyan

# 1. Find instances dynamically
Write-Host "Scanning for Orbit hardware..."
$devices = & $pnputil /enum-devices /connected
$videoMatch = $devices | Select-String "USB\\VID_046D&PID_08C2&MI_00"
$audioMatch = $devices | Select-String "USB\\VID_046D&PID_08C2&MI_02"

if (-not $videoMatch) { 
    Write-Warning "Could not find Orbit Video interface. Is it plugged in?"
    exit 1 
}

$videoInstance = $videoMatch.ToString().Split(":")[1].Trim()
$audioInstance = if ($audioMatch) { $audioMatch.ToString().Split(":")[1].Trim() } else { $null }

Write-Host "Found Video Instance: $videoInstance"
if ($audioInstance) { Write-Host "Found Audio Instance: $audioInstance" }

# 2. Add UVC Force INF to Store
Write-Host "[1/3] Adding UVC Force INF to driver store..."
try {
    # Use relative path in quotes
    & $pnputil /add-driver "$infPath" /install
    Write-Host "INF added/installed in store."
}
catch {
    Write-Warning "Failed to add driver via /add-driver. Error: $_"
}

# 3. Force Windows to re-evaluate drivers (Alternative to /update-driver)
Write-Host "[2/3] Forcing hardware re-evaluation..."
Write-Host "Removing device instances temporarily..."
& $pnputil /remove-device "$videoInstance"
if ($audioInstance) { & $pnputil /remove-device "$audioInstance" }

Write-Host "Scanning for hardware changes..."
& $pnputil /scan-devices
Write-Host "Wait 5 seconds for Windows to re-install..."
Start-Sleep -s 5

# 4. Final verification output
Write-Host "[3/3] Final Status Check:" -ForegroundColor Cyan
& $pnputil /enum-devices /instanceid "$videoInstance"
if ($audioInstance) { & $pnputil /enum-devices /instanceid "$audioInstance" }

Write-Host "--- Fix Complete ---" -ForegroundColor Cyan
Write-Host "Please check Device Manager. If 'USB Video Device' appears under Cameras, you are set."
