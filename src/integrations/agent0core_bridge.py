# ImpressionCore Header — Created: June 29, 2025
# Module: src.integrations.agent0core_bridge
# Description: Startup wiring — injects platform services into agent0core's DI boundary
"""
Agent0core startup bridge.

Call :func:`wire_agent0core` once during application bootstrap (e.g. in
``triad_api.py`` startup or ``src/main.py``) to inject concrete
ImpressionCore platform services into agent0core's Dependency Inversion
boundary.  After this call, agent0core code can use
``get_vector_provider()`` and ``get_triad_provider()`` without importing
anything from ``src/``.

Usage::

    from src.integrations.agent0core_bridge import wire_agent0core
    wire_agent0core()        # registers VectorMemoryConnector + UnifiedBrainTriad
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def wire_agent0core(triad_instance=None) -> None:
    """Register ImpressionCore platform services with agent0core's DI layer.

    This is safe to call multiple times — providers are only created once.
    Failures are logged but never crash the application.

    Args:
        triad_instance: Optional existing UnifiedBrainTriad instance.
            If provided, reuses it instead of creating a new one.
    """
    _wire_vector_provider()
    _wire_triad_provider(triad_instance)
    _wire_b3_native_provider()


def _wire_vector_provider() -> None:
    """Inject :class:`VectorMemoryConnector` as the vector provider."""
    try:
        from agent0core.integrations.impressioncore import (
            get_vector_provider,
            register_vector_provider,
        )

        if get_vector_provider() is not None:
            logger.debug("VectorMemoryProvider already registered — skipping")
            return

        from src.orchestrator.vector_connector import VectorMemoryConnector

        register_vector_provider(VectorMemoryConnector())
    except ImportError as exc:
        logger.warning("Could not wire VectorMemoryProvider: %s", exc)
    except Exception as exc:
        logger.error("Unexpected error wiring VectorMemoryProvider: %s", exc, exc_info=True)


def _wire_triad_provider(triad_instance=None) -> None:
    """Inject :class:`UnifiedBrainTriad` as the LLM triad provider."""
    try:
        from agent0core.integrations.impressioncore import (
            get_triad_provider,
            register_triad_provider,
        )

        if get_triad_provider() is not None:
            logger.debug("LLMTriadProvider already registered — skipping")
            return

        if triad_instance is not None:
            register_triad_provider(triad_instance)
        else:
            from src.orchestrator.unified_triad import UnifiedBrainTriad

            register_triad_provider(UnifiedBrainTriad())
    except ImportError as exc:
        logger.warning("Could not wire LLMTriadProvider: %s", exc)
    except Exception as exc:
        logger.error("Unexpected error wiring LLMTriadProvider: %s", exc, exc_info=True)


def _wire_b3_native_provider() -> None:
    """Inject :class:`B3NativeLLMProvider` as the native B3 Hope v1 provider.

    Additive: registered independently of the Left/Right/Colossus triad so
    callers can opt into pure B3 inference (via the ``b3_native`` agent0core
    backend) without disturbing existing triad wiring. Loading is lazy —
    the checkpoint is only loaded into memory on first ``generate()`` call.
    """
    try:
        from agent0core.integrations.impressioncore import (
            get_b3_native_provider,
            register_b3_native_provider,
        )

        if get_b3_native_provider() is not None:
            logger.debug("B3NativeLLMProvider already registered — skipping")
            return

        from src.inference.b3_native_inference import B3NativeLLMProvider

        register_b3_native_provider(B3NativeLLMProvider(lazy=True))
    except ImportError as exc:
        logger.warning("Could not wire B3NativeLLMProvider: %s", exc)
    except Exception as exc:
        logger.error("Unexpected error wiring B3NativeLLMProvider: %s", exc, exc_info=True)
