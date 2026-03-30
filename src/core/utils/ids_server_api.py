#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #command_line #documentation #memory_management #python #source_code #src/core/utils/ids_server_api.py
**Category:** Core Implementation
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #api #command_line #documentation #memory_management #python #source_code #src\\core\\utils\\ids_server_api.py
# Category:** Core Implementation
# Status:** Active

"""
IDS Server API Entrypoint
========================
Unified CLI and Python API for ImpressionCore Documentation System (IDS)

Exposes all major IDS features as commands for DPA, automation, and user workflows:
  - update: Full documentation/tag/index update
  - tag: Tag and categorize all docs
  - sync: Sync memlog and persistent memory
  - status: Show IDS/documentation system status
  - search: Search docs by keyword/tag
  - generate-docs: Generate user/dev/API docs

Usage (CLI):
  python ids_server_api.py update
  python ids_server_api.py tag
  python ids_server_api.py sync
  python ids_server_api.py status
  python ids_server_api.py search <query>
  python ids_server_api.py generate-docs

Usage (Python):
  from src.core.utils.ids_server_api import ids_update, ids_tag, ids_sync, ids_status, ids_search, ids_generate_docs
  ids_update()

Author: ImpressionCore Copilot
Created: 2025-07-01
"""

import sys
from pathlib import Path

# Import core IDS modules
from src.core.utils.automated_ids_maintenance import AutomatedIDSMaintenance
from src.core.utils.ids_documentation_generator import IDSDocumentationGenerator
from src.core.utils.ids_tool_interface import IDSToolInterface

PROJECT_ROOT = Path(__file__).parent.parent.parent
DOCS_ROOT = PROJECT_ROOT / "docs"

# Unified API functions
def ids_update():
    """Run full IDS update (maintenance, tagging, index)."""
    maint = AutomatedIDSMaintenance(str(PROJECT_ROOT))
    maint.run_full_maintenance()

def ids_tag():
    """Run IDS tagging and categorization only."""
    maint = AutomatedIDSMaintenance(str(PROJECT_ROOT))
    maint.run_tagging_only()

def ids_sync():
    """Sync memlog and persistent memory with IDS."""
    maint = AutomatedIDSMaintenance(str(PROJECT_ROOT))
    maint.run_memlog_sync()

def ids_status():
    """Show IDS/documentation system status."""
    tool = IDSToolInterface()
    print(tool.get_status_summary())

def ids_search(query: str):
    """Search docs by keyword or tag."""
    tool = IDSToolInterface()
    results = tool.search(query)
    for r in results:
        print(f"{r.file_path} | {r.category} | tags: {', '.join(r.tags)} | score: {r.relevance_score:.2f}")

def ids_generate_docs():
    """Generate user, developer, and API documentation."""
    gen = IDSDocumentationGenerator()
    print(gen.generate_comprehensive_developer_guide())

# CLI Entrypoint
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ids_server_api.py <command> [args]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "update":
        ids_update()
    elif cmd == "tag":
        ids_tag()
    elif cmd == "sync":
        ids_sync()
    elif cmd == "status":
        ids_status()
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: python ids_server_api.py search <query>")
            sys.exit(1)
        ids_search(' '.join(sys.argv[2:]))
    elif cmd == "generate-docs":
        ids_generate_docs()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
