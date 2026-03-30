# 2025-06-29: Embedding Pipeline and Loader Update

**Created:** June 29, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\data_prep_notes.md #command_line #documentation #memory_management #testing #training  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Embedding Pipeline Overview

- All curated data in F:/b2_datasets/ is embedded using the ImpressionCore B2 encoders (TextEncoder, VisionEncoder, AudioEncoder, VideoEncoder) via `src/training/embed_b2_datasets.py`.
- Embeddings are saved as .npy files in F:/b2_embeddings/[modality]/.
- An embedding catalogue (F:/b2_embeddings/b2_embedding_catalogue.json) lists all embedding file paths by modality.
- The embedding script uses ImpressionCore's rich logging and status animation for progress and error reporting.

## Embedding-Based DataLoaders

- New dataset classes (`TextEmbeddingDataset`, `ImageEmbeddingDataset`, `AudioEmbeddingDataset`, `VideoEmbeddingDataset`) in `src/training/datasets/data_loading.py` load precomputed embeddings from .npy files.
- The `get_embedding_dataloaders` function returns DataLoaders for each modality, using the embedding catalogue.
- This enables efficient, memory-optimized training on precomputed embeddings, critical for GTX 1050 Ti constraints.

## Training Pipeline Integration

- The main B2 training script (`src/training/train_b2.py`) now uses the embedding-based DataLoaders for all modalities.
- A `CombinedEmbeddingLoader` zips the modalities for joint training batches.
- This pipeline supports large-scale, memory-efficient training and is ready for 3B parameter, 128k context experiments.

## Usage Notes

- Run the curation script to update and validate the dataset: `python src/training/curate_b2_datasets.py`
- Run the embedding script to generate embeddings: `python src/training/embed_b2_datasets.py`
- Train the model using the embedding-based pipeline: `python src/training/train_b2.py`

All changes logged by GitHub Copilot on 2025-06-29.

# Data Preparation Notes for B2

- 2025-06-29: Initial F:/datasets directory structure and sample files created for all modalities.
- Each folder contains at least one sample file for loader and pipeline validation.
- 2025-06-29: All data loaders (text, images, audio, video) successfully validated with real, non-placeholder files. Loader test script passed for all modalities. System is ready for model initialization and training pipeline setup. (Logged by GitHub Copilot)

## B2 Dataset Schema and Requirements (as of 2025-06-29)

### File Formats and Structure

- **Text:** .txt (plain text), .jsonl (one JSON object per line, e.g., {"input":..., "output":...})
- **Images:** .png, .jpg, .jpeg (RGB, properly labeled)
- **Audio:** .wav, .mp3 (mono or stereo, readable by soundfile)
- **Video:** .mp4, .avi (short clips, readable by standard video tools)

### Directory Layout

- All curated files are moved to F:/b2_datasets/[modality]/
- A catalogue of all curated files is saved as F:/b2_datasets/b2_data_catalogue.json

### Labeling Conventions

- **Text:** If .jsonl, each line should include fields for input, output, and (optionally) intent or class.
- **Images:** Filenames or a separate .csv/.json file should provide class/label info if needed.
- **Audio:** Filenames or a separate .csv/.json file should provide class/label info if needed.
- **Video:** Filenames or a separate .csv/.json file should provide class/label info if needed.

### Preprocessing/Normalization

- All files are checked for readability and format compliance.
- Images are verified to be loadable by PIL.Image.
- Audio is verified to be readable by soundfile.
- Text is checked for UTF-8 encoding and basic readability.
- Video is checked for existence and nonzero size.
- Sample/placeholder/test files are ignored during curation.

### Notes

- The curation script can be rerun to update the catalogue and curated dataset folders as new data arrives.
- All steps are logged and summarized in the terminal and this document.
