# ImpressionCore Copilot Memory Cache Utils Guide

**Created:** July 28, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\Copilot_Memory_Cache_Utils_Guide.md #api #command_line #docs\copilot_memory_cache_utils_guide.md #documentation #memory_management  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Overview

`copilot_memory_cache_utils.py` provides persistent memory and logic concept cache management for ImpressionCore. It supports both CLI/API and Python import usage, enabling agentic workflows, MCP server integration, and RAG (retrieval-augmented generation) context retrieval.

---

## Features

- Persistent memory storage (SQLite)
- Markdown log for baton pass and audit
- Logic concept cache sync (from/to markdown and DB)
- RAG/context search API
- CLI for initialization, sync, query, and session logging
- HTTP API (Flask) for agentic/MCP integration

---

## Usage

### 1. CLI Usage

- **Initialize DB:**

  ```sh
  python copilot_memory_cache_utils.py --init
  ```

- **Sync logic concept cache to DB:**

  ```sh
  python copilot_memory_cache_utils.py --sync-cache
  ```

- **Sync DB to logic concept cache:**

  ```sh
  python copilot_memory_cache_utils.py --sync-db
  ```

- **Query memory:**

  ```sh
  python copilot_memory_cache_utils.py --query "search term" --topk 5
  ```

- **Log a session:**

  ```sh
  python copilot_memory_cache_utils.py --log-session "Summary" "Outstanding tasks" "Key decisions"
  ```

### 2. HTTP API Usage

- **Start API server:**

  ```sh
  python copilot_memory_cache_utils.py --api
  ```

- **Endpoints:**
  - `GET /query?q=term&topk=3` — Search memory
  - `POST /sync-cache` — Sync logic concept cache to DB
  - `POST /sync-db` — Sync DB to logic concept cache

### 3. Python Import

```python
from src.core.utils.copilot_memory_cache_utils import write_memory, read_memory, search_memory
```

---

## Integration

- **MCP Servers:**
  - Import and call functions directly, or use HTTP API for agentic workflows.
- **Automation:**
  - Use CLI or API in scripts for scheduled or event-driven memory/context operations.
- **RAG/Context Retrieval:**
  - Use `search_memory()` for context injection in LLM or agentic tasks.

---

## File Locations

- **Source:** `src/core/utils/copilot_memory_cache_utils.py`
- **SQLite DB:** `src/memlog/copilot_memory.sqlite`
- **Markdown log:** `src/memlog/copilot_memory.md`
- **Logic concept cache:** `docs/logic_concept_cache.md`

---

## Example Workflows

### Sync Logic Concept Cache

1. Update `docs/logic_concept_cache.md` with new logic blocks.
2. Run:

   ```sh
   python copilot_memory_cache_utils.py --sync-cache
   ```

3. Concepts are now available in persistent memory for RAG and agentic use.

### Retrieve Context for Agent

1. Start API server:

   ```sh
   python copilot_memory_cache_utils.py --api
   ```

2. Agent sends GET request to `/query?q=embedding&topk=2`.
3. Receives relevant logic/concept blocks for use in reasoning or LLM prompts.

---

## Maintenance

- Regularly sync between markdown and DB to keep logic cache up to date.
- Use session logging to track key decisions and outstanding tasks.
- Review and update `docs/logic_concept_cache.md` as new solution patterns emerge.

---

## See Also

- [docs/logic_concept_cache.md](../docs/logic_concept_cache.md)
- [src/memlog/copilot_memory_schema.sql](../../src/memlog/copilot_memory_schema.sql)
- [docs/DOCUMENTATION_INDEX.md](../docs/DOCUMENTATION_INDEX.md)

---

*For questions or contributions, see ImpressionCore documentation or contact the ImpressionCore Team.*
