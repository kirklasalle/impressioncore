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

set "VENV=.venv310"
set "PYTHON=%VENV%\Scripts\python.exe"
set "PIP=%VENV%\Scripts\pip.exe"
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
:: CHECK 1: Python virtual environment
:: ------------------------------------------------------------------
echo  [1/7] Checking Python virtual environment...
if not exist "%PYTHON%" (
    echo.
    echo  [FAIL] Virtual environment not found at: %VENV%\
    echo         Run:  python -m venv .venv310
    echo               .venv310\Scripts\pip install -e ".[all]"
    echo.
    pause
    exit /b 1
)

:: Activate the environment for subsequent commands
call "%VENV%\Scripts\activate.bat"
echo        OK -- %VENV% activated

:: ------------------------------------------------------------------
:: CHECK 2: Python version
:: ------------------------------------------------------------------
echo  [2/7] Checking Python version...
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
echo        OK -- %PYVER%

:: ------------------------------------------------------------------
:: CHECK 3: Core dependencies
:: ------------------------------------------------------------------
echo  [3/7] Checking core dependencies...
set "MISSING="

python -c "import flask" 2>nul
if errorlevel 1 set "MISSING=!MISSING! flask"

python -c "import flask_cors" 2>nul
if errorlevel 1 set "MISSING=!MISSING! flask-cors"

python -c "import jinja2" 2>nul
if errorlevel 1 set "MISSING=!MISSING! jinja2"

python -c "import werkzeug" 2>nul
if errorlevel 1 set "MISSING=!MISSING! werkzeug"

python -c "import torch" 2>nul
if errorlevel 1 set "MISSING=!MISSING! torch"

if defined MISSING (
    echo.
    echo  [WARN] Missing packages:%MISSING%
    echo         Attempting to install...
    pip install%MISSING% --quiet
    if errorlevel 1 (
        echo  [FAIL] Could not install missing packages. Run manually:
        echo         pip install%MISSING%
        pause
        exit /b 1
    )
    echo        OK -- Missing packages installed
) else (
    echo        OK -- flask, flask-cors, jinja2, werkzeug, torch
)

:: ------------------------------------------------------------------
:: CHECK 4: GPU / CUDA availability
:: ------------------------------------------------------------------
echo  [4/7] Checking GPU availability...
for /f "tokens=*" %%g in ('python -c "import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU-only (no CUDA)')" 2^>^&1') do set "GPU=%%g"
echo        OK -- %GPU%

:: ------------------------------------------------------------------
:: CHECK 5: Server entry point exists
:: ------------------------------------------------------------------
echo  [5/7] Checking server entry point...
if not exist "%SERVER%" (
    echo.
    echo  [FAIL] Server not found: %SERVER%
    echo         Ensure the repository is intact.
    pause
    exit /b 1
)
echo        OK -- %SERVER%

:: ------------------------------------------------------------------
:: CHECK 6: Compile Python bytecode (pre-warm)
:: ------------------------------------------------------------------
echo  [6/7] Compiling Python bytecode...
python -m compileall -q src\interfaces\web\ >nul 2>&1
python -m compileall -q src\core\utils\ >nul 2>&1
echo        OK -- bytecode compiled

:: ------------------------------------------------------------------
:: CHECK 7: React Builder client (builder_client)
:: ------------------------------------------------------------------
echo  [7/7] Checking React Builder client...
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
python "%SERVER%"

:: ------------------------------------------------------------------
:: Shutdown
:: ------------------------------------------------------------------
echo.
echo  Server stopped. Goodbye.
pause
exit /b 0
