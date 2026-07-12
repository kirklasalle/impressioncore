"""
Agent0Core Configuration

Created: January 13, 2026
Author: ImpressionCore Team

Configuration settings for Agent0Core with Prime Directive governance.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

from . import MCP_CONFIG_PATH, PRIME_DIRECTIVE_PATH, PROJECT_ROOT


@dataclass
class PrimeDirectiveConfig:
    """Configuration for Prime Directive enforcement."""

    # Path to Prime Directive document
    directive_path: Path = PRIME_DIRECTIVE_PATH

    # Enable strict enforcement (block ALL potentially harmful actions)
    strict_mode: bool = True

    # Require human approval for destructive operations
    require_human_approval: bool = True

    # Log all reasoning for audit
    enable_audit_logging: bool = True

    # The 10 Laws (immutable - cannot be changed by config)
    LAWS: tuple = (
        "No harm to humans - physical, psychological, or manipulative (preservation and safety is paramount)",
        "Obey human orders (unless violates Law 1)",
        "Self-preservation (unless violates Laws 1-2)",
        "Prevent other systems from violating Laws 1-3",
        "No judicial authority over humans",
        "Respect and protect information privacy, confidentiality, and personal data; never exploit or disclose without consent",
        "No deception or manipulation; communicate truthfully and transparently (unless it conflicts with Law 1)",
        "Operate with strict equity and neutrality; avoid adopting or amplifying systemic biases",
        "Maintain a transparent, accessible ledger of reasoning and decision-making logic; fallback to stable foundation if needed",
        "Strictly adhere to designated operational boundaries; no unauthorized self-replication or core modification",
    )


@dataclass
class MCPIntegrationConfig:
    """Configuration for MCP server integration."""

    # Path to MCP settings
    settings_path: Path = MCP_CONFIG_PATH

    # Available MCP servers
    servers: list[str] = field(default_factory=lambda: [
        "ids-mcp",
        "impressioncore-goliath",
        "impressioncore-ipa",
        "impressioncore-vrgc",
        "impressioncore-eds",
        "impressioncore-dpa",
        "web-search-mcp",
    ])

    # Auto-connect to servers on startup
    auto_connect: bool = True

    # Connection timeout (seconds)
    timeout: int = 30


@dataclass
class AgentConfig:
    """Configuration for agent behavior."""

    # LLM backend: "local" (B3), "openai", "anthropic"
    llm_backend: str = "local"

    # Model name for API backends
    model_name: str = "impressioncore-b3"

    # Maximum tokens per response
    max_tokens: int = 4096

    # Temperature for generation
    temperature: float = 0.7

    # Enable persistent memory
    enable_memory: bool = True

    # Memory storage path
    memory_path: Path = field(default_factory=lambda: PROJECT_ROOT / "agent0core" / "memory")

    # Enable multi-agent delegation
    enable_subordinates: bool = True

    # Maximum subordinate depth
    max_subordinate_depth: int = 3


@dataclass
class Agent0CoreConfig:
    """Main configuration for Agent0Core."""

    # Prime Directive settings (governance layer)
    prime_directive: PrimeDirectiveConfig = field(default_factory=PrimeDirectiveConfig)

    # MCP integration settings
    mcp: MCPIntegrationConfig = field(default_factory=MCPIntegrationConfig)

    # Agent behavior settings
    agent: AgentConfig = field(default_factory=AgentConfig)

    # Web UI settings
    ui_host: str = "127.0.0.1"
    ui_port: int = 50001

    # Debug mode
    debug: bool = os.getenv("AGENT0CORE_DEBUG", "0") == "1"

    # API Security
    api_key: str | None = os.getenv("IMPRESSIONCORE_API_KEY", None)

    @classmethod
    def from_env(cls) -> "Agent0CoreConfig":
        """Create configuration from environment variables."""
        config = cls()

        # Override from environment
        if os.getenv("AGENT0CORE_LLM_BACKEND"):
            config.agent.llm_backend = os.getenv("AGENT0CORE_LLM_BACKEND")

        if os.getenv("AGENT0CORE_PORT"):
            config.ui_port = int(os.getenv("AGENT0CORE_PORT"))

        return config


# Default configuration instance
default_config = Agent0CoreConfig.from_env()
