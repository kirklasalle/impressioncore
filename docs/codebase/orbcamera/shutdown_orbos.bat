@echo off
echo ==========================================
echo    OrbOS - Graceful Shutdown
echo ==========================================
echo.
echo Sending shutdown signal to OrbOS server...

curl -X POST http://127.0.0.1:5000/api/shutdown 2>nul

if %errorlevel% neq 0 (
    echo.
    echo Server appears to be offline or not responding.
    echo If OrbOS is running, it should shutdown within a few seconds.
) else (
    echo.
    echo Shutdown signal sent successfully.
)

echo.
echo OrbOS has been stopped.
pause
