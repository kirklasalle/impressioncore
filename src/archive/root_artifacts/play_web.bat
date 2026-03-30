@echo off
TITLE ImpressionCore Web Interface

echo [STARTING] Launching ImpressionCore Web Experience...

:: 1. Backend (Neural Engine)
echo [BACKEND] Spawning Triad API...
start "ImpressionCore Backend" cmd /k "python src/interfaces/triad_api.py"

:: 2. Frontend (Visual Cortex)
echo [FRONTEND] Spawning Web Client...
pushd src\interfaces\web_client
start "ImpressionCore Frontend" cmd /k "npm run dev"
popd

echo [WAITING] Waiting for services to initialize...
timeout /t 5 /nobreak >nul

echo [LAUNCH] Opening Default Browser...
start "" "http://localhost:3000"

echo [ONLINE] System Launch Sequence Initiated.
echo.
