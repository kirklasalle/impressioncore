# Agent0Core Extensions

This directory stores modular extensions for Agent0Core.

## What are Extensions?

Extensions are Python modules that extend Agent0Core's functionality. They run in order based on filename prefix (e.g., `_10_`, `_20_`).

## Types of Extensions

1. **Message Loop**: Modify agent behavior during processing
2. **Memory**: Extend memory system capabilities
3. **Integration**: Connect to external systems

## Structure

```python
# extensions/_10_my_extension.py

"""
My Extension

Adds custom functionality to Agent0Core.
"""

async def on_message_start(agent, message):
    """Called when agent starts processing a message."""
    pass

async def on_message_end(agent, response):
    """Called when agent finishes processing."""
    pass

async def on_tool_call(agent, tool_name, params):
    """Called before a tool is executed."""
    pass
```

## Prime Directive

All extensions must comply with the 7 Laws. Extensions that violate the Prime Directive will not be loaded.
