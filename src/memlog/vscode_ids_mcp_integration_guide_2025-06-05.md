# Adding IDS MCP Server to VS Code Insiders - 2025-06-05

## Overview
Setting up the IDS MCP server as a tool in VS Code Insiders so it appears in the "Configure tools..." menu alongside your existing 60 tools.

## VS Code Insiders MCP Integration Steps

### 1. Locate VS Code Insiders Settings

VS Code Insiders typically stores MCP server configurations in:
- **Windows**: `%APPDATA%\Code - Insiders\User\settings.json`
- **Mac**: `~/Library/Application Support/Code - Insiders/User/settings.json`
- **Linux**: `~/.config/Code - Insiders/User/settings.json`

### 2. Add IDS MCP Server Configuration

Add this to your VS Code Insiders `settings.json`:

```json
{
  "mcp.servers": {
    "ids-mcp": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "D:/Projects/impressioncore/.mcp/ids-mcp",
      "env": {
        "PYTHONPATH": "D:/Projects/impressioncore"
      }
    }
  }
}
```

### 3. Alternative: Use VS Code Workspace Settings

Create or update `.vscode/settings.json` in your ImpressionCore project:

```json
{
  "mcp.servers": {
    "impressioncore-ids": {
      "command": "python", 
      "args": [".mcp/ids-mcp/server.py"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

### 4. Verify Server Configuration

The IDS MCP server will provide these tools in VS Code:

1. **IDS Search** (`ids_search`)
   - Search through 1,667+ documentation files
   - Filter by tags, limit results
   - Get relevance-scored results

2. **IDS File Info** (`ids_get_file_info`)
   - Get detailed metadata about specific files
   - View tags, descriptions, modification dates

3. **IDS List Tags** (`ids_list_tags`)
   - Browse 2,900+ available tags
   - Filter by category or pattern

4. **IDS System Status** (`ids_get_system_status`)
   - View system statistics and health
   - Monitor indexed files and tag usage

5. **IDS Find by Tag** (`ids_find_by_tag`)
   - Find files with specific tag combinations
   - Support for AND/OR tag matching

### 5. Testing the Integration

After adding the configuration:

1. **Restart VS Code Insiders**
2. **Open ImpressionCore project**
3. **Check "Configure tools..." menu** - you should see the IDS tools
4. **Test with a search**: Try searching for "authentication security"

### 6. Expected Behavior

When you use the IDS search tool from VS Code:

**Input Example**:
```
Query: "authentication security implementation"
Tags: ["security", "api"]
Max Results: 5
```

**Expected Output**:
```
Found 3 results for query: 'authentication security implementation'

1. **src/core/security/authentication.py** (Score: 25)
   Description: Core authentication module with JWT and session management
   Tags: security, authentication, core, api
   Last Modified: 2025-06-05

2. **docs/api/security_endpoints.md** (Score: 18)
   Description: Security-related API endpoint documentation
   Tags: api, security, endpoints, documentation
   Last Modified: 2025-06-04

3. **docs/developer/security_architecture.md** (Score: 15)
   Description: Security architecture and implementation guidelines
   Tags: security, architecture, developer, implementation
   Last Modified: 2025-06-03
```

### 7. Troubleshooting

If the tools don't appear:

1. **Check Python Environment**:
   ```bash
   cd .mcp/ids-mcp
   python check_system.py
   ```

2. **Verify Server Starts**:
   ```bash
   cd .mcp/ids-mcp
   python server.py
   ```

3. **Check VS Code Console**:
   - Open VS Code Developer Tools
   - Look for MCP server connection logs

4. **Validate Configuration**:
   - Ensure paths are correct for your system
   - Check that Python can find the required modules

### 8. Benefits in VS Code

Once integrated, you can:

- **Search Documentation**: Direct access to all ImpressionCore docs from VS Code
- **Discover Related Files**: Find files by tags while coding
- **Get Context**: Quickly access relevant documentation for your current work
- **Monitor System**: Check documentation coverage and system health
- **Navigate by Tags**: Explore codebase through the tag system

### 9. Usage Tips

- **Use specific queries**: "authentication JWT implementation" vs "auth"
- **Combine with tags**: Search with relevant tags for better results
- **Limit results**: Use max_results for focused searches
- **Explore tags**: Use ids_list_tags to discover available categories

### 10. Future Enhancements

Potential improvements for VS Code integration:

- **Quick Actions**: Right-click menu integration
- **Inline Results**: Show results in VS Code panels
- **Auto-suggestions**: Tag suggestions as you type
- **File Navigation**: Click results to open files
- **Real-time Updates**: Live documentation updates as you edit

---

**Created**: 2025-06-05 15:00:00  
**Status**: Ready for VS Code Integration  
**Next Steps**: Add to VS Code settings and test functionality
