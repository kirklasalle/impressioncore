@echo off
echo =====================================
echo ImpressionCore Troubleshooting Utility
echo =====================================
echo.

echo Checking environment...
echo ---------------------
echo Python Version:
python --version
echo.

echo Checking packages...
python -c "import pkg_resources; print('Package check: OK')" 2>nul
if %ERRORLEVEL% NEQ 0 echo Package resources not available - possible installation issue

echo.
echo Checking PyTorch...
python -c "import torch; print(f'PyTorch Version: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}')" 2>nul
if %ERRORLEVEL% NEQ 0 echo PyTorch not installed or has issues.

echo.
echo Checking Flask...
python -c "import flask; print(f'Flask Version: {flask.__version__}')" 2>nul
if %ERRORLEVEL% NEQ 0 echo Flask not installed or has issues.

echo.
echo Checking directory structure...
echo ----------------------------

if not exist "src\web\templates" mkdir templates & echo Created missing templates directory
if not exist "src\web\static" mkdir static & echo Created missing static directory
if not exist "src\web\static\js" mkdir static\js & echo Created missing static\js directory
if not exist "src\web\static\css" mkdir static\css & echo Created missing static\css directory
if not exist "src\web\static\img" mkdir static\img & echo Created missing static\img directory

echo.
echo Verifying key files...
echo -------------------

if not exist "src\web\server.py" echo MISSING: src\web\server.py - Server file not found!
if not exist "src\web\static\js\walkthrough.js" echo MISSING: static\js\walkthrough.js - Walkthrough script not found!

echo.
echo Checking GPU configuration...
echo -------------------------
python -c "import torch; print('GPU(s) detected:' + ('None' if not torch.cuda.is_available() else '')); [print(f' - {i}: {torch.cuda.get_device_name(i)}') for i in range(torch.cuda.device_count())]" 2>nul
if %ERRORLEVEL% NEQ 0 echo Could not check GPU configuration.

echo.
echo Troubleshooting complete. Please address any issues identified above.
echo.
