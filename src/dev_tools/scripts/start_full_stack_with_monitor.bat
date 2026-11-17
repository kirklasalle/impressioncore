@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%\..\..\..") do set "REPO_ROOT=%%~fI"
set "PY_EXE="
set "VENV_DIR="
if exist "%REPO_ROOT%\.venv310\Scripts\python.exe" (
    set "VENV_DIR=.venv310"
    set "PY_EXE=%REPO_ROOT%\.venv310\Scripts\python.exe"
) else if exist "%REPO_ROOT%\.venv\Scripts\python.exe" (
    set "VENV_DIR=.venv"
    set "PY_EXE=%REPO_ROOT%\.venv\Scripts\python.exe"
) else (
    for /f "delims=" %%p in ('where python 2^>nul') do if not defined PY_EXE set "PY_EXE=%%p"
)
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

if defined VENV_DIR (
    call :check_file "%VENV_DIR%\Scripts\activate.bat" "Python venv activation"
    call :check_file "%VENV_DIR%\Scripts\python.exe" "Python interpreter"
) else if defined PY_EXE (
    echo [OK] Python interpreter fallback ^(%PY_EXE%^)
) else (
    echo [MISSING] Python interpreter ^(.venv310, .venv, or PATH^)
    set "FAIL=1"
)
call :check_file "src\interfaces\triad_api.py" "Backend entrypoint"
call :check_file "src\core\utils\vrgc_autonomous_monitor.py" "Monitor entrypoint"
call :check_file "src\interfaces\web_client\package.json" "Frontend package"

call :check_cmd python "Python"
call :check_cmd node "Node.js"
call :check_cmd npm "npm"
call :check_python_module cv2 "OpenCV cv2"
call :check_python_module fastapi "FastAPI"
call :check_python_module uvicorn "Uvicorn"
call :check_python_module multipart "python-multipart"

if not "!FAIL!"=="0" (
    echo.
    echo [ERROR] Startup checks failed. Install the missing Python packages with:
    echo         "%PY_EXE%" -m pip install -r requirements.txt
    exit /b 1
)

echo.
echo [STORAGE] Checking required model and data directories...
"%PY_EXE%" -m src.core.config.data_paths
if errorlevel 1 (
    echo [ERROR] Storage check failed. No services were launched or stopped.
    exit /b 1
)

echo.
echo [OK] Startup checks passed.

if "%CHECKS_ONLY%"=="1" (
    echo [INFO] Checks-only mode enabled. Exiting without launching services.
    exit /b 0
)

echo.
echo [LOCAL RUNTIME] Starting supervised API, UI and monitor.
echo Open http://127.0.0.1:5173/ after Vite reports ready.
echo Models use the local cache. Camera capture starts only with explicit consent.
echo Existing services are never terminated by this launcher.
echo Press Ctrl+C to stop the services started by this window.
"%PY_EXE%" "%REPO_ROOT%\src\dev_tools\scripts\run_local_runtime.py" --monitor
exit /b %errorlevel%

:check_file
if exist "%~1" (
    echo [OK] %~2
) else (
    echo [MISSING] %~2 ^(%~1^)
    set "FAIL=1"
)
exit /b 0

:check_python_module
"%PY_EXE%" -c "import %~1" >nul 2>&1
if errorlevel 1 (
    echo [MISSING] Python module %~2
    set "FAIL=1"
) else (
    echo [OK] Python module %~2 available
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
