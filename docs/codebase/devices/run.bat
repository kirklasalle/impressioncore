@echo off
cd /d "%~dp0"

REM Logging wrapper
call :MAIN > launcher.log 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Launcher failed. See launcher.log for details.
    pause
)
goto :EOF

:MAIN
echo [%DATE% %TIME%] Starting Device Manager Launcher (Simple Mode)...

REM Try launching with standard python command
echo [%DATE% %TIME%] Attempting to launch with 'python'...
python main.py
if %ERRORLEVEL% EQU 0 goto :Success

REM Fallback to py check
echo [%DATE% %TIME%] 'python' failed or exited with error. Trying 'py'...
py main.py
if %ERRORLEVEL% EQU 0 goto :Success

echo [%DATE% %TIME%] ERROR: Application failed to start using both 'python' and 'py'.
exit /b 1

:Success
echo [%DATE% %TIME%] Application exited successfully.
exit /b 0
