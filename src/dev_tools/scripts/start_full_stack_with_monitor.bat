@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%\..\..\..") do set "REPO_ROOT=%%~fI"
set "PY_EXE=%REPO_ROOT%\.venv310\Scripts\python.exe"
cd /d "%REPO_ROOT%"

set "CHECKS_ONLY=0"
set "NO_CLEANUP=0"

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--checks-only" set "CHECKS_ONLY=1"
if /I "%~1"=="--no-cleanup" set "NO_CLEANUP=1"
shift
goto parse_args

:args_done

echo.
echo ================================================================
echo ImpressionCore Startup Orchestrator
echo ================================================================
echo Repo Root: %REPO_ROOT%
echo.

set "FAIL=0"

call :check_file ".venv310\Scripts\activate.bat" "Python venv activation"
call :check_file ".venv310\Scripts\python.exe" "Python interpreter"
call :check_file "src\interfaces\triad_api.py" "Backend entrypoint"
call :check_file "src\core\utils\vrgc_autonomous_monitor.py" "Monitor entrypoint"
call :check_file "src\interfaces\web_client\package.json" "Frontend package"

call :check_cmd python "Python"
call :check_cmd node "Node.js"
call :check_cmd npm "npm"

if "%FAIL%"=="1" (
    echo.
    echo [ERROR] Startup checks failed. Fix the missing requirements above.
    exit /b 1
)

echo.
echo [OK] Startup checks passed.

if "%CHECKS_ONLY%"=="1" (
    echo [INFO] Checks-only mode enabled. Exiting without launching services.
    exit /b 0
)

if "%NO_CLEANUP%"=="1" (
    echo.
    echo [INFO] No-cleanup mode enabled. Skipping process cleanup.
) else (
    echo.
    echo [CLEANUP] Ensuring clean process state...
    taskkill /FI "WINDOWTITLE eq ImpressionCore Backend*" /T /F >nul 2>&1
    taskkill /FI "WINDOWTITLE eq ImpressionCore Frontend*" /T /F >nul 2>&1
    taskkill /FI "WINDOWTITLE eq ImpressionCore Monitor*" /T /F >nul 2>&1

    for %%P in (8000 5173) do (
            for /f "tokens=5" %%K in ('netstat -ano ^| findstr /R /C:":%%P .*LISTENING"') do (
                    taskkill /PID %%K /F >nul 2>&1
            )
    )

    echo [OK] Clean process state prepared.
)

echo.
echo [BACKEND] Launching Triad API on port 8000...
start "ImpressionCore Backend" /D "%REPO_ROOT%" cmd /k ""%PY_EXE%" "%REPO_ROOT%\src\interfaces\triad_api.py""

echo [FRONTEND] Launching Vite web client on port 5173...
start "ImpressionCore Frontend" cmd /k "cd /d ""%REPO_ROOT%\src\interfaces\web_client"" && npm run dev -- --host 0.0.0.0 --port 5173"

echo [MONITOR] Launching VRGC autonomous monitor...
start "ImpressionCore Monitor" /D "%REPO_ROOT%" cmd /k ""%PY_EXE%" "%REPO_ROOT%\src\core\utils\vrgc_autonomous_monitor.py""

echo.
echo [WAIT] Waiting for backend API readiness (http://127.0.0.1:8000/v1/system/status)...
set "API_READY=0"
for /L %%I in (1,1,30) do (
    powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/v1/system/status' -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) { exit 0 } else { exit 1 } } catch { exit 1 }"
    if not errorlevel 1 (
        set "API_READY=1"
        goto :api_ready
    )
    timeout /t 1 /nobreak >nul
)

:api_ready
if "%API_READY%"=="1" (
    echo [OK] Backend API is reachable.
) else (
    echo [WARN] Backend API not reachable yet. Opening URLs anyway.
)

echo [WEB] Opening frontend and system monitor URLs in browser...
start "" "http://127.0.0.1:5173/"
start "" "http://127.0.0.1:8000/system_monitor.html"

echo.
echo [DONE] Backend + Frontend + Monitor launch sequence initiated.
echo        Backend:  http://127.0.0.1:8000
echo        Frontend: http://127.0.0.1:5173
echo        Monitor:  http://127.0.0.1:8000/system_monitor.html
echo.
exit /b 0

:check_file
if exist "%~1" (
    echo [OK] %~2
) else (
    echo [MISSING] %~2 ^(%~1^)
    set "FAIL=1"
)
exit /b 0

:check_cmd
where %~1 >nul 2>&1
if errorlevel 1 (
    echo [MISSING] %~2 command not found in PATH
    set "FAIL=1"
) else (
    echo [OK] %~2 command found
)
exit /b 0
