#!/bin/bash

# ImpressionCore IDS MCP SSE Server Startup Script
# This script starts the SSE server for VS Code MCP integration

echo "🚀 Starting ImpressionCore IDS MCP SSE Server..."

# Change to the server directory
cd "$(dirname "$0")/.mcp/ids-mcp" || {
    echo "❌ Error: Could not change to server directory"
    exit 1
}

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed or not in PATH"
    exit 1
fi

# Check if server_sse.py exists
if [ ! -f "server_sse.py" ]; then
    echo "❌ Error: server_sse.py not found in $(pwd)"
    exit 1
fi

# Check if the server is already running
if curl -s --connect-timeout 2 http://127.0.0.1:3001/health > /dev/null 2>&1; then
    echo "⚠️  Server is already running on port 3001"
    echo "🔍 Server status:"
    curl -s http://127.0.0.1:3001/health | python -m json.tool
    exit 0
fi

echo "📁 Working directory: $(pwd)"
echo "🐍 Python version: $(python --version 2>&1)"
echo "🌐 Starting server on http://127.0.0.1:3001"
echo "📡 SSE endpoint: http://127.0.0.1:3001/sse"
echo ""
echo "✨ All 17 ImpressionCore IDS tools will be available"
echo "🔧 Server can be stopped with Ctrl+C"
echo ""

# Start the server
python server_sse.py
