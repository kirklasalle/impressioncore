#!/usr/bin/env python3
"""Web Search MCP — stdio JSON-RPC server.

This is a hand-rolled stdio MCP server (matching the protocol shape used by
the sibling impressioncore-vrgc server) that exposes the existing
`utils.search.perform_search` + `utils.citation.generate_citations`
pipeline as a single MCP tool: `web_search`.

The previous `server.py` ran a FastAPI/uvicorn HTTP service on port 8765,
which is incompatible with Prism's stdio MCP transport. The original is
preserved at `server_uvicorn_backup.py`.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict

# Make sure relative imports work when launched from any cwd.
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from utils.search import perform_search  # type: ignore  # noqa: E402
from utils.citation import generate_citations  # type: ignore  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("web-search-mcp")

CONFIG_PATH = os.path.join(HERE, "config.json")
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
except Exception as exc:  # pragma: no cover - best-effort defaults
    logger.error("Failed to load config.json: %s", exc)
    CONFIG = {
        "search": {
            "default_num_results": 5,
            "max_num_results": 10,
            "safe_search": True,
            "timeout": 30,
        }
    }

SEARCH_CFG = CONFIG.get("search", {})
DEFAULT_NUM = int(SEARCH_CFG.get("default_num_results", 5))
MAX_NUM = int(SEARCH_CFG.get("max_num_results", 10))
SAFE_SEARCH = bool(SEARCH_CFG.get("safe_search", True))
TIMEOUT = int(SEARCH_CFG.get("timeout", 30))

SERVER_INFO = {
    "name": "web-search-mcp",
    "version": "1.1.0",
}

TOOLS = [
    {
        "name": "web_search",
        "description": (
            "Perform a DuckDuckGo web search and optionally generate "
            "citations for each result."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string.",
                },
                "num_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": MAX_NUM,
                    "default": DEFAULT_NUM,
                    "description": f"Number of results to return (1-{MAX_NUM}).",
                },
                "require_citations": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to enrich results with citations.",
                },
            },
            "required": ["query"],
        },
    }
]


async def _run_web_search(args: Dict[str, Any]) -> Dict[str, Any]:
    query = str(args.get("query", "")).strip()
    if not query:
        raise ValueError("'query' is required and must be a non-empty string")
    num_results = int(args.get("num_results", DEFAULT_NUM))
    num_results = max(1, min(num_results, MAX_NUM))
    require_citations = bool(args.get("require_citations", True))

    results = await perform_search(
        query=query,
        num_results=num_results,
        safe_search=SAFE_SEARCH,
        timeout=TIMEOUT,
    )
    if require_citations:
        results = await generate_citations(results)

    return {
        "query": query,
        "result_count": len(results),
        "results": results,
    }


def _ok(req_id: Any, result: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _err(req_id: Any, code: int, message: str) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": code, "message": message},
    }


async def _handle(request: Dict[str, Any]) -> Dict[str, Any] | None:
    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params") or {}

    if method == "initialize":
        return _ok(
            req_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
            },
        )

    if isinstance(method, str) and method.startswith("notifications/"):
        # Notifications carry no id and require no response.
        return None

    if method == "tools/list":
        return _ok(req_id, {"tools": TOOLS})

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments") or {}
        if tool_name != "web_search":
            return _err(req_id, -32601, f"Unknown tool: {tool_name}")
        try:
            payload = await _run_web_search(arguments)
            return _ok(
                req_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(payload, ensure_ascii=False),
                        }
                    ],
                    "isError": False,
                },
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("web_search failed")
            return _ok(
                req_id,
                {
                    "content": [
                        {"type": "text", "text": f"web_search error: {exc}"}
                    ],
                    "isError": True,
                },
            )

    if method == "ping":
        return _ok(req_id, {})

    return _err(req_id, -32601, f"Method not found: {method}")


async def _main() -> None:
    logger.info("web-search-mcp stdio server starting")
    loop = asyncio.get_running_loop()
    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            logger.info("stdin closed; exiting")
            return
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            sys.stdout.write(
                json.dumps(_err(None, -32700, f"Parse error: {exc}")) + "\n"
            )
            sys.stdout.flush()
            continue
        try:
            response = await _handle(request)
        except Exception as exc:  # noqa: BLE001
            logger.exception("handler crashed")
            response = _err(request.get("id"), -32603, f"Internal error: {exc}")
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass
