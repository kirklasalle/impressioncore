# Impressioncore B1 Sound Processing

**Created:** May 21, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\developer\impressioncore_b1_sound_processing.md #documentation #inference #memory_management #multimodal #tokenization #training  
**Category:** Developer Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

date: 2025-05-23
Last updated: 2025-05-31
Responsible: @GitHubCopilot
---

# Sound Processing Pipeline (Character-Based Implementation)

## 1. Overview

This document details the sound processing pipeline in ImpressionCore-b1, which currently focuses on a **character-based approach** for both audio input processing and speech generation. It integrates the `AudioProcessor` for converting speech to character sequences or embeddings, and the `SpeechSynthesisPipeline` for generating speech from text or character sequences. This serves as a foundation for future true phoneme-level understanding and synthesis.

## 2. Core Components

* **Audio Input Processor (`AudioProcessor`)**: Responsible for processing raw audio signals into character sequences or their corresponding embeddings. It internally uses components from the `PhonemeEmbeddingModule` for this.
  * Located at: `src/data/preprocessing/audio.py`
* **Speech Generation (`SpeechSynthesisPipeline`)**: Responsible for synthesizing audible speech from textual descriptions or character sequences. It also leverages components initially conceived for the `PhonemeEmbeddingModule`.
  * Located at: `src/inference/pipelines/speech_synthesis_pipeline.py`
* **Character Processing Components (formerly `PhonemeEmbeddingModule` parts)**: These are now integrated within the `AudioProcessor` and `SpeechSynthesisPipeline`.
  * `PhonemeExtractor`: Extracts character sequences from audio (e.g., using Wav2Vec2).
  * `PhonemeTokenizer`: Tokenizes character sequences.
  * `PhonemeEmbedder`: Converts tokenized characters into dense embeddings.
  * `PhonemeToSoundSynthesizer`: Synthesizes sound from processed text/characters (e.g., using SpeechT5 and HiFiGAN).
  * Located at: `src/modules/phoneme_embedding/`

## 3. Character-Based Processing Details

The "Phoneme Embedding Module" as a distinct, future component for *true phonemes* is still relevant. However, its initial concepts for character-level processing have been implemented and integrated directly into the `AudioProcessor` and `SpeechSynthesisPipeline`.

Refer to `docs/developer/components/phoneme_embedding_module.md` for the original design concepts, noting that character-level aspects are now implemented as described herein.

## 4. Sound Processing Pipeline Stages

```mermaid
%% ImpressionCore-b1 Sound Processing Flow (2025-05-23)
graph TD
    subgraph Audio Input Processing
        direction LR
        AudioInput[("fa:fa-file-audio Raw Audio<br>(Waveform/File Path)")] --> AP[AudioProcessor]
        AP --> AP_Resample{Resample & Normalize}
        AP_Resample --> PE[PhonemeExtractor<br>(Wav2Vec2-based)]
        PE --> CharSeq["Character Sequence<br>e.g., ['h','e','l','l','o']"]
        CharSeq --> PT[PhonemeTokenizer]
        PT --> TokenIDs["Token IDs<br>e.g., [12, 5, 15, 15, 20]"]
        TokenIDs --> PEM[PhonemeEmbedder<br>(nn.Embedding)]
        PEM --> OutputEmbeds[("fa:fa-wave-square Character Embeddings<br>(Tensor)")]
        CharSeq --> OutputChars[("fa:fa-font Character Sequence<br>(Direct Output)")]
    end

    subgraph Speech Generation
        direction LR
        TextInput[("fa:fa-keyboard Text Input<br>'Hello world'")] --> SSP[SpeechSynthesisPipeline]
        CharInput[("fa:fa-font Character Sequence Input<br>['h','e','l','l','o']")] --> SSP
        SSP --> P2S[PhonemeToSoundSynthesizer<br>(SpeechT5 & HiFiGAN Vocoder)]
        P2S --> AudioOutput[("fa:fa-volume-up Synthesized Speech<br>(Waveform)")]
    end

    style AudioInput fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style AP fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style PE fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style PT fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style PEM fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style OutputEmbeds fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style OutputChars fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px

    style TextInput fill:#ffebee,stroke:#c62828,stroke-width:2px
    style CharInput fill:#ffebee,stroke:#c62828,stroke-width:2px
    style SSP fill:#ffebee,stroke:#c62828,stroke-width:2px
    style P2S fill:#ffebee,stroke:#c62828,stroke-width:2px
    style AudioOutput fill:#fff9c4,stroke:#f57f17,stroke-width:2px

    linkStyle default stroke-width:2px,fill:none,stroke:grey
```

### 4.1. Audio Input Processing (`AudioProcessor`)

* The `AudioProcessor` takes raw audio waveforms (as files or tensors) and an optional `input_sample_rate_hint`.
* **Resampling & Normalization**: Audio is resampled to a target sample rate (e.g., 16kHz) and normalized.
* **Character Extraction**: The `PhonemeExtractor` (utilizing a pre-trained Wav2Vec2 model) processes the waveform to produce a sequence of characters.
* **Tokenization & Embedding (Optional Output)**:
  * The `PhonemeTokenizer` converts the character sequence into numerical token IDs.
  * The `PhonemeEmbedder` (a simple `nn.Embedding` layer) maps these token IDs to dense vector embeddings.
* **Output**: The `AudioProcessor` can return a dictionary containing:
  * The processed waveform and its sample rate.
  * The extracted character sequence (if `output_type="characters"`).
  * The character embeddings (if `output_type="features"`).
  * A success flag.

### 4.2. Speech Generation (`SpeechSynthesisPipeline`)

* The `SpeechSynthesisPipeline` takes either a plain text string or a list of characters as input.
* It utilizes the `PhonemeToSoundSynthesizer`, which employs:
  * A **SpeechT5** model to convert the input text/characters into a Mel-spectrogram.
  * A **HiFiGAN** vocoder to convert the Mel-spectrogram into an audible waveform.
* Speaker embeddings can be provided to influence the voice characteristics of the synthesized speech.
* **Output**: The pipeline returns the generated waveform (as a NumPy array) and its sample rate.

### 4.3. Future Enhancement: True Phoneme-Driven Synthesis

* The current character-based system provides a strong foundation. Future work will focus on integrating **true phoneme recognition** (e.g., using G2P models or dedicated phoneme ASR) into the `AudioProcessor`.
* Similarly, the `SpeechSynthesisPipeline` could be enhanced or augmented with models that directly consume phoneme sequences (e.g., Tacotron 2, direct phoneme-to-waveform models) for more precise control over pronunciation, intonation, and prosody.
* This would involve training or fine-tuning models on datasets with aligned audio and detailed phonemic transcriptions.

## 5. Training Strategy

### 5.1. Objectives

* Learn robust representations of spoken language at the character level.
* Enable intelligible speech synthesis from text and character sequences.
* Integrate audio modality effectively with text and (eventually) image modalities.
* Lay groundwork for future true phoneme-level processing.

### 5.2. Training Phases

* **Phase 1: Component Sourcing & Fine-tuning**:
  * Utilize pre-trained models for character extraction (Wav2Vec2 via `PhonemeExtractor`) and speech synthesis (SpeechT5, HiFiGAN via `PhonemeToSoundSynthesizer`).
  * Fine-tune these components on domain-specific data if necessary to improve performance on target voice characteristics or acoustic environments.
  * Train the `PhonemeEmbedder` (character embedding layer) if not relying solely on pre-trained ASR features for downstream tasks.
* **Phase 2: Multimodal Integration**:
  * Fine-tune the entire ImpressionCore-b1 model with the `AudioProcessor` and `SpeechSynthesisPipeline` integrated.
  * Use multimodal datasets where audio/speech is paired with text and/or images to learn cross-modal alignments.
* **Phase 3: True Phoneme Processing (Future)**:
  * Develop or integrate models for true phoneme recognition.
  * Train or fine-tune synthesis models that leverage explicit phoneme sequences. This will require datasets with accurate phonemic transcriptions.

## 6. Integration with ImpressionCore-b1

* The `AudioProcessor` output (character sequences or embeddings) is fed to the `Multimodal Fusion Layer`.
* The `SpeechSynthesisPipeline` can be invoked by the `MultiModalProcessor` or other system components when speech generation is required, taking input from the `Output Head` (if generating from model's internal state) or directly from text/character inputs.
* Configuration for audio models, sample rates, and processing options are managed via `PhonemeEmbeddingConfig` (see `src/modules/phoneme_embedding/config.py`) and passed to relevant components.
* Key Python modules are located in:
  * `src/data/preprocessing/audio.py` (`AudioProcessor`)
  * `src/modules/phoneme_embedding/` (sub-components like `PhonemeExtractor`, `PhonemeEmbedder`, `PhonemeToSoundSynthesizer`, `PhonemeTokenizer`, `PhonemeEmbeddingConfig`)
  * `src/inference/pipelines/speech_synthesis_pipeline.py` (`SpeechSynthesisPipeline`)

## 7. Future Work & Enhancements

* **Transition to True Phonemes**: Integrate robust grapheme-to-phoneme (G2P) converters and/or dedicated phoneme recognition models.
* **Expressive Speech Synthesis**: Incorporate control over prosody (pitch, duration, rhythm) and emotional tone in synthesized speech.
* **Speaker Adaptation/Cloning**: Improve capabilities for mimicking specific speaker voices with less data.
* **Noise Robustness**: Enhance the `AudioProcessor` to be more robust to noisy environments.
* **Advanced Vocoders**: Explore newer, potentially more efficient or higher-fidelity vocoders.
* **Memory & Performance Optimization**: Continuously profile and optimize all audio components for the target hardware.
* **Cross-lingual Capabilities**: Extend character/phoneme processing and synthesis to support multiple languages.
