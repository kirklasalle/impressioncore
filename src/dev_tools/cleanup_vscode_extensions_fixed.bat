@echo off
REM VS Code Extensions Cleanup Script for ImpressionCore - Dependency Aware
REM Generated: January 17, 2025

echo 🧹 Starting VS Code Extensions Cleanup for ImpressionCore...
echo This will remove extensions not needed for Python AI/ML development.
echo Handling dependencies properly...
echo.

echo === Removing Java Development Stack ===
echo Removing Java extensions in dependency order...
code-insiders --uninstall-extension vscjava.vscode-java-test
code-insiders --uninstall-extension vscjava.vscode-java-debug
code-insiders --uninstall-extension vscjava.vscode-java-dependency
code-insiders --uninstall-extension vscjava.vscode-gradle
code-insiders --uninstall-extension vscjava.vscode-maven
code-insiders --uninstall-extension vscjava.vscode-java-pack
code-insiders --uninstall-extension redhat.java
echo.

echo === Removing C# Development Stack ===
code-insiders --uninstall-extension ms-dotnettools.csdevkit
code-insiders --uninstall-extension ms-dotnettools.csharp
code-insiders --uninstall-extension ms-dotnettools.vscode-dotnet-runtime
echo.

echo === Removing C++ Development Stack ===
code-insiders --uninstall-extension ms-vscode.cpptools-extension-pack
code-insiders --uninstall-extension ms-vscode.cpptools-themes
code-insiders --uninstall-extension ms-vscode.cmake-tools
code-insiders --uninstall-extension ms-vscode.cpptools
echo.

echo === Removing Container/Docker Tools ===
code-insiders --uninstall-extension ms-vscode-remote.remote-containers
code-insiders --uninstall-extension ms-azuretools.vscode-containers
code-insiders --uninstall-extension ms-kubernetes-tools.vscode-kubernetes-tools
code-insiders --uninstall-extension docker.docker
echo.

echo === Removing Web Development Tools ===
code-insiders --uninstall-extension christian-kohler.npm-intellisense
code-insiders --uninstall-extension esbenp.prettier-vscode
code-insiders --uninstall-extension ecmel.vscode-html-css
code-insiders --uninstall-extension formulahendry.code-runner
echo.

echo === Removing Browser/Debugging Tools ===
code-insiders --uninstall-extension firefox-devtools.vscode-firefox-debug
code-insiders --uninstall-extension ms-edgedevtools.vscode-edge-devtools
echo.

echo === Removing Redundant/Unused Tools ===
code-insiders --uninstall-extension alefragnani.project-manager
code-insiders --uninstall-extension henriquebruno.github-repository-manager
code-insiders --uninstall-extension donjayamanne.githistory
code-insiders --uninstall-extension ms-vscode.powershell
code-insiders --uninstall-extension ms-vscode.vscode-speech
echo.

echo 🎉 Extension cleanup completed!
echo.
echo Checking remaining extensions...
code-insiders --list-extensions
