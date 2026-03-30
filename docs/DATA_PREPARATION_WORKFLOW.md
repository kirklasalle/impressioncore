# Data Preparation Workflow

**Created:** July 05, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\DATA_PREPARATION_WORKFLOW.md #command_line #docs\data_preparation_workflow.md #documentation #multimodal #training  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# ImpressionCore Data Preparation Workflow

**Last updated:** 2025-07-05

## Overview

This document describes the workflow, manifest format, and best practices for preparing multimodal data for ImpressionCore B2 training.

## Manifest Format

Each sample in the manifest (JSON) must include:

- `conversation_id`: Unique string identifier
- `text`: Conversation text
- `embedding_path`: Path to embedding file (if used)
- `image_path`: Path to image file (relative to data root)
- `audio_path`: Path to audio file (relative to data root)
- `sentiment_label`: Integer (0=negative, 1=neutral, 2=positive)
- `intent_label`: Integer (0-9)
- `quality_score`: Float (0.0-1.0)
- `data_split`: 'train' or 'val'
- `metadata`: Dict with timestamp, source, and optional fields

## Data Preparation Steps

1. **Create sample or real-data manifests** using `prepare_raw_data.py`.
2. **Ensure all referenced files exist** (images, audio, embeddings). Placeholders are auto-generated if missing.
3. **Validate dataset** using `--validate` (checks structure, label ranges, file existence, and duplicate IDs).
4. **Use `--force` to overwrite** existing output, or `--dry-run` to preview actions.

## CLI Usage

```bash
python prepare_raw_data.py --generate-real-manifest --catalogue-path <path> --output-dir <dir> [--force] [--dry-run]
python prepare_raw_data.py --validate [--no-file-check]
```

## Best Practices

- Always validate before training.
- Keep manifests and media files organized in the same root directory.
- Document any changes to the manifest format in this file.

---
