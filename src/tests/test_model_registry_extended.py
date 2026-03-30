#!/usr/bin/env python3
"""Tests for extended model registry (b2 + helper)."""
import pytest

pytest.importorskip("core.models", reason="core.models not available in current path layout")
from core.models.registry import get_model, list_models


def test_b2_factory_available():
    models = list_models()
    assert 'b2_multimodal' in models


def test_get_b2_model_instantiates():
    payload = get_model('b2_multimodal', {'embed_dim': 64, 'num_layers': 1, 'num_heads': 2})
    assert isinstance(payload, dict)
    inst = payload['instance']
    cfg = payload['config']
    assert cfg['embed_dim'] == 64
    # Light forward smoke test with minimal fake embeddings
    import torch
    inputs = {
        'text': torch.randn(1, 64),
        'vision': torch.randn(1, 64),
        'audio': torch.randn(1, 64),
        'video': torch.randn(1, 64),
    }
    out = inst(inputs, output_modality='conversation', use_precomputed_embeddings=True)
    assert 'hidden_state' in out


def test_missing_model_keyerror():
    with pytest.raises(KeyError):
        get_model('nonexistent_model_foo')
