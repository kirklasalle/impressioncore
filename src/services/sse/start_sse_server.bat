@echo off
rem ImpressionCore IDS MCP SSE Server Startup Script (Windows)
rem This script starts the SSE server for VS Code MCP integration

echo 🚀 Starting ImpressionCore IDS MCP SSE Server...

rem Change to the server directory
cd /d "%~dp0\.mcp\ids-mcp" || (
    echo ❌ Error: Could not change to server directory
    exit /b 1
)

rem Check if Python is available
python --version >nul 2>&1 || (
    echo ❌ Error: Python is not installed or not in PATH
    exit /b 1
)

rem Check if server_sse.py exists
if not exist "server_sse.py" (
    echo ❌ Error: server_sse.py not found in %cd%
    exit /b 1
)

rem Check if the server is already running
curl -s --connect-timeout 2 http://127.0.0.1:3001/health >nul 2>&1 && (
    echo ⚠️  Server is already running on port 3001
    echo 🔍 Server status:
    curl -s http://127.0.0.1:3001/health
    exit /b 0
)

echo 📁 Working directory: %cd%
python --version
echo 🌐 Starting server on http://127.0.0.1:3001
echo 📡 SSE endpoint: http://127.0.0.1:3001/sse
echo.
echo ✨ All 17 ImpressionCore IDS tools will be available
echo 🔧 Server can be stopped with Ctrl+C
echo.

rem Start the server
python server_sse.py
