#!/usr/bin/env python3
"""
ImpressionCore: B3 Native Inference Loader

Loads the trained B3 Hope v1 model from F:\\ and provides a clean inference API.
This eliminates the Ollama dependency for text generation by running the B3 model
natively on the GTX 1050 Ti.

File: inference/b3_native_inference.py
Project: ImpressionCore
Created: 2026-07-01
Version: 1.0.0

Authors:
    - Kirk LaSalle <kirk@impressioncore.ai>
    - Antigravity AI Agent

Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
"""

import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

import torch
import torch.nn.functional as F

logger = logging.getLogger(__name__)


class B3NativeInference:
    """
    Native inference engine for ImpressionCore B3 models.
    
    Loads trained checkpoints from F:\\ drive and runs generation
    directly on the local GPU/CPU — no external LLM dependency.
    """

    def __init__(
        self,
        checkpoint_path: Optional[str] = None,
        config_path: Optional[str] = None,
        device: Optional[str] = None,
        max_vram_gb: float = 3.5,
    ):
        """
        Initialize the B3 native inference engine.

        Args:
            checkpoint_path: Path to model checkpoint (.pt/.pth). Defaults to B3 Hope v1.
            config_path: Path to model config JSON. Defaults to B3 Hope v1 config.
            device: Force device ('cuda', 'cpu'). Auto-detected if None.
            max_vram_gb: VRAM budget for GTX 1050 Ti safety.
        """
        self.max_vram_gb = max_vram_gb
        self.model = None
        self.config = None
        self.tokenizer = None
        self._device = None
        self._loaded = False

        # Resolve paths
        try:
            from core.config.data_paths import (
                B3_HOPE_V1_WEIGHTS, B3_HOPE_V1_CONFIG, get_best_b3_checkpoint
            )
            self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else B3_HOPE_V1_WEIGHTS
            self.config_path = Path(config_path) if config_path else B3_HOPE_V1_CONFIG
        except ImportError:
            default_ckpt = Path("F:/models/production/b3_hope_v1/impressioncore_b3_hope.pt")
            default_cfg = Path("F:/models/production/b3_hope_v1/config.json")
            self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else default_ckpt
            self.config_path = Path(config_path) if config_path else default_cfg

        # Resolve device
        if device:
            self._device = torch.device(device)
        elif torch.cuda.is_available():
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
            if vram_gb >= 2.0:
                self._device = torch.device("cuda")
                logger.info(f"Using CUDA: {torch.cuda.get_device_name(0)} ({vram_gb:.1f} GB)")
            else:
                self._device = torch.device("cpu")
                logger.warning(f"VRAM too low ({vram_gb:.1f} GB), using CPU")
        else:
            self._device = torch.device("cpu")
            logger.info("CUDA not available, using CPU")

    def load(self) -> bool:
        """Load model and tokenizer. Returns True on success."""
        if self._loaded:
            return True

        # Load config
        if not self.config_path.exists():
            logger.error(f"Config not found: {self.config_path}")
            return False

        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

        logger.info(f"B3 Config: {json.dumps(self.config, indent=2)}")

        # Build model from architecture
        try:
            from core.models.impressioncore_b3_architecture import (
                ImpressionCoreB3Model, B3Config
            )
        except ImportError:
            from src.core.models.impressioncore_b3_architecture import (
                ImpressionCoreB3Model, B3Config
            )

        b3_config = B3Config(**self.config)
        self.model = ImpressionCoreB3Model(b3_config)

        # Load trained weights
        if not self.checkpoint_path.exists():
            logger.error(f"Checkpoint not found: {self.checkpoint_path}")
            return False

        logger.info(f"Loading checkpoint: {self.checkpoint_path}")
        checkpoint = torch.load(
            self.checkpoint_path,
            map_location=self._device,
            weights_only=False,
        )

        # Handle different checkpoint formats
        if isinstance(checkpoint, dict):
            if 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            elif 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            else:
                state_dict = checkpoint
        else:
            state_dict = checkpoint

        # Remap legacy checkpoint keys if architecture has changed
        state_dict = self._remap_legacy_keys(state_dict)

        # Load with flexible key matching
        try:
            self.model.load_state_dict(state_dict, strict=True)
            logger.info("Weights loaded (strict mode)")
        except RuntimeError:
            missing, unexpected = self.model.load_state_dict(state_dict, strict=False)
            if missing:
                logger.warning(f"Missing keys: {len(missing)}")
            if unexpected:
                logger.warning(f"Unexpected keys: {len(unexpected)}")
            logger.info("Weights loaded (non-strict mode)")

        self.model.to(self._device)
        self.model.eval()

        param_count = sum(p.numel() for p in self.model.parameters())
        logger.info(f"Model loaded: {param_count:,} parameters on {self._device}")

        # Load tokenizer
        self._load_tokenizer()

        self._loaded = True
        return True

    @staticmethod
    def _remap_legacy_keys(state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remap checkpoint keys from the legacy AssemblyOfExperts structure
        to the current architecture.

        `AssemblyOfExperts` instances live nested inside the model, e.g.
        `layers.<n>.aoe.experts.<i>.<j>.*` and `layers.<n>.aoe.router.<j>.*`,
        so the remap must match on a suffix/anchor basis rather than requiring
        the key to start at `experts.`/`router.`.

        Legacy expert Sequential (3 submodules, no LayerNorm/Dropout):
            0: nn.Linear(embed_dim, expert_dim)
            1: nn.GELU()
            2: nn.Linear(expert_dim, embed_dim)

        Current expert Sequential (5 submodules):
            0: nn.LayerNorm(embed_dim)
            1: nn.Linear(embed_dim, expert_dim)
            2: nn.GELU()
            3: nn.Linear(expert_dim, embed_dim)
            4: nn.Dropout(dropout)

        Legacy router Sequential (3 submodules, no LayerNorm):
            0: nn.Linear(embed_dim, embed_dim)
            1: nn.GELU()
            2: nn.Linear(embed_dim, num_experts)

        Current router Sequential (4 submodules):
            0: nn.LayerNorm(embed_dim)
            1: nn.Linear(embed_dim, embed_dim)
            2: nn.GELU()
            3: nn.Linear(embed_dim, num_experts)

        In both cases, the legacy Linear-in (index 0) maps to the current
        Linear-in (index 1), and the legacy Linear-out (index 2) maps to the
        current Linear-out (index 3). The newly-inserted LayerNorm (index 0)
        has no legacy counterpart and is left at its module default (loaded
        via non-strict fallback).

        Args:
            state_dict: Raw checkpoint state dict, possibly using legacy
                `experts`/`router` submodule indices.

        Returns:
            A new state dict with legacy `experts.<i>.0.*` / `experts.<i>.2.*`
            and `router.0.*` / `router.2.*` keys (at any key depth) remapped
            to their current index-shifted equivalents. Non-matching keys
            pass through unchanged.
        """
        import re

        # Matches "...experts.<i>.<0|2>.<param>" or "...router.<0|2>.<param>"
        # anywhere in the key, capturing an optional prefix so nested paths
        # like "layers.5.aoe.experts.0.0.weight" are handled correctly.
        legacy_pattern = re.compile(
            r"^(?P<prefix>.*\b(?:experts\.\d+|router))\.(?P<sub>0|2)\.(?P<param>weight|bias)$"
        )
        legacy_to_current = {"0": "1", "2": "3"}

        # Legacy attention submodule was named `mla` (Multi-head Latent Attention);
        # it was renamed to `attention` on BrainInspiredTransformerLayer, with the
        # internal submodule names (feature_map/q_proj/k_proj/v_proj/out_proj)
        # unchanged. Matches "layers.<n>.mla." anywhere in the key.
        mla_pattern = re.compile(r"^(?P<prefix>.*\blayers\.\d+)\.mla\.(?P<rest>.+)$")

        remapped: Dict[str, Any] = {}
        remapped_count = 0
        mla_remapped_count = 0

        for key, value in state_dict.items():
            match = legacy_pattern.match(key)
            if match:
                prefix = match.group("prefix")
                current_sub_idx = legacy_to_current[match.group("sub")]
                param_name = match.group("param")
                new_key = f"{prefix}.{current_sub_idx}.{param_name}"
                remapped[new_key] = value
                remapped_count += 1
                continue

            mla_match = mla_pattern.match(key)
            if mla_match:
                new_key = f"{mla_match.group('prefix')}.attention.{mla_match.group('rest')}"
                remapped[new_key] = value
                mla_remapped_count += 1
                continue

            remapped[key] = value

        if remapped_count > 0:
            logger.info(
                f"Remapped {remapped_count} legacy AssemblyOfExperts/router keys "
                f"(old Linear indices 0/2 -> new indices 1/3)"
            )
        if mla_remapped_count > 0:
            logger.info(
                f"Remapped {mla_remapped_count} legacy 'mla' attention keys "
                f"to current 'attention' submodule name"
            )

        return remapped

    def _load_tokenizer(self):
        """Load GPT-2 tokenizer for B3 (vocab_size=50257)."""
        try:
            from transformers import GPT2Tokenizer
            self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            logger.info("GPT-2 tokenizer loaded")
        except ImportError:
            logger.warning("transformers not installed, tokenizer unavailable")
            self.tokenizer = None

    @torch.no_grad()
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 128,
        temperature: float = 0.7,
        top_k: int = 50,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1,
    ) -> Dict[str, Any]:
        """
        Generate text from a prompt using the B3 model.

        Args:
            prompt: Input text prompt.
            max_new_tokens: Maximum tokens to generate.
            temperature: Sampling temperature (lower = more deterministic).
            top_k: Top-K sampling parameter.
            top_p: Nucleus sampling threshold.
            repetition_penalty: Penalty for repeating tokens.

        Returns:
            Dict with 'text', 'tokens_generated', 'latency_ms', 'tokens_per_second'.
        """
        if not self._loaded:
            if not self.load():
                return {"text": "", "error": "Model not loaded"}

        if self.tokenizer is None:
            return {"text": "", "error": "Tokenizer not available"}

        start_time = time.time()

        # Encode prompt
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self._device)

        # Track generated token IDs for repetition penalty
        generated_ids = input_ids.clone()

        for step in range(max_new_tokens):
            # Trim to max context
            max_seq = self.config.get("max_seq_length", 4096)
            context = generated_ids[:, -max_seq:]

            # Forward pass
            outputs = self.model(input_ids=context)
            logits = outputs["logits"][:, -1, :]

            # Apply temperature
            logits = logits / max(temperature, 1e-8)

            # Apply repetition penalty
            if repetition_penalty != 1.0:
                for token_id in set(generated_ids[0].tolist()):
                    if logits[0, token_id] > 0:
                        logits[0, token_id] /= repetition_penalty
                    else:
                        logits[0, token_id] *= repetition_penalty

            # Top-K filtering
            if top_k > 0:
                top_k_vals, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < top_k_vals[:, [-1]]] = float("-inf")

            # Top-P (nucleus) filtering
            if top_p < 1.0:
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                mask = cumulative_probs - F.softmax(sorted_logits, dim=-1) >= top_p
                sorted_logits[mask] = float("-inf")
                logits = sorted_logits.scatter(1, sorted_indices, sorted_logits)

            # Sample
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

            generated_ids = torch.cat([generated_ids, next_token], dim=1)

            # Stop on EOS
            if next_token.item() == self.tokenizer.eos_token_id:
                break

        elapsed = time.time() - start_time
        tokens_generated = generated_ids.size(1) - input_ids.size(1)
        tps = tokens_generated / elapsed if elapsed > 0 else 0

        # Decode output
        output_text = self.tokenizer.decode(
            generated_ids[0, input_ids.size(1):],
            skip_special_tokens=True,
        )

        return {
            "text": output_text,
            "prompt": prompt,
            "tokens_generated": tokens_generated,
            "latency_ms": round(elapsed * 1000, 1),
            "tokens_per_second": round(tps, 1),
            "device": str(self._device),
            "model": str(self.checkpoint_path.name),
        }

    def get_status(self) -> Dict[str, Any]:
        """Return current engine status."""
        status = {
            "loaded": self._loaded,
            "device": str(self._device),
            "checkpoint": str(self.checkpoint_path),
            "checkpoint_exists": self.checkpoint_path.exists(),
            "config_exists": self.config_path.exists(),
            "tokenizer_available": self.tokenizer is not None,
        }
        if self._loaded and self.model:
            status["parameters"] = sum(p.numel() for p in self.model.parameters())
            if self._device.type == "cuda":
                status["vram_allocated_mb"] = round(
                    torch.cuda.memory_allocated() / 1024**2, 1
                )
        return status


def create_inference_engine(
    checkpoint: Optional[str] = None,
    device: Optional[str] = None,
) -> B3NativeInference:
    """Factory function to create and load a B3 inference engine."""
    engine = B3NativeInference(checkpoint_path=checkpoint, device=device)
    engine.load()
    return engine


class B3NativeLLMProvider:
    """
    Adapter exposing :class:`B3NativeInference` through the simple
    ``generate(prompt, **kwargs) -> str`` shape expected by agent0core's
    ``LLMTriadProvider`` protocol (see
    ``agent0core/integrations/impressioncore.py``).

    This lets the native B3 Hope v1 model be registered as an independent,
    additive LLM provider — alongside (not replacing) the existing
    ``UnifiedBrainTriad`` provider — so callers can opt into pure B3
    inference without the Left/Right/Colossus triad overhead.
    """

    def __init__(
        self,
        checkpoint_path: Optional[str] = None,
        device: Optional[str] = None,
        lazy: bool = True,
    ):
        """
        Args:
            checkpoint_path: Optional override for the B3 checkpoint path.
            device: Optional forced device ('cuda'/'cpu').
            lazy: If True (default), defers model load until first `generate()`
                call to keep process startup fast.
        """
        self._engine = B3NativeInference(checkpoint_path=checkpoint_path, device=device)
        if not lazy:
            self._engine.load()

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate text for *prompt* using the native B3 model.

        Args:
            prompt: Input text prompt.
            **kwargs: Forwarded to :meth:`B3NativeInference.generate`
                (max_new_tokens, temperature, top_k, top_p, repetition_penalty).

        Returns:
            The generated text (empty string on error, logged separately).
        """
        result = self._engine.generate(prompt, **kwargs)
        if "error" in result:
            logger.error(f"B3NativeLLMProvider generation failed: {result['error']}")
            return ""
        return result.get("text", "")

    def get_model_status(self) -> Dict[str, Any]:
        """Return engine status (mirrors UnifiedBrainTriad.get_model_status shape)."""
        return self._engine.get_status()

    def is_available(self) -> bool:
        """Whether the checkpoint/config exist on disk (does not force-load)."""
        return self._engine.checkpoint_path.exists() and self._engine.config_path.exists()
