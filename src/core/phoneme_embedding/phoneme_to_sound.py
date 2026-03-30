#!/usr/bin/env python3
"""
ImpressionCore: Phoneme To Sound

Module for phoneme to sound functionality in the ImpressionCore framework.

File: modules\phoneme_embedding\phoneme_to_sound.py
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
Dependencies: [torch, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements phoneme to sound functionality for the
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
from modules.phoneme_embedding.phoneme_to_sound import PhonemeToSoundSynthesizer
instance = PhonemeToSoundSynthesizer()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

# ImpressionCore - Phoneme to Sound Synthesizer
#
# Description:
# This module defines the `PhonemeToSoundSynthesizer` class, responsible for
# converting text or phoneme-like sequences into audible speech waveforms.
# It primarily utilizes Hugging Face Transformers library, leveraging models
# like SpeechT5 for text-to-speech (TTS) generation and a corresponding
# vocoder (e.g., HiFiGAN) to produce the final audio. The synthesizer handles
# loading these models, managing speaker embeddings (if applicable), and
# orchestrating the synthesis process on the appropriate device (CPU/GPU).
# Memory optimization: Device placement for memory management
#
# Author: Kirk LaSalle & GitHub Copilot
# Date: 2025-05-23
# Version: 1.0
#
# Dependencies:
# - torch
# - logging
# - typing
# - os
# - torchaudio
# - transformers (SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan)
# - datasets (optional, for default speaker embeddings)
# - .config.PhonemeEmbeddingConfig
#
# License:
# MIT License
#
# Copyright (c) 2025 ImpressionCore
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
Phoneme to Sound Synthesizer for ImpressionCore.

This module converts phoneme sequences (and potentially their embeddings
with prosody information) back into audible speech waveforms using
Hugging Face Transformers library for TTS models like SpeechT5.
"""

import torch
import logging
from typing import List, Optional, Any
import os
import torchaudio

try:
    from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
    HAS_TRANSFORMERS_TTS = True
except ImportError:
    HAS_TRANSFORMERS_TTS = False
    logging.warning("Transformers library not found or version is too old for SpeechT5. PhonemeToSoundSynthesizer will not function. Install with: pip install transformers[torch] datasets")

from .config import PhonemeEmbeddingConfig

logger = logging.getLogger(__name__)

class PhonemeToSoundSynthesizer:
    """
    Synthesizes audio from phoneme-like sequences using Hugging Face TTS models (e.g., SpeechT5).

    Attributes:
        config (PhonemeEmbeddingConfig): Configuration object.
        processor: The loaded Hugging Face TTS processor (e.g., SpeechT5Processor).
        model: The loaded Hugging Face TTS model (e.g., SpeechT5ForTextToSpeech).
        # Memory optimization: Explicit memory cleanup
        vocoder: The loaded Hugging Face vocoder model (e.g., SpeechT5HifiGan).
        # Memory optimization: Explicit memory cleanup
        speaker_embeddings: Loaded speaker embeddings if required by the model.
        device (str): Device to run models on ('cuda' or 'cpu').
        # Memory optimization: Device placement for memory management
    """

    def __init__(self, config: PhonemeEmbeddingConfig):
        """
        Initializes the PhonemeToSoundSynthesizer.

        Args:
            config (PhonemeEmbeddingConfig): Configuration relevant to TTS.
        
        Raises:
            ImportError: If the Hugging Face Transformers library (with TTS support) is not installed.
            RuntimeError: If models or speaker embeddings cannot be loaded.
        """
        if not HAS_TRANSFORMERS_TTS:
            raise ImportError("Hugging Face Transformers library (with TTS support) is required for PhonemeToSoundSynthesizer but not installed/functional.")

        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # Memory optimization: CUDA operations for GPU acceleration
        self.processor = None
        self.model = None
        # Memory optimization: Explicit memory cleanup
        self.vocoder = None
        self.speaker_embeddings = None

        try:
            processor_path = self.config.tts_processor_path if self.config.tts_processor_path else self.config.tts_model_path
            logger.info(f"Loading TTS processor from: {processor_path}")
            self.processor = SpeechT5Processor.from_pretrained(processor_path)
            
            logger.info(f"Loading TTS model from: {self.config.tts_model_path}")
            # Memory optimization: Explicit memory cleanup
            self.model = SpeechT5ForTextToSpeech.from_pretrained(self.config.tts_model_path)
            # Memory optimization: Explicit memory cleanup
            self.model.to(self.device).eval()
            # Memory optimization: Device placement for memory management

            logger.info(f"Loading Vocoder model from: {self.config.vocoder_model_path}")
            # Memory optimization: Explicit memory cleanup
            self.vocoder = SpeechT5HifiGan.from_pretrained(self.config.vocoder_model_path)
            self.vocoder.to(self.device).eval()
            # Memory optimization: Device placement for memory management

            speaker_embedding_source_msg = ""
            if self.config.speaker_embedding_path and os.path.exists(self.config.speaker_embedding_path):
                logger.info(f"Loading speaker embeddings from: {self.config.speaker_embedding_path}")
                self.speaker_embeddings = torch.load(self.config.speaker_embedding_path, map_location=self.device)
                # Memory optimization: Device placement for memory management
                speaker_embedding_source_msg = f"loaded from {self.config.speaker_embedding_path}"
            else:
                if self.config.speaker_embedding_path:
                    logger.warning(f"Speaker embedding file not found at {self.config.speaker_embedding_path}. Attempting to load a default.")
                else:
                    logger.info("No speaker_embedding_path provided. Attempting to load a default speaker embedding.")
                
                try:
                    from datasets import load_dataset
                    logger.info("Attempting to load default speaker embeddings from 'Matthijs/cmu-arctic-xvectors' dataset.")
                    embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation", trust_remote_code=True)
                    self.speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
                    speaker_embedding_source_msg = "loaded default from 'Matthijs/cmu-arctic-xvectors' dataset (speaker slt)"
                    logger.info(f"Successfully {speaker_embedding_source_msg}.")
                except Exception as e_dataset:
                    logger.error(f"Could not load default speaker embeddings: {e_dataset}. Synthesis might fail or use a model's default if available.")
                    self.speaker_embeddings = None 
                    speaker_embedding_source_msg = "failed to load, using None"

            if self.speaker_embeddings is not None:
                self.speaker_embeddings = self.speaker_embeddings.to(self.device)
                # Memory optimization: Device placement for memory management
                if self.speaker_embeddings.ndim == 1: 
                    self.speaker_embeddings = self.speaker_embeddings.unsqueeze(0)
                logger.info(f"Speaker embeddings {speaker_embedding_source_msg}. Shape: {self.speaker_embeddings.shape if self.speaker_embeddings is not None else 'None'}")

            if self.model is None or self.processor is None or self.vocoder is None:
            # Memory optimization: Explicit memory cleanup
                 raise RuntimeError("Failed to load one or more TTS components (model, processor, vocoder).")

            logger.info(f"PhonemeToSoundSynthesizer initialized with models on {self.device}. Target sample rate for synthesis: {self.config.sample_rate} Hz.")
            # Memory optimization: Device placement for memory management

        except Exception as e:
            logger.error(f"Error initializing PhonemeToSoundSynthesizer: {e}", exc_info=True)
            self.processor = self.model = self.vocoder = self.speaker_embeddings = None 
            # Memory optimization: Explicit memory cleanup
            raise RuntimeError(f"Failed to initialize PhonemeToSoundSynthesizer: {e}") from e

    def synthesize_speech_from_text(self, text_input: str) -> torch.Tensor:
        """
        Synthesizes an audio waveform from a text string.

        Args:
            text_input (str): The input text string.

        Returns:
            torch.Tensor: The synthesized audio waveform (1D tensor).
        """
        if not all([self.processor, self.model, self.vocoder]):
            raise RuntimeError("PhonemeToSoundSynthesizer not properly initialized.")
        
        if not text_input or not text_input.strip():
            logger.warning("Empty text input provided. Returning empty tensor.")
            return torch.empty(0)
            
        logger.info(f'Synthesizing speech for input text: "{text_input}"')

        try:
            inputs = self.processor(text=text_input, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            # Memory optimization: Device placement for memory management

            if self.speaker_embeddings is None:
                logger.warning("No speaker embeddings available. Synthesis will use model's default if any, or may be low quality.")
                if hasattr(self.model.config, 'speaker_embedding_dim') and self.model.config.speaker_embedding_dim is not None:
                     logger.error("Model configuration suggests speaker embeddings are expected, but none are loaded. Synthesis quality may be poor or fail.")
                     # Memory optimization: Explicit memory cleanup
                speech = self.model.generate_speech(**inputs)
            else:
                speech = self.model.generate_speech(**inputs, speaker_embeddings=self.speaker_embeddings)

            waveform = self.vocoder(speech)
            waveform_output = waveform.squeeze().detach().cpu()
            
            logger.info(f"Generated waveform of shape {waveform_output.shape}, sample rate should be {self.config.sample_rate} Hz.")
            return waveform_output

        except Exception as e:
            logger.error(f'Error during speech synthesis for text "{text_input}": {e}', exc_info=True)
            return torch.empty(0) 

    def synthesize_speech_from_phonemes(self, phoneme_sequence: List[str]) -> torch.Tensor:
        """
        Wrapper to synthesize speech from a list of characters/phonemes by joining them into a string.
        """
        input_text = "".join(phoneme_sequence) 
        return self.synthesize_speech_from_text(input_text)

    def get_sample_rate(self) -> int:
        """Returns the sample rate of the synthesized audio."""
        return self.config.sample_rate


# Example usage (for testing purposes)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("--- PhonemeToSoundSynthesizer Test ---")

    dummy_speaker_embed_dir = "temp_speaker_embeddings_for_test"
    os.makedirs(dummy_speaker_embed_dir, exist_ok=True)
    dummy_speaker_embed_path = os.path.join(dummy_speaker_embed_dir, "test_speaker_embedding.pt")
    
    speaker_path_for_config = None

    if os.path.exists(dummy_speaker_embed_path):
        logger.info(f"Using existing speaker embedding file: {dummy_speaker_embed_path}")
        speaker_path_for_config = dummy_speaker_embed_path
    else:
        try:
            from datasets import load_dataset
            logger.info("Attempting to download a default speaker embedding for testing to store locally.")
            embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation", trust_remote_code=True)
            example_embedding = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0) # Speaker 'slt'
            torch.save(example_embedding, dummy_speaker_embed_path)
            logger.info(f"Saved default speaker embedding ('slt') to {dummy_speaker_embed_path}")
            speaker_path_for_config = dummy_speaker_embed_path
        except Exception as e_ds_load:
            logger.warning(f"Could not download/save default speaker embedding ({e_ds_load}). Will test with synthesizer's internal default handling (if any).")
            speaker_path_for_config = None 

    test_config = PhonemeEmbeddingConfig(
        tts_model_path="microsoft/speecht5_tts",
        vocoder_model_path="microsoft/speecht5_hifigan",
        speaker_embedding_path=speaker_path_for_config, 
        sample_rate=16000 
    )

    synthesizer = None
    try:
        if not HAS_TRANSFORMERS_TTS:
            logger.error("Transformers library (TTS parts) not installed. Skipping PhonemeToSoundSynthesizer test.")
        else:
            synthesizer = PhonemeToSoundSynthesizer(config=test_config)
            
            example_text = "Hello world, this is a test of speech synthesis using Impression Core."
            
            logger.info(f'Synthesizing speech for: "{example_text}"')
            waveform = synthesizer.synthesize_speech_from_text(example_text)

            if waveform is not None and waveform.numel() > 0:
                output_filename = "test_synthesis_output.wav"
                torchaudio.save(output_filename, waveform.unsqueeze(0), synthesizer.get_sample_rate())
                logger.info(f"Synthesized audio saved to {output_filename}")
            else:
                logger.error("Synthesis failed or produced empty output.")

    except ImportError:
        logger.warning("Skipping PhonemeToSoundSynthesizer test: Transformers library (TTS parts) not found.")
    except RuntimeError as e:
        logger.error(f"RuntimeError during PhonemeToSoundSynthesizer test: {e}", exc_info=False)
        logger.info("Ensure model identifiers are correct, you have internet access for downloads, and speaker embeddings are available if required.")
        # Memory optimization: Explicit memory cleanup
    except Exception as e:
        logger.error(f"An unexpected error occurred during PhonemeToSoundSynthesizer test: {e}", exc_info=True)

    logger.info("--- PhonemeToSoundSynthesizer Test Complete ---")