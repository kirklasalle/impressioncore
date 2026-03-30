# orbit_nuke_legacy_filters.ps1
# Nukes the legacy LVUSBS64 class filters and instance-level filters that cause Code 10.

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

$classes = @(
    "{4d36e96c-e325-11ce-bfc1-08002be10318}", # Media
    "{6bdd1fc6-810f-11d0-bec7-08002be2092f}"  # Imaging Devices
)

Write-Host "--- Nuking Legacy Logitech Filters ---" -ForegroundColor Cyan

# 1. Class-level Cleanup
foreach ($cls in $classes) {
    $path = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\$cls"
    if (Test-Path $path) {
        $val = Get-ItemProperty -Path $path -Name "LowerFilters" -ErrorAction SilentlyContinue
        if ($val -and ($val.LowerFilters -contains "LVUSBS64")) {
            Write-Host "Found LVUSBS64 in Class $cls. Removing..."
            $newFilters = $val.LowerFilters | Where-Object { $_ -ne "LVUSBS64" }
            if ($newFilters) {
                Set-ItemProperty -Path $path -Name "LowerFilters" -Value $newFilters
            }
            else {
                Remove-ItemProperty -Path $path -Name "LowerFilters"
            }
            Write-Host "Cleanup successful for $cls." -ForegroundColor Green
        }
    }
}

# 2. Instance-level Cleanup (Purge WdmCompanionFilter and WUDF configs)
$videoInstance = "USB\VID_046D&PID_08C2&MI_00\6&16853086&4&0000"
$instPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\$videoInstance"

if (Test-Path $instPath) {
    Write-Host "Cleaning instance filters for Video..."
    Remove-ItemProperty -Path $instPath -Name "LowerFilters" -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path $instPath -Name "ConfigFlags" -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $instPath -Name "ConfigFlags" -Value 0
    
    $wudfPath = Join-Path $instPath "Device Parameters\WUDF"
    if (Test-Path $wudfPath) {
        Write-Host "Nuking WUDF / Companion configuration..."
        Remove-Item -Path $wudfPath -Recurse -Force
    }
}

# 3. Force Reset
Write-Host "Removing device instances..."
& $pnputil /remove-device "$videoInstance"

Write-Host "Scanning for hardware changes..."
& $pnputil /scan-devices

Write-Host "Wait 5 seconds..."
Start-Sleep -s 5

Write-Host "--- Fix Complete ---" -ForegroundColor Cyan
Write-Host "Now try manually assigning 'USB Video Device' again in Device Manager."
Write-Host "It should work without Code 10 now that the legacy filters are purged."
