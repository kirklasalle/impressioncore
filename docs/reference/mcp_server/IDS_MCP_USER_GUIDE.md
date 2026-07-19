# ImpressionCore IDS MCP Server User Guide

**Created:** July 07, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\mcp_server\IDS_MCP_USER_GUIDE.md #docs\reference\mcp_server\ids_mcp_user_guide.md #documentation #security  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# File: IDS_MCP_USER_GUIDE.md

# Last updated: 2025-07-07

# Author: GitHub Copilot (Virtually Robotic Copilot)

---

## Overview

The ImpressionCore IDS MCP Server provides a unified, tag-based documentation and knowledge search system for the ImpressionCore project. It enables advanced search, tagging, and metadata queries across all project documentation, code, and reference files, supporting both developers and end-users.

---

## Features

- **Tag-based search**: Find documentation and code by tags, topics, or categories.
- **File metadata queries**: Retrieve file details, last modified times, and responsible parties.
- **System status**: Get statistics on documentation coverage, tag usage, and system health.
- **Tool integration**: All features are available as MCP tools in VS Code.

---

## Setup & Configuration

1. **Dependencies**: Ensure all Python dependencies in `.mcp/ids-mcp/requirements.txt` are installed in your active environment.
2. **Index Files**: The following YAML files must exist and be valid in `/docs/`:
   - `unified_tags_index.yaml`
   - `reverse_tag_index.yaml`
   - `file_metadata.yaml` (auto-generated, may be large)
3. **Config Files**: Ensure `.mcp/ids-mcp/config.json` and `.mcp/ids-mcp/mcp_config.json` are present and valid.
4. **VS Code Integration**: The IDS MCP server must be listed in `.vscode/mcp.json` under the `servers` key.

---

## Usage

- **Start the IDS MCP server**: This is typically managed by the MCP extension. To start manually:

  ```bash
  source .venv310/Scripts/activate
  python .mcp/ids-mcp/server.py
  ```

- **Access tools**: Use the VS Code command palette to search for IDS tools (e.g., `mcp_impressioncor_ids_search`).
- **Search by tag**: Use the tag-based search tool to find all files related to a topic.
- **Get file info**: Retrieve metadata for any documentation or code file.
- **Check system status**: View documentation coverage, tag statistics, and health.

---

## Troubleshooting

- **Missing/Corrupt Index Files**: Regenerate using the provided automation script or by running the IDS MCP server with the `--rebuild-index` flag (if available).
- **Dependency Issues**: Reinstall requirements with `pip install -r .mcp/ids-mcp/requirements.txt`.
- **Tool Not Registered**: Ensure the server is running and `.vscode/mcp.json` is correct. Restart VS Code if needed.
- **Large file_metadata.yaml**: This file is auto-generated and may exceed 50MB. If corrupt, delete and restart the server to trigger regeneration.

---

## Maintenance

- **Regenerate Indexes**: Run the IDS MCP server with the appropriate flag or script to rebuild indexes after major documentation changes.
- **Update Dependencies**: Periodically update Python packages for security and compatibility.
- **Backup**: Regularly back up `/docs/` and `.mcp/ids-mcp/` directories.

### 2026-2027 Documentation Control Workflow

For the active delivery cycle, include these checks after major documentation changes:

1. Refresh `docs/DOCUMENTATION_INDEX.md` entries impacted by roadmap/PRD/guide updates.
2. Confirm execution backlog visibility from `docs/process/EXECUTION_APPENDIX_2026_2027.md`.
3. Run IDS queries to verify discoverability of updated files.
4. Record any indexing issues in process docs before release tagging.

---

## Integration with ImpressionCore Documentation System

- The IDS MCP server is the backbone of the ImpressionCore documentation and search system.
- It integrates with all MCP tools and supports advanced developer workflows.
- For more details, see `/docs/reference/mcp_server/IDS_DEVELOPER_GUIDE.md` and `/docs/logic_concept_cache.md`.

---

## FAQ

**Q: How do I add a new tag or update file metadata?**
A: Edit the relevant YAML index or use the automation tools provided in `.mcp/ids-mcp/`.

**Q: What if a tool is missing in VS Code?**
A: Restart VS Code and ensure the IDS MCP server is running and properly configured.

**Q: How do I regenerate `file_metadata.yaml`?**
A: Delete the file and restart the IDS MCP server; it will auto-rebuild from the current `/docs/` structure.

---

## Contact & Support

For advanced troubleshooting, see `/docs/reference/mcp_server/IDS_TROUBLESHOOTING.md` or contact the ImpressionCore development team.

---

# End of User Guide
