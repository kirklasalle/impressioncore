# Changelog

All notable changes to the `.mcp` Model Context Protocol Enterprise Tooling Fleet will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-10-23

### Comprehensive Fleet Audit & Phase 0 Stabilization Release

This major release consolidates the fleet under a single, unified repository layout (`dpa`, `eds`, `goliath`, `ids`, `ipa`, `loc`, `vrgc`, `web-search`), establishes strict protocol compliance with the Model Context Protocol (MCP) date-versioned standard (`2025-11-25`), and introduces robust protocol-isolation infrastructure.

### Added
- **`LICENSE`**: Official Apache License, Version 2.0 ensuring enterprise protection and open-source adoption.
- **`pyproject.toml` & `requirements.txt`**: Unified PEP 517/621 packaging standard supporting 1-command `pip install -e .` and `uv` workspace resolution.
- **`scripts/configure_clients.py`**: Automated dynamic client configuration generator auto-detecting fleet root, Python executable, and host OS with `--install` support.
- **`.github/workflows/ci.yml`**: Multi-OS automated GitHub Actions CI/CD matrix verifying protocol gate (8/8 OK) on Ubuntu, Windows, and macOS.
- **Public Product Website (`D:\Projects\Websites\.mcp`)**: Interactive developer portal and command center featuring live telemetry, server explorer, terminal sandbox, and Chart.js competitive radar.
- **`shared/stdio_guard.py`**: Protocol-safe stdio stream isolation. Duplicates file descriptor 1 and redirects Python/C-level `stdout` to `stderr`, completely eliminating JSON-RPC protocol corruption caused by stray prints, banners, and progress bars.
- **`shared/sdk_adapter.py`**: Unified SDK wrapper providing consistent server instantiation, exception mapping to `isError=True` payloads, and JSON-RPC message serialization across both `FastMCP` and low-level `Server` implementations.
- **Automated Probe Suite (`tests/probe_v2.py`)**: Protocol and functional verification harness executing `initialize`, `tools/list`, positive tool execution, and negative tool handling (`isError=True`) against live servers.
- **1-Click Client Configurations**: Pre-validated JSON configurations for Google Antigravity IDE (`antigravity_mcp_config.json`), Anthropic Claude Desktop (`claude_desktop_config.json`), Cursor/Windsurf (`mcp-settings.json`), and Nexus (`nexus-mcp-settings.json`).
- **Comprehensive Documentation Suite**:
  - `docs/PRD.md`: Formal Product Requirements Document defining product architecture, functional specifications, and market positioning.
  - `docs/MARKET_RESEARCH.md`: Global 2026 MCP ecosystem analysis, competitive benchmarking, moats, and financial TAM models.
  - `docs/WEBSITE_REQUIREMENTS_AUDIT.md`: Complete audit and specification for the public digital presence.
  - `docs/USER_GUIDE.md`: End-user installation, 1-click IDE configuration, and tool workflow reference.
  - `docs/DEVELOPER_GUIDE.md`: Architecture manual, stdio stream safety, tool creation patterns, and testing guidelines.
  - `assets/images/`: Visual assets including repo hero banner, architecture schematic, user workflow diagram, and secure tool execution lifecycle.

### Changed
- **Directory Normalization**: Migrated legacy directory names to canonical micro-server packages (`impressioncore-dpa` → `dpa`, `impressioncore-eds` → `eds`, `impressioncore-goliath` → `goliath`, `ids-mcp` → `ids`, `impressioncore-ipa` → `ipa`, `loc-mcp-server` → `loc`, `impressioncore-vrgc` → `vrgc`, `web-search-mcp` → `web-search`).
- **Protocol Version Negotiation**: Updated server capability negotiation to target MCP `2025-11-25`.
- **DPA Server (`dpa/server.py`)**: Restructured NLU fallback chain to eliminate `TypeError: 'NoneType' object is not callable` in `get_intent` and resolved import pathing.
- **IPA Server (`ipa/server_ultimate.py`)**: Integrated `shared.stdio_guard` and fixed `FLEET_ROOT` path resolution, enabling `ipa_research_capabilities` and arXiv search tools to execute reliably without `ModuleNotFoundError`.
- **Goliath Orchestrator (`goliath/server.py`)**: Corrected tool bridge dispatch method call from `find_tool_bridge` to `get_tool_bridge`.
- **Documentation Audit**: Aligned `README.md` and `shared/MCP_ARCHITECTURE_DOCUMENTATION.md` with true operational state, eliminating misleading operational claims and labeling work-in-progress components with `[CURRENT STATE]`.

### Fixed
- Fixed 25 `SyntaxWarning` occurrences in docstrings caused by unescaped `\i` tags.
- Fixed JSON-RPC stream breakage across `eds`, `ipa`, and `vrgc` caused by startup ASCII art and logging to stdout.
- Fixed false-success bug where tool execution failures and non-existent tool requests returned `isError: false`. All servers now strictly adhere to standard JSON-RPC error protocols and `isError: true`.

---

## [1.5.0] - 2026-09-29

### Multi-Server Registry & Cross-Server Bridges
- Added Goliath master orchestrator multiplexing child servers via internal bridge modules.
- Introduced persistent swarm memory blackboard (`goliath_swarm_memory.json`).
- Integrated Library of Congress (`loc`) research server for catalog, newspaper, and legislative archives.
- Implemented DuckDuckGo and Google search fallback cascades in `web-search`.

---

## [1.0.0] - 2025-08-04

### Initial Prototype Monorepo
- Initial implementation of specialized micro-servers: `dpa`, `eds`, `ids`, `ipa`, and `vrgc`.
- Basic JSON-RPC 2.0 stdio server loops.
- Preliminary integration with Kirk LaSalle's Agentic Sacred Covenant and Prime Directive.
