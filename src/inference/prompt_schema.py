#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #inference #multimodal #python #source_code #src/inference/prompt_schema.py
**Category:** Source Code
**Status:** Active
"""









# Prompt Schema

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #inference #multimodal #python #source_code #src/inference/prompt_schema.py
# Category:** Source Code
# Status:** Active

"""
Prompt schema and interface definitions for ImpressionCore-b1 inference engine.

Defines the unified prompt structure for text, image, and metadata fields.
"""
from typing import Any


def create_prompt(text: str | None = None, image: Any | None = None, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Create a unified prompt dictionary for multimodal inference.

    Args:
        text (Optional[str]): Text prompt (can be None).
        image (Optional[Any]): Image data (can be None, type depends on pipeline).
        metadata (Optional[Dict[str, Any]]): Additional metadata (user, context, etc).

    Returns:
        Dict[str, Any]: Unified prompt dictionary.
    """
    return {
        "text": text,
        "image": image,
        "metadata": metadata or {}
    }

# Example interface for prompt validation/extension
def validate_prompt(prompt: dict[str, Any]) -> bool:
    """
    Validate the prompt structure.

    Args:
        prompt (Dict[str, Any]): Prompt dictionary.

    Returns:
        bool: True if valid, False otherwise.
    """
    return "text" in prompt or "image" in prompt
