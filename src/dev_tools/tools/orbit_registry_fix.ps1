# orbit_registry_fix.ps1
# Removes problematic filters and forces Orbit MI_00 to use a clean UVC driver.

$ErrorActionPreference = "Stop"

function Test-Admin {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    Write-Error "This script MUST be run as Administrator."
    exit 1
}

$pnputil = "$env:SystemRoot\System32\pnputil.exe"
if (-not (Test-Path $pnputil)) { $pnputil = "$env:SystemRoot\Sysnative\pnputil.exe" }

$videoInstance = "USB\VID_046D&PID_08C2&MI_00\6&16853086&4&0000"
$regPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\$videoInstance"

Write-Host "--- Starting Orbit Registry Fix ---" -ForegroundColor Cyan

# 1. Clear problematic filters
if (Test-Path $regPath) {
    Write-Host "Found Registry Key for Orbit Video."
    $val = Get-ItemProperty -Path $regPath -Name "LowerFilters" -ErrorAction SilentlyContinue
    if ($val) {
        Write-Host "Removing LowerFilters: $($val.LowerFilters)"
        Remove-ItemProperty -Path $regPath -Name "LowerFilters"
        Write-Host "LowerFilters removed." -ForegroundColor Green
    }
    else {
        Write-Host "No LowerFilters found."
    }
}
else {
    Write-Warning "Could not find registry path $regPath"
}

# 2. Force removal and re-scan
Write-Host "Removing device instance to trigger clean re-evaluation..."
& $pnputil /remove-device "$videoInstance"

Write-Host "Scanning for hardware changes..."
& $pnputil /scan-devices

Write-Host "Wait 5 seconds..."
Start-Sleep -s 5

Write-Host "Final Status check:"
& $pnputil /enum-devices /instanceid "$videoInstance"

Write-Host "--- Fix Complete ---" -ForegroundColor Cyan
Write-Host "If it still shows Code 10, check if 'USB Video Device' now works in Device Manager."
