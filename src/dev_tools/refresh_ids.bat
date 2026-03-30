@echo off
REM ImpressionCore IDS Quick Refresh - One-line command
REM Usage: Just run this batch file before using IDS tools

cd /d "%~dp0..\.."
call .venv\Scripts\activate.bat
python src\dev_tools\ids_refresh.py
