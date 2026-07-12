"""Model loading & embedding extraction utilities for one-time evaluation.
Created: August 17, 2025
Author: GitHub Copilot
"""
from __future__ import annotations

import sys
from typing import Any

import torch
from torch import nn

from .config import CheckpointConfig

sys.path.append(r'd:/Projects/impressioncore/src')
from src.core.models.impressioncore_b3_architecture import ImpressionCoreB3Model
from src.core.models.unified_tokenizer_system import UnifiedTokenizerSystem

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")



class ImpressionCoreEncoder(nn.Module):
    def __init__(self, model, tokenizer_system):
        super().__init__()
        self.model = model
        self.tokenizer_system = tokenizer_system

    def encode_text(self, batch):
        embs = []
        for text in batch:
            emb = self.tokenizer_system.encode_for_inference(text)
            if emb is not None:
                embs.append(emb.squeeze(0).cpu())
            else:
                embs.append(torch.zeros(self.model.config.embed_dim))
        return torch.stack(embs)

def load_checkpoint(cfg: CheckpointConfig) -> nn.Module:
    """Load ImpressionCore model from checkpoint and expose encode_text(batch: List[str]) -> Tensor."""
    model = _load_model_from_checkpoint(cfg.path)
    tokenizer_system = _init_unified_tokenizer_system()
    return ImpressionCoreEncoder(model, tokenizer_system)

def _load_model_from_checkpoint(path: str) -> nn.Module:
    model = ImpressionCoreB3Model()
    raw = torch.load(path, map_location=DEVICE)
    state_dict = _extract_state_dict(raw)
    model.load_state_dict(state_dict, strict=False)
    model.to(DEVICE)
    model.eval()
    return model

def _init_unified_tokenizer_system() -> UnifiedTokenizerSystem:
    tokenizer_system = UnifiedTokenizerSystem()
    tokenizer_system.initialize_tokenizers()
    return tokenizer_system


def _extract_state_dict(raw):
    """Extract the model state dict from a checkpoint object, minimizing cognitive complexity."""
    if not isinstance(raw, dict):
        raise ValueError(f"Unsupported checkpoint object type: {type(raw)}")
    # Try common keys
    for k in ("model_state_dict", "state_dict", "model"):
        v = raw.get(k)
        if isinstance(v, dict):
            return v
    # Single-key dict
    if len(raw) == 1:
        only_key = next(iter(raw))
        v = raw[only_key]
        if isinstance(v, dict):
            return v
    # Flat dict of tensors
    if all(isinstance(v, torch.Tensor) for v in raw.values()):
        return raw
    raise ValueError("No valid state dict found in checkpoint.")


def normalize_embeddings(x: torch.Tensor) -> torch.Tensor:
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def embed_texts(model: Any, texts, normalize: bool = True):
    embs = model.encode_text(texts)
    if normalize:
        embs = normalize_embeddings(embs)
    return embs
