# Impressioncore B1 Multimodal Io

**Created:** May 23, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\developer\impressioncore_b1_multimodal_io.md #api #attention_mechanism #documentation #gpu_optimization #inference #memory_management #multimodal #pytorch #tokenization #training #transformer  
**Category:** Developer Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

Last updated: 2025-05-31
Responsible: @GitHubCopilot
---

# ImpressionCore-b1: Multimodal Input/Output Architecture

_Last updated: 2025-05-27_
_Responsible: GitHub Copilot_

## 1. Introduction

This document details the input and output (I/O) architecture for the ImpressionCore-b1 system. It describes how data from different modalities (text, image, audio) is ingested, processed by encoders, fed into the **Multimodal Processing Pipeline (`src/multimodal/pipeline.py`)** which includes the Multimodal Fusion Layer, and how outputs from the core model are handled by decoders to produce multimodal responses. The **Brain Simulation Adapter (`src/adapters/brain_sim_adapter.py`)** can influence various stages of this pipeline, and the **Adaptive Memory Manager (`src/core/memory_manager.py`)** oversees resource utilization throughout.

This document complements the main `impressioncore_b1_architecture.md` by focusing specifically on the data flow and transformations at the boundaries of the core system, incorporating recent integrations.

## 2. Overall Multimodal I/O Flow

The following diagram illustrates the high-level flow of data through the ImpressionCore-b1 system, including the new components:

```mermaid
graph LR
    subgraph User/External Inputs
        direction LR
        UserInputText["Text Input<br>(e.g., user query, document)"]
        UserInputImage["Image Input<br>(e.g., uploaded file)"]
        UserInputAudio["Audio Input<br>(e.g., uploaded speech file)"]
    end

    subgraph System Services
        direction TB
        AMM[Adaptive Memory Manager<br>(src/core/memory_manager.py)]
        BSA[Brain Simulation Adapter<br>(src/adapters/brain_sim_adapter.py)]
    end

    subgraph Encoding Stage
        direction LR
        UserInputText --> TE[Text Encoder]
        UserInputImage --> IE[Image Encoder]
        UserInputAudio --> AP[Audio Processor<br>(incl. Phoneme Extractor/Embedder)]
        TE --> EncodedText["Encoded Text<br>(Embeddings/Tokens)"]
        IE --> EncodedImage["Encoded Image<br>(Feature Maps/Embeddings)"]
        AP --> EncodedAudio["Encoded Audio<br>(Character Embeddings)"]
    end

    EncodedText --> MPP[Multimodal Processing Pipeline<br>(src/multimodal/pipeline.py)]
    EncodedImage --> MPP
    EncodedAudio --> MPP
    MPP -- contains --> MFL[Multimodal Fusion Layer]

    MFL --> CoreModel[Core ImpressionCore-b1 Model<br>(MoE, Experts, etc.)]
    CoreModel --> OH[Output Head]

    subgraph Decoding Stage
        direction LR
        OH --> DecodedText["Text Data for Decoder"] --> TD[Text Decoder]
        OH --> DecodedImage["Image Data for Decoder"] --> ID[Image Decoder]
        OH --> DecodedAudio["Audio Data for Synthesis"] --> SSP[Speech Synthesis Pipeline]
        TD --> OutputText["Generated Text Output"]
        ID --> OutputImage["Generated Image Output"]
        SSP --> OutputAudio["Synthesized Speech Output"]
    end

    AMM -.-> EncodingStage(Encoding Stage)
    AMM -.-> MPP
    AMM -.-> CoreModel
    AMM -.-> DecodingStage(Decoding Stage)
    BSA -.-> MPP
    BSA -.-> CoreModel
    BSA -.-> OH

    style UserInputText fill:#cce5ff,stroke:#007bff
    style UserInputImage fill:#cce5ff,stroke:#007bff
    style UserInputAudio fill:#cce5ff,stroke:#007bff
    style TE fill:#d4edda,stroke:#28a745
    style IE fill:#d4edda,stroke:#28a745
    style AP fill:#d4edda,stroke:#28a745
    style MPP fill:#e2d9f3,stroke:#6f42c1
    style MFL fill:#fff3cd,stroke:#ffc107
    style CoreModel fill:#fff3cd,stroke:#ffc107
    style OH fill:#fff3cd,stroke:#ffc107
    style TD fill:#f8d7da,stroke:#dc3545
    style ID fill:#f8d7da,stroke:#dc3545
    style SSP fill:#f8d7da,stroke:#dc3545
    style OutputText fill:#e9ecef,stroke:#6c757d
    style OutputImage fill:#e9ecef,stroke:#6c757d
    style OutputAudio fill:#e9ecef,stroke:#6c757d
    style AMM fill:#d1ecf1,stroke:#0c5460
    style BSA fill:#d1ecf1,stroke:#0c5460
```

## 3. Input Processing Pipelines

### 3.1. Text Input

- **Sources:** User-typed queries via an interface, text from uploaded documents (.txt, .md, etc.).
- **Preprocessing:**
  - Cleaning: Removal of irrelevant characters, HTML tags (if applicable).
  - Normalization: Lowercasing, unicode normalization.
  - Sentence/word tokenization (preliminary, before model-specific tokenizer).
- **`TextEncoder` Interface:**
  - **Input:** Raw or preprocessed text string.
  - **Processing:** Utilizes a model-specific tokenizer (e.g., BPE, WordPiece) to convert text into token IDs. These IDs are then passed through an embedding layer.
  - **Output:** A tensor of token embeddings (e.g., `shape: [sequence_length, embedding_dim]`) and corresponding attention masks.
  - **Relevant Modules:** `src/data/preprocessing/text_processor.py` (conceptual), specific model tokenizers from libraries like Hugging Face Transformers.

### 3.2. Image Input

- **Sources:** Uploaded image files (e.g., .jpg, .png).
- **Preprocessing:**
  - Decoding image file into pixel data.
  - Resizing to a fixed input dimension expected by the `ImageEncoder`.
  - Normalization (e.g., pixel values to [0, 1] or [-1, 1], channel normalization based on dataset statistics).
  - Augmentation (if applicable during training, typically minimal for "b1" inference).
- **`ImageEncoder` Interface:**
  - **Input:** Preprocessed image tensor (e.g., `shape: [channels, height, width]`).
  - **Processing:** Passes the image tensor through a vision model (e.g., a CNN like ResNet, or a Vision Transformer).
  - **Output:** A tensor of image embeddings or feature maps (e.g., `shape: [num_patches, embedding_dim]` for ViT, or `shape: [feature_map_channels, H', W']` for CNNs, subsequently flattened or pooled).
  - **Relevant Modules:** `src/data/preprocessing/image_processor.py` (conceptual), specific vision models from libraries like `torchvision` or Hugging Face Transformers.

### 3.3. Audio Input

- **Sources:** Uploaded audio files (e.g., .wav, .mp3). For "b1", focus is primarily on pre-recorded files.
- **`AudioProcessor` (`src/data/preprocessing/audio_processor.py`):**
  - **Input:** Path to audio file or raw waveform.
  - **Initial Processing:**
    - Loading audio file.
    - Resampling to the target sample rate (e.g., 16kHz) required by downstream models.
    - Normalization of waveform amplitude.
  - **Character Sequence Extraction (via `PhonemeExtractor`):**
    - The normalized waveform is passed to `src/modules/phoneme_embedding/phoneme_extractor.py`.
    - This uses an ASR model (e.g., Wav2Vec2) to transcribe the audio into a sequence of characters (e.g., `['h', 'e', 'l', 'l', 'o']`). These characters serve as a proxy for phonemes in "b1".
  - **Tokenization and Embedding (via `PhonemeTokenizer` and `PhonemeEmbedder`):**
    - The extracted character sequence is tokenized by `src/modules/phoneme_embedding/phoneme_embedder.py::PhonemeTokenizer` into numerical IDs.
    - These IDs are then converted into dense vector embeddings by `src/modules/phoneme_embedding/phoneme_embedder.py::PhonemeEmbedder`.
  - **Output to Fusion Layer:** A tensor of character embeddings (e.g., `shape: [sequence_length, embedding_dim]`) and corresponding attention masks/padding information.

## 4. Multimodal Processing Pipeline & Fusion Layer Input

The **`MultimodalProcessingPipeline` (`src/multimodal/pipeline.py`)** orchestrates the combination and further processing of inputs from the individual modality encoders. It internally manages or incorporates the `MultimodalFusionLayer`.

- **Input Data to Pipeline:**
  - Text Embeddings: From `TextEncoder`.
  - Image Embeddings/Features: From `ImageEncoder`.
  - Audio (Character) Embeddings: From `AudioProcessor`.
- **Influence of `BrainSimulationAdapter`:**
  - The `BrainSimulationAdapter` can provide contextual biases, attentional focus, or simulated emotional states that influence how the `MultimodalProcessingPipeline` combines or weighs different modalities within the fusion process.
- **`MultimodalFusionLayer` (within or called by the Pipeline):**
  - **Formatting & Alignment:**
    - Embeddings from different modalities might have different sequence lengths and potentially different embedding dimensions (though often projected to a common dimension before or during fusion).
    - **Concatenation:** A common strategy is to concatenate the sequences of embeddings, possibly with special separator tokens.
    - **Attention Mechanisms:** Cross-attention or co-attention mechanisms within the fusion layer can learn relationships between modalities without requiring strict sequence alignment.
    - For "b1", a simpler fusion strategy (e.g., concatenation followed by a few transformer layers) might be adopted initially.
  - **Output from Pipeline:** A unified multimodal representation (sequence of embeddings) that is fed into the main `CoreModel`.
  - **Oversight by `AdaptiveMemoryManager`:** The `AdaptiveMemoryManager` monitors the VRAM usage of the pipeline and fusion operations, potentially triggering CPU offloading for large intermediate tensors if necessary.

## 5. Output Processing Pipelines

After the `CoreModel` (MoE, Experts, etc.) processes the fused multimodal input (potentially influenced by the `BrainSimulationAdapter`), the `OutputHead` directs information to the appropriate decoders based on the desired output modality or task. The `BrainSimulationAdapter` can also influence the selection or behavior of the `OutputHead` and subsequent decoders.

### 5.1. Text Output

- **Input to `TextDecoder`:** Typically a sequence of hidden states from the `OutputHead`, along with a start-of-sequence token or prompt.
- **`TextDecoder` Interface:**
  - **Processing:** An autoregressive language model (e.g., a Transformer decoder) generates text token by token.
  - **Output:** A string of generated text.
  - **Relevant Modules:** `src/modules/decoders/text_decoder.py` (conceptual), standard language models from Hugging Face Transformers.

### 5.2. Image Output

- **Input to `ImageDecoder`:** A representation from the `OutputHead` (e.g., a latent vector, or text/multimodal embeddings to condition image generation).
- **`ImageDecoder` Interface:**
  - **Processing:** A generative model (e.g., a GAN, a diffusion model like in `src/diffusion/`, or a VAE decoder) synthesizes an image.
  - **Output:** Pixel data for the generated image (e.g., a NumPy array or PyTorch tensor), which can then be saved to a file or displayed.
  - **Note for "b1":** Image generation might be simplified (e.g., retrieving a relevant image based on input, or very basic generative capabilities) or use pre-trained components.
  - **Relevant Modules:** `src/modules/decoders/image_decoder.py` (conceptual), generative models from libraries.

### 5.3. Audio Output (Speech Synthesis)

- **Input to `SpeechSynthesisPipeline`:** Text generated by the `TextDecoder` or directly from the `OutputHead` if the task is direct speech generation from a multimodal context.
- **`SpeechSynthesisPipeline` (`src/inference/pipelines/speech_synthesis_pipeline.py`):**
  - **Processing:**
    - Takes text (or character sequence) as input.
    - Utilizes `PhonemeToSoundSynthesizer` (`src/modules/phoneme_embedding/phoneme_to_sound.py`).
    - This synthesizer uses a TTS model (e.g., SpeechT5) to convert text to a spectrogram or intermediate representation.
    - A vocoder (e.g., HiFiGAN) converts this intermediate representation into an audible waveform.
  - **Output:** A raw audio waveform (e.g., 1D PyTorch tensor or NumPy array), which can be played or saved to a file.
  - **Sample Rate:** The output sample rate is determined by the configuration of the TTS and vocoder models (e.g., 16kHz or 22.05kHz).

## 6. Data Formats and Contracts

Detailed data formats (e.g., specific tensor shapes, metadata, JSON schemas for API communication if applicable) for each component interface, including interactions with the `AdaptiveMemoryManager` and `BrainSimulationAdapter`, should be strictly defined and maintained. These will be further elaborated in `docs/developer/api_contracts.md`.

Key considerations:

- **Tensor Shapes:** Consistent use of batch size, sequence length, embedding dimensions.
- **Padding and Attention Masks:** Proper handling for variable-length sequences.
- **Device Management:** Ensuring tensors are on the correct device (CPU/GPU) at each stage.

## 7. Future Considerations for I/O

- **Streaming I/O:** For real-time applications (e.g., live microphone input, continuous video feed).
- **Advanced Preprocessing:** More sophisticated techniques for noise reduction, data augmentation, and feature engineering.
- **Other Modalities:** Support for video, tabular data, sensor data, etc.
- **Bidirectional Data Flow:** More complex interactions where decoders might feed information back into the core model for iterative refinement.
- **Standardized Intermediate Representations:** Defining common formats for inter-component data exchange to improve modularity.
