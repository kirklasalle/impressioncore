"""Teacher model generation utilities for knowledge distillation.

This subpackage groups scripts and helpers that invoke external / local
teacher models (e.g. Ollama served models) to produce reference outputs
later consumed by processing/convert_teacher_outputs.py during the
distillation pipeline.

Modules:
    ollama_generate: Batch generation of teacher responses from local
        Ollama models with resilient HTTP/CLI fallback logic and rich
        progress display when available.
"""

__all__ = [
    "ollama_generate",
]
