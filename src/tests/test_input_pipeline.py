#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #multimodal #python #source_code #src/tests/test_input_pipeline.py #testing
**Category:** Testing Framework
**Status:** Active
"""









# Test Input Pipeline

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #multimodal #python #source_code #src\\tests\\test_input_pipeline.py #testing
# Category:** Testing Framework
# Status:** Active

"""
test_input_pipeline.py
Test the input/output data flow between text encoder, vision/audio/video encoders, and the unified embedding layer.
"""
import os
import sys

import torch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.models.b2_multimodal.core.multimodal_embeddings import build_multimodal_embeddings
from src.models.b2_multimodal.encoders.audio_encoder import build_audio_encoder
from src.models.b2_multimodal.encoders.text_encoder import build_text_encoder
from src.models.b2_multimodal.encoders.video_encoder import build_video_encoder
from src.models.b2_multimodal.encoders.vision_encoder import build_vision_encoder

# Dummy config for all modules
config = {
    'vocab_size': 1000,
    'text_vocab_size': 1000,
    'embed_dim': 768,
    'vision_patch_dim': 256,
    'audio_feat_dim': 128,
    'video_feat_dim': 512,
    'sp_model_path': 'dummy.model',  # Replace with actual model path
    'max_seq_len': 32,
    'use_rope': True
}

def test_pipeline():
    import pytest
    if not os.path.exists(config['sp_model_path']):
        pytest.skip(f"SentencePiece model not found: {config['sp_model_path']}")
    # Instantiate encoders and embedding layer
    text_encoder = build_text_encoder(config)
    vision_encoder = build_vision_encoder(config)
    audio_encoder = build_audio_encoder(config)
    video_encoder = build_video_encoder(config)
    embedding_layer = build_multimodal_embeddings(config)

    # Dummy input data
    batch_size = 2
    seq_len = 32
    text_ids = torch.randint(0, config['vocab_size'], (batch_size, seq_len))
    vision_patches = torch.randn(batch_size, seq_len, config['vision_patch_dim'])
    audio_feats = torch.randn(batch_size, seq_len, config['audio_feat_dim'])
    video_feats = torch.randn(batch_size, seq_len, config['video_feat_dim'])
    modality_type = torch.randint(0, 4, (batch_size, seq_len))

    # Forward through encoders
    text_emb = text_encoder(text_ids)
    vision_encoder(vision_patches)
    audio_encoder(audio_feats)
    video_encoder(video_feats)

    # Forward through unified embedding layer
    inputs = {
        'text_emb': text_emb,
        'vision': vision_patches,
        'audio': audio_feats,
        'video': video_feats,
        'modality_type': modality_type
    }
    unified_emb = embedding_layer(inputs)
    print('Unified embedding shape:', unified_emb.shape)

if __name__ == '__main__':
    test_pipeline()
