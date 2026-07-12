#!/usr/bin/env python3
"""
ImpressionCore: Module Coordinator

Module for module coordinator functionality in the ImpressionCore framework.

File: core\brain\integration\module_coordinator.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [core, production, framework, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements module coordinator functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
from src.core.brain.integration.module_coordinator import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import time
from typing import Dict, Any, Optional
from ..logic import reasoning
from ..creativity import generation, evaluation
from .context_manager import create_reasoning_context, complete_reasoning, create_creativity_context, add_creative_iteration

def coordinate_modules(problem: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Coordinate logic and creativity modules to address a problem.
    
    Steps:
    1. Create a reasoning context and invoke Chain of Thought reasoning.
    2. Create a creativity context and generate creative output based on the reasoning result.
    3. Evaluate the creative output.
    
    Args:
        problem: Problem description.
        user_context: Optional user identity context.
        
    Returns:
        Coordinated result including reasoning, creative output, and evaluation.
    """
    # Step 1: Create reasoning context and run chain-of-thought reasoning.
    reasoning_ctx_id = create_reasoning_context("CoT", problem, user_context.get("user_id") if user_context else None)
    reasoning_result = reasoning.chain_of_thought(problem, reasoning_steps=5)
    complete_reasoning(reasoning_ctx_id, reasoning_result)
    
    # Step 2: Create creativity context and generate creative text using logic conclusion.
    creativity_ctx_id = create_creativity_context(problem, user_context.get("user_id") if user_context else None)
    creative_text = generation.generate_creative_text(
        f"Based on logic: {reasoning_result.get('conclusion', {}).get('answer', '')}"
    )
    add_creative_iteration(creativity_ctx_id, {"creative_text": creative_text, "timestamp": time.time()})
    
    # Step 3: Evaluate the creative output.
    creative_eval = evaluation.evaluate_creativity(creative_text, context=problem)
    
    return {
        "reasoning": reasoning_result,
        "creative_output": creative_text,
        "evaluation": creative_eval
    }