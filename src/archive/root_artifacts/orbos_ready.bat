@echo off
SETLOCAL EnableDelayedExpansion
TITLE ImpressionCore Orchestrator

set CONSOLE_LOG=logs\orchestrator.log
if not exist logs mkdir logs

:: Helper function for logging
echo --- [%DATE% %TIME%] ORBOS STARTUP INITIATED --- > %CONSOLE_LOG%

echo  [CLEANUP] Purging existing ImpressionCore and sensory processes...
echo INFO:ImpressionCore:[%TIME%] [STARTUP] INFO: Running pre-launch cleanup via orbos_stop.ps1 >> %CONSOLE_LOG%
powershell -NoProfile -ExecutionPolicy Bypass -File orbos_stop.ps1

echo  [SUCCESS] System Slate Cleared.
timeout /t 2 /nobreak >nul

echo  [STARTING] Spawning Neural Engine...
echo INFO:ImpressionCore:[%TIME%] [STARTUP] INFO: Launching Triad API (Port 8000) >> %CONSOLE_LOG%     
start "ImpressionCore Backend" cmd /k "py -3.10 src/interfaces/triad_api.py"

echo  [STARTING] Spawning Visual Cortex...
echo INFO:ImpressionCore:[%TIME%] [STARTUP] INFO: Launching Vite Frontend (Port 3000) >> %CONSOLE_LOG% 
pushd src\interfaces\web_client
start "ImpressionCore Frontend" cmd /k "npm run dev"
popd

echo  [WAITING] Calibrating Neural Ports (8000)...
:WAIT_BACKEND
powershell -Command "$status = try { Invoke-RestMethod -Uri 'http://localhost:8000/v1/system/status' -ErrorAction SilentlyContinue } catch { $null }; if ($status) { Write-Host \" [STATUS] Phase: $($status.loading_phase)\"; if ($status.loading_phase -eq 'READY') { exit 0 } else { exit 1 } } else { exit 1 }"
if %ERRORLEVEL% NEQ 0 (
    timeout /t 1 /nobreak >nul
    goto WAIT_BACKEND
)
echo  [READY] Neural Engine Online.
echo INFO:ImpressionCore:[%TIME%] [STARTUP] SUCCESS: Neural Engine READY >> %CONSOLE_LOG% 

echo  [WAITING] Initializing Visual Cortex (3000)...
:WAIT_FRONTEND
powershell -Command "try { $c = New-Object System.Net.Sockets.TcpClient; $c.Connect('127.0.0.1', 3000); $c.Dispose(); exit 0 } catch { exit 1 }"
if %ERRORLEVEL% NEQ 0 (
    timeout /t 1 /nobreak >nul
    goto WAIT_FRONTEND
)
echo  [READY] Visual Cortex Online.
echo INFO:ImpressionCore:[%TIME%] [STARTUP] SUCCESS: Visual Cortex READY >> %CONSOLE_LOG%

echo  [LAUNCH] Opening Holodeck...
echo INFO:ImpressionCore:[%TIME%] [STARTUP] INFO: Opening Application in Browser >> %CONSOLE_LOG%      
start "" "http://localhost:3000"

echo  [MONITOR] Starting System Monitor...
echo INFO:ImpressionCore:[%TIME%] [STARTUP] INFO: Opening System Monitor >> %CONSOLE_LOG%
start "" "http://localhost:3000/system_monitor.html"

echo.
echo  [ONLINE] System Ready.
echo.
echo INFO:ImpressionCore:[%TIME%] [STARTUP] SUCCESS: Full System ONLINE >> %CONSOLE_LOG%
pause
