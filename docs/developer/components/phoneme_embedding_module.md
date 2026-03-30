# Phoneme Embedding Module

**Created:** May 21, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\developer\components\phoneme_embedding_module.md #documentation #inference #memory_management #multimodal #pytorch #tokenization  
**Category:** Developer Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

date: 2025-05-21
responsible: @GitHubCopilot
Last updated: 2025-05-31
---

# Phoneme Embedding Module (Character-Based)

**Last Updated:** 2025-05-31  
**Responsible:** GitHub Copilot

## Overview

The Phoneme Embedding Module has been re-architected to operate on a **character basis** rather than traditional phonemes derived from G2P (Grapheme-to-Phoneme) conversion. This module is a collection of components responsible for:

1.  **Character Sequence Extraction:** Extracting sequences of characters directly from raw audio waveforms.
2.  **Character Tokenization:** Converting character sequences into token IDs suitable for embedding models.
3.  **Character Embedding:** Generating dense vector representations (embeddings) from character token IDs.
4.  **Speech Synthesis:** Generating audible speech from text strings or character sequences.

This shift to character-based processing simplifies the pipeline by removing the dependency on external G2P tools and allows for potentially more robust handling of out-of-vocabulary words or diverse pronunciations, as the models learn directly from characters present in the audio.

## Components

The module resides in `src/modules/phoneme_embedding/` and consists of the following key Python files:

### 1. `config.py`

- **Purpose:** Defines the `PhonemeEmbeddingConfig` dataclass.
- **Details:** This configuration class centralizes settings for all components within the module, including:
  - Paths or identifiers for pre-trained models used (e.g., Hugging Face model names for character extraction and speech synthesis).
  - Model-specific parameters like embedding dimensions, vocabulary sizes (for character sets), maximum character sequence lengths, and target sample rates.
  - Default values are provided, typically pointing to suitable Hugging Face models like `facebook/wav2vec2-base-960h` for character extraction and `microsoft/speecht5_tts` for synthesis.
- **Usage:** Instances of `PhonemeEmbeddingConfig` are passed to other components during their initialization to ensure consistent behavior and easy configuration management.

### 2. `phoneme_extractor.py`

- **Class:** `PhonemeExtractor`
- **Purpose:** Extracts a sequence of characters from an audio waveform.
- **Underlying Model:** Typically utilizes a pre-trained speech recognition model capable of outputting character sequences, such as Hugging Face's Wav2Vec2 (`facebook/wav2vec2-base-960h` or similar). The specific model is defined in `PhonemeEmbeddingConfig`.
- **Input:** Raw audio waveform (as a PyTorch tensor or NumPy array) and its original sample rate.
- **Output:** A list of strings, where each string is a character.
- **Memory Consideration:** Loads a significant pre-trained model. Memory usage depends on the chosen model.

### 3. `phoneme_embedder.py`

- **Classes:**
  - `PhonemeTokenizer` (Character Tokenizer)
  - `PhonemeEmbedder` (Character Embedder)
- **`PhonemeTokenizer`:**
  - **Purpose:** Converts lists of characters into sequences of token IDs and vice-versa.
  - **Details:** Manages a character vocabulary (can be predefined or derived). It handles padding and truncation to ensure fixed-length input for the embedder. The vocabulary is implicitly defined by the character set the chosen Hugging Face models (extractor/synthesizer) operate on, or can be explicitly managed.
- **`PhonemeEmbedder`:**
  - **Purpose:** Converts sequences of character token IDs into dense vector embeddings.
  - **Underlying Model:** Typically a simple embedding layer (e.g., `torch.nn.Embedding`). The embedding dimension is specified in `PhonemeEmbeddingConfig`.
  - **Input:** A batch of character token ID sequences.
  - **Output:** A batch of character embedding sequences (PyTorch tensors).
- **Memory Consideration:** The embedding layer itself is usually small, but the overall memory depends on batch size and sequence length.

### 4. `phoneme_to_sound.py`

- **Class:** `PhonemeToSoundSynthesizer`
- **Purpose:** Synthesizes audible speech from input text or a sequence of characters.
- **Underlying Model:** Utilizes a pre-trained Text-to-Speech (TTS) model, such as Hugging Face's SpeechT5 (`microsoft/speecht5_tts`). The specific model and associated vocoder (e.g., `microsoft/speecht5_hifigan`) are defined in `PhonemeEmbeddingConfig`.
- **Input:**
  - A string of text.
  - OR a list of characters.
- **Output:** A NumPy array representing the audio waveform.
- **Memory Consideration:** Loads a significant pre-trained TTS model and potentially a vocoder model. Memory usage is a key concern and depends on the chosen models.

## Integration and Usage

- **Audio Processing (`src/data/preprocessing/audio.py`):** The `AudioProcessor` class uses `PhonemeExtractor` to get character sequences from audio and `PhonemeEmbedder` to convert these characters into embeddings if requested (`output_type="features"`).
- **Speech Synthesis Pipeline (`src/inference/pipelines/speech_synthesis_pipeline.py`):** The `SpeechSynthesisPipeline` class uses `PhonemeToSoundSynthesizer` to provide an end-to-end text/character-to-speech service.
- **Multimodal Pipeline (`src/pipelines/multimodal.py`):** The `MultiModalProcessor` integrates both the audio processing capabilities (via the main `AudioProcessor`) and the speech synthesis capabilities (via `SpeechSynthesisPipeline`), often using a shared `PhonemeEmbeddingConfig`.

## Configuration

All components are configured via the `PhonemeEmbeddingConfig` object. Key configurable parameters include:

- `extractor_model_path`: Hugging Face identifier for the character extraction model.
- `extractor_processor_path`: Hugging Face identifier for the processor associated with the extractor model.
- `tts_model_path`: Hugging Face identifier for the TTS model.
- `tts_vocoder_path`: Hugging Face identifier for the vocoder model.
- `sample_rate`: Target audio sample rate (e.g., 16000 Hz).
- `embedding_dim`: Dimension for character embeddings.
- `max_char_len`: Maximum length for character sequences.

## Memory and Performance

- The choice of Hugging Face models for character extraction (Wav2Vec2) and speech synthesis (SpeechT5) significantly impacts memory usage and performance.
- These models are powerful but can be resource-intensive. Efforts should be made to use quantized versions or apply other optimization techniques if targeting severely constrained hardware.
- The `PhonemeEmbeddingConfig` allows for specifying different model versions, which can be leveraged for performance tuning.

## Future Considerations

- Exploration of even more lightweight models for character extraction and synthesis.
- Finer-grained control over character vocabularies if needed.
- Advanced error handling and fallback mechanisms within each component.
