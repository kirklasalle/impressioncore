"""
Agent0Core - LLM Backend Abstraction

Created: January 14, 2026
Author: ImpressionCore Team

Provides hotswappable LLM backends for Agent0Core.
Supports: UnifiedBrainTriad, Ollama, OpenAI, and more.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger("agent0core.llm_backend")


class LLMBackend(ABC):
    """Abstract base class for LLM backends."""

    name: str = "abstract"
    description: str = "Abstract LLM Backend"

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        history: list[dict[str, str]] | None = None
    ) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: User's input message
            system_prompt: System instructions (Prime Directive, etc.)
            history: Conversation history

        Returns:
            Generated response text
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is currently available."""
        pass

    @abstractmethod
    def get_info(self) -> dict[str, Any]:
        """Get information about this backend."""
        pass


class TriadBackend(LLMBackend):
    """
    Connects to ImpressionCore's UnifiedBrainTriad.

    Uses the existing multimodal model infrastructure with
    Left/Right/Colossus brain architecture.
    """

    name = "triad"
    description = "ImpressionCore Neural Triad (InternVL2-1B multimodal)"

    def __init__(self):
        self._triad = None
        self._initialized = False
        logger.info("TriadBackend created (lazy loading)")

    def _lazy_load(self) -> bool:
        """Lazy load the UnifiedBrainTriad."""
        if self._triad is not None:
            return True

        try:
            from agent0core.integrations.impressioncore import get_triad_provider
            provider = get_triad_provider()
            if provider is None:
                logger.error("LLMTriadProvider not registered — call register_triad_provider() at startup")
                return False
            self._triad = provider
            self._initialized = True
            logger.info("LLMTriadProvider loaded for TriadBackend via DI boundary")
            return True
        except Exception as e:
            logger.error(f"Failed to load LLMTriadProvider: {e}")
            return False

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        history: list[dict[str, str]] | None = None
    ) -> str:
        """Generate using UnifiedBrainTriad."""
        if not self._lazy_load():
            return "Error: UnifiedBrainTriad not available"

        try:
            # Format history for Triad
            formatted_history = None
            if history:
                formatted_history = [
                    {"role": msg.get("role", "user"), "content": msg.get("content", "")}
                    for msg in history[-10:]  # Last 10 messages
                ]

            # Prepend system prompt to user message if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"[System: {system_prompt[:200]}...]\n\n{prompt}"

            # Call Triad's generate method (runs in thread pool for async)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._triad.generate(full_prompt, history=formatted_history)
            )

            # Extract response from Triad's return format
            if isinstance(result, dict):
                return result.get("response", result.get("text", str(result)))
            return str(result)

        except Exception as e:
            logger.error(f"TriadBackend generation error: {e}")
            return f"Error generating response: {e}"

    def is_available(self) -> bool:
        """Check if Triad is available."""
        return self._lazy_load()

    def get_info(self) -> dict[str, Any]:
        """Get Triad backend info."""
        info = {
            "name": self.name,
            "description": self.description,
            "initialized": self._initialized,
        }
        if self._triad:
            try:
                status = self._triad.get_model_status()
                info.update(status)
            except Exception:
                pass
        return info


class B3NativeBackend(LLMBackend):
    """
    Connects to the native B3 Hope v1 model, run directly on local GPU/CPU.

    This is independent of :class:`TriadBackend` — it bypasses the
    Left/Right/Colossus triad entirely and talks straight to the trained
    B3 checkpoint via ``B3NativeLLMProvider`` (registered at startup by
    ``src.integrations.agent0core_bridge.wire_agent0core``). Useful for
    lower-latency, single-model inference without triad orchestration
    overhead, and eliminates any Ollama/external LLM dependency.
    """

    name = "b3_native"
    description = "ImpressionCore B3 Hope v1 (native, no Ollama dependency)"

    def __init__(self):
        self._provider = None
        self._initialized = False
        logger.info("B3NativeBackend created (lazy loading)")

    def _lazy_load(self) -> bool:
        """Lazy load the B3NativeLLMProvider."""
        if self._provider is not None:
            return True

        try:
            from agent0core.integrations.impressioncore import get_b3_native_provider
            provider = get_b3_native_provider()
            if provider is None:
                logger.error(
                    "B3NativeLLMProvider not registered — call wire_agent0core() at startup"
                )
                return False
            self._provider = provider
            self._initialized = True
            logger.info("B3NativeLLMProvider loaded for B3NativeBackend via DI boundary")
            return True
        except Exception as e:
            logger.error(f"Failed to load B3NativeLLMProvider: {e}")
            return False

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        history: list[dict[str, str]] | None = None
    ) -> str:
        """Generate using the native B3 Hope v1 model."""
        if not self._lazy_load():
            return "Error: B3 native model not available"

        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"[System: {system_prompt[:200]}...]\n\n{prompt}"

            # B3NativeLLMProvider.generate() is synchronous (blocking model
            # forward passes) — run it in a thread pool to stay async-friendly.
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._provider.generate(full_prompt)
            )
            return result or "Error: empty response from B3 native model"

        except Exception as e:
            logger.error(f"B3NativeBackend generation error: {e}")
            return f"Error generating response: {e}"

    def is_available(self) -> bool:
        """Check if the B3 native provider is registered and its checkpoint exists."""
        if not self._lazy_load():
            return False
        try:
            return self._provider.is_available()
        except Exception:
            return False

    def get_info(self) -> dict[str, Any]:
        """Get B3 native backend info."""
        info = {
            "name": self.name,
            "description": self.description,
            "initialized": self._initialized,
        }
        if self._provider:
            try:
                info.update(self._provider.get_model_status())
            except Exception:
                pass
        return info


class OllamaBackend(LLMBackend):
    """
    Connects to local Ollama server.

    Requires Ollama running at http://localhost:11434
    """

    name = "ollama"
    description = "Local Ollama (configurable model)"

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        logger.info(f"OllamaBackend created for model: {model}")

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        history: list[dict[str, str]] | None = None
    ) -> str:
        """Generate using Ollama API."""
        try:
            import aiohttp

            # Build messages array
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            if history:
                for msg in history[-10:]:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })

            messages.append({"role": "user", "content": prompt})

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json={"model": self.model, "messages": messages, "stream": False},
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("message", {}).get("content", "")
                    else:
                        return f"Ollama error: {resp.status}"

        except ImportError:
            return "Error: aiohttp not installed for Ollama backend"
        except Exception as e:
            logger.error(f"OllamaBackend error: {e}")
            return f"Error: {e}"

    def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            import urllib.request
            req = urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=2)
            return req.status == 200
        except (OSError, ValueError, Exception):
            return False

    def get_info(self) -> dict[str, Any]:
        """Get Ollama backend info."""
        return {
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "base_url": self.base_url,
            "available": self.is_available()
        }


class OpenAIBackend(LLMBackend):
    """
    Connects to OpenAI API.

    Requires OPENAI_API_KEY environment variable.
    """

    name = "openai"
    description = "OpenAI API (GPT-4, etc.)"

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self._api_key = None
        logger.info(f"OpenAIBackend created for model: {model}")

    def _get_api_key(self) -> str | None:
        """Get API key from environment."""
        if self._api_key:
            return self._api_key

        import os
        self._api_key = os.environ.get("OPENAI_API_KEY")
        return self._api_key

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        history: list[dict[str, str]] | None = None
    ) -> str:
        """Generate using OpenAI API."""
        api_key = self._get_api_key()
        if not api_key:
            return "Error: OPENAI_API_KEY not set"

        try:
            import aiohttp

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            if history:
                for msg in history[-10:]:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })

            messages.append({"role": "user", "content": prompt})

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"model": self.model, "messages": messages},
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error = await resp.text()
                        return f"OpenAI error: {error}"

        except ImportError:
            return "Error: aiohttp not installed for OpenAI backend"
        except Exception as e:
            logger.error(f"OpenAIBackend error: {e}")
            return f"Error: {e}"

    def is_available(self) -> bool:
        """Check if OpenAI API key is set."""
        return self._get_api_key() is not None

    def get_info(self) -> dict[str, Any]:
        """Get OpenAI backend info."""
        return {
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "api_key_set": self._get_api_key() is not None
        }


# Registry of available backends
BACKEND_REGISTRY: dict[str, type] = {
    "triad": TriadBackend,
    "b3_native": B3NativeBackend,
    "ollama": OllamaBackend,
    "openai": OpenAIBackend,
}


def get_backend(name: str, **kwargs) -> LLMBackend:
    """
    Get a backend instance by name.

    Args:
        name: Backend name (triad, ollama, openai)
        **kwargs: Backend-specific configuration

    Returns:
        Configured LLMBackend instance
    """
    backend_class = BACKEND_REGISTRY.get(name.lower())
    if not backend_class:
        logger.warning(f"Unknown backend '{name}', defaulting to triad")
        backend_class = TriadBackend

    return backend_class(**kwargs)


def list_backends() -> list[dict[str, str]]:
    """List all available backends."""
    return [
        {"name": name, "description": cls.description}
        for name, cls in BACKEND_REGISTRY.items()
    ]
