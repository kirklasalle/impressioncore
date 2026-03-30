"""
Agent0Core - ImpressionCore Agentic Intelligence Layer

Created: January 13, 2026
Author: ImpressionCore Team

This package provides autonomous agent capabilities for ImpressionCore,
integrating Agent Zero framework with existing MCP servers and the B3 model.

All agents are governed by the Prime Directive (7 Laws for Intelligent Systems).
"""

__version__ = "0.1.0"
__author__ = "ImpressionCore Team"

from pathlib import Path

# Package paths
AGENT0CORE_ROOT = Path(__file__).parent
PROJECT_ROOT = AGENT0CORE_ROOT.parent
PRIME_DIRECTIVE_PATH = PROJECT_ROOT / "Prime_Directive.txt"
MCP_CONFIG_PATH = PROJECT_ROOT / ".mcp" / "mcp-settings.json"

# Verify Prime Directive exists
if not PRIME_DIRECTIVE_PATH.exists():
    raise FileNotFoundError(
        f"Prime Directive not found at {PRIME_DIRECTIVE_PATH}. "
        "Agent0Core requires the Prime Directive for ethical governance."
    )

__all__ = [
    "AGENT0CORE_ROOT",
    "MCP_CONFIG_PATH",
    "PRIME_DIRECTIVE_PATH",
    "PROJECT_ROOT",
    "__version__",
]
