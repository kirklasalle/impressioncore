# ============================================================================
# ImpressionCore (ORBOS) Autonomous Preparedness Orchestrator
# RESTORED: React/Vite Frontend Mode
# ============================================================================
$Host.UI.RawUI.WindowTitle = "ORBOS System Preparedness Check"
Write-Host ""
Write-Host " [SYSTEM] Initiating Autonomous Preparedness Sequence..." -ForegroundColor Cyan
Write-Host " ----------------------------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""

# 1. Admin Check
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if ($isAdmin) {
    Write-Host " [OK] Administrative Privileges Verified." -ForegroundColor Green
}
else {
    Write-Host " [CAUTION] Not running as Administrator. Hardware scan or installs may fail." -ForegroundColor Yellow
    Write-Host "           Consider right-clicking and 'Run as Administrator'." -ForegroundColor Gray
}

# 2. Python Engine Discovery
Write-Host " [PRE-FLIGHT] Verifying Python Engine..."
# Filter out the Microsoft Store "dummy" aliases
$pythonExe = where.exe python 2>$null | Where-Object { $_ -notlike "*WindowsApps*" } | Select-Object -First 1

$pyValid = $false
if ($pythonExe) {
    try {
        $testVer = & $pythonExe --version 2>&1
        if ($LASTEXITCODE -eq 0) { $pyValid = $true }
    }
    catch { }
}

if (-not $pyValid) {
    # Fallback search
    $searchPaths = @(
        "$env:USERPROFILE\AppData\Local\Programs\Python\Python*",
        "$env:LocalAppData\Programs\Python\Python*",
        "C:\Program Files\Python*",
        "C:\Program Files (x86)\Python*",
        "C:\Python*"
    )
    foreach ($path in $searchPaths) {
        if (Test-Path $path) {
            $found = Get-ChildItem -Path $path -Filter "python.exe" -File -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($found) {
                try {
                    & $found.FullName --version 2>&1 | Out-Null
                    if ($LASTEXITCODE -eq 0) {
                        $pythonExe = $found.FullName
                        break
                    }
                }
                catch { }
            }
        }
    }
}

if (-not $pythonExe) {
    Write-Host " [CRITICAL] Python 3.x is not installed." -ForegroundColor Red
    pause; exit
}
$pyVer = & $pythonExe --version
Write-Host " [OK] Python Engine Online: $pyVer" -ForegroundColor Green

# 3. Node.js Discovery (RESTORED)
Write-Host " [PRE-FLIGHT] Verifying Node.js Engine..."
$nodeVer = node --version 2>$null
if ($nodeVer) {
    Write-Host " [OK] Node.js Engine Online: $nodeVer" -ForegroundColor Green
}
else {
    Write-Host " [CRITICAL] Node.js is not installed or not in PATH." -ForegroundColor Red
    Write-Host "            Please install Node.js LTS to run the React client." -ForegroundColor Yellow
    pause; exit
}

# 4. Project Source & Deps
if (-not (Test-Path "src\interfaces\triad_api.py")) {
    Write-Host " [CRITICAL] Directory error! Run from project root." -ForegroundColor Red
    pause; exit
}

# 5. Port Cleanup
Write-Host "`n [PRE-FLIGHT] Sanitizing Communication Ports..."
$ports = @(8000, 5173, 3000)
foreach ($port in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        Write-Host " [WARNING] Port $port is occupied by PID $($conn.OwningProcess)." -ForegroundColor Yellow
        Stop-Process -Id $conn.OwningProcess -Force
        Write-Host " [OK] Port $port Cleared." -ForegroundColor Green
    }
}

# 6. Ignition
Write-Host "`n ----------------------------------------------------------------------------" -ForegroundColor Cyan
Write-Host " [IGNITION] Launching ImpressionCore Ecosystem (React/Hybrid)..." -ForegroundColor Cyan
Write-Host " ----------------------------------------------------------------------------`n" -ForegroundColor Cyan

# Launch Backend
Write-Host " [STARTING] Spawning Neural Engine..." -ForegroundColor Gray
$backendStartInfo = New-Object System.Diagnostics.ProcessStartInfo
$backendStartInfo.FileName = "cmd.exe"
$backendStartInfo.Arguments = "/c start /min cmd /k `"$pythonExe`" src/interfaces/triad_api.py"
$backendStartInfo.WindowStyle = "Hidden" 
[System.Diagnostics.Process]::Start($backendStartInfo)

# Wait for Port 8000
Write-Host " [WAITING] Calibrating Neural Ports (8000)..." -ForegroundColor Gray
while (-not (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue)) { Start-Sleep -Seconds 1 }
Write-Host " [OK] Neural Engine Online." -ForegroundColor Green

# Launch Frontend (React)
Write-Host " [STARTING] Spawning Web Interface..." -ForegroundColor Gray
$webClientPath = Join-Path $PWD "src\interfaces\web_client"

# Check Node Modules
if (-not (Test-Path "$webClientPath\node_modules")) {
    Write-Host " [INFO] Installing Frontend Dependencies (First Run)..." -ForegroundColor Yellow
    Push-Location $webClientPath
    try { npm install } finally { Pop-Location }
}

$frontendStartInfo = New-Object System.Diagnostics.ProcessStartInfo
$frontendStartInfo.FileName = "cmd.exe"
# Using 'npm run dev' for Vite
$frontendStartInfo.Arguments = "/c start /max cmd /k npm run dev"
$frontendStartInfo.WorkingDirectory = $webClientPath # CRITICAL FIX: Explicitly set CWD
$frontendStartInfo.WindowStyle = "Hidden"
[System.Diagnostics.Process]::Start($frontendStartInfo)

Write-Host "`n [SUCCESS] System Live.`n" -ForegroundColor Green
Write-Host " Press any key to exit this check window..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
