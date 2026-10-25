#!/usr/bin/env python3
"""
stdio_guard: protocol-safe stdio for MCP servers
==================================================

The MCP stdio transport requires that **stdout carries only JSON-RPC messages**.
A single stray ``print()``, banner, progress bar, or C-extension write corrupts the
stream and the client drops the connection.

``protect_stdout()`` makes that class of bug impossible:

1. It duplicates the real stdout file descriptor and keeps it private for protocol traffic.
2. It points fd 1 (and ``sys.stdout``) at stderr, so anything printed by user code,
   third-party libraries, or native extensions lands in the log stream instead.

Call it **as early as possible** in a server entrypoint, before importing modules that
may print at import time:

    from shared.stdio_guard import protect_stdout, stdio_server
    protect_stdout()
    ...
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

The function is idempotent and safe to call more than once.
"""

from __future__ import annotations

import io
import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator, BinaryIO, Optional, Tuple

_protocol_out: Optional[BinaryIO] = None


def protect_stdout() -> BinaryIO:
    """Reserve the real stdout for MCP protocol traffic; redirect everything else to stderr.

    Returns the binary stream that must be used for protocol output.
    """
    global _protocol_out
    if _protocol_out is not None:
        return _protocol_out

    try:
        sys.stdout.flush()
    except Exception:
        pass

    try:
        saved_fd = os.dup(1)
        _protocol_out = os.fdopen(saved_fd, "wb", buffering=0)
        os.dup2(2, 1)  # fd 1 now writes to stderr (covers native/C-level writes too)
    except OSError:
        # No real fd 1 (embedded interpreters / some test harnesses): fall back to Python level.
        _protocol_out = sys.stdout.buffer  # type: ignore[assignment]

    # Python-level redirect so print() goes to stderr regardless of buffering state.
    sys.stdout = sys.stderr
    return _protocol_out  # type: ignore[return-value]


@asynccontextmanager
async def stdio_server() -> AsyncIterator[Tuple[object, object]]:
    """Drop-in replacement for ``mcp.server.stdio.stdio_server`` that writes protocol
    messages to the protected stdout stream returned by :func:`protect_stdout`."""
    import anyio
    from mcp.server.stdio import stdio_server as _sdk_stdio_server

    out = protect_stdout()
    stdin = anyio.wrap_file(io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace"))
    stdout = anyio.wrap_file(io.TextIOWrapper(out, encoding="utf-8", newline="", write_through=True))
    async with _sdk_stdio_server(stdin=stdin, stdout=stdout) as streams:
        yield streams
