#!/usr/bin/env python3
"""
sdk_adapter: serve legacy dict-based tool servers through the official MCP SDK
================================================================================

Several fleet servers expose their tools as plain Python objects:

    server.get_tools()            -> list[dict]   # {"name", "description", "inputSchema", ...}
    await server.call_tool(n, a)  -> dict | str | list

and previously hand-rolled their own JSON-RPC loops. Hand-rolled loops are a
reliability hazard (missing ids, replies to notifications, no protocol version
negotiation, no cancellation). This adapter puts those objects behind the official
``mcp`` low-level ``Server`` so protocol handling is spec-compliant by construction.

Error semantics: a result that represents failure is raised, so the SDK returns
``isError: true`` to the client. A dict counts as a failure if it carries a truthy
``error`` key and its ``status``/``success`` fields don't indicate success.
"""

from __future__ import annotations

import inspect
import json
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Union

from shared.stdio_guard import protect_stdout, stdio_server

ToolDict = Dict[str, Any]
ListFn = Callable[[], Union[Iterable[ToolDict], Awaitable[Iterable[ToolDict]]]]
CallFn = Callable[[str, Dict[str, Any]], Any]


class ToolExecutionError(RuntimeError):
    """Raised to signal a tool-level failure (mapped to ``isError: true``)."""


def is_error_result(result: Any) -> bool:
    """Heuristic used fleet-wide to decide whether a dict result is a failure."""
    if not isinstance(result, dict):
        return False
    if result.get("isError") is True:
        return True
    if not result.get("error"):
        return False
    status = str(result.get("status", "")).lower()
    if status in {"success", "ok", "partial"} or result.get("success") is True:
        return False
    return True


def to_text(result: Any) -> str:
    if isinstance(result, str):
        return result
    try:
        return json.dumps(result, indent=2, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(result)


async def _maybe_await(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


def build_server(
    name: str,
    version: str,
    list_tools: ListFn,
    call_tool: CallFn,
    instructions: Optional[str] = None,
):
    """Create an official-SDK low-level Server that wraps dict-based tool callables."""
    from mcp import types
    from mcp.server.lowlevel import Server

    app = Server(name, version=version, instructions=instructions)
    _allowed = set(types.Tool.model_fields.keys())

    def _to_tool(d: ToolDict) -> "types.Tool":
        data = {k: v for k, v in d.items() if k in _allowed}
        data.setdefault("description", "")
        data.setdefault("inputSchema", {"type": "object", "properties": {}})
        return types.Tool(**data)

    @app.list_tools()
    async def _list_tools() -> List["types.Tool"]:
        tools = await _maybe_await(list_tools())
        return [_to_tool(t) if isinstance(t, dict) else t for t in tools]

    @app.call_tool(validate_input=False)
    async def _call_tool(tool_name: str, arguments: Dict[str, Any]):
        result = await _maybe_await(call_tool(tool_name, arguments or {}))
        if is_error_result(result):
            raise ToolExecutionError(to_text(result))
        if isinstance(result, list) and result and hasattr(result[0], "type"):
            return result
        return [types.TextContent(type="text", text=to_text(result))]

    return app


async def serve_stdio(app) -> None:
    """Run an SDK Server over protected stdio."""
    protect_stdout()
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
