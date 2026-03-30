# ImpressionCore Orbos Shutdown Script
# Refined for maximum hygiene and system monitor observability

$ports = @(8000, 3000) # 8000: Triad API, 3000: Vite Frontend
$consoleLog = "logs/triad_api_console.log"

# Function to log to both console and the file read by system_monitor.html
function Log-Monitor($message, $level = "INFO") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $logEntry = "INFO:ImpressionCore:[$timestamp] [SHUTDOWN] ${level}: $message"
    Write-Host " [SHUTDOWN] $message" -ForegroundColor Cyan
    try {
        Add-Content -Path $consoleLog -Value $logEntry -ErrorAction SilentlyContinue
    }
    catch {}
}

Log-Monitor "INITIATING SYSTEM HALT SEQUENCE" "IMPORTANT"

# 1. Kill processes listening on specified ports
foreach ($port in $ports) {
    Log-Monitor "Scanning port $port..."
    $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess -Unique | 
    Get-Process -ErrorAction SilentlyContinue

    if ($process) {
        $pName = $process.Name
        $pId = $process.Id
        Log-Monitor "Terminating service: $pName (PID: $pId) on port $port" "WARNING"
        Stop-Process -Id $pId -Force
        Start-Sleep -Seconds 1
    }
    else {
        Log-Monitor "Port $port is already clear." "DEBUG"
    }
}

# 2. Kill orphaned Python/Node processes
Log-Monitor "Cleaning up orphaned runtime processes (Python/Node)..."
Get-Process | Where-Object { $_.Name -match "python|node" } | ForEach-Object {
    try {
        $p = $_
        $cmd = $p.CommandLine
        # Target anything matching the project name or key files
        if ($cmd -match "impressioncore" -or $cmd -match "triad_api" -or $cmd -match "vite" -or $cmd -match "npm run") {
            Log-Monitor "Killing orphaned process: $($p.Name) (PID: $($p.Id))" "WARNING"
            Stop-Process -Id $p.Id -Force
        }
    }
    catch {}
}

# 3. Final Verification
Log-Monitor "Performing final port audit..."
$activePorts = @()
foreach ($port in $ports) {
    if (Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue) {
        $activePorts += $port
    }
}

if ($activePorts.Count -eq 0) {
    Log-Monitor "SUCCESS: All ImpressionCore systems halted. Ports are released." "SUCCESS"
}
else {
    Log-Monitor "WARNING: Ports still active: $($activePorts -join ', ')" "ERROR"
}

Log-Monitor "SHUTDOWN SEQUENCE COMPLETE. GOODBYE." "IMPORTANT"
