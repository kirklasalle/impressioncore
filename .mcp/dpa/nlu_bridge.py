#!/usr/bin/env python3
"""
DPA NLU Bridge
==============

Thin adapter between the DPA MCP server and the local NLU engine
(``dpa/nlp/nlu_engine.py``).

The engine exposes *synchronous* helpers (``quick_analyze``,
``extract_intent_only``, ``extract_entities_only``). This bridge:

- fails loudly if the engine cannot be imported (no silent stubs);
- offers async variants that run the CPU-bound work in a worker thread;
- returns JSON-serializable dicts (enums -> values, dataclasses -> dicts).
"""

import asyncio
import dataclasses
import sys
from enum import Enum
from pathlib import Path
from typing import Any

CURRENT_DIR = Path(__file__).resolve().parent
FLEET_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(FLEET_ROOT))
sys.path.insert(0, str(CURRENT_DIR))

# Import failures must be loud: silently substituting stubs previously turned
# every NLU tool into a "'NoneType' object is not callable" error at call time.
from nlp.nlu_engine import (  # noqa: E402
    NLUEngine,  # re-exported for callers that construct engines directly
    quick_analyze,
    extract_intent_only,
    extract_entities_only,
)

__all__ = ["DPANLUBridge", "NLUEngine", "to_jsonable"]


def to_jsonable(obj: Any) -> Any:
    """Convert NLU results (dataclasses, enums, datetimes, containers) to JSON-safe data."""
    if isinstance(obj, Enum):
        return obj.value
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: to_jsonable(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_jsonable(v) for v in obj]
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return obj


class DPANLUBridge:
    """Bridge for DPA to use the NLU engine for user input analysis."""

    def __init__(self, max_memory_mb: int = 20):
        self.max_memory_mb = max_memory_mb

    # --- synchronous API -------------------------------------------------
    def analyze(self, text: str) -> dict:
        """Full analysis: intent, entities, sentiment."""
        return to_jsonable(quick_analyze(text))

    def get_intent(self, text: str) -> dict:
        """Intent only."""
        return {"text": text, "intent": to_jsonable(extract_intent_only(text))}

    def get_entities(self, text: str) -> dict:
        """Entities only."""
        return {"text": text, "entities": to_jsonable(extract_entities_only(text))}

    # --- async API (runs CPU-bound work off the event loop) ---------------
    async def analyze_async(self, text: str) -> dict:
        return await asyncio.to_thread(self.analyze, text)

    async def get_intent_async(self, text: str) -> dict:
        return await asyncio.to_thread(self.get_intent, text)

    async def get_entities_async(self, text: str) -> dict:
        return await asyncio.to_thread(self.get_entities, text)

    def shutdown(self):
        """Safe no-op shutdown; helper functions manage their own engine lifecycle."""
        return True


if __name__ == "__main__":
    import json

    bridge = DPANLUBridge()
    print(json.dumps(bridge.analyze("Schedule a meeting for tomorrow at 2:00 PM"), indent=2))
