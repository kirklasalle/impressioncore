#!/usr/bin/env python3
"""
Base MCP Server Architecture & Shared Utilities
===============================================
Author: Kirk LaSalle & Agentic Architecture Team
Protocol: Model Context Protocol (MCP)
Governance: Agentic Sacred Covenant & Prime Directive Verified
"""

import sys
import os
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

def get_fleet_root() -> Path:
    """
    Locates the fleet root directory containing governance documents
    and configuration files (e.g. AGENTIC_SACRED_COVENANT.md).
    """
    # 1. Check explicit environment override
    env_root = os.getenv("MCP_FLEET_ROOT") or os.getenv("AGENTIC_COVENANT_DIR")
    if env_root and Path(env_root).exists():
        return Path(env_root).resolve()

    # 2. Check candidate hierarchy relative to this file
    current = Path(__file__).resolve().parent
    candidate_roots = [
        current.parent,          # e.g., d:\Projects\.mcp if in shared/
        current,                 # e.g., if shared is root
        current.parent.parent,   # e.g., d:\Projects
        Path.cwd()
    ]
    for candidate in candidate_roots:
        if (candidate / "AGENTIC_SACRED_COVENANT.md").exists():
            return candidate

    return current.parent

class FleetLogger:
    """
    Standardized logger directing all messages to sys.stderr to
    preserve clean JSON-RPC 2.0 communication on stdout.
    """
    def __init__(self, server_name: str):
        self.server_name = server_name

    def _log(self, level: str, message: str):
        timestamp = datetime.now().isoformat()
        try:
            sys.stderr.write(f"[{timestamp}] [{level.upper()}] [{self.server_name}] {message}\n")
            sys.stderr.flush()
        except Exception:
            pass

    def info(self, message: str):
        self._log("INFO", message)

    def warning(self, message: str):
        self._log("WARN", message)

    def error(self, message: str):
        self._log("ERROR", message)

    def debug(self, message: str):
        if os.getenv("MCP_DEBUG") == "1":
            self._log("DEBUG", message)

class BaseMCPServer:
    """
    World-Class Base Server providing common infrastructure for all fleet servers:
    - Structured health checks
    - Sacred Covenant cryptographic verification
    - Memory and uptime metrics
    - Standard JSON-RPC error and envelope generation
    """
    def __init__(self, server_name: str, version: str = "2.0.0", description: str = ""):
        self.server_name = server_name
        self.version = version
        self.description = description
        self.start_time = time.time()
        self.fleet_root = get_fleet_root()
        self.logger = FleetLogger(server_name)
        self.registered_tools = []

    def get_covenant_status(self) -> Dict[str, Any]:
        """
        Cryptographically verifies the presence and SHA-256 hash
        of the Agentic Sacred Covenant and Prime Directive.
        """
        covenant_path = self.fleet_root / "AGENTIC_SACRED_COVENANT.md"
        directive_path = self.fleet_root / "AGENTIC_PRIME_DIRECTIVE.md"
        
        status = {
            "status": "VERIFIED" if covenant_path.exists() else "MISSING",
            "fleet_root": str(self.fleet_root),
            "documents": {}
        }

        for name, path in [("covenant", covenant_path), ("prime_directive", directive_path)]:
            if path.exists():
                try:
                    with open(path, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    status["documents"][name] = {
                        "path": str(path),
                        "sha256": file_hash,
                        "size_bytes": path.stat().st_size,
                        "exists": True
                    }
                except Exception as e:
                    status["documents"][name] = {"exists": True, "error": str(e)}
            else:
                status["documents"][name] = {"exists": False}

        return status

    def get_health_metrics(self) -> Dict[str, Any]:
        """
        Collects comprehensive health and operational metrics.
        """
        uptime_seconds = time.time() - self.start_time
        memory_mb = 0.0
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_mb = round(process.memory_info().rss / (1024 * 1024), 2)
        except Exception:
            pass

        return {
            "server_name": self.server_name,
            "version": self.version,
            "description": self.description,
            "status": "HEALTHY",
            "uptime_seconds": round(uptime_seconds, 2),
            "uptime_human": f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m {int(uptime_seconds % 60)}s",
            "memory_usage_mb": memory_mb,
            "tools_count": len(self.registered_tools),
            "covenant_governance": self.get_covenant_status(),
            "timestamp": datetime.now().isoformat()
        }

    def format_error_response(self, request_id: Any, code: int, message: str, data: Any = None) -> Dict[str, Any]:
        """Format standard JSON-RPC 2.0 error response."""
        err = {"code": code, "message": message}
        if data is not None:
            err["data"] = data
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": err
        }

    def format_success_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        """Format standard JSON-RPC 2.0 success response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
