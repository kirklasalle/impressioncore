# orbit_verify_lws.ps1
# Verifies that the Logitech driver installed correctly after LWS installation.

$ErrorActionPreference = "SilentlyContinue"

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  Orbit Camera - Post-LWS Installation Verification" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

$pnputil = "$env:SystemRoot\System32\pnputil.exe"
if (-not (Test-Path $pnputil)) { $pnputil = "$env:SystemRoot\Sysnative\pnputil.exe" }

# Check device status
Write-Host "[1/3] Checking Orbit Camera Device Status..." -ForegroundColor Yellow

$videoInstance = "USB\VID_046D&PID_08C2&MI_00\6&16853086&4&0000"
$details = & $pnputil /enum-devices /instanceid "$videoInstance"

if ($details -match "Status:\s+Started") {
    Write-Host "  Video Interface (MI_00): STARTED" -ForegroundColor Green
    $videoOK = $true
}
elseif ($details -match "Problem Code:\s+(\d+)") {
    $code = $matches[1]
    Write-Host "  Video Interface (MI_00): FAILED (Code $code)" -ForegroundColor Red
    $videoOK = $false
}
else {
    Write-Host "  Video Interface (MI_00): NOT FOUND" -ForegroundColor Red
    $videoOK = $false
}

# Check what driver is loaded
Write-Host ""
Write-Host "[2/3] Checking Loaded Driver..." -ForegroundColor Yellow

$regPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\$videoInstance"
if (Test-Path $regPath) {
    $service = (Get-ItemProperty -Path $regPath -Name "Service" -ErrorAction SilentlyContinue).Service
    $desc = (Get-ItemProperty -Path $regPath -Name "DeviceDesc" -ErrorAction SilentlyContinue).DeviceDesc
    
    Write-Host "  Service: $service"
    Write-Host "  Description: $desc"
    
    if ($service -eq "LVUVC64") {
        Write-Host "  Driver: Logitech LVUVC64 (CORRECT!)" -ForegroundColor Green
        $driverOK = $true
    }
    elseif ($service -eq "libusbK") {
        Write-Host "  Driver: libusbK (Need to switch)" -ForegroundColor Yellow
        $driverOK = $false
    }
    elseif ($service -eq "usbvideo") {
        Write-Host "  Driver: Microsoft UVC (May not work)" -ForegroundColor Yellow
        $driverOK = $false
    }
    else {
        Write-Host "  Driver: $service (Unknown)" -ForegroundColor Yellow
        $driverOK = $false
    }
}
else {
    Write-Host "  Registry path not found." -ForegroundColor Red
    $driverOK = $false
}

# Check DirectShow visibility
Write-Host ""
Write-Host "[3/3] Checking DirectShow Visibility..." -ForegroundColor Yellow

try {
    Add-Type -AssemblyName System.Windows.Forms
    
    # Use PowerShell to query DirectShow (simplified check)
    $dsCheck = & powershell -Command {
        try {
            [System.Reflection.Assembly]::LoadWithPartialName("DirectShowLib") | Out-Null
            $devices = [DirectShowLib.DsDevice]::GetDevicesOfCat([DirectShowLib.FilterCategory]::VideoInputDevice)
            foreach ($d in $devices) {
                if ($d.Name -match "Orbit|Sphere|QuickCam") {
                    Write-Output $d.Name
                }
            }
        }
        catch {
            # Fallback: just check WMI
            Get-WmiObject Win32_PnPEntity | Where-Object { $_.Name -match "Orbit|Sphere|QuickCam" } | ForEach-Object { $_.Name }
        }
    } 2>&1
    
    if ($dsCheck) {
        Write-Host "  Found in DirectShow/WMI: $dsCheck" -ForegroundColor Green
        $dsOK = $true
    }
    else {
        Write-Host "  NOT visible in DirectShow/WMI" -ForegroundColor Red
        $dsOK = $false
    }
}
catch {
    Write-Host "  DirectShow check failed: $_" -ForegroundColor Yellow
    $dsOK = $false
}

# Summary
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  VERIFICATION SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

if ($videoOK -and $driverOK) {
    Write-Host ""
    Write-Host "  SUCCESS! Logitech driver is installed and running." -ForegroundColor Green
    Write-Host "  You should now be able to use the Orbit camera with OpenCV/DirectShow." -ForegroundColor Green
    Write-Host ""
    Write-Host "  Test with:" -ForegroundColor White
    Write-Host "    python -c `"import cv2; c=cv2.VideoCapture(0); print(c.read()[0]); c.release()`"" -ForegroundColor Cyan
}
elseif ($videoOK) {
    Write-Host ""
    Write-Host "  PARTIAL SUCCESS. Device started but with non-Logitech driver." -ForegroundColor Yellow
    Write-Host "  Motor control may not work. Video might work." -ForegroundColor Yellow
}
else {
    Write-Host ""
    Write-Host "  FAILED. The Logitech driver did not install correctly." -ForegroundColor Red
    Write-Host ""
    Write-Host "  Recommended next step: Proceed to Option C (Custom WinUSB Pipeline)." -ForegroundColor Yellow
}
