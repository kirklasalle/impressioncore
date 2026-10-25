"""Automated Client Configuration Generator for .mcp Enterprise Fleet.

Dynamically detects repository root, Python runtime, and host OS to generate
portable, 1-click configuration files for Claude Desktop, Antigravity IDE,
Cursor, and Windsurf.

Usage:
    python scripts/configure_clients.py            # Generates local config files
    python scripts/configure_clients.py --install  # Also installs directly to Claude Desktop / Cursor
"""

import argparse
import json
import os
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

SERVERS = {
    "goliath": {
        "script": "goliath/server.py",
        "cwd": "goliath",
        "env": {"GOLIATH_DEBUG": "1"},
        "transport": "stdio",
    },
    "ids": {
        "script": "ids/server_ai_enhanced.py",
        "cwd": "ids",
        "transport": "stdio",
    },
    "eds": {
        "script": "eds/server_enhanced.py",
        "cwd": "eds",
        "transport": "stdio",
    },
    "ipa": {
        "script": "ipa/server_ultimate.py",
        "cwd": "ipa",
        "transport": "stdio",
    },
    "vrgc": {
        "script": "vrgc/server_enhanced.py",
        "cwd": "vrgc",
        "transport": "stdio",
    },
    "dpa": {
        "script": "dpa/server.py",
        "cwd": "dpa",
        "transport": "stdio",
    },
    "web-search": {
        "script": "web-search/server.py",
        "cwd": "web-search",
        "transport": "stdio",
    },
    "loc": {
        "script": "loc/server.py",
        "cwd": "loc",
        "transport": "stdio",
    },
}


def build_config(transport_field: bool = False, pythonpath_env: bool = False):
    out = {"mcpServers": {}}
    for name, spec in SERVERS.items():
        server_path = str(ROOT / spec["script"])
        server_cwd = str(ROOT / spec["cwd"])
        entry = {
            "command": PY,
            "args": [server_path],
            "cwd": server_cwd,
            "env": {
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUTF8": "1",
                **spec.get("env", {}),
            },
        }
        if transport_field and "transport" in spec:
            entry["transport"] = spec["transport"]
        if pythonpath_env:
            sep = ";" if platform.system() == "Windows" else ":"
            entry["env"]["PYTHONPATH"] = f"{server_cwd}{sep}{ROOT}"
        out["mcpServers"][name] = entry
    return out


def main():
    parser = argparse.ArgumentParser(description="Generate MCP client configurations.")
    parser.add_argument("--install", action="store_true", help="Install into host Claude / Cursor directories")
    args = parser.parse_args()

    print(f"[*] Detected Fleet Root: {ROOT}")
    print(f"[*] Detected Python:     {PY}")
    print(f"[*] Host OS:             {platform.system()} ({platform.release()})")

    # 1. Claude Desktop config (no transport field)
    claude_cfg = build_config(transport_field=False, pythonpath_env=False)
    (ROOT / "claude_desktop_config.json").write_text(json.dumps(claude_cfg, indent=2), encoding="utf-8")
    print(f"[+] Wrote: {ROOT / 'claude_desktop_config.json'}")

    # 2. Antigravity IDE config (with transport="stdio")
    antigravity_cfg = build_config(transport_field=True, pythonpath_env=False)
    (ROOT / "antigravity_mcp_config.json").write_text(json.dumps(antigravity_cfg, indent=2), encoding="utf-8")
    print(f"[+] Wrote: {ROOT / 'antigravity_mcp_config.json'}")

    # 3. Cursor / Windsurf settings (with PYTHONPATH)
    cursor_cfg = build_config(transport_field=False, pythonpath_env=True)
    (ROOT / "mcp-settings.json").write_text(json.dumps(cursor_cfg, indent=2), encoding="utf-8")
    print(f"[+] Wrote: {ROOT / 'mcp-settings.json'}")

    # 4. Nexus fleet settings
    nexus_cfg = {
        "nexusMcpFleet": {
            "operator": "Kirk LaSalle",
            "version": "2.0.0",
            "fleet_root": str(ROOT),
            "python_executable": PY,
            "covenant_enforcement": "STRICT_GOVERNANCE",
        },
        **cursor_cfg,
    }
    (ROOT / "nexus-mcp-settings.json").write_text(json.dumps(nexus_cfg, indent=2), encoding="utf-8")
    print(f"[+] Wrote: {ROOT / 'nexus-mcp-settings.json'}")

    if args.install:
        if platform.system() == "Windows":
            appdata = os.environ.get("APPDATA")
            if appdata:
                claude_target = Path(appdata) / "Claude" / "claude_desktop_config.json"
                if claude_target.parent.exists():
                    claude_target.write_text(json.dumps(claude_cfg, indent=2), encoding="utf-8")
                    print(f"[✓] Installed to Claude Desktop: {claude_target}")
        print("[✓] Client installation complete.")


if __name__ == "__main__":
    main()
