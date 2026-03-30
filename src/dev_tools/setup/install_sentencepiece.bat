@echo off
echo Setting up Visual Studio 2022 Build Tools environment...
call "G:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\LaunchDevCmd.bat"

echo.
echo Environment variables set:
echo PATH=%PATH%
echo INCLUDE=%INCLUDE%
echo LIB=%LIB%

echo.
echo Activating Python virtual environment...
call "D:\Projects\impressioncore\.venv\Scripts\activate.bat"

echo.
echo Installing SentencePiece...
python -m pip install --upgrade pip
python -m pip install sentencepiece --verbose

echo.
echo Installation complete!
pause
