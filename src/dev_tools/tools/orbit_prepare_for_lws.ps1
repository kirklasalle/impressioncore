# orbit_prepare_for_lws.ps1
# Disables Windows 10 "Secure Camera" features and prepares system for legacy Logitech driver.
# Run as Administrator BEFORE installing Logitech Webcam Software 2.80.

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

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  Orbit Camera - Prepare for Logitech Webcam Software (LWS)" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# --- Step 1: Disable SecureUSBVideo UMDF Driver ---
Write-Host "[1/5] Disabling SecureUSBVideo UMDF Companion Driver..." -ForegroundColor Yellow

$secureUsbKey = "HKLM:\SOFTWARE\Classes\CLSID\{37850557-6CB0-441B-9AE5-E9B00AC30BD0}"
if (-not (Test-Path $secureUsbKey)) {
    New-Item -Path $secureUsbKey -Force | Out-Null
}
Set-ItemProperty -Path $secureUsbKey -Name "Disabled" -Value 1 -Type DWord
Write-Host "  SecureUSBVideo disabled via registry." -ForegroundColor Green

# --- Step 2: Remove Instance-Level Filters ---
Write-Host "[2/5] Removing instance-level filters from Orbit device..." -ForegroundColor Yellow

$videoInstance = "USB\VID_046D&PID_08C2&MI_00\6&16853086&4&0000"
$audioInstance = "USB\VID_046D&PID_08C2&MI_02\6&16853086&4&0002"

$videoPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\$videoInstance"
$audioPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\$audioInstance"

if (Test-Path $videoPath) {
    Remove-ItemProperty -Path $videoPath -Name "LowerFilters" -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path $videoPath -Name "UpperFilters" -ErrorAction SilentlyContinue
    # Reset ConfigFlags to default
    Set-ItemProperty -Path $videoPath -Name "ConfigFlags" -Value 0 -Type DWord -ErrorAction SilentlyContinue
    
    # Remove WUDF/Companion configurations
    $wudfPath = Join-Path $videoPath "Device Parameters\WUDF"
    if (Test-Path $wudfPath) {
        Remove-Item -Path $wudfPath -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  Removed WUDF configuration from video interface." -ForegroundColor Green
    }
}

if (Test-Path $audioPath) {
    Remove-ItemProperty -Path $audioPath -Name "LowerFilters" -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path $audioPath -Name "UpperFilters" -ErrorAction SilentlyContinue
}

Write-Host "  Instance filters cleared." -ForegroundColor Green

# --- Step 3: Remove Class-Level Legacy Filters (LVUSBS64) ---
Write-Host "[3/5] Removing legacy Logitech class filters (LVUSBS64)..." -ForegroundColor Yellow

$classesToClean = @(
    "{4d36e96c-e325-11ce-bfc1-08002be10318}", # MEDIA
    "{6bdd1fc6-810f-11d0-bec7-08002be2092f}", # Imaging Devices
    "{ca3e7ab9-b4c3-4ae6-8251-579ef933890f}"  # Camera
)

foreach ($cls in $classesToClean) {
    $path = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\$cls"
    if (Test-Path $path) {
        $lower = Get-ItemProperty -Path $path -Name "LowerFilters" -ErrorAction SilentlyContinue
        if ($lower -and $lower.LowerFilters) {
            $newFilters = $lower.LowerFilters | Where-Object { $_ -ne "LVUSBS64" }
            if ($newFilters -and $newFilters.Count -gt 0) {
                Set-ItemProperty -Path $path -Name "LowerFilters" -Value $newFilters
            }
            else {
                Remove-ItemProperty -Path $path -Name "LowerFilters" -ErrorAction SilentlyContinue
            }
            Write-Host "  Cleaned LVUSBS64 from class $cls" -ForegroundColor Green
        }
    }
}

# --- Step 4: Remove ALL existing third-party Orbit drivers from Store ---
Write-Host "[4/5] Removing conflicting third-party drivers from Driver Store..." -ForegroundColor Yellow

# Known conflicting OEM drivers for Orbit
$oemsToDelete = @("oem55.inf", "oem56.inf", "oem57.inf", "oem49.inf", "oem68.inf")

foreach ($oem in $oemsToDelete) {
    Write-Host "  Attempting to delete $oem..."
    try {
        $result = & $pnputil /delete-driver $oem /uninstall /force 2>&1
        if ($result -match "deleted successfully") {
            Write-Host "    Deleted $oem" -ForegroundColor Green
        }
        else {
            Write-Host "    $oem not found or already deleted." -ForegroundColor DarkGray
        }
    }
    catch {
        Write-Host "    Failed to delete ${oem}: $_" -ForegroundColor DarkGray
    }
}

# --- Step 5: Remove and Re-scan Device ---
Write-Host "[5/5] Removing device instances and triggering re-scan..." -ForegroundColor Yellow

& $pnputil /remove-device "$videoInstance" 2>&1 | Out-Null
& $pnputil /remove-device "$audioInstance" 2>&1 | Out-Null
& $pnputil /scan-devices

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  PREPARATION COMPLETE" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "The system is now prepared for Logitech Webcam Software installation." -ForegroundColor White
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Run the Logitech Webcam Software installer:" -ForegroundColor White
Write-Host "   d:\Projects\impressioncore\docs\codebase\devices\Device software\lws280.exe" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. REBOOT your computer after installation completes." -ForegroundColor White
Write-Host ""
Write-Host "3. Check Device Manager for 'Logitech QuickCam Orbit/Sphere MP' under Imaging Devices." -ForegroundColor White
Write-Host ""
