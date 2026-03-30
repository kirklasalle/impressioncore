# VS Code Insiders - IDS MCP Server Troubleshooting Guide

**Created:** June 05, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\mcp_server\mcp_server_troubleshooting.md #command_line #documentation #security #testing  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Issue: "New Tools available (1)" but tools not loading

### Current Status

- ✅ IDS MCP Server initializes correctly
- ✅ All 5 tools are available (ids_search, ids_get_file_info, ids_list_tags, ids_get_system_status, ids_find_by_tag)
- ✅ Server responds to tool calls
- ❌ VS Code not loading the tools properly

### Troubleshooting Steps

#### 1. Check VS Code Output Panel

1. Open VS Code Insiders
2. Go to View > Output
3. Select "Model Context Protocol" from the dropdown
4. Look for error messages about the IDS server

#### 2. Verify Server Configuration

Current VS Code settings in `.vscode/settings.json`:
```json
{
  "mcp.servers": {
    "impressioncore-ids": {
      "command": ".mcp/ids-mcp/start_for_vscode.bat",
      "args": [],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

#### 3. Alternative Configuration Options

**Option A: Direct Python Command**
```json
{
  "mcp.servers": {
    "impressioncore-ids": {
      "command": "G:\\Program Files\\Python313\\python.exe",
      "args": [".mcp/ids-mcp/server.py"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

**Option B: Absolute Path**
```json
{
  "mcp.servers": {
    "impressioncore-ids": {
      "command": "G:\\Program Files\\Python313\\python.exe",
      "args": ["d:/Projects/impressioncore/.mcp/ids-mcp/server.py"],
      "cwd": "d:/Projects/impressioncore",
      "env": {
        "PYTHONPATH": "d:/Projects/impressioncore"
      }
    }
  }
}
```

#### 4. Manual Testing Steps

1. **Test the batch file directly:**

```bash
cd "d:\Projects\impressioncore"
.mcp\ids-mcp\start_for_vscode.bat
```

2. **Test the Python server directly:**

```bash
cd "d:\Projects\impressioncore\.mcp\ids-mcp"
python test_vscode_integration.py
```

3. **Check VS Code Developer Console:**
   - Press Ctrl+Shift+I in VS Code
   - Look for JavaScript errors related to MCP

#### 5. Force Refresh Steps

1. **Restart VS Code completely**
2. **Clear VS Code cache:**
   - Close VS Code
   - Delete: `%APPDATA%\Code - Insiders\User\workspaceStorage\[workspace-hash]\`
3. **Reload window:** Ctrl+Shift+P > "Developer: Reload Window"

#### 6. Check MCP Extension Status

1. Go to Extensions (Ctrl+Shift+X)
2. Search for "Model Context Protocol" or "MCP"
3. Ensure the extension is:
   - Installed
   - Enabled
   - Up to date

#### 7. Validate Tool Detection

After making changes:

1. Look for the refresh button in the lower right
2. Click it when it shows "New Tools available"
3. Check "Configure tools..." menu for the 5 IDS tools:
   - IDS Search
   - IDS File Info  
   - IDS List Tags
   - IDS System Status
   - IDS Find by Tag

#### 8. Common Issues and Solutions

**Issue: Python not found**

- Solution: Use absolute path to Python executable

**Issue: Module import errors**

- Solution: Ensure PYTHONPATH includes project root

**Issue: Server starts but no tools**

- Solution: Check server.py for syntax errors

**Issue: VS Code doesn't detect server**

- Solution: Restart VS Code and check MCP extension

#### 9. Debug Mode Configuration

Add debug logging to VS Code settings:
```json
{
  "mcp.servers": {
    "impressioncore-ids": {
      "command": "G:\\Program Files\\Python313\\python.exe",
      "args": [".mcp/ids-mcp/server.py"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "MCP_DEBUG": "true",
        "PYTHONUNBUFFERED": "1"
      }
    }
  },
  "mcp.debug": true
}
```

#### 10. Expected Final Result

When working correctly, you should see:

- No "New Tools available" notification
- 5 IDS tools in "Configure tools..." menu
- Ability to run searches like: "Use IDS search to find authentication security documentation"
- Tools return formatted results with file paths, scores, and metadata

### Next Steps if Still Not Working

1. Check VS Code Insiders version (ensure it supports MCP)
2. Try with a minimal MCP server to isolate the issue
3. Check VS Code Insiders documentation for MCP configuration
4. Consider using the Claude Dev extension as an alternative MCP client

---

**Created**: 2025-06-05 17:15:00
**Status**: Troubleshooting in progress
