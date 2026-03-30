@echo off
REM VS Code Extensions Cleanup Script for ImpressionCore
REM Generated: January 17, 2025

echo 🧹 Starting VS Code Extensions Cleanup for ImpressionCore...
echo This will remove extensions not needed for Python AI/ML development.
echo.

echo === Phase 1: Removing Java Development Stack (7 extensions) ===
echo Removing Java Language Support...
code-insiders --uninstall-extension redhat.java
echo Removing Gradle for Java...
code-insiders --uninstall-extension vscjava.vscode-gradle
echo Removing Java Debugger...
code-insiders --uninstall-extension vscjava.vscode-java-debug
echo Removing Java Dependency Viewer...
code-insiders --uninstall-extension vscjava.vscode-java-dependency
echo Removing Java Extension Pack...
code-insiders --uninstall-extension vscjava.vscode-java-pack
echo Removing Java Test Runner...
code-insiders --uninstall-extension vscjava.vscode-java-test
echo Removing Maven for Java...
code-insiders --uninstall-extension vscjava.vscode-maven
echo.

echo === Phase 2: Removing C# Development Stack (3 extensions) ===
echo Removing C# Dev Kit...
code-insiders --uninstall-extension ms-dotnettools.csdevkit
echo Removing C# Language Support...
code-insiders --uninstall-extension ms-dotnettools.csharp
echo Removing .NET Runtime...
code-insiders --uninstall-extension ms-dotnettools.vscode-dotnet-runtime
echo.

echo === Phase 3: Removing C++ Development Stack (4 extensions) ===
echo Removing CMake Tools...
code-insiders --uninstall-extension ms-vscode.cmake-tools
echo Removing C/C++ Extension...
code-insiders --uninstall-extension ms-vscode.cpptools
echo Removing C/C++ Extension Pack...
code-insiders --uninstall-extension ms-vscode.cpptools-extension-pack
echo Removing C/C++ Themes...
code-insiders --uninstall-extension ms-vscode.cpptools-themes
echo.

echo === Phase 4: Removing Container/Docker Tools (4 extensions) ===
echo Removing Docker...
code-insiders --uninstall-extension docker.docker
echo Removing Azure Container Tools...
code-insiders --uninstall-extension ms-azuretools.vscode-containers
echo Removing Remote - Containers...
code-insiders --uninstall-extension ms-vscode-remote.remote-containers
echo Removing Kubernetes Tools...
code-insiders --uninstall-extension ms-kubernetes-tools.vscode-kubernetes-tools
echo.

echo === Phase 5: Removing Web Development Tools (4 extensions) ===
echo Removing npm IntelliSense...
code-insiders --uninstall-extension christian-kohler.npm-intellisense
echo Removing Prettier Code Formatter...
code-insiders --uninstall-extension esbenp.prettier-vscode
echo Removing HTML CSS Support...
code-insiders --uninstall-extension ecmel.vscode-html-css
echo Removing Code Runner...
code-insiders --uninstall-extension formulahendry.code-runner
echo.

echo === Phase 6: Removing Browser/Debugging Tools (2 extensions) ===
echo Removing Firefox Debugger...
code-insiders --uninstall-extension firefox-devtools.vscode-firefox-debug
echo Removing Edge DevTools...
code-insiders --uninstall-extension ms-edgedevtools.vscode-edge-devtools
echo.

echo === Phase 7: Removing Redundant/Unused Tools (5 extensions) ===
echo Removing Project Manager...
code-insiders --uninstall-extension alefragnani.project-manager
echo Removing GitHub Repository Manager...
code-insiders --uninstall-extension henriquebruno.github-repository-manager
echo Removing Git History...
code-insiders --uninstall-extension donjayamanne.githistory
echo Removing PowerShell...
code-insiders --uninstall-extension ms-vscode.powershell
echo Removing VS Code Speech...
code-insiders --uninstall-extension ms-vscode.vscode-speech
echo.

echo 🎉 Extension cleanup completed!
echo.
echo Remaining extensions should be focused on:
echo - Python development (PyTorch, AI/ML)
echo - Jupyter notebooks
echo - GitHub Copilot and MCP integration
echo - Git/GitHub workflow
echo - Documentation (Markdown, YAML)
echo - Productivity tools for ImpressionCore development
echo.
echo 💡 Consider reviewing AI assistant extensions:
echo - You have 4 AI assistants installed (Copilot, Gemini, Roo Cline, Claude Dev)
echo - Consider keeping only 1-2 that you actively use
echo.
echo Run 'code-insiders --list-extensions' to see current extensions.
pause
