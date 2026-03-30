"""Inference session protocols for prompt → response generation."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class InferenceSessionProtocol(Protocol):
    """Contract for inference engines / RAG inference sessions.

    Satisfied by InferenceEngine, B3RAGInference, and future backends.
    """

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 256,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate text from a prompt string.  Return the response text."""
        ...


@runtime_checkable
class EmbedderProtocol(Protocol):
    """Contract for multimodal embedding generators (UnifiedEmbedder, etc.)."""

    def embed_text_long(self, text: str, seq_len: int = 512) -> np.ndarray:
        """Embed a text string into a dense vector."""
        ...

    def embed_image(self, img_path: str) -> np.ndarray:
        """Embed an image file into a dense vector."""
        ...

    def embed_audio(self, waveform_np: np.ndarray) -> np.ndarray:
        """Embed an audio waveform into a dense vector."""
        ...

    def embed_unified(
        self,
        text: str | None = None,
        img_path: str | None = None,
        audio_waveform: np.ndarray | None = None,
    ) -> np.ndarray:
        """Produce a fused multimodal embedding."""
        ...
