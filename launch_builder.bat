@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: ================================================================
::  ImpressionCore Model Builder -- Launcher
::  Created: February 21, 2026
::  Author: Kirk LaSalle
::
::  Performs pre-flight checks, compiles static assets,
::  and launches the Flask-based Builder UI on port 5000.
:: ================================================================

title ImpressionCore Model Builder

set "REPO_ROOT=%~dp0"
cd /d "%REPO_ROOT%"

set "VENV="
set "PYTHON="
if exist "%REPO_ROOT%\.venv310\Scripts\python.exe" (
    set "VENV=.venv310"
    set "PYTHON=%REPO_ROOT%\.venv310\Scripts\python.exe"
) else if exist "%REPO_ROOT%\.venv\Scripts\python.exe" (
    set "VENV=.venv"
    set "PYTHON=%REPO_ROOT%\.venv\Scripts\python.exe"
) else (
    for /f "delims=" %%p in ('where python 2^>nul') do if not defined PYTHON set "PYTHON=%%p"
)
set "SERVER=src\interfaces\web\server.py"
set "PORT=5000"
set "URL=http://127.0.0.1:%PORT%"

echo.
echo  ==============================================================================
echo  ------------------------------------------------------------------------------
echo   ___ __  __ ____  ____  _____ ____ ____ ___ ___  _   _  ____ ___  ____  _____
echo   ^|_ _^|  \/  ^|  _ \^|  _ \^| ____/ ___/ ___^|_ _/ _ \^| \ ^| ^|/ ___/ _ \^|  _ \^| ____^|
echo    ^| ^|^| ^|\/^| ^| ^|_) ^| ^|_) ^|  _^| \___ \___ \^| ^| ^| ^| ^|  \^| ^| ^|  ^| ^| ^| ^| ^|_) ^|  _^|
echo    ^| ^|^| ^|  ^| ^|  __/^|  _ ^<^| ^|___ ___) ^|__) ^| ^| ^|_^| ^| ^|\  ^| ^|__^| ^|_^| ^|  _ ^<^| ^|___
echo   ^|___^|_^|  ^|_^|_^|   ^|_^| \_\_____^|____/____/___\___/^|_^| \_^|\____\___/^|_^| \_\_____^|
echo.
echo  ------------------------------------------------------------------------------
echo  ==============================================================================
echo.
echo  The ImpressionCore Model Builder 
echo  - Digital Security and Privacy control through AI Democritization
echo  - Digital Impression of Human, Plant, Animal, Geoligical, etc. 
echo  - Human support, safety and protection guided by, the 10 laws and framework. 
echo  ==============================================================================
echo.

:: ------------------------------------------------------------------
:: CHECK 1: Python runtime (local venv or system Python fallback)
:: ------------------------------------------------------------------
echo  [1/8] Checking Python environment...
if not defined PYTHON (
    echo.
    echo  [FAIL] No Python interpreter found ^(.venv310, .venv, or PATH^).
    echo         Run:  python -m venv .venv
    echo               .venv\Scripts\pip install -e ".[all]"
    echo.
    pause
    exit /b 1
)

if defined VENV if exist "%REPO_ROOT%\%VENV%\Scripts\activate.bat" (
    call "%REPO_ROOT%\%VENV%\Scripts\activate.bat"
    echo        OK -- %VENV% activated
) else (
    echo        OK -- Using system Python ^(%PYTHON%^)
)

:: ------------------------------------------------------------------
:: CHECK 2: Python version
:: ------------------------------------------------------------------
echo  [2/8] Checking Python version...
for /f "tokens=*" %%v in ('"%PYTHON%" --version 2^>^&1') do set "PYVER=%%v"
echo        OK -- %PYVER%

:: ------------------------------------------------------------------
:: CHECK 3: External storage
:: ------------------------------------------------------------------
echo  [3/8] Checking required model and data directories...
set "PYTHONPATH=%REPO_ROOT%"
"%PYTHON%" -m src.core.config.data_paths
if errorlevel 1 (
    echo  [FAIL] Storage check failed. The Builder was not started.
    pause
    exit /b 1
)

:: ------------------------------------------------------------------
:: CHECK 4: Core dependencies
:: ------------------------------------------------------------------
echo  [4/8] Checking core dependencies...
set "MISSING="

"%PYTHON%" -c "import flask" 2>nul
if errorlevel 1 set "MISSING=!MISSING! flask"

"%PYTHON%" -c "import flask_cors" 2>nul
if errorlevel 1 set "MISSING=!MISSING! flask-cors"

"%PYTHON%" -c "import jinja2" 2>nul
if errorlevel 1 set "MISSING=!MISSING! jinja2"

"%PYTHON%" -c "import werkzeug" 2>nul
if errorlevel 1 set "MISSING=!MISSING! werkzeug"

"%PYTHON%" -c "import torch" 2>nul
if errorlevel 1 set "MISSING=!MISSING! torch"

if defined MISSING (
    echo.
    echo  [WARN] Missing packages:%MISSING%
    echo         Attempting to install...
    "%PYTHON%" -m pip install%MISSING% --quiet
    if errorlevel 1 (
        echo  [FAIL] Could not install missing packages. Run manually:
        echo         "%PYTHON%" -m pip install%MISSING%
        pause
        exit /b 1
    )
    echo        OK -- Missing packages installed
) else (
    echo        OK -- flask, flask-cors, jinja2, werkzeug, torch
)

:: ------------------------------------------------------------------
:: CHECK 5: GPU / CUDA availability
:: ------------------------------------------------------------------
echo  [5/8] Checking GPU availability...
for /f "tokens=*" %%g in ('"%PYTHON%" -c "import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU-only (no CUDA)')" 2^>^&1') do set "GPU=%%g"
echo        OK -- %GPU%

:: ------------------------------------------------------------------
:: CHECK 6: Server entry point exists
:: ------------------------------------------------------------------
echo  [6/8] Checking server entry point...
if not exist "%SERVER%" (
    echo.
    echo  [FAIL] Server not found: %SERVER%
    echo         Ensure the repository is intact.
    pause
    exit /b 1
)
echo        OK -- %SERVER%

:: ------------------------------------------------------------------
:: CHECK 7: Compile Python bytecode (pre-warm)
:: ------------------------------------------------------------------
echo  [7/8] Compiling Python bytecode...
"%PYTHON%" -m compileall -q src\interfaces\web\ >nul 2>&1
"%PYTHON%" -m compileall -q src\core\utils\ >nul 2>&1
echo        OK -- bytecode compiled

:: ------------------------------------------------------------------
:: CHECK 8: React Builder client (builder_client)
:: ------------------------------------------------------------------
echo  [8/8] Checking React Builder client...
set "BUILDER_CLIENT=src\interfaces\builder_client"
if exist "%BUILDER_CLIENT%\dist\index.html" (
    echo        OK -- production build found
) else if exist "%BUILDER_CLIENT%\package.json" (
    echo        dist/ not found — building React client...
    where npm >nul 2>&1
    if errorlevel 1 (
        echo        [WARN] npm not found — React UI unavailable
        echo               Install Node.js from https://nodejs.org
    ) else (
        pushd "%BUILDER_CLIENT%"
        if not exist "node_modules" (
            echo        Installing dependencies...
            call npm install >nul 2>&1
        )
        echo        Running production build...
        call npx vite build >nul 2>&1
        if exist "dist\index.html" (
            echo        OK -- React client built successfully
        ) else (
            echo        [WARN] Build failed -- React UI unavailable
        )
        popd
    )
) else (
    echo        [SKIP] builder_client not found -- using Jinja templates only
)

:: ------------------------------------------------------------------
:: Pre-flight summary
:: ------------------------------------------------------------------
echo.
echo  ===================================================================
echo   Pre-flight checks PASSED
echo   Server  : %URL%
echo   GPU     : %GPU%
echo   Python  : %PYVER%
echo  ===================================================================
echo.

:: ------------------------------------------------------------------
:: Check if port is already in use
:: ------------------------------------------------------------------
netstat -ano | findstr ":%PORT% " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo  [WARN] Port %PORT% is already in use.
    echo         Another instance may be running.
    echo.
    for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT% " ^| findstr "LISTENING"') do set "PORT_PID=%%p"
    echo         PID using port %PORT%: !PORT_PID!
    choice /C RN /M "  Restart existing process and launch fresh? (R/N)"
    if !errorlevel! == 1 (
        echo  Stopping process !PORT_PID! ...
        taskkill /PID !PORT_PID! /F >nul 2>&1
        timeout /t 2 /nobreak >nul
        echo        OK -- previous process stopped
    ) else (
        echo.
        echo  Aborting. Stop the existing process on port %PORT% first.
        pause
        exit /b 1
    )
)

:: ------------------------------------------------------------------
:: Launch the Flask server
:: ------------------------------------------------------------------
echo  Starting ImpressionCore Model Builder on port %PORT%...
echo  Press Ctrl+C to stop the server.
echo.

:: Set PYTHONPATH to repo root so "from src.*" imports resolve correctly
set "PYTHONPATH=%REPO_ROOT%"

:: Open browser after a short delay (background)
start "" /b cmd /c "timeout /t 3 /nobreak >nul && start "" %URL%"

:: Run the server (foreground — Ctrl+C to stop)
"%PYTHON%" "%SERVER%"
set "SERVER_EXIT_CODE=%ERRORLEVEL%"

:: ------------------------------------------------------------------
:: Shutdown
:: ------------------------------------------------------------------
echo.
if not "%SERVER_EXIT_CODE%"=="0" (
    echo  [FAIL] Builder server exited with code %SERVER_EXIT_CODE%. Review the error above.
) else (
    echo  Server stopped. Goodbye.
)
pause
exit /b %SERVER_EXIT_CODE%
