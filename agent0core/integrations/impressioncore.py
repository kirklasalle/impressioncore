# ImpressionCore Header — Created: June 29, 2025
# Module: agent0core.integrations.impressioncore
# Description: Dependency Inversion boundary — abstracts ImpressionCore platform services
"""
Dependency Inversion boundary for ImpressionCore platform services.

Agent0core code MUST NOT import directly from ``src/``. Instead all
platform capabilities (vector search, LLM generation) are accessed
through the abstract protocols defined here. Concrete implementations
are registered by ``src/`` at application startup via the
``register_*`` helpers.

Usage inside agent0core::

    from agent0core.integrations.impressioncore import get_vector_provider

    provider = get_vector_provider()
    if provider is not None:
        results = provider.search(query, top_k=5)

Startup wiring (done once in src/)::

    from agent0core.integrations.impressioncore import (
        register_vector_provider, register_triad_provider,
    )
    from src.orchestrator.vector_connector import VectorMemoryConnector
    from src.orchestrator.unified_triad import UnifiedBrainTriad

    register_vector_provider(VectorMemoryConnector())
    register_triad_provider(UnifiedBrainTriad())
"""
from __future__ import annotations

import logging
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Abstract protocols — agent0core depends ONLY on these
# ---------------------------------------------------------------------------


@runtime_checkable
class VectorMemoryProvider(Protocol):
    """Abstract vector-DB operations that agent0core needs."""

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Return up to *top_k* results matching *query*."""
        ...

    def add_memory(self, text: str, metadata: dict[str, Any]) -> None:
        """Persist a text fragment with metadata into the vector store."""
        ...


@runtime_checkable
class LLMTriadProvider(Protocol):
    """Abstract LLM generation that agent0core needs."""

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text for the given *prompt*."""
        ...


# ---------------------------------------------------------------------------
# Singleton registry — populated by src/ at startup
# ---------------------------------------------------------------------------

_vector_provider: VectorMemoryProvider | None = None
_triad_provider: LLMTriadProvider | None = None
# Additive: native B3 Hope v1 provider, independent of the Left/Right/Colossus
# triad. Registered separately so callers can opt into pure B3 inference
# without disturbing the existing triad wiring.
_b3_native_provider: LLMTriadProvider | None = None


def register_vector_provider(provider: VectorMemoryProvider) -> None:
    """Register the platform's vector-memory provider (called once at startup)."""
    global _vector_provider
    _vector_provider = provider
    logger.info("agent0core: VectorMemoryProvider registered (%s)", type(provider).__name__)


def register_triad_provider(provider: LLMTriadProvider) -> None:
    """Register the platform's LLM triad provider (called once at startup)."""
    global _triad_provider
    _triad_provider = provider
    logger.info("agent0core: LLMTriadProvider registered (%s)", type(provider).__name__)


def get_vector_provider() -> VectorMemoryProvider | None:
    """Return the registered vector provider, or ``None`` if not yet wired."""
    return _vector_provider


def get_triad_provider() -> LLMTriadProvider | None:
    """Return the registered LLM triad provider, or ``None`` if not yet wired."""
    return _triad_provider


def register_b3_native_provider(provider: LLMTriadProvider) -> None:
    """Register the native B3 Hope v1 provider (additive, called once at startup)."""
    global _b3_native_provider
    _b3_native_provider = provider
    logger.info("agent0core: B3NativeLLMProvider registered (%s)", type(provider).__name__)


def get_b3_native_provider() -> LLMTriadProvider | None:
    """Return the registered native B3 provider, or ``None`` if not yet wired."""
    return _b3_native_provider
