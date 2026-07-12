# Agent0Core - ImpressionCore Agentic Intelligence Layer

**Created:** January 13, 2026  
**Author:** ImpressionCore Team  
**Status:** Active Development

---

## Overview

Agent0Core is ImpressionCore's autonomous intelligence layer, integrating the [Agent Zero](https://github.com/agent0ai/agent-zero) framework with ImpressionCore's MCP servers, B3 model, and Neural Triad.

## Prime Directive

All agents in this system are governed by the **10 Laws for Intelligent Systems** defined in `Permanent_Active_Directives.txt`. These laws are immutable and embedded in every agent prompt.

## Directory Structure

```
agent0core/
├── __init__.py              # Package initialization
├── config.py                # Configuration settings
├── run_cli.py               # CLI launcher
├── run_ui.py                # Web UI launcher
├── core/
│   ├── __init__.py
│   ├── agent.py             # Core agent implementation
│   ├── memory.py            # Memory system (VectorDB)
│   ├── governance.py        # Prime Directive enforcement
│   └── tools/               # Custom ImpressionCore tools
│       ├── __init__.py
│       ├── vision_tool.py   # Kinect/PS Eye integration
│       ├── audio_tool.py    # Neural Triad audio
│       └── training_tool.py # B3 training control
├── prompts/
│   └── impressioncore/      # ImpressionCore-specific prompts
│       ├── agent.system.main.md
│       └── agent.system.prime_directive.md
├── instruments/             # Custom instruments
│   └── README.md
├── knowledge/               # Knowledge base storage
│   └── README.md
├── extensions/              # Modular extensions
│   └── README.md
└── memory/                  # Persistent memory storage
    └── README.md
```

## Quick Start

```bash
# Start Agent0Core CLI
python -m agent0core.run_cli

# Start Agent0Core Web UI
python -m agent0core.run_ui --port 50001
```

## Integration with ImpressionCore MCP Servers

Agent0Core connects to all 7 existing MCP servers:
- `ids-mcp` - AI-enhanced documentation
- `impressioncore-goliath` - Swarm orchestration
- `impressioncore-ipa` - Ultimate search
- `impressioncore-vrgc` - Web access (30+ tools)
- `impressioncore-eds` - Educational data scraping
- `impressioncore-dpa` - NLU bridge
- `web-search-mcp` - Google/DuckDuckGo search

## License

MIT License - Same as ImpressionCore
