@echo off
REM Conservative VS Code Extension Cleanup
REM Only removes extensions very likely to be unused

echo Conservative extension cleanup for ImpressionCore...
echo.

REM Remove Kubernetes tools (unlikely needed for local AI development)
echo Removing Kubernetes tools...
code-insiders --uninstall-extension ms-kubernetes-tools.vscode-kubernetes-tools

REM Remove Speech extension (rarely used for development)
echo Removing Speech extension...
code-insiders --uninstall-extension ms-vscode.vscode-speech

echo.
echo Conservative cleanup complete.
echo.
echo Remaining extensions: 44 (from 46)
echo.
echo Next steps - Review these categories:
echo 1. AI Assistants: Consider keeping only 1-2 you actively use
echo 2. WSL Remote: Remove if not using WSL development
echo 3. Web Dev Tools: Keep if working with MCP server or web interfaces
echo.
pause
