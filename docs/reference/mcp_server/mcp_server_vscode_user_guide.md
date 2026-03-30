# ImpressionCore IDS MCP Tools - VS Code User Guide

**Created:** June 07, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\mcp_server\mcp_server_vscode_user_guide.md #documentation #memory_management  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## ✅ Server Status: PRODUCTION READY

- **17 tools registered and available**
- **Server configuration verified**
- **No conflicts detected**

## 🛠️ Available Tools

Your ImpressionCore IDS MCP server provides these 17 tools:

1. **search** - Search through ImpressionCore documentation using IDS tagging system
2. **get-file-info** - Get detailed information about a specific file
3. **list-tags** - List all available tags in the IDS system
4. **get-system-status** - Get current status and statistics of the IDS system
5. **find-by-tag** - Find all files associated with specific tags
6. **bookmark-management** - Manage documentation bookmarks and favorites
7. **rebuild-index** - Rebuild the documentation index from source files
8. **get-documentation-stats** - Get comprehensive statistics about documentation
9. **validate-index** - Validate the integrity of the documentation index
10. **export-data** - Export documentation data to various formats
11. **import-data** - Import documentation data from external sources
12. **get-recent-changes** - Get recently modified documentation files
13. **search-content** - Perform full-text search within documentation content
14. **manage-tags** - Add, remove, or modify tags for documentation files
15. **analyze-documentation** - Perform comprehensive analysis of documentation quality
16. **backup-system** - Create a complete backup of the documentation system
17. **restore-system** - Restore documentation system from backup

## 🔍 How to Access Tools in VS Code

### Method 1: Command Palette

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "MCP" to see MCP-related commands
3. Look for commands like:
   - `MCP: List Tools`
   - `MCP: Call Tool`
   - `MCP: Show MCP Status`

### Method 2: GitHub Copilot Chat

1. Open Copilot Chat (`Ctrl+Shift+I` or view panel)
2. Use the `@` symbol to mention MCP tools:

   ```
   @mcp search for authentication documentation
   @mcp list-tags to see available categories
   @mcp get-system-status
   ```

### Method 3: Extensions View

1. Go to Extensions (`Ctrl+Shift+X`)
2. Search for "MCP" or "Model Context Protocol"
3. Check if the MCP extension is installed and active

### Method 4: Settings Check

1. Open Settings (`Ctrl+,`)
2. Search for "MCP"
3. Verify that MCP servers are configured

## 🔧 Troubleshooting

### If tools aren't visible:

1. **Restart VS Code completely**
   - Close all VS Code windows
   - Reopen your workspace

2. **Check MCP Server Status**
   - Open Command Palette (`Ctrl+Shift+P`)
   - Run `MCP: Show MCP Status`
   - Verify "impressioncore-ids" server is running

3. **Verify Configuration**

   ```bash

   # Run this diagnostic script

   cd "d:\Projects\impressioncore"
   python .mcp/ids-mcp/diagnose_vscode.py
   ```

4. **Clear VS Code Cache** (if needed)

   ```bash
   cd "d:\Projects\impressioncore"
   python .mcp/ids-mcp/clear_vscode_cache.py
   ```

5. **Check Developer Console**
   - Help → Toggle Developer Tools
   - Look for MCP-related errors in the console

## 📋 Example Usage

### Using the search tool:

``` text
@mcp search for memory optimization techniques
```

### Getting system information:

``` text
@mcp get-system-status
```

### Finding files by topic:

``` text
@mcp find-by-tag machine-learning, optimization
```

### Listing available categories:

``` text
@mcp list-tags
```

## 🚨 Quick Diagnostic

If you're still having issues, run this command to verify everything:

```bash
cd "d:\Projects\impressioncore"
python .mcp/ids-mcp/list_tools.py
```

This should show all 17 tools. If it does, the server is working correctly, and the issue is likely with VS Code's MCP integration discovery.

## 📞 Next Steps

1. **Restart VS Code completely**
2. **Try accessing tools via Copilot Chat with `@mcp`**
3. **Check Command Palette for MCP commands**
4. **If still no luck, run the diagnostic script and share the output**

The server is production-ready and all tools are registered correctly! 🎉
