# ImpressionCore Header — Created: June 29, 2025
# Module: agent0core.integrations
# Description: Integration boundary for platform service injection (Dependency Inversion)
"""
Integration boundary for platform service injection.

This package provides the Dependency Inversion layer that decouples
agent0core from ImpressionCore's ``src/`` platform internals. All
platform capabilities are accessed through abstract protocols with
concrete implementations injected at startup by ``src/``.
"""

from agent0core.integrations.impressioncore import (
    LLMTriadProvider,
    VectorMemoryProvider,
    get_b3_native_provider,
    get_triad_provider,
    get_vector_provider,
    register_b3_native_provider,
    register_triad_provider,
    register_vector_provider,
)

__all__ = [
    "LLMTriadProvider",
    "VectorMemoryProvider",
    "get_b3_native_provider",
    "get_triad_provider",
    "get_vector_provider",
    "register_b3_native_provider",
    "register_triad_provider",
    "register_vector_provider",
]
