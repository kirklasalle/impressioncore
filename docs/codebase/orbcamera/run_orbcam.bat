@echo off
setlocal
echo ==========================================
echo    OrbOS - Intelligent Camera System
echo ==========================================
echo.
echo 1) Launch OrbOS Preview
echo 2) Launch OrbOS Chat Interface (AI Assistant)
echo 3) Run OrbOS Autonomous Agent
echo 4) Run OrbOS System Diagnostics
echo 5) Exit
echo.
set /p choice="Select an option (1-5): "

if "%choice%"=="1" goto preview
if "%choice%"=="2" goto chat
if "%choice%"=="3" goto agent
if "%choice%"=="4" goto diagnose
if "%choice%"=="5" exit
goto start

:preview
echo.
echo Launching OrbOS Preview...
python -m orbcam.cli --debug preview
pause
exit

:chat
echo.
echo ==========================================
echo    Starting OrbOS Chat Interface...
echo ==========================================
echo.
echo Opening http://127.0.0.1:5000 in your browser...
python -m orbcam.cli chat
pause
exit

:agent
echo.
echo Launching OrbOS Autonomous Agent...
python autonomous_agent.py
pause
exit

:diagnose
echo.
echo Running OrbOS System Diagnostics...
python -m orbcam.cli diagnose
echo.
echo Diagnostics complete. Check 'diagnose_report.txt' for details.
pause
exit
