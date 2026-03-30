@echo off
REM Refined VS Code Extension Cleanup for ImpressionCore
REM Based on user feedback - June 16, 2025

echo 🧹 ImpressionCore Extension Cleanup - User Refined
echo.
echo Based on your feedback:
echo ✅ Keeping Speech extension (used for voice prompting)
echo ✅ Keeping Web Dev tools (needed for MCP server and future web interfaces)
echo ❌ Removing Windows AI Studio (unused AI assistant)
echo ❌ Removing Kubernetes tools (not needed for local AI development)
echo.

echo === Confirmed Removals ===

echo Removing Windows AI Studio (unused AI assistant)...
code-insiders --uninstall-extension ms-windows-ai-studio.windows-ai-studio
if %errorlevel% == 0 (
    echo ✅ Successfully removed Windows AI Studio
) else (
    echo ❌ Windows AI Studio not found or already removed
)
echo.

echo Removing Kubernetes tools (not needed for local AI development)...
code-insiders --uninstall-extension ms-kubernetes-tools.vscode-kubernetes-tools
if %errorlevel% == 0 (
    echo ✅ Successfully removed Kubernetes tools
) else (
    echo ❌ Kubernetes tools not found or already removed
)
echo.

echo === Optional Removals ===
echo.
set /p remove_wsl="Remove Remote WSL extension? (y/N): "
if /i "%remove_wsl%"=="y" (
    echo Removing Remote WSL...
    code-insiders --uninstall-extension ms-vscode-remote.remote-wsl
    echo ✅ Removed Remote WSL
)

echo.
set /p remove_powershell="Remove PowerShell extension? (y/N): "
if /i "%remove_powershell%"=="y" (
    echo Removing PowerShell...
    code-insiders --uninstall-extension ms-vscode.powershell
    echo ✅ Removed PowerShell
)

echo.
echo 🎉 Extension cleanup completed!
echo.
echo Current AI Assistants remaining:
echo - GitHub Copilot (Essential)
echo - Google Gemini Code Assist
echo - Roo Cline
echo - Claude Dev
echo.
echo 💡 All Web Development extensions kept for MCP server and future web interfaces
echo 💡 Speech extension kept for voice prompting with AI assistants
echo.

echo Checking final extension count...
code-insiders --list-extensions | find /c /v ""
echo.
pause
