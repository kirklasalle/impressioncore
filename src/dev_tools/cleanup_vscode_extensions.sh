#!/bin/bash
# VS Code Extensions Cleanup Script for ImpressionCore
# Generated: January 17, 2025

echo "🧹 Starting VS Code Extensions Cleanup for ImpressionCore..."
echo "This will remove extensions not needed for Python AI/ML development."
echo ""

# Function to uninstall extension with confirmation
uninstall_extension() {
    local ext_id="$1"
    local description="$2"
    echo "Removing: $ext_id ($description)"
    code-insiders --uninstall-extension "$ext_id"
    if [ $? -eq 0 ]; then
        echo "✅ Successfully removed $ext_id"
    else
        echo "❌ Failed to remove $ext_id"
    fi
    echo ""
}

echo "=== Phase 1: Removing Java Development Stack (7 extensions) ==="
uninstall_extension "redhat.java" "Java Language Support"
uninstall_extension "vscjava.vscode-gradle" "Gradle for Java"
uninstall_extension "vscjava.vscode-java-debug" "Java Debugger"
uninstall_extension "vscjava.vscode-java-dependency" "Java Dependency Viewer"
uninstall_extension "vscjava.vscode-java-pack" "Java Extension Pack"
uninstall_extension "vscjava.vscode-java-test" "Java Test Runner"
uninstall_extension "vscjava.vscode-maven" "Maven for Java"

echo "=== Phase 2: Removing C# Development Stack (3 extensions) ==="
uninstall_extension "ms-dotnettools.csdevkit" "C# Dev Kit"
uninstall_extension "ms-dotnettools.csharp" "C# Language Support"
uninstall_extension "ms-dotnettools.vscode-dotnet-runtime" ".NET Runtime"

echo "=== Phase 3: Removing C++ Development Stack (4 extensions) ==="
uninstall_extension "ms-vscode.cmake-tools" "CMake Tools"
uninstall_extension "ms-vscode.cpptools" "C/C++ Extension"
uninstall_extension "ms-vscode.cpptools-extension-pack" "C/C++ Extension Pack"
uninstall_extension "ms-vscode.cpptools-themes" "C/C++ Themes"

echo "=== Phase 4: Removing Container/Docker Tools (4 extensions) ==="
uninstall_extension "docker.docker" "Docker"
uninstall_extension "ms-azuretools.vscode-containers" "Azure Container Tools"
uninstall_extension "ms-vscode-remote.remote-containers" "Remote - Containers"
uninstall_extension "ms-kubernetes-tools.vscode-kubernetes-tools" "Kubernetes Tools"

echo "=== Phase 5: Removing Web Development Tools (4 extensions) ==="
uninstall_extension "christian-kohler.npm-intellisense" "npm IntelliSense"
uninstall_extension "esbenp.prettier-vscode" "Prettier Code Formatter"
uninstall_extension "ecmel.vscode-html-css" "HTML CSS Support"
uninstall_extension "formulahendry.code-runner" "Code Runner"

echo "=== Phase 6: Removing Browser/Debugging Tools (2 extensions) ==="
uninstall_extension "firefox-devtools.vscode-firefox-debug" "Firefox Debugger"
uninstall_extension "ms-edgedevtools.vscode-edge-devtools" "Edge DevTools"

echo "=== Phase 7: Removing Redundant/Unused Tools (5 extensions) ==="
uninstall_extension "alefragnani.project-manager" "Project Manager"
uninstall_extension "henriquebruno.github-repository-manager" "GitHub Repository Manager"
uninstall_extension "donjayamanne.githistory" "Git History"
uninstall_extension "ms-vscode.powershell" "PowerShell"
uninstall_extension "ms-vscode.vscode-speech" "VS Code Speech"

echo "=== Phase 8: Optional - GitHub Actions (not currently used) ==="
read -p "Remove GitHub Actions extension? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    uninstall_extension "github.vscode-github-actions" "GitHub Actions"
fi

echo "=== Phase 9: Optional - Remote WSL (not currently used) ==="
read -p "Remove Remote WSL extension? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    uninstall_extension "ms-vscode-remote.remote-wsl" "Remote - WSL"
fi

echo "🎉 Extension cleanup completed!"
echo ""
echo "Remaining extensions should be focused on:"
echo "- Python development (PyTorch, AI/ML)"
echo "- Jupyter notebooks"
echo "- GitHub Copilot and MCP integration"
echo "- Git/GitHub workflow"
echo "- Documentation (Markdown, YAML)"
echo "- Productivity tools for ImpressionCore development"
echo ""
echo "💡 Consider reviewing AI assistant extensions:"
echo "- You have 4 AI assistants installed (Copilot, Gemini, Roo Cline, Claude Dev)"
echo "- Consider keeping only 1-2 that you actively use"
echo ""
echo "Run 'code-insiders --list-extensions' to see current extensions."
