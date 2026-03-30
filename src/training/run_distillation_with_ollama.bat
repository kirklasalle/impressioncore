@echo off
echo ========================================================
echo ImpressionCore Knowledge Distillation with Ollama
echo ========================================================

echo Step 1: Checking if Ollama is running...
curl -s http://localhost:11434/api/version > nul
if %ERRORLEVEL% NEQ 0 (
    echo Ollama is not running! Please start Ollama first.
    echo Run 'ollama serve' in a separate terminal.
    pause
    exit /b 1
)

echo Ollama is running! Available models:
ollama list

echo.
echo Step 2: Checking Python environment...
if not exist env (
    echo Python environment not found. Setting up...
    call setup_environment.bat
) else (
    echo Python environment exists.
)

echo.
echo Step 3: Create directory structure if needed...
if not exist training\web (
    echo Creating necessary directories...
    call create_structure.bat
) else (
    echo Directory structure exists.
)

echo.
echo Step 4: Installing Flask-CORS if needed...
if not exist env\Lib\site-packages\flask_cors (
    echo Installing Flask-CORS...
    call env\Scripts\pip install flask-cors
) else (
    echo Flask-CORS already installed.
)

echo.
echo Step 5: Starting the training server...
start /b python run_training_server.py

echo.
echo Step 6: Opening dashboard in browser...
timeout /t 3 > nul
start http://localhost:5000

echo.
echo ========================================================
echo ImpressionCore Knowledge Distillation is now running!
echo.
echo Instructions:
echo 1. In the web dashboard, select your Ollama model as the teacher
echo 2. Configure student model and training parameters
echo 3. Click "Start Training" to begin knowledge distillation
echo 4. Monitor progress in the dashboard
echo.
echo To stop the server, close the command prompt window that opened
echo ========================================================

pause
