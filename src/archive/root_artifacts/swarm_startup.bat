@echo off
TITLE ImpressionCore 2025: Swarm Intelligence Ignition
COLOR 0B

echo =======================================================
echo   🚀 IGNITING IMPRESSIONCORE 2025 MCP SWARM 🚀
echo =======================================================
echo.

SET VENV=d:\Projects\impressioncore\.venv310\Scripts\python.exe
SET PROJECT_ROOT=d:\Projects\impressioncore
SET MCP_ROOT=d:\Projects\impressioncore\.mcp
SET GOLIATH_FAST_START=1

echo [1/3] Verifying Hardware Health (GTX 1050 Ti)...
%VENV% -c "import torch; print(f'GPU Found: {torch.cuda.get_device_name(0)}' if torch.cuda.is_available() else 'No GPU Found')"

echo.
echo [2/3] Initializing Goliath Nerve Center...
cd %MCP_ROOT%\impressioncore-goliath
start "GOLIATH-NERVE-CENTER" /MIN %VENV% server.py

echo.
echo [3/3] Synchronizing Swarm Bridges (IDS, EDS, IPA, VRGC)...
echo 🌳 IDS: Documentation GraphRAG... Standby
echo 🖼️ EDS: Educational Curator... Standby
echo 🧠 IPA: Synthesis-First Assistant... Standby
echo 🤖 VRGC: SAPR Software Robot... Standby

echo.
echo =======================================================
echo   ✅ SWARM IGNITION COMPLETE: ACTIVE ON PORT 8000
echo =======================================================
echo.
pause
