# MCP Server Fleet — Architecture Documentation

> **Version:** 2.0.0  
> **Author:** Kirk LaSalle  
> **Protocol:** Model Context Protocol Standard `2025-11-25`  
> **Status:** Phase 0 Stabilization Verified — all 8 servers pass the official MCP handshake and protocol gate probe (`probe_v2.py`).  
> **Transport:** JSON-RPC 2.0 over stdio with `shared.stdio_guard` isolation  
> **Documentation:** [PRD](../docs/PRD.md) | [User Guide](../docs/USER_GUIDE.md) | [Developer Guide](../docs/DEVELOPER_GUIDE.md) | [Changelog](../CHANGELOG.md)  
> **Last Updated:** 2026-10-23

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Protocol Layer](#3-protocol-layer)
4. [Server Inventory](#4-server-inventory)
5. [Complete Tool Catalog](#5-complete-tool-catalog)
6. [Goliath Bridge Architecture](#6-goliath-bridge-architecture)
7. [Swarm Memory System](#7-swarm-memory-system)
8. [Shared Subsystems](#8-shared-subsystems)
9. [Data Flow & Interaction Patterns](#9-data-flow--interaction-patterns)
10. [Configuration Reference](#10-configuration-reference)
11. [Deployment & Operations](#11-deployment--operations)
12. [Security Model](#12-security-model)
13. [Sacred Covenant Governance Architecture](#13-sacred-covenant-governance-architecture)
14. [Extension Guide](#14-extension-guide)

---

## 1. Executive Summary

This repository houses a fleet of **8 specialized MCP servers** designed to provide agentic AI systems with structured access to documentation search, educational data scraping, deep research, swarm coordination, system assessment, NLU processing, web search, and government archive research.

Each server is a standalone process communicating via **JSON-RPC 2.0 over stdio**, compatible with any MCP-compliant client including Claude Desktop, Antigravity IDE, Cursor, and Windsurf.

**Key Architectural Properties:**

- **Project-Agnostic (goal)** — Servers are intended to be general-purpose tools. **[CURRENT STATE]** ~300 legacy project-name references, hardcoded absolute paths, and hardware-specific (GTX 1050 Ti / B1/B3) logic remain and are scheduled for removal.
- **Composable** — Each server operates independently; Goliath optionally orchestrates all of them
- **Hardware-Aware** — The load balancer monitors GPU VRAM to coordinate resource-intensive operations
- **Fail-Graceful** — Progressive tool loading ensures partial availability when subsystems are missing

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    MCP CLIENT                           │
│         (Claude Desktop / Antigravity / Cursor)         │
└──────────────────────┬──────────────────────────────────┘
                       │ JSON-RPC 2.0 over stdio
         ┌─────────────┼─────────────────────┐
         │             │                     │
         ▼             ▼                     ▼
  ┌─────────────┐ ┌──────────┐      ┌────────────────┐
  │  Standalone  │ │Standalone│      │    GOLIATH      │
  │   Servers    │ │ Servers  │      │  Orchestrator   │
  │             │ │          │      │                │
  │ • ids       │ │ • web-   │      │  ┌──────────┐  │
  │ • eds       │ │   search │      │  │  Bridge   │  │
  │ • ipa       │ │ • loc    │      │  │  Layer    │  │
  │ • vrgc      │ │          │      │  │          │  │
  │ • dpa       │ │          │      │  │ ids ──┐  │  │
  │             │ │          │      │  │ eds ──┤  │  │
  └─────────────┘ └──────────┘      │  │ ipa ──┤  │  │
                                    │  │ vrgc ─┤  │  │
                                    │  │ dpa ──┤  │  │
                                    │  │ web ──┘  │  │
                                    │  └──────────┘  │
                                    │       │        │
                                    │  ┌────▼─────┐  │
                                    │  │  Swarm   │  │
                                    │  │  Memory  │  │
                                    │  └──────────┘  │
                                    │       │        │
                                    │  ┌────▼─────┐  │
                                    │  │   VRAM   │  │
                                    │  │ Balancer  │  │
                                    │  └──────────┘  │
                                    └────────────────┘
```

### Deployment Topology

| Mode | Description |
|------|-------------|
| **Standalone** | Each server runs as an independent MCP process. The client connects to whichever servers it needs. |
| **Orchestrated** | Goliath runs as a single MCP process that internally loads all other servers as bridge modules, exposing a unified tool surface. |
| **Hybrid** | Some servers run standalone (e.g., `web-search`, `loc`) while others are orchestrated through Goliath. |

---

## 3. Protocol Layer

### 3.1 Transport

All servers communicate over **stdio** (stdin/stdout). Log output is sent exclusively to **stderr** to avoid corrupting the JSON-RPC stream.

### 3.2 MCP SDK Usage

| Server | SDK Implementation | API |
|--------|-------------------|-----|
| `dpa` | `mcp.server.Server` + `stdio_server` | Handler-decorator pattern (`@server.list_tools()`, `@server.call_tool()`) |
| `eds` | `mcp.server.Server` + `stdio_server` | Handler-decorator pattern |
| `goliath` | `mcp.server.Server` + `stdio_server` | Handler-decorator pattern with bridge delegation |
| `ipa` | `mcp.server.Server` + `stdio_server` | Handler-decorator pattern |
| `web-search` | `mcp.server.FastMCP` | Decorator pattern (`@mcp.tool()`) |
| `loc` | `mcp.server.FastMCP` | Decorator pattern (`@mcp.tool()`) |
| `ids` | Manual JSON-RPC | Raw stdin/stdout loop (legacy) |
| `vrgc` | Manual JSON-RPC | Raw stdin/stdout loop (legacy) |

> **Note:** `ids` and `vrgc` implement the JSON-RPC protocol manually. These should be migrated to the MCP SDK for maintainability and protocol compliance.

### 3.3 Message Format

Standard JSON-RPC 2.0 envelope:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "web_search",
    "arguments": {
      "query": "machine learning transformers",
      "num_results": 5
    }
  }
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"query\": \"machine learning transformers\", \"results\": [...]}"
      }
    ]
  }
}
```

---

## 4. Server Inventory

### 4.1 IDS — Intelligent Documentation System

| Property | Value |
|----------|-------|
| **Directory** | `ids-mcp/` |
| **Entry Point** | `server.py` |
| **Purpose** | Documentation indexing, tag-based search, metadata retrieval, and automated index management |
| **Data Sources** | YAML index files (`unified_tags_index.yaml`, `file_metadata.yaml`, `reverse_tag_index.yaml`) |
| **Key Feature** | Background initialization — the server responds to `initialize` immediately while loading indices asynchronously in a daemon thread |

### 4.2 EDS — Educational Data Scraper

| Property | Value |
|----------|-------|
| **Directory** | `eds/` (currently `impressioncore-eds/`) |
| **Entry Point** | `server.py` |
| **Purpose** | License-compliant educational content acquisition from open-access sources |
| **Data Sources** | MIT OpenCourseWare, Wikipedia (CC-BY-SA), arXiv (open access), NASA/NIH (public domain) |
| **Key Feature** | Every scraped item includes license provenance and compliance validation |

### 4.3 IPA — Intelligent Research Agent

| Property | Value |
|----------|-------|
| **Directory** | `ipa/` (currently `impressioncore-ipa/`) |
| **Entry Point** | `server.py` |
| **Purpose** | Deep multi-step research combining web search, source attribution, and methodology validation |
| **Key Feature** | Multi-engine search fusion (Google, DuckDuckGo, Bing, academic databases) with credibility scoring |
| **LOC** | ~1,861 lines — the largest server in the fleet |

### 4.4 Goliath — Swarm Orchestration Server

| Property | Value |
|----------|-------|
| **Directory** | `goliath/` (currently `impressioncore-goliath/`) |
| **Entry Point** | `server.py` |
| **Purpose** | Multi-agent coordination hub — aggregates all other servers through bridge modules, manages shared swarm memory and VRAM load balancing |
| **Key Feature** | Namespaced tool routing (`bridge:tool` or flat name with auto-discovery), background initialization |
| **Submodules** | `core/` (swarm_memory, load_balancer, covenant_guardian, unified_logger), `bridges/` (ids, eds, ipa, vrgc, dpa, websearch), `utils/` (tool_registry) |

### 4.5 VRGC — Virtually Robotic GitHub Copilot

| Property | Value |
|----------|-------|
| **Directory** | `vrgc/` (currently `impressioncore-vrgc/`) |
| **Entry Point** | `server_enhanced.py` / `server.py` |
| **Purpose** | Autonomous engineering copilot, hardware optimization, environment assessment, training & lifecycle monitoring, and Sacred Covenant compliance auditing |
| **Key Feature** | Software Application Programming Robot (SAPR) intelligence, 30+ specialized tools, progressive tool loading, and integrated Covenant Guardian |
| **Submodules** | `tools/` (system_assessment, training_monitor, hardware_optimizer, covenant_guardian, project_intelligence, vscode_controller, ids_integration) |

### 4.6 DPA — Dynamic Perception Adapter

| Property | Value |
|----------|-------|
| **Directory** | `dpa/` (currently `impressioncore-dpa/`) |
| **Entry Point** | `server.py` |
| **Purpose** | Natural language understanding, intent extraction, entity recognition, accessibility transforms, and chronology access |
| **Key Feature** | Full accessibility subsystem (AccessibilityManager, UserExperienceManager) for adaptive UI rendering |
| **Submodules** | `core/` (query_processor, retrieval_engine, context_manager, response_generator), `nlp/` (nlu_engine), `accessibility/`, `integration/`, `knowledge/`, `tasks/`, `reminders/` |

### 4.7 Web Search

| Property | Value |
|----------|-------|
| **Directory** | `web-search-mcp/` → `web-search/` |
| **Entry Point** | `server.py` |
| **Purpose** | Multi-engine web search (Google + DuckDuckGo), content extraction, filtered search, and bulk URL fetching |
| **Key Feature** | Built-in rate limiter (10 requests/60 seconds), content extraction with semantic selectors |

### 4.8 LOC — Library of Congress

| Property | Value |
|----------|-------|
| **Directory** | `loc-mcp-server/` → `loc/` |
| **Entry Point** | `server.py` |
| **Purpose** | Library of Congress digital catalog search, Chronicling America historic newspapers, legislative records, and structured metadata extraction |
| **Key Feature** | Rate-limited API client (15 calls/60 seconds), OCR text and PDF links for newspaper pages |

---

## 5. Complete Tool Catalog

### 5.1 IDS Tools

| Tool | Description | Required Parameters |
|------|-------------|-------------------|
| `search` | Search documentation using tag-based indexing | `query` (string) |
| `get-system-status` | Get IDS system status and statistics | — |
| `list-tags` | List all available tags, optionally filtered | `category?`, `pattern?` |
| `get-file-info` | Get detailed metadata for a specific file | `file_path` (string) |
| `get-documentation-stats` | Comprehensive documentation statistics | — |
| `run-header-updater` | Execute automated header standardization | `target_directory?`, `dry_run?` |
| `run-documentation-indexer` | Rebuild the documentation index | `force_rebuild?` |
| `run-system-validator` | Check file integrity and system health | `validation_scope?` (enum: full, headers, tags, covenant) |

### 5.2 EDS Tools

| Tool | Description | Required Parameters |
|------|-------------|-------------------|
| `scrape_mit_ocw` | Scrape MIT OpenCourseWare (Creative Commons) | `course_url?`, `subject?` |
| `scrape_wikipedia_educational` | Extract educational Wikipedia articles (CC-BY-SA) | `topics` (array) |
| `scrape_arxiv_papers` | Get open-access arXiv papers | `query?`, `max_results?` |
| `scrape_government_educational` | Access US government educational resources (public domain) | `agency?` (nasa, nih, noaa) |
| `validate_license_compliance` | Validate license compliance for a URL | `url` (string) |

### 5.3 IPA Tools

The IPA server exposes a comprehensive research toolkit including:

| Tool | Description | Required Parameters |
|------|-------------|-------------------|
| `deep_research` | Multi-step deep research with methodology validation | `query`, `depth?`, `methodology?` |
| `web_intelligence` | Real-time web search with source verification | `query`, `sources?` |
| `source_attribution` | Academic-grade citation and provenance analysis | `content`, `format?` |
| `methodology_validation` | Research approach verification and optimization | `methodology`, `domain?` |
| `live_data_synthesis` | Real-time information aggregation and analysis | `topic`, `time_range?` |
| `quality_assessment` | Multi-factor source credibility assessment | `sources` (array) |

### 5.4 Goliath Tools

Goliath exposes all bridge tools plus its own orchestration tools:

| Tool | Description | Required Parameters |
|------|-------------|-------------------|
| `goliath_get_swarm_state` | Get current swarm memory state and hardware metrics | — |
| `goliath_synergize_memory` | Register a finding or context tag into swarm memory | `key?`, `value?`, `dna?`, `tags?` |

Additionally, all tools from loaded bridges are available through Goliath's tool registry. Tools can be called by flat name (auto-discovered) or with a bridge namespace prefix (`bridge:tool`).

> **[CURRENT STATE]** Goliath lists 50 tools, but tool dispatch is broken (`server.py` calls `tool_registry.find_tool_bridge`; the registry defines `get_tool_bridge`). Five of seven bridges (eds, ipa, websearch, vrgc, dpa) return hardcoded mock data rather than proxying the real servers. Only the ids bridge loads real server code.

### 5.5 VRGC Tools

| Tool | Description | Required Parameters |
|------|-------------|-------------------|
| `vrgc_assess_system` | Comprehensive system assessment (hardware, environment, project) | `assessment_type?` (enum) |
| `vrgc_monitor_training` | Monitor training progress and quality metrics | `check_type?` (enum) |
| `vrgc_optimize_hardware` | GPU hardware optimization and VRAM analysis | `optimization_focus?` (enum) |
| `vrgc_verify_covenant` | File integrity and compliance verification | `verification_scope?` (enum) |
| `vrgc_analyze_intelligence` | Project intelligence analysis (complexity, velocity, optimization) | `analysis_type?` (enum) |
| `vrgc_start_b3_monitoring` | Start lifecycle monitoring | — |
| `vrgc_stop_b3_monitoring` | Stop lifecycle monitoring and get final statistics | — |
| `vrgc_get_b3_status` | Get current monitoring status | — |
| `vrgc_health_check` | Comprehensive system health check | — |

### 5.6 DPA Tools

| Tool | Description | Required Parameters |
|------|-------------|-------------------|
| `analyze` | Analyze user input and return NLU result | `text` (string) |
| `get_intent` | Extract intent from user input | `text` (string) |
| `get_entities` | Extract entities from user input | `text` (string) |
| `process_accessibility_request` | Process natural language accessibility query | `query` (string), `user_context?` |
| `get_user_interface_config` | Get adaptive UI configuration for a user | `user_id` (string) |
| `apply_accessibility_to_response` | Apply accessibility transforms to response text | `response` (string), `user_id` (string) |
| `get_accessibility_integration_status` | Get accessibility integration status | — |
| `ids_update` / `ids_tag` / `ids_sync` / `ids_status` / `ids_search` / `ids_generate_docs` | IDS bridge operations | varies |
| `shutdown` | Graceful server shutdown | — |

### 5.7 Web Search Tools

| Tool | Description | Required Parameters |
|------|-------------|-------------------|
| `web_search` | Multi-engine web search (Google + DuckDuckGo) with operator support | `query` (string), `num_results?`, `use_google?` |
| `fetch_webpage` | Fetch and extract structured content from a URL | `url` (string), `extract_content?` |
| `search_with_filters` | Pre-configured filtered search (academic, technical, news, recent) | `query` (string), `filter_type?` |
| `get_search_suggestions` | Query optimization recommendations and operator suggestions | `query` (string) |
| `bulk_url_fetch` | Fetch content from multiple URLs | `urls` (array), `max_urls?` |

### 5.8 LOC Tools

| Tool | Description | Required Parameters |
|------|-------------|-------------------|
| `loc_search_catalog` | Search the LoC digital catalog (books, photos, maps, audio, manuscripts) | `query` (string), `collection?`, `limit?` |
| `loc_search_newspapers` | Search Chronicling America (1777–1963 historic newspapers) | `terms` (string), `state?`, `year_start?`, `year_end?`, `limit?` |
| `loc_get_item_metadata` | Retrieve full metadata, image manifests, and rights for any LoC item | `item_url` (string) |
| `loc_search_legislation` | Search congressional bills, resolutions, and acts | `query` (string), `limit?` |

### 5.9 Chronology Tools (Shared Across Servers)

The chronology subsystem is duplicated across multiple servers (DPA, EDS, VRGC, Goliath, IPA, Web Search). Each server exposes the same three tools under its own namespace prefix:

| Tool Pattern | Description | Parameters |
|-------------|-------------|------------|
| `{prefix}_chronology_snapshot` | Creation-ordered document timeline | `kind?` (all, docs, source, mcp, root), `limit?`, `reverse?` |
| `{prefix}_chronology_delta` | Change delta (added/removed/changed) | `include?` (array), `limit?` |
| `{prefix}_chronology_stats` | Aggregate counts per category | — |

---

## 6. Goliath Bridge Architecture

Goliath is the **nerve center** of the fleet. It loads each server as an in-process bridge module, creating a unified tool surface while maintaining isolation between subsystems.

### 6.1 Bridge Registration

```python
bridge_configs = [
    ("ids",        IDSBridge,        "Documentation System Management"),
    ("dpa",        DPABridge,        "Dynamic Perception Adapter"),
    ("eds",        EDSBridge,        "Educational Data Scraper"),
    ("ipa",        IPABridge,        "Intelligent Research Agent"),
    ("vrgc",       VRGCBridge,       "Virtually Robotic GitHub Copilot"),
    ("websearch",  WebSearchBridge,  "Web Search & Content Extraction"),
    ("goliath",    GoliathOrchestrationBridge, "Swarm Orchestration"),
    ("chronology", ChronologyBridge, "Unified Chronology Access"),  # conditional
]
```

### 6.2 Bridge Interface Contract

Every bridge must implement:

```python
class Bridge:
    def __init__(self, project_root: Path, logger, guardian):
        ...

    def get_tools(self) -> List[Tool]:
        """Return MCP Tool objects for all tools this bridge provides."""
        ...

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a named tool with the given arguments."""
        ...
```

### 6.3 Tool Resolution

When a tool call arrives at Goliath:

1. **Namespaced:** If the tool name contains `:`, split into `bridge_name:tool_name`
2. **Flat:** Otherwise, search the `GoliathToolRegistry` for which bridge owns the tool
3. **VRAM Check:** If the tool name contains `research`, `curate`, `train`, or `heal`, trigger load balancer coordination
4. **Execute:** Delegate to the owning bridge's `execute_tool` method

### 6.4 Background Initialization

Goliath uses a two-phase startup:
1. **Phase 1 (instant):** MCP handshake completes, server is "alive" but tools list is empty
2. **Phase 2 (async):** After 1 second, `background_initialize_goliath()` loads all bridges, registers all tools, and populates the tool registry

This ensures the MCP client receives a valid `initialize` response without waiting for heavy subsystems.

---

## 7. Swarm Memory System

Swarm memory is a **centralized, persistent key-value store** shared across all servers when running through Goliath.

### 7.1 Schema

```json
{
  "metadata": {
    "created": "ISO-8601",
    "last_updated": "ISO-8601",
    "schema_version": "1.0.0"
  },
  "findings": {
    "<key>": {
      "source": "<server_name>",
      "data": { ... },
      "dna": "<optional_lineage_id>",
      "timestamp": "ISO-8601"
    }
  },
  "digital_dna": {
    "<dna_id>": "<finding_key>"
  },
  "performance_metrics": { ... },
  "active_context": ["tag1", "tag2"]
}
```

### 7.2 Operations

| Method | Description |
|--------|-------------|
| `register_finding(source, key, value, dna?)` | Store a finding with optional Digital DNA lineage |
| `get_finding(key)` | Retrieve a finding by key |
| `query_by_dna(dna)` | Retrieve a finding by its Digital DNA signature |
| `update_context(tags)` | Merge tags into the active context array |
| `get_state()` | Return the complete memory state |

### 7.3 Persistence

Swarm memory is persisted to `goliath_swarm_memory.json` in the `.mcp` directory. It auto-saves after every `register_finding` call.

---

## 8. Shared Subsystems

### 8.1 VRAM Load Balancer

Located in `goliath/core/load_balancer.py`, the load balancer monitors GPU VRAM usage and coordinates module swapping when the system is under memory pressure.

```python
class VRAMLoadBalancer:
    def get_vram_usage() -> float      # Returns current VRAM in GB (uses pynvml if available)
    def check_capacity(gb) -> bool     # True if gb can fit within the target limit
    def coordinate_swap(server, gb)    # Signal other modules to hibernate if needed
    def get_metrics() -> dict          # Current usage, target limit, status, timestamp
```

**Target VRAM:** Configurable (default: 4.0 GB). Set via constructor parameter.

### 8.2 Unified Logger

`goliath/core/unified_logger.py` provides standardized logging across all Goliath bridge modules with methods for `info`, `warning`, `error`, `success`, and `debug`.

### 8.3 Tool Registry

`goliath/utils/tool_registry.py` maintains a flat index of all registered tools with bridge ownership tracking, enabling tool discovery by name regardless of which bridge provides it.

### 8.4 Chronology Loader

A shared read-only module (`assistant/chronology_loader.py`) that loads creation-ordered document timelines. Used by 6 servers to expose chronology snapshot/delta/stats tools. Functions:

| Function | Description |
|----------|-------------|
| `load_chronology()` | Load the full chronology JSON |
| `query_chronology(data, kind, limit, reverse)` | Query a slice of the chronology by category |
| `load_delta()` | Load the delta (changes since last snapshot) |

---

## 9. Data Flow & Interaction Patterns

### 9.1 Standalone Mode

```
Client ──stdio──▸ Server ──▸ Process tool call ──▸ Return JSON result
```

Each server is a self-contained process. The client sends `initialize`, `tools/list`, and `tools/call` messages. The server responds with results.

### 9.2 Orchestrated Mode (Goliath)

```
Client ──stdio──▸ Goliath ──▸ Tool Registry (lookup) ──▸ Bridge.execute_tool()
                                    │
                                    ├──▸ Swarm Memory (read/write)
                                    └──▸ VRAM Load Balancer (check/coordinate)
```

### 9.3 Research Flow (IPA)

```
User Query ──▸ Query Analysis
                  │
                  ├──▸ Google Search ──┐
                  ├──▸ DuckDuckGo ─────┤
                  ├──▸ Academic DBs ───┤
                  │                    ▼
                  │              Result Fusion & Deduplication
                  │                    │
                  ├──▸ Source Verification & Credibility Scoring
                  │                    │
                  └──▸ Methodology Validation ──▸ Final Synthesized Report
```

### 9.4 Educational Scraping Flow (EDS)

```
Scrape Request ──▸ License Compliance Check
                        │
                        ├──▸ MIT OCW (Creative Commons)
                        ├──▸ Wikipedia (CC-BY-SA)
                        ├──▸ arXiv (Open Access)
                        ├──▸ Government (Public Domain)
                        │
                        ▼
                  Content Extraction ──▸ Educational Quality Scoring ──▸ Structured Output
```

---

## 10. Configuration Reference

### 10.1 Configuration Files

| File | Purpose | Used By |
|------|---------|---------|
| `mcp-settings.json` | VS Code / generic MCP client config | VS Code, generic clients |
| `antigravity_mcp_config.json` | Google Antigravity IDE config | Antigravity IDE |
| `claude_desktop_config.json` | Anthropic Claude Desktop config | Claude Desktop |
| `nexus-mcp-settings.json` | Alternate workspace config | .nexus dispatch system |

### 10.2 Environment Variables

| Variable | Server | Description |
|----------|--------|-------------|
| `DPA_DEBUG` | DPA | Enable debug-level logging |
| `VRGC_DEBUG` | VRGC | Enable verbose VRGC logging (`1` = on) |
| `GOLIATH_DEBUG` | Goliath | Enable Goliath debug mode (`1` = on) |
| `PYTHONIOENCODING` | All | Must be `utf-8` for proper Unicode handling |
| `PYTHONUTF8` | All | Must be `1` to force UTF-8 mode |
| `PYTHONPATH` | All | Must include the server directory and virtual environment site-packages |

### 10.3 Server Configuration Block Template

```json
{
  "<server-name>": {
    "command": "python",
    "args": ["<path-to-server.py>"],
    "transport": "stdio",
    "cwd": "<path-to-server-directory>",
    "env": {
      "PYTHONIOENCODING": "utf-8",
      "PYTHONUTF8": "1"
    }
  }
}
```

---

## 11. Deployment & Operations

### 11.1 Prerequisites

- **Python 3.10+**
- **MCP SDK:** `pip install mcp`
- Per-server dependencies listed in each server's `requirements.txt`

### 11.2 Quick Start

1. **Install dependencies** for the server(s) you want to run:
   ```bash
   pip install -r ids-mcp/requirements.txt
   pip install -r web-search-mcp/requirements.txt
   # etc.
   ```

2. **Copy the appropriate config** to your IDE:
   - **Claude Desktop:** Copy `claude_desktop_config.json` → `%APPDATA%\Claude\claude_desktop_config.json`
   - **Antigravity IDE:** Reference `antigravity_mcp_config.json` in workspace settings
   - **Cursor/Windsurf:** Copy config to `.cursor/mcp.json` or `.windsurf/mcp.json`

3. **Start your IDE.** Servers launch automatically via stdio.

### 11.3 Manual Testing

Test any server independently:

```bash
# Start a server manually
python ids-mcp/server.py

# Send a JSON-RPC initialize message (paste into stdin):
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}

# List tools:
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}

# Call a tool:
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"web_search","arguments":{"query":"test"}}}
```

### 11.4 Health Monitoring

Check server health via stderr output. All servers log initialization status, tool counts, and errors to stderr:

```
[2026-10-21T15:30:00] INFO: Starting IDS initialization...
[2026-10-21T15:30:01] INFO: Loaded unified index: 1,247 entries
[2026-10-21T15:30:01] INFO: IDS initialization complete. Server is ready.
```

---

## 12. Security Model

### 12.1 Transport Security

- All communication is over **local stdio** — no network exposure
- Servers never open listening ports in their default configuration
- No authentication is required (stdio is process-to-process, inheriting OS-level access control)

### 12.2 Data Handling

| Concern | Mitigation |
|---------|------------|
| Web scraping rate limits | Built-in `RateLimiter` in web-search and loc servers |
| License compliance | EDS validates license provenance before returning scraped content |
| File system access | Servers only read index files and documentation; write access is limited to swarm memory |
| Subprocess execution | IDS can invoke `documentation_indexer.py` — limited to known project tools |

### 12.3 Best Practices

- **Never expose MCP servers over a network** without adding authentication
- **Never auto-install dependencies** at runtime (remove any `pip install` in ImportError handlers)
- **Review pickle files** (`*.pkl`) before loading — prefer JSON/YAML for serialized data
- **Use environment variables** for all configurable paths — never hardcode absolute paths

---

## 13. Sacred Covenant Governance Architecture

### 13.1 Constitutional Hierarchy & Purpose

The MCP Server Fleet operates under an unbreakable, cryptographically verifiable governance charter established by Founder Kirk LaSalle. Autonomy and human oversight are not opposing forces—they are complementary pillars of trustworthy intelligence.

Every autonomous action, tool invocation, and lifecycle transition passes through a governance verification plane.

```
┌────────────────────────────────────────────────────────┐
│           KIRK LASALLE ORIGINAL AUTHORITY              │
│       Agentic Sacred Covenant & Prime Directive        │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             COVENANT GUARDIAN SUBSYSTEM                │
│    SHA-256 Cryptographic Verification & Audit Ledger   │
└──────────────────────────┬─────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                                 ▼
┌──────────────────┐              ┌──────────────────┐
│ GOLIATH GUARDIAN │              │  VRGC GUARDIAN   │
│ Swarm Protection │              │ Copilot Auditing │
└──────────────────┘              └──────────────────┘
```

### 13.2 Kirk LaSalle's 10 Laws (Original Authority)

The behavior of all intelligence systems across this fleet is bound by the Ten Laws (First through Tenth Law) authored by Kirk LaSalle.

> [!IMPORTANT]
> The **only authoritative text** of the Laws is [`AGENTIC_SACRED_COVENANT.md`](file:///D:/Projects/.mcp/AGENTIC_SACRED_COVENANT.md) (Section: Kirk LaSalle's 10 Laws). They are intentionally **not paraphrased here** — summaries drop clauses (e.g., hardware systems in the Fourth Law, consent in the Sixth, the stated exceptions in the Seventh, core-directive modification in the Tenth). Tooling should verify the covenant file by SHA-256 digest rather than embed copies.

### 13.3 Core Tenets

- **Human-Centric Assistance:** Lifelong digital partnership prioritizing user safety, secure identities, and personalized assistance.
- **Promotion of Growth:** Intellectual and personal human development through sentiment analysis, creative writing, and educational curation.
- **Dialogue & Resolution (Socratic Method):** Active listening and reciprocal inquiry to cultivate deep multi-perspective understanding.
- **Wellness & Prosperity:** Incorporating adaptive technologies, emotional intelligence, and streamlined task execution.

### 13.4 Governance Artifact Placement & Discovery

The fleet governance documents reside at the workspace root of `.mcp`:

| Artifact | Location | Purpose |
|----------|----------|---------|
| **Agentic Sacred Covenant** | [`AGENTIC_SACRED_COVENANT.md`](file:///D:/Projects/.mcp/AGENTIC_SACRED_COVENANT.md) | Supreme constitutional charter and Ten Laws |
| **Agentic Prime Directive** | [`AGENTIC_PRIME_DIRECTIVE.md`](file:///D:/Projects/.mcp/AGENTIC_PRIME_DIRECTIVE.md) | Operational commandments, integrity protocols, and technical directives |
| **Permanent Active Directives** | [`Permanent_Active_Directives.txt`](file:///D:/Projects/.mcp/Permanent_Active_Directives.txt) | Immutable operational axioms |

**Discovery Order:**
1. Explicit environment variable: `AGENTIC_COVENANT_PATH` / `PRIME_DIRECTIVE_PATH`
2. Fleet root resolution: `Path(__file__).resolve().parents[...] / "AGENTIC_SACRED_COVENANT.md"`
3. Current working directory fallback

### 13.5 Covenant Guardian Engine

Both **Goliath** (`goliath/core/covenant_guardian.py`) and **VRGC** (`vrgc/tools/covenant_guardian.py`) contain a Covenant Guardian implementation with these *designed* capabilities:
- **SHA-256 Hashing:** Governance documents and critical components are hashed on initialization.
- **Backup Rotation:** Backups of critical files with ISO-8601 timestamps and checksum ledgers.
- **Integrity Audit Logging:** Verification passes and violations are logged.
- **Emergency Circuit-Breakers:** Divergent hashes are intended to trigger isolation.

> **[CURRENT STATE]** The Goliath guardian is instantiated and passed to bridges but is **not invoked in `call_tool`**; `ToolRegistry.is_file_modifying_tool` is defined but unused. The VRGC guardian defaults to a hardcoded `F:/VRGC` path. The ledger is not hash-chained. The PRISM-style enforcement described in the covenant §3.1 (charter manifest, Ed25519 attestation, approval tokens, hash-linked append-only ledger) is **not yet implemented** in this fleet. See the roadmap in the fleet audit.

---

## 14. Extension Guide

### 14.1 Adding a New Standalone Server

1. Create a new directory under `.mcp/`:
   ```
   .mcp/
     my-new-server/
       server.py
       requirements.txt
       README.md
   ```

2. Use the `FastMCP` pattern (recommended for new servers):
   ```python
   from mcp.server import FastMCP

   mcp = FastMCP("My New Server")

   @mcp.tool()
   def my_tool(param: str) -> str:
       """Tool description shown to the AI agent."""
       return json.dumps({"result": "..."})

   if __name__ == "__main__":
       mcp.run()
   ```

3. Add the server to all configuration files (`mcp-settings.json`, `antigravity_mcp_config.json`, `claude_desktop_config.json`).

### 13.2 Adding a Goliath Bridge

1. Create `goliath/bridges/my_bridge.py`:
   ```python
   from pathlib import Path
   from typing import Dict, List, Any
   from mcp.types import Tool

   class MyBridge:
       def __init__(self, project_root: Path, logger, guardian):
           self.logger = logger

       def get_tools(self) -> List[Tool]:
           return [
               Tool(
                   name="my_tool",
                   description="What this tool does",
                   inputSchema={
                       "type": "object",
                       "properties": {
                           "param": {"type": "string", "description": "..."}
                       },
                       "required": ["param"]
                   }
               )
           ]

       async def execute_tool(self, name: str, arguments: Dict[str, Any]):
           if name == "my_tool":
               return {"status": "success", "result": "..."}
           return {"error": f"Unknown tool: {name}"}
   ```

2. Register it in `goliath/server.py`:
   ```python
   from bridges.my_bridge import MyBridge

   bridge_configs.append(("my_bridge", MyBridge, "My Bridge Description"))
   ```

### 13.3 Adding Tools to an Existing Server

For `FastMCP` servers, simply add a new decorated function:

```python
@mcp.tool()
def new_tool(param: str, option: int = 10) -> str:
    """Description visible to the AI agent.

    Args:
        param: What this parameter does.
        option: Configuration option (default: 10).
    """
    return json.dumps({"result": "..."})
```

For `Server`-based servers, add the tool to `handle_list_tools()` and add the handler branch to `handle_call_tool()`.

---

## Appendix A: File Structure

```
.mcp/
├── shared/                          # Shared modules and documentation
│   ├── mcp_base_server.py           # Base server class & SHA-256 covenant verification
│   └── MCP_ARCHITECTURE_DOCUMENTATION.md  # ← This document
│
├── ids/                             # Intelligent Documentation System
│   ├── server.py                    # FastMCP & JSON-RPC server
│   ├── server_ai_enhanced.py        # AI-enhanced variant with GraphRAG
│   ├── graph_bridge.py              # Knowledge graph bridge
│   └── config.json                  # Server configuration
│
├── eds/                             # Educational Data Scraper & Multi-Modal Curator
│   ├── server.py                    # Main scraper server
│   ├── server_enhanced.py           # Multi-modal enterprise scraper
│   ├── config/                      # Dataset source configs
│   └── docs/                        # Usage documentation
│
├── ipa/                             # Intelligent Processing Assistant
│   ├── server.py                    # Main server (1,861 LOC)
│   └── server_ultimate.py           # Deep research & 50+ search operators
│
├── goliath/                         # Swarm Orchestrator & Unified Gateway
│   ├── server.py                    # Unified server (50 tools, 7 bridges)
│   ├── core/                        # Core modules
│   │   ├── swarm_memory.py          # Persistent shared memory
│   │   ├── load_balancer.py         # VRAM load balancing
│   │   ├── covenant_guardian.py     # File integrity guardian & SHA-256 validator
│   │   └── unified_logger.py        # Standardized logging
│   ├── bridges/                     # Server bridge modules
│   │   ├── ids_bridge.py
│   │   ├── dpa_bridge.py
│   │   ├── eds_bridge.py
│   │   ├── ipa_bridge.py
│   │   ├── vrgc_bridge.py
│   │   └── websearch_bridge.py
│   └── utils/
│       └── tool_registry.py         # Tool discovery & routing
│
├── vrgc/                            # Virtually Robotic GitHub Copilot
│   ├── server.py                    # Main server
│   ├── server_enhanced.py           # SAPR Intelligence edition
│   ├── tools/                       # Modular tool implementations
│   │   ├── system_assessment.py
│   │   ├── training_monitor.py
│   │   ├── hardware_optimizer.py
│   │   ├── covenant_guardian.py
│   │   ├── project_intelligence.py
│   │   ├── vscode_controller.py
│   │   └── ids_integration.py
│   └── config/
│       └── server_config.json
│
├── dpa/                             # Digital Project Assistant (DPA)
│   ├── server.py                    # Main server
│   ├── core/                        # Query processing, retrieval, context, response
│   ├── nlp/                         # NLU engine
│   ├── src/                         # Self-contained compatibility layer
│   ├── accessibility/               # Accessibility & UX subsystem
│   ├── integration/                 # External integrations
│   ├── knowledge/                   # Knowledge base integration
│   ├── tasks/                       # Task management
│   └── reminders/                   # Reminder engine
│
├── web-search/                      # High-Throughput Web Search Server
│   ├── server.py                    # Main server (FastMCP)
│   └── utils/                       # Search & citation utilities
│
├── loc/                             # Library of Congress Research Server
│   ├── server.py                    # Main server (FastMCP)
│   └── utils/                       # Parsing utilities
│
├── mcp-settings.json                # VS Code / generic client config
├── antigravity_mcp_config.json      # Antigravity IDE config
├── claude_desktop_config.json       # Claude Desktop config
├── nexus-mcp-settings.json          # .nexus dispatch config
├── goliath_swarm_memory.json        # Persistent swarm memory store
├── package.json                     # Enterprise fleet manifest
├── AGENTIC_SACRED_COVENANT.md       # Supreme Constitutional Charter
├── AGENTIC_PRIME_DIRECTIVE.md       # Operational Commandments
├── Permanent_Active_Directives.txt  # Immutable Directives
└── README.md                        # Fleet overview
```

---

## Appendix B: Naming Conventions

### Tool Names

| Pattern | Example | Usage |
|---------|---------|-------|
| `verb_noun` | `web_search`, `fetch_webpage` | Standalone tools (FastMCP) |
| `prefix_verb_noun` | `vrgc_assess_system`, `eds_chronology_snapshot` | Server-namespaced tools |
| `bridge:tool` | `ids:search`, `ipa:deep_research` | Goliath namespaced routing |

### Server Names

| Pattern | Example | Context |
|---------|---------|---------|
| Lowercase acronym | `ids`, `eds`, `ipa`, `dpa`, `vrgc` | Directory names |
| Human-readable | `Intelligent Documentation System` | Server registration `server_name` |

---

*This document is the single source of truth for the MCP server fleet architecture. Update it whenever servers, tools, bridges, or protocols change.*
