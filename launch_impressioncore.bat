@echo off
setlocal EnableExtensions

set "REPO_ROOT=%~dp0"
cd /d "%REPO_ROOT%"

if not exist "src\dev_tools\scripts\start_full_stack_with_monitor.bat" (
    echo [ERROR] Launcher not found: src\dev_tools\scripts\start_full_stack_with_monitor.bat
    exit /b 1
)

echo.
echo ================================================================
echo ImpressionCore Root Launcher
echo ================================================================
echo Root: %REPO_ROOT%
echo.

call "src\dev_tools\scripts\start_full_stack_with_monitor.bat" %*
exit /b %ERRORLEVEL%
