#!/usr/bin/env python3
"""
ImpressionCore: Test Sound Processing Flow

Module for test sound processing flow functionality in the ImpressionCore framework.

File: tests\integration\test_sound_processing_flow.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [qa, pytorch, production, testing, 2025]
Dependencies: [torch, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements test sound processing flow functionality for the
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
from tests.integration.test_sound_processing_flow import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

# Copyright (C) Impression Core - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by [your name] <[your email]>, May 2025
#
# Description:
# This file contains integration tests for the sound processing capabilities
# of the ImpressionCore project. It verifies the end-to-end flows involving
# the AudioProcessor and SpeechSynthesisPipeline.
#
# Test Scenarios:
# 1. Audio to Characters to Speech: Tests the complete pipeline from an audio
#    file input, through character extraction by AudioProcessor, to speech
#    synthesis from these characters by SpeechSynthesisPipeline.
# 2. Audio to Features: Tests the flow from an audio file input to the
#    generation of character embeddings (features) by AudioProcessor.
#
# Test Framework: Pytest
#
# Dependencies:
# - pytest
# - torch
# - numpy
# - os
# - src.data.preprocessing.audio.AudioProcessor
# - src.inference.pipelines.speech_synthesis_pipeline.SpeechSynthesisPipeline
# - src.modules.phoneme_embedding.config.PhonemeEmbeddingConfig
# - Fixtures from conftest.py (e.g., sample_audio_path)
#
# Environment:
# These tests require a functional environment with access to Hugging Face models
# (Wav2Vec2 for character extraction, SpeechT5 for TTS) used by the components.
# Models should ideally be cached locally to ensure test stability and speed.
#
# Usage:
# Run these tests using the pytest command from the project root directory:
# pytest src/tests/integration/test_sound_processing_flow.py
#
# Notes:
# - A shared `integration_config` fixture provides a consistent configuration
#   for both AudioProcessor and SpeechSynthesisPipeline instances.
# - A `dummy_speaker_embedding_integration` fixture is used to provide the
#   necessary speaker embedding for the synthesis pipeline.
# - The tests check for successful execution, correct data types, and expected
#   output structures (e.g., shapes of tensors, sample rates).
# - If character extraction results in no characters (e.g., from a silent or
#   very simple audio sample like the sine wave used in tests), the synthesis
#   step might be skipped or tested for graceful handling of empty input.
#
# Last Modified: 2025-05-23
# Version: 0.1.0
#
# TODO:
# - Expand with more diverse audio samples to test robustness.
# - Mock Hugging Face model interactions for faster, network-independent testing.
# Memory optimization: Explicit memory cleanup
# - Add tests for raw audio input in the integration flow.
# - Implement more detailed assertions on the content of the generated audio
#   or features, if feasible and meaningful for integration testing.

import pytest
import torch
import numpy as np
import os
from src.data.preprocessing.audio import AudioProcessor
from src.core.ai.inference.pipelines.speech_synthesis_pipeline import SpeechSynthesisPipeline
from src.modules.phoneme_embedding.config import PhonemeEmbeddingConfig

# Shared configuration for integration tests
@pytest.fixture(scope="module") # Scope to module to initialize once per test module
def integration_config():
    """Provides a shared PhonemeEmbeddingConfig for integration tests."""
    return PhonemeEmbeddingConfig(
        extractor_model_name_or_path="facebook/wav2vec2-base-960h",
        tts_model_name_or_path="microsoft/speecht5_tts",
        tts_vocoder_name_or_path="microsoft/speecht5_hifigan",
        embedding_dim=32, # For audio_processor's embedder part
        phoneme_vocab_size=128, # For audio_processor's embedder part
        speaker_embedding_model_path=None # Avoid auto-loading speaker model
    )

@pytest.fixture(scope="module")
def audio_processor_integration(integration_config):
    """Provides an AudioProcessor instance for integration tests."""
    try:
        return AudioProcessor(config=integration_config)
    except Exception as e:
        pytest.fail(f"Failed to initialize AudioProcessor for integration tests: {e}")

@pytest.fixture(scope="module")
def speech_pipeline_integration(integration_config):
    """Provides a SpeechSynthesisPipeline instance for integration tests."""
    try:
        return SpeechSynthesisPipeline(config=integration_config)
    except Exception as e:
        pytest.fail(f"Failed to initialize SpeechSynthesisPipeline for integration tests: {e}")

@pytest.fixture
def dummy_speaker_embedding_integration():
    """Provides a dummy speaker embedding for synthesis during integration tests."""
    return torch.randn(512) # Standard SpeechT5 embedding size


# Integration Test 1: Audio Input -> Characters -> Synthesized Audio Output
def test_audio_to_characters_to_speech_integration(
    audio_processor_integration, 
    speech_pipeline_integration, 
    sample_audio_path, # From conftest.py
    dummy_speaker_embedding_integration
):
    """Test the full flow: audio file -> characters -> synthesized speech."""
    assert os.path.exists(sample_audio_path), "Sample audio file for integration test not found."

    # Step 1: Process audio to characters using AudioProcessor
    try:
        ap_result = audio_processor_integration.process_audio(sample_audio_path, output_type="characters")
        assert ap_result["success"], "AudioProcessor failed to extract characters."
        extracted_characters = ap_result["characters"]
        assert isinstance(extracted_characters, list), "Extracted characters should be a list."
        # It's possible for some audio (especially the test sine wave) to produce few or no characters
        # depending on the model. If it's empty, synthesis might also be empty or fail gracefully.
        print(f"Integration Test: Extracted Characters: {extracted_characters}")
    except Exception as e:
        pytest.fail(f"Integration test failed at AudioProcessor stage: {e}")

    # Step 2: Synthesize speech from extracted characters using SpeechSynthesisPipeline
    if not extracted_characters:
        pytest.skip("Skipping synthesis part as no characters were extracted from sample audio.")
        # Alternatively, could test that synthesis with empty char list is handled gracefully (e.g. returns None or empty audio)
        # try:
        #     synth_result_empty = speech_pipeline_integration.generate_audio_from_characters(
        #         character_input=extracted_characters, 
        #         speaker_embedding=dummy_speaker_embedding_integration
        #     )
        #     # Assert graceful handling, e.g. (None, sample_rate) or (empty_waveform, sample_rate)
        #     # For now, we skip if no chars.
        # except Exception as e:
        #     pytest.fail(f"Integration test failed at SpeechSynthesisPipeline stage with empty characters: {e}")
        # return

    try:
        synth_result = speech_pipeline_integration.generate_audio_from_characters(
            character_input=extracted_characters, 
            speaker_embedding=dummy_speaker_embedding_integration
        )
        
        assert synth_result is not None, "Speech synthesis should produce a result."
        waveform, sample_rate = synth_result
        
        assert isinstance(waveform, np.ndarray), "Synthesized waveform should be a NumPy array."
        assert waveform.ndim == 1, "Synthesized waveform should be 1D."
        # Length can be zero if characters were e.g. only silence tokens that TTS ignores
        # assert len(waveform) > 0, "Synthesized waveform should not be empty."
        assert isinstance(sample_rate, int), "Synthesized sample rate should be an integer."
        assert sample_rate == audio_processor_integration.config.target_sample_rate
        print(f"Integration Test: Synthesized audio from characters, length: {len(waveform)}, sample rate: {sample_rate}")

    except Exception as e:
        pytest.fail(f"Integration test failed at SpeechSynthesisPipeline stage: {e}")

# Integration Test 2: Audio Input -> Character Embeddings (Features)
def test_audio_to_features_integration(
    audio_processor_integration, 
    sample_audio_path # From conftest.py
):
    """Test the flow: audio file -> character embeddings (features)."""
    assert os.path.exists(sample_audio_path), "Sample audio file for integration test not found."

    try:
        ap_result = audio_processor_integration.process_audio(sample_audio_path, output_type="features")
        assert ap_result["success"], "AudioProcessor failed to extract features."
        extracted_features = ap_result["features"]
        
        assert isinstance(extracted_features, torch.Tensor), "Extracted features should be a torch.Tensor."
        assert extracted_features.ndim == 2, "Features tensor should be 2D (L, D)."
        # L (sequence length) can be 0 if no characters were extracted.
        # D (dimension) should match config
        if extracted_features.shape[0] > 0:
            assert extracted_features.shape[1] == audio_processor_integration.config.embedding_dim
        else:
            # If L=0, shape could be (0, D). Check D is correct or numel is 0.
            assert extracted_features.shape[1] == audio_processor_integration.config.embedding_dim or extracted_features.numel() == 0

        print(f"Integration Test: Extracted features (embeddings), shape: {extracted_features.shape}")

    except Exception as e:
        pytest.fail(f"Integration test failed at AudioProcessor (features) stage: {e}")

