#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #inference #memory_management #python #source_code #src/inference/engine.py #tokenization
**Category:** Source Code
**Status:** Active
"""









# Engine

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #inference #memory_management #python #source_code #src/inference/engine.py #tokenization
# Category:** Source Code
# Status:** Active

"""
Minimal inference engine for ImpressionCore-b1.

Coordinates prompt processing, model inference, cache, and sampling.
"""
from typing import Any

from src.brainsim.brainsim3 import augment_prompt
from src.brainsim.memory.uks import retrieve_context
from src.data.tokenization.tokenizer import tokenize
from src.inference.cache import KVCacher
from src.inference.sampling import Sampler, SamplingParams
from src.models.wrapper import ModelWrapper


class InferenceEngine:
    """
    Main entry point for running inference in ImpressionCore-b1.

    Coordinates prompt processing, model inference, cache, and sampling.
    """
    def __init__(self, model_config: dict):
        self.model_wrapper = ModelWrapper(model_config)
        self.model_wrapper.load()
        self.tokenizer = tokenize
        self.cache = KVCacher()
        self.sampler = None  # Will be set per request

    def generate(self, prompt: dict[str, Any], sampling_params: dict) -> Any:
        """
        Run inference on a prompt with given sampling parameters.

        Args:
            prompt (Dict[str, Any]): Unified prompt (text, image, metadata).
            sampling_params (dict): Sampling configuration.

        Returns:
            Any: Model output (decoded text, etc).
        """
        # 1. Retrieve context from UKS
        context = retrieve_context(prompt)
        # 2. Augment prompt with BrainSimIII
        augmented_prompt = augment_prompt(prompt, context)
        # 3. Tokenize prompt
        tokenized = self.tokenizer(augmented_prompt)
        # 4. Check cache for prefix reuse (stub: use text as key)
        cache_key = str(tokenized.get('text_ids'))
        cached = self.cache.get(cache_key)
        if cached is not None:
            model_output = cached
        else:
            # 5. Run model forward
            model_output = self.model_wrapper.forward(tokenized)
            self.cache.set(cache_key, model_output)
        # 6. Sample output
        self.sampler = Sampler(SamplingParams(**sampling_params))
        sampled = self.sampler.sample(model_output)
        return sampled
