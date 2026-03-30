# orbit_driver_cleaner.ps1
# Removes all third-party drivers for the Orbit camera to force fallback to standard Windows drivers.

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

Write-Host "--- Starting Orbit Driver Cleanup ---" -ForegroundColor Cyan

# 1. Identify all OEM drivers for the Orbit hardware
Write-Host "Searching for conflicting driver packages..."
$drivers = & $pnputil /enum-drivers
$oemList = @()

# Logic: Find every INF that mentions Orbit, Sphere, or the VID/PID 046D&PID_08C2
# We search for the "Original Name" or "Provider Name" that isn't Microsoft
# But safer to just look for packages that match the hardware IDs if possible via enum-drivers output

# We'll use the results from previous enumeration for efficiency, but let's automate it:
$oemMatches = $drivers | Select-String -Pattern "Published Name:\s+(oem\d+\.inf)" -Context 0, 10
foreach ($match in $oemMatches) {
    $oemName = $match.Matches.Groups[1].Value
    $context = $match.Context.PostContext -join " "
    if ($context -like "*Orbit*" -or $context -like "*Sphere*" -or $context -like "*libusbK*" -or $context -like "*Logitech*") {
        if ($context -like "*oem55.inf*" -or $context -like "*oem56.inf*" -or $context -like "*oem57.inf*" -or $context -like "*oem49.inf*" -or $context -like "*oem68.inf*") {
            # These are confirmed matches from previous logs
            $oemList += $oemName
        }
    }
}

# Add the ones we specifically found in logs
$knownOems = @("oem57.inf", "oem56.inf", "oem55.inf", "oem49.inf", "oem68.inf")
foreach ($oem in $knownOems) {
    if ($oemList -notcontains $oem) { $oemList += $oem }
}

$oemList = $oemList | Select-Object -Unique

Write-Host "Packages identified for removal: $($oemList -join ', ')"

# 2. Delete the packages
foreach ($oem in $oemList) {
    Write-Host "Deleting $oem..."
    try {
        & $pnputil /delete-driver $oem /uninstall /force
        Write-Host "Deleted $oem." -ForegroundColor Green
    }
    catch {
        Write-Warning "Could not delete ${oem}: $_"
    }
}

# 3. Find devices and remove them
Write-Host "Removing active device instances..."
$devices = & $pnputil /enum-devices /connected
$videoMatch = $devices | Select-String "USB\\VID_046D&PID_08C2&MI_00"
$audioMatch = $devices | Select-String "USB\\VID_046D&PID_08C2&MI_02"

if ($videoMatch) {
    $inst = $videoMatch.ToString().Split(":")[1].Trim()
    & $pnputil /remove-device "$inst"
}
if ($audioMatch) {
    $inst = $audioMatch.ToString().Split(":")[1].Trim()
    & $pnputil /remove-device "$inst"
}

# 4. Scan for changes
Write-Host "Scanning for hardware changes. Windows will now re-install using built-in drivers..."
& $pnputil /scan-devices
Write-Host "Wait 5 seconds..."
Start-Sleep -s 5

# 5. Final Check
Write-Host "Final Verification:" -ForegroundColor Cyan
& $pnputil /enum-devices /connected /instanceid "USB\VID_046D&PID_08C2*"

Write-Host "--- Cleanup Complete ---" -ForegroundColor Cyan
Write-Host "Check Device Manager. The Orbit should now appear as 'USB Video Device' and 'USB Audio Device'."
