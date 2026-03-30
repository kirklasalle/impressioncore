# Memlog Directory Structure

## Overview

This directory contains system logs, state tracking, and persistent data storage for the ImpressionCore project.

## Directory Structure

### /state

Contains system state changes and configuration tracking

- Current system state
- Configuration changes
- Environment variables
- Hardware utilization logs
- **Indexing**: Add an index file to track state changes for faster retrieval.
- Add an `index.json` file to track entries for faster retrieval.

### /tasks

Tracks project tasks and their progress

- Active tasks
- Completed tasks
- Task dependencies
- Progress metrics
- **Search Capability**: Implement a search tool to query tasks by status or priority.
- Implement a `search.py` script to query tasks by status, priority, or other metadata.

### /persistence

Stores persistent data across system operations

- User preferences
- System settings
- Cache data
- Session information
- **Efficient Organization**: Use subdirectories for different data types (e.g., preferences/, settings/, cache/).
- Organize `persistence` into subdirectories for different data types (e.g., `preferences/`, `settings/`, `cache/`).
- Add a `README.md` in each subdirectory to document its purpose and usage.

### /changelogs

Maintains detailed change history

- Version changes
- System updates
- Feature additions
- Bug fixes
- **Indexing**: Maintain a summary file for quick access to recent changes.
- Add an `index.json` file to track entries for faster retrieval.

## Usage Guidelines

1. All logs must include timestamps
2. Use standardized log formats
3. Regular cleanup of old logs
4. Maintain backup of critical data
5. Verify integrity before operations
6. **Enhancements**:
   - Add indexing for faster retrieval.
   - Implement search tools for querying logs and tasks.
   - Organize data into subdirectories for better management.

No Additional Setup Required

The MCP servers are configured at the VSCode level, not the project level
The absolute paths in cline_mcp_settings.json ensure the servers can be found regardless of your current working directory
Using MCP Tools in a New Project

In your new project, you can immediately use the MCP tools with the same syntax:
<use_mcp_tool>
<server_name>memory</server_name>
<tool_name>setValue</tool_name>
<arguments>
{
  "key": "projectConfig",
  "value": "Some project-specific value"
}
</arguments>
</use_mcp_tool>
Project-Specific Data Handling

For filesystem operations, you can specify paths relative to your new project:
<use_mcp_tool>
<server_name>filesystem</server_name>
<tool_name>listFiles</tool_name>
<arguments>
{
  "path": "."  // This will list files in your new project directory
}
</arguments>
</use_mcp_tool>
For SQLite operations, you can create a project-specific database:
<use_mcp_tool>
<server_name>sqlite</server_name>
<tool_name>executeRun</tool_name>
<arguments>
{
  "sql": "CREATE TABLE IF NOT EXISTS project_data (id INTEGER PRIMARY KEY, name TEXT)"
}
</arguments>
</use_mcp_tool>
Verifying MCP Server Access in a New Project
To confirm the MCP servers are accessible in your new project:

Test a Simple Tool Call

Try a simple call to get the current time:
<use_mcp_tool>
<server_name>time</server_name>
<tool_name>getCurrentTime</tool_name>
<arguments>
{}
</arguments>
</use_mcp_tool>
Check Console for Errors

Look for any error messages in the VSCode output console
Common issues would be path-related errors if the MCP servers can't be found
Customizing MCP Server Settings for a Project
If you need project-specific customizations:

Project-Specific Configuration

You can create a local copy of the MCP settings in your project root
Name it .mcp-settings.json (with a leading dot to indicate it's a configuration file)
This will override specific settings for this project only
Environment Variables

For servers like DALLE or API-connected services, you might want different API keys per project
Edit the global settings file to use environment variables, which you can set differently per project
Example Workflow in a New Project
Here's a sample workflow using MCP servers in a new project:

Store Project Configuration

<use_mcp_tool>
<server_name>memory</server_name>
<tool_name>setValue</tool_name>
<arguments>
{
  "key": "projectName",
  "value": "My New Project"
}
</arguments>
</use_mcp_tool>
Convert Documentation

<use_mcp_tool>
<server_name>markdownify</server_name>
<tool_name>pdf-to-markdown</tool_name>
<arguments>
{
  "filepath": "./docs/requirements.pdf"
}
</arguments>
</use_mcp_tool>
Create a Database

<use_mcp_tool>
<server_name>sqlite</server_name>
<tool_name>executeRun</tool_name>
<arguments>
{
  "sql": "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"
}
</arguments>
</use_mcp_tool>
Test Web UI

<use_mcp_tool>
<server_name>browser-tools</server_name>
<tool_name>takeScreenshot</tool_name>
<arguments>
{}
</arguments>
</use_mcp_tool>
The MCP servers will continue to run and be available until you close VSCode, regardless of which project you're working on.
