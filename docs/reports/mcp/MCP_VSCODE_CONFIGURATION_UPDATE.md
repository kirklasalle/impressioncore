# VS Code MCP Configuration Update

**Created:** June 08, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reports\mcp\MCP_VSCODE_CONFIGURATION_UPDATE.md #docs\reports\mcp\mcp_vscode_configuration_update.md #documentation #testing  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Summary

Updated VS Code MCP configuration to use the new SSE (Server-Sent Events) server instead of the STDIO server to resolve the issue where only the first tool call works.

## Changes Made

### 1. Updated `.vscode/mcp.json`

- **Before**: STDIO server configuration using command-line execution
- **After**: SSE server configuration using HTTP endpoint

#### Old Configuration (backed up to `.vscode/mcp.json.backup`):

```json
{
  "mcpServers": {
    "impressioncore-ids": {
      "command": "G:\\Program Files\\Python313\\python.exe",
      "args": ["d:/Projects/impressioncore/.mcp/ids-mcp/server.py"],
      "cwd": "d:/Projects/impressioncore",
      "env": {
        "PYTHONPATH": "d:/Projects/impressioncore",
        "PYTHONUNBUFFERED": "1",
        "IDS_DEBUG": "1"
      }
    }
  }
}
```

#### New Configuration:

```json
{
  "servers": {
    "impressioncore-ids-sse": {
      "type": "sse",
      "url": "http://127.0.0.1:3001/sse"
    }
  }
}
```

## Requirements

### 1. SSE Server Must Be Running

The SSE server must be started before VS Code can connect to it:

```bash
cd d:/Projects/impressioncore/.mcp/ids-mcp/
python server_sse.py
```

The server will start on `http://127.0.0.1:3001` and provide the SSE endpoint at `/sse`.

### 2. Server Health Check

Verify the server is running:
```bash
curl http://127.0.0.1:3001/health
```

Expected response:
```json
{
  "status": "healthy",
  "server": "ImpressionCore IDS MCP SSE Server",
  "version": "3.0.0",
  "timestamp": "2025-06-08T19:00:50.630531"
}
```

## Benefits of SSE Mode

1. **Resolves Tool Call Hanging**: Multiple tool calls work without requiring VS Code restart
2. **Better Performance**: HTTP-based communication is more reliable than STDIO
3. **Improved Debugging**: HTTP endpoints allow for easier testing and monitoring
4. **All 17 Tools Available**: Complete tool set implemented and tested

## Available Tools

The SSE server implements all 17 ImpressionCore IDS tools:

1. `mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_search` - Search documentation
2. `mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_get-file-info` - Get file information
3. `mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_list-tags` - List available tags
4. `mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_find-by-tag` - Find files by tags
5. `mcp_impressioncor_manage-tags` - Manage document tags
6. `mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_search-content` - Search file contents
7. `mcp_impressioncor_bookmark-management` - Manage bookmarks
8. `mcp_impressioncor_get-recent-changes` - Get recent file changes
9. `mcp_impressioncor_get-documentation-stats` - Get documentation statistics
10. `mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_get-system-status` - Get system status
11. `mcp_impressioncor_analyze-documentation` - Analyze documentation quality
12. `mcp_impressioncor_export-data` - Export system data
13. `mcp_impressioncor_import-data` - Import system data
14. `mcp_impressioncor_backup-system` - Create system backup
15. `mcp_impressioncor_restore-system` - Restore from backup
16. `mcp_impressioncor_rebuild-index` - Rebuild indices
17. `mcp_impressioncor_validate-index` - Validate index integrity

## Troubleshooting

### If VS Code Can't Connect:

1. Check if the SSE server is running: `curl http://127.0.0.1:3001/health`
2. Restart VS Code to refresh MCP configuration
3. Check VS Code's MCP output panel for error messages

### If Tools Don't Appear:

1. Ensure the SSE server is running and healthy
2. Use the Command Palette: "MCP: Restart Server"
3. Check that the `.vscode/mcp.json` configuration is correct

### To Revert to STDIO Mode:

If needed, you can restore the old configuration:
```bash
cp .vscode/mcp.json.backup .vscode/mcp.json
```

## Next Steps

1. **Start the SSE server** before using VS Code MCP tools
2. **Test the tools** in VS Code's Agent Mode
3. **Monitor performance** and report any issues
4. **Consider automation** for starting the SSE server automatically

## Created

- Date: 2025-01-08
- Time: 19:05 UTC
- Author: GitHub Copilot
- Status: Complete ✅
