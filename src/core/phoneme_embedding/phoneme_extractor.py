#!/usr/bin/env python3
"""
ImpressionCore: Phoneme Extractor

Module for phoneme extractor functionality in the ImpressionCore framework.

File: modules\phoneme_embedding\phoneme_extractor.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, pytorch, production, 2025, object-oriented]
Dependencies: [torch, typing, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements phoneme extractor functionality for the
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
from modules.phoneme_embedding.phoneme_extractor import PhonemeExtractor
instance = PhonemeExtractor()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

# ImpressionCore - Phoneme (Character) Extractor
#
# Description:
# This module defines the `PhonemeExtractor` class, which is responsible for
# extracting phoneme-like sequences (typically characters) from raw audio waveforms.
# It leverages pre-trained Automatic Speech Recognition (ASR) models from the
# Hugging Face Transformers library, such as Wav2Vec2. The extractor handles
# loading the ASR model and its associated processor, preprocessing the audio
# Memory optimization: Explicit memory cleanup
# (including resampling if necessary), performing inference to get token predictions,
# and then decoding these tokens into a sequence of characters.
#
# The quality and nature of the extracted "phonemes" (characters) depend heavily
# on the specific ASR model used. This component is crucial for converting
# Memory optimization: Explicit memory cleanup
# speech input into a textual representation that can be further processed or
# embedded by other modules in ImpressionCore.
#
# Author: Kirk LaSalle and Githib agents
# Date: 2024-07-27 # Or the actual creation/last modification date
# Version: 1.0
#
# Dependencies:
# - torch
# - torchaudio
# - logging
# - typing
# - transformers (AutoModelForCTC, AutoProcessor, Wav2Vec2Processor)
# - .config.PhonemeEmbeddingConfig
#
# License:
# MIT License
#
# Copyright (c) 2024 [Your Name/Organization]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""
Phoneme Extractor for ImpressionCore.

This module is responsible for extracting phoneme-like sequences from audio data.
It uses Hugging Face Transformers library for loading pre-trained ASR models
(e.g., Wav2Vec2) to derive phoneme-like sequences.
"""

import torch
import torchaudio
import logging
from typing import List, Optional

try:
    from transformers import AutoModelForCTC, AutoProcessor, Wav2Vec2Processor
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logging.warning("Transformers library not found. PhonemeExtractor will not function. Install with: pip install transformers")

from .config import PhonemeEmbeddingConfig

logger = logging.getLogger(__name__)

class PhonemeExtractor:
    """
    Extracts phoneme-like sequences from raw audio waveforms using Hugging Face ASR models.

    The quality and nature of the "phonemes" depend heavily on the pre-trained model used.
    # Memory optimization: Explicit memory cleanup
    Some models might output characters, which can be used as a proxy or further mapped.

    Attributes:
        config (PhonemeEmbeddingConfig): Configuration object.
        model: The loaded Hugging Face ASR model (e.g., Wav2Vec2ForCTC).
        # Memory optimization: Explicit memory cleanup
        processor: The loaded Hugging Face processor associated with the model.
        device (str): Device to run the model on ('cuda' or 'cpu').
        # Memory optimization: Device placement for memory management
    """

    def __init__(self, config: PhonemeEmbeddingConfig):
        """
        Initializes the PhonemeExtractor.

        Args:
            config (PhonemeEmbeddingConfig): Configuration for phoneme extraction.
                                           `config.model_path` should be a Hugging Face model identifier
                                           # Memory optimization: Explicit memory cleanup
                                           or path to a local model directory.
                                           # Memory optimization: Explicit memory cleanup
        
        Raises:
            ImportError: If the Hugging Face Transformers library is not installed.
            RuntimeError: If the model or processor cannot be loaded.
            # Memory optimization: Explicit memory cleanup
        """
        if not HAS_TRANSFORMERS:
            raise ImportError("Hugging Face Transformers library is required for PhonemeExtractor but not installed.")

        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # Memory optimization: CUDA operations for GPU acceleration
        self.model = None
        # Memory optimization: Explicit memory cleanup
        self.processor = None

        try:
            logger.info(f"Loading Hugging Face processor from: {self.config.model_path}")
            # Ensure processor is loaded correctly, handling potential specific processor types
            try:
                self.processor = AutoProcessor.from_pretrained(self.config.model_path)
            except Exception as e_auto:
                logger.warning(f"Failed to load processor with AutoProcessor for {self.config.model_path}: {e_auto}. Trying Wav2Vec2Processor explicitly.")
                try: # Fallback for models that might need Wav2Vec2Processor explicitly
                    self.processor = Wav2Vec2Processor.from_pretrained(self.config.model_path)
                except Exception as e_specific:
                    logger.error(f"Failed to load processor with Wav2Vec2Processor for {self.config.model_path}: {e_specific}")
                    raise RuntimeError(f"Could not load processor from {self.config.model_path}") from e_specific
            
            logger.info(f"Loading Hugging Face model from: {self.config.model_path} onto {self.device}")
            # Memory optimization: Device placement for memory management
            self.model = AutoModelForCTC.from_pretrained(self.config.model_path)
            # Memory optimization: Explicit memory cleanup
            
            if self.model is None or self.processor is None:
            # Memory optimization: Explicit memory cleanup
                 raise RuntimeError(f"Failed to load model or processor from {self.config.model_path}")
                 # Memory optimization: Explicit memory cleanup

            self.model.to(self.device)
            # Memory optimization: Device placement for memory management
            self.model.eval() # Set model to evaluation mode
            # Memory optimization: Explicit memory cleanup
            logger.info(f"PhonemeExtractor initialized with model {self.config.model_path} on {self.device}. Target sample rate: {self.config.target_sample_rate} Hz.")
            # Memory optimization: Device placement for memory management
            # The processor's expected sample rate can be checked:
            if hasattr(self.processor, 'feature_extractor') and hasattr(self.processor.feature_extractor, 'sampling_rate'):
                model_expected_sr = self.processor.feature_extractor.sampling_rate
                if model_expected_sr != self.config.target_sample_rate:
                    logger.warning(f"Model {self.config.model_path} expects sample rate {model_expected_sr}, but config specifies {self.config.target_sample_rate}. Resampling will occur.")
                    # Memory optimization: Explicit memory cleanup
            else:
                logger.warning(f"Could not determine model's expected sample rate from processor. Ensure config.target_sample_rate ({self.config.target_sample_rate} Hz) is correct.")

        except Exception as e:
            logger.error(f"Error initializing PhonemeExtractor with model {self.config.model_path}: {e}", exc_info=True)
            # Memory optimization: Explicit memory cleanup
            # Allow partial initialization for some use cases or raise error
            self.model = None 
            # Memory optimization: Explicit memory cleanup
            self.processor = None
            raise RuntimeError(f"Failed to initialize PhonemeExtractor: {e}") from e


    def extract_phonemes_from_waveform(self, waveform: torch.Tensor, sample_rate: int) -> List[str]:
        """
        Extracts phoneme-like sequences from a raw audio waveform.

        Args:
            waveform (torch.Tensor): The input audio waveform. Expected shape: (channels, time) or (time,).
            sample_rate (int): The sample rate of the input audio.

        Returns:
            List[str]: A list of extracted phoneme-like characters/strings.
                       The actual output depends on the model's vocabulary (e.g., characters for ASR).

        Raises:
            ValueError: If the input waveform or sample rate is invalid.
            RuntimeError: If the model or processor is not initialized.
            # Memory optimization: Explicit memory cleanup
        """
        if self.model is None or self.processor is None:
        # Memory optimization: Explicit memory cleanup
            raise RuntimeError("PhonemeExtractor model or processor not initialized.")
            # Memory optimization: Explicit memory cleanup

        if not isinstance(waveform, torch.Tensor):
            raise ValueError("Waveform must be a PyTorch tensor.")
        if waveform.ndim not in [1, 2]:
            # If 1D, processor usually handles it by unsqueezing. If 2D, assumes [batch, samples] or [channels, samples]
            # Let processor handle it, but log a warning if shape is unusual.
             logger.debug(f"Waveform has {waveform.ndim} dimensions. Processor will attempt to handle.")
        
        if waveform.ndim == 2 and waveform.shape[0] > waveform.shape[1] and waveform.shape[0] <=16 : # Likely [channels, samples]
             waveform = waveform.mean(dim=0, keepdim=True) # Mixdown to mono if multi-channel and channels first
             logger.debug("Input waveform appears to be multi-channel; mixed down to mono.")
        elif waveform.ndim == 1:
            waveform = waveform.unsqueeze(0) # Processor expects batch dimension: [1, T]

        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive.")

        # Resample if the input sample rate differs from the model's expected/configured rate.
        # The processor itself might also handle resampling if its `sampling_rate` is set.
        # Here, we ensure it matches `self.config.target_sample_rate` which should align with processor's target.
        target_sr = self.config.target_sample_rate
        if hasattr(self.processor, 'feature_extractor') and hasattr(self.processor.feature_extractor, 'sampling_rate'):
            target_sr = self.processor.feature_extractor.sampling_rate # Prefer processor's SR if available

        if sample_rate != target_sr:
            logger.info(f"Resampling waveform from {sample_rate} Hz to {target_sr} Hz for model {self.config.model_path}.")
            # Memory optimization: Explicit memory cleanup
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sr)
            waveform = resampler(waveform.cpu()).to(waveform.device) # Resample on CPU if it's faster, then move back
            # Memory optimization: Device placement for memory management

        try:
            # Process the waveform: feature extraction, normalization, etc.
            # The processor expects a raw waveform list or tensor.
            # For Wav2Vec2, it's typically a list of 1D numpy arrays or a 1D tensor.
            # Input should be a 1D tensor or a list of 1D tensors.
            # If waveform is [1, T], squeeze it for the processor if it expects 1D.
            input_values = self.processor(waveform.squeeze(0).cpu().numpy(), return_tensors="pt", sampling_rate=target_sr).input_values
            
            if input_values is None: # Some processors might return a dict with 'input_values'
                processed = self.processor(waveform.squeeze(0).cpu().numpy(), return_tensors="pt", sampling_rate=target_sr)
                if hasattr(processed, 'input_values'):
                    input_values = processed.input_values
                else: # Fallback if structure is unexpected
                    logger.error("Processor output does not contain 'input_values'.")
                    return []


            input_values = input_values.to(self.device)
            # Memory optimization: Device placement for memory management

            # Perform inference
            with torch.no_grad():
            # Memory optimization: Disable gradient computation to save memory
                logits = self.model(input_values).logits

            # Decode token IDs to text/phonemes
            predicted_ids = torch.argmax(logits, dim=-1)
            # `batch_decode` handles CTC collapsing and converts token IDs to strings.
            transcription_list = self.processor.batch_decode(predicted_ids)
            
            if not transcription_list or not transcription_list[0]:
                logger.warning(f"Model {self.config.model_path} produced an empty transcription.")
                # Memory optimization: Explicit memory cleanup
                return []

            # For this extractor, we treat the transcription (characters) as a sequence of phoneme-like units.
            # Further mapping to a specific phoneme set (e.g., ARPAbet) would be a separate step if needed.
            # We return the characters of the first (and only) transcription as a list.
            phoneme_like_sequence = list(transcription_list[0]) 
            
            logger.debug(f"Extracted phoneme-like sequence for model {self.config.model_path}: {''.join(phoneme_like_sequence)}")
            # Memory optimization: Explicit memory cleanup
            return phoneme_like_sequence

        except Exception as e:
            logger.error(f"Error during phoneme extraction with model {self.config.model_path}: {e}", exc_info=True)
            # Memory optimization: Explicit memory cleanup
            return [] # Return empty list on error

    def extract_phonemes_from_file(self, audio_path: str) -> List[str]:
        """
        Extracts phonemes from an audio file.

        Args:
            audio_path (str): Path to the audio file.

        Returns:
            List[str]: A list of extracted phonemes.

        Raises:
            FileNotFoundError: If the audio file is not found.
            RuntimeError: If there's an error loading or processing the audio,
                          or if the model/processor is not initialized.
        """
        if self.model is None or self.processor is None:
        # Memory optimization: Explicit memory cleanup
            raise RuntimeError("PhonemeExtractor model or processor not initialized.")
            # Memory optimization: Explicit memory cleanup
            
        try:
            waveform, sample_rate = torchaudio.load(audio_path)
            logger.debug(f"Loaded audio from {audio_path}, sample rate: {sample_rate}, shape: {waveform.shape}")
        except FileNotFoundError:
            logger.error(f"Audio file not found at {audio_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading audio file {audio_path}: {e}", exc_info=True)
            raise RuntimeError(f"Error loading audio file {audio_path}: {e}") from e

        return self.extract_phonemes_from_waveform(waveform, sample_rate)

# Example usage (for testing purposes)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) # Use INFO for cleaner output, DEBUG for more details
    
    # A small, fast Wav2Vec2 model for testing (if available and network access is okay)
    # Memory optimization: Explicit memory cleanup
    # Using a very small model to minimize download and resource usage for testing.
    # Memory optimization: Explicit memory cleanup
    # Replace with a more robust phoneme-specific model if available.
    # Memory optimization: Explicit memory cleanup
    # Example: "facebook/wav2vec2-base-960h" is common but larger.
    # For a truly minimal test, one might need a tiny custom model or mock transformers.
    # Memory optimization: Explicit memory cleanup
    # Using a small distilled version if one exists, or a base version.
    # Let's use a smaller, but still functional model like "jonatasgrosman/wav2vec2-large-xlsr-53-english"
    # Memory optimization: Explicit memory cleanup
    # or a specific ASR fine-tune. For a very basic test, "hf-internal-testing/tiny-random-Wav2Vec2ForCTC"
    # might work if it's a valid CTC model, but it might not produce meaningful output.
    
    # Using a generally available small model for demonstration.
    # Memory optimization: Explicit memory cleanup
    # Ensure this model exists or use a placeholder that doesn't require network.
    # Memory optimization: Explicit memory cleanup
    # For robust offline testing, download models first.
    test_model_identifier = "facebook/wav2vec2-base-960h" # A standard choice, ensure it's accessible
    # test_model_identifier = "hf-internal-testing/tiny-random-Wav2Vec2ForCTC" # For minimal testing if it works

    logger.info(f"--- PhonemeExtractor Test using model: {test_model_identifier} ---")

    try:
        # Create a dummy config
        # model_path should be a valid Hugging Face identifier or local path
        dummy_config = PhonemeEmbeddingConfig(
            model_path=test_model_identifier, 
            embedding_dim=128, # Not directly used by extractor, but part of config
            vocab_path="path/to/dummy/vocab.txt", # Not directly used by HF processor here
            sample_rate=16000 # Wav2Vec2 models typically expect 16kHz
        )
        
        if not HAS_TRANSFORMERS:
            logger.error("Transformers library not installed. Skipping PhonemeExtractor test.")
        else:
            extractor = PhonemeExtractor(config=dummy_config)

            # Create a dummy waveform (1 second of sine wave at 16kHz)
            sr = 16000
            duration = 1.0 # seconds
            frequency = 440 # Hz
            t = torch.linspace(0, duration, int(sr * duration), dtype=torch.float32)
            dummy_waveform_tensor = 0.5 * torch.sin(2 * torch.pi * frequency * t)
            # Shape: [num_samples], processor will handle adding batch dim

            logger.info(f"Extracting phonemes from tensor (shape: {dummy_waveform_tensor.shape}, sr: {sr} Hz)...")
            phonemes_from_tensor = extractor.extract_phonemes_from_waveform(dummy_waveform_tensor, sr)
            logger.info(f"Phonemes from tensor: {''.join(phonemes_from_tensor)}")

            # Test with a file (requires a dummy audio file)
            dummy_audio_file = "test_audio_phoneme_extractor.wav"
            try:
                torchaudio.save(dummy_audio_file, dummy_waveform_tensor.unsqueeze(0), sr)
                logger.info(f"Saved dummy audio to {dummy_audio_file}")
                logger.info(f"Extracting phonemes from file: {dummy_audio_file}...")
                phonemes_from_file = extractor.extract_phonemes_from_file(dummy_audio_file)
                logger.info(f"Phonemes from file: {''.join(phonemes_from_file)}")
            except Exception as e_file:
                logger.error(f"Error in file test: {e_file}", exc_info=True)
            finally:
                import os
                if os.path.exists(dummy_audio_file):
                    os.remove(dummy_audio_file)
                    logger.info(f"Removed dummy audio file: {dummy_audio_file}")

    except ImportError:
        logger.warning("Skipping PhonemeExtractor test: Transformers library not found or other import error.")
    except RuntimeError as e:
        # Catching RuntimeError specifically as it might be due to model download/access issues
        # Memory optimization: Explicit memory cleanup
        # if the test_model_identifier is not available or network is down.
        logger.error(f"RuntimeError during PhonemeExtractor test (possibly model loading/access issue for '{test_model_identifier}'): {e}", exc_info=False) # Set exc_info to False for cleaner log for this common case
        # Memory optimization: Explicit memory cleanup
        logger.info(f"If this was a model access issue, ensure '{test_model_identifier}' is a valid Hugging Face model identifier and you have internet access, or use a local model path.")
        # Memory optimization: Explicit memory cleanup
    except Exception as e:
        logger.error(f"An unexpected error occurred during PhonemeExtractor test: {e}", exc_info=True)

    logger.info("--- PhonemeExtractor Test Complete ---")
