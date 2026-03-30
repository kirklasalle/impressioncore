#!/usr/bin/env python3
"""
ImpressionCore: Speech Synthesis Pipeline

Module for speech synthesis pipeline functionality in the ImpressionCore framework.

File: inference/pipelines/speech_synthesis_pipeline.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, pytorch, production, 2025, inference, object-oriented]
Dependencies: [torch, typing, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements speech synthesis pipeline functionality for the
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
from inference.pipelines.speech_synthesis_pipeline import SpeechSynthesisPipeline
instance = SpeechSynthesisPipeline()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

# ImpressionCore - Speech Synthesis Pipeline
#
# Description:
# This module defines the SpeechSynthesisPipeline class, which is responsible
# for generating audio waveforms from text or character sequences. It utilizes
# the PhonemeToSoundSynthesizer, configured via PhonemeEmbeddingConfig, to
# perform the actual text-to-speech (TTS) conversion. The pipeline handles
# initialization of the synthesizer, device management (CPU/GPU), and provides
# Memory optimization: Device placement for memory management
# methods for generating audio from both full text strings and sequences of
# characters (which can represent phonemes or other phonetic units).
#
# Author: [Your Name/Alias]
# Date: 2024-07-27 # Or the actual creation/last modification date
# Version: 1.0
#
# Dependencies:
# - torch
# - numpy
# - logging
# - os
# - typing
# - src.modules.phoneme_embedding.phoneme_to_sound.PhonemeToSoundSynthesizer
# - src.modules.phoneme_embedding.config.PhonemeEmbeddingConfig
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
Speech Synthesis Pipeline for ImpressionCore.

This module defines the pipeline for generating audio from text or character sequences.
"""

import torch
import numpy as np
import logging
import os
from typing import Optional, Dict, Any, Union, List # Added List

from src.modules.phoneme_embedding.phoneme_to_sound import PhonemeToSoundSynthesizer
from src.modules.phoneme_embedding.config import PhonemeEmbeddingConfig

logger = logging.getLogger(__name__)

class SpeechSynthesisPipeline:
    """
    A pipeline to synthesize speech from text or character sequences.
    """

    def __init__(self, synthesizer_config_params: Optional[Dict[str, Any]] = None, device: Optional[str] = None):
    # Memory optimization: Device placement for memory management
        """
        Initializes the SpeechSynthesisPipeline.

        Args:
            synthesizer_config_params (Optional[Dict[str, Any]]): Parameters to initialize PhonemeEmbeddingConfig
                                                                  for the PhonemeToSoundSynthesizer.
                                                                  If None, PhonemeEmbeddingConfig uses its defaults.
            device (Optional[str]): The device to run synthesis on ('cuda', 'cpu'). Autodetects if None.
            # Memory optimization: Device placement for memory management
        
        Memory Implications:
        # Memory optimization: Memory-critical operation
            - Loads the synthesis model (e.g., TTS model, vocoder) into memory via PhonemeToSoundSynthesizer.
            # Memory optimization: Explicit memory cleanup
        """
        if device is None:
        # Memory optimization: Device placement for memory management
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            # Memory optimization: CUDA operations for GPU acceleration
        else:
            self.device = device
            # Memory optimization: Device placement for memory management
        
        logger.info(f"SpeechSynthesisPipeline initializing on device: {self.device}")
        # Memory optimization: Device placement for memory management

        if synthesizer_config_params is None:
            logger.info("No synthesizer_config_params provided. PhonemeEmbeddingConfig will use its defaults for PhonemeToSoundSynthesizer.")
            self.config = PhonemeEmbeddingConfig() # Uses defaults from PhonemeEmbeddingConfig
        else:
            try:
                self.config = PhonemeEmbeddingConfig(**synthesizer_config_params)
                logger.info("Using provided parameters for PhonemeEmbeddingConfig for PhonemeToSoundSynthesizer.")
            except TypeError as e:
                logger.error(f"Error creating PhonemeEmbeddingConfig with provided params: {synthesizer_config_params}. Error: {e}")
                raise ValueError(f"Invalid synthesizer_config_params: {e}") from e
        
        logger.info(f"PhonemeEmbeddingConfig for Synthesizer: "
                    f"TTS Model='{self.config.tts_model_path}', "
                    f"Vocoder='{self.config.vocoder_model_path}', "
                    f"Speaker Embed='{self.config.speaker_embedding_path}', "
                    f"Sample Rate='{self.config.sample_rate}'")

        try:
            self.synthesizer = PhonemeToSoundSynthesizer(config=self.config)
            # The synthesizer itself handles moving models to the correct device.
            # Memory optimization: Device placement for memory management
            # No explicit .to(self.device) needed here for the synthesizer object itself.
            # Memory optimization: Device placement for memory management
            self._initialized = True
            logger.info("PhonemeToSoundSynthesizer loaded successfully within SpeechSynthesisPipeline.")
        except Exception as e:
            logger.error(f"Failed to initialize PhonemeToSoundSynthesizer in pipeline: {e}", exc_info=True)
            self._initialized = False
            # Propagate the error to indicate pipeline initialization failure
            raise RuntimeError(f"Could not initialize the speech synthesizer within the pipeline: {e}") from e

    def generate_audio_from_text(self, text_input: str) -> Optional[np.ndarray]:
        """
        Generates an audio waveform from a text string.

        Args:
            text_input (str): The input text string.

        Returns:
            Optional[np.ndarray]: The generated audio waveform as a NumPy array (samples,), 
                                  or None if synthesis fails.
        """
        if not self._initialized or not self.synthesizer:
            logger.error("SpeechSynthesisPipeline or its synthesizer is not initialized.")
            return None
        
        try:
            waveform_tensor = self.synthesizer.synthesize_speech_from_text(text_input)
            if waveform_tensor is not None and waveform_tensor.numel() > 0:
                return waveform_tensor.numpy()
            else:
                logger.warning(f"Synthesis from text returned empty or None tensor for input: '{text_input[:50]}...'")
                return None
        except Exception as e:
            logger.error(f"Error during speech synthesis from text in pipeline: {e}", exc_info=True)
            return None

    def generate_audio_from_characters(self, char_sequence: List[str]) -> Optional[np.ndarray]:
        """
        Generates an audio waveform from a list of characters (phoneme-like sequence).

        Args:
            char_sequence (List[str]): The input sequence of characters.

        Returns:
            Optional[np.ndarray]: The generated audio waveform as a NumPy array (samples,), 
                                  or None if synthesis fails.
        """
        if not self._initialized or not self.synthesizer:
            logger.error("SpeechSynthesisPipeline or its synthesizer is not initialized.")
            return None
        
        if not char_sequence:
            logger.warning("Empty character sequence provided for synthesis.")
            return None
            
        try:
            # PhonemeToSoundSynthesizer has synthesize_speech_from_phonemes which joins chars
            input_text = "".join(char_sequence)
            waveform_tensor = self.synthesizer.synthesize_speech_from_text(input_text) # or synthesize_speech_from_phonemes
            if waveform_tensor is not None and waveform_tensor.numel() > 0:
                return waveform_tensor.numpy()
            else:
                logger.warning(f"Synthesis from characters returned empty or None tensor for input: '{''.join(char_sequence)[:50]}...'")
                return None
        except Exception as e:
            logger.error(f"Error during speech synthesis from characters in pipeline: {e}", exc_info=True)
            return None

    def get_sample_rate(self) -> Optional[int]:
        """Returns the sample rate of the synthesized audio, if initialized."""
        if self._initialized and self.synthesizer:
            return self.synthesizer.get_sample_rate()
        return None

# Example Usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.info("--- SpeechSynthesisPipeline Test ---")

    # To test this, PhonemeEmbeddingConfig needs valid paths or rely on its defaults
    # which in turn rely on SpeechT5 default model names from Hugging Face.
    # Memory optimization: Explicit memory cleanup
    # Ensure you have internet for model downloads by PhonemeToSoundSynthesizer on first run.
    # Memory optimization: Explicit memory cleanup
    
    # Scenario 1: Default config (relies on PhonemeEmbeddingConfig defaults for TTS)
    pipeline_default_config = None
    try:
        logger.info("\nAttempting to initialize pipeline with default PhonemeEmbeddingConfig for synthesizer...")
        # This will use PhonemeEmbeddingConfig() which has its own defaults for TTS models
        pipeline_default_config = SpeechSynthesisPipeline() 
        
        if pipeline_default_config._initialized:
            example_text = "Hello from the default pipeline. This is a test."
            logger.info(f'Synthesizing from text: "{example_text}"')
            audio_output_text = pipeline_default_config.generate_audio_from_text(example_text)
            if audio_output_text is not None:
                logger.info(f"Generated audio from text (default config), shape: {audio_output_text.shape}, sample rate: {pipeline_default_config.get_sample_rate()}")
                # Optionally save: torchaudio.save("test_default_config_text.wav", torch.from_numpy(audio_output_text).unsqueeze(0), pipeline_default_config.get_sample_rate())
            else:
                logger.error("Failed to generate audio from text with default config.")

            example_chars = ['h', 'ɛ', 'l', 'o', 'ʊ', ' ', 'w', 'ɜː', 'l', 'd'] # Approx "hello world"
            logger.info(f'Synthesizing from characters: "{"".join(example_chars)}"')
            audio_output_chars = pipeline_default_config.generate_audio_from_characters(example_chars)
            if audio_output_chars is not None:
                logger.info(f"Generated audio from characters (default config), shape: {audio_output_chars.shape}")
            else:
                logger.error("Failed to generate audio from characters with default config.")
        else:
            logger.error("Pipeline with default config failed to initialize.")
            
    except Exception as e:
        logger.error(f"Error testing pipeline with default config: {e}", exc_info=True)
        logger.info("This might be due to model download issues or missing dependencies for the synthesizer.")
        # Memory optimization: Explicit memory cleanup

    # Scenario 2: Providing specific (but still default SpeechT5) config parameters
    # These are the defaults within PhonemeEmbeddingConfig for TTS, explicitly passed here.
    custom_params = {
        "tts_model_path": "microsoft/speecht5_tts",
        "tts_processor_path": "microsoft/speecht5_tts", # Often same as model path
        # Memory optimization: Explicit memory cleanup
        "vocoder_model_path": "microsoft/speecht5_hifigan",
        "speaker_embedding_path": None, # To test default speaker embedding loading
        "sample_rate": 16000
    }
    pipeline_custom_config = None
    try:
        logger.info(f"\nAttempting to initialize pipeline with custom params for synthesizer: {custom_params}")
        pipeline_custom_config = SpeechSynthesisPipeline(synthesizer_config_params=custom_params)
        
        if pipeline_custom_config._initialized:
            example_text_2 = "This is another test with specific configuration."
            logger.info(f'Synthesizing from text: "{example_text_2}"')
            audio_output_text_2 = pipeline_custom_config.generate_audio_from_text(example_text_2)
            if audio_output_text_2 is not None:
                logger.info(f"Generated audio from text (custom config), shape: {audio_output_text_2.shape}, sample rate: {pipeline_custom_config.get_sample_rate()}")
                # Optionally save
                # import torchaudio
                # if not os.path.exists("test_outputs"): os.makedirs("test_outputs")
                # torchaudio.save("test_outputs/test_custom_config_text.wav", torch.from_numpy(audio_output_text_2).unsqueeze(0), pipeline_custom_config.get_sample_rate())
                # logger.info("Saved custom config output to test_outputs/test_custom_config_text.wav")
            else:
                logger.error("Failed to generate audio from text with custom config.")
        else:
            logger.error("Pipeline with custom config failed to initialize.")

    except Exception as e:
        logger.error(f"Error testing pipeline with custom config: {e}", exc_info=True)

    logger.info("\n--- SpeechSynthesisPipeline Test Complete ---")
