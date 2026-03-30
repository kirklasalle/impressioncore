# ImpressionCore B2 Curriculum Distillation Pipeline

**Created:** July 01, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\B2_DISTILLATION_PIPELINE.md #docs\b2_distillation_pipeline.md #documentation #memory_management #training  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Overview

This document describes the architecture, setup, and usage of the ImpressionCore B2 curriculum-based knowledge distillation pipeline. The B2 pipeline is fully decoupled from B1, uses B2-specific models, embeddings, and directories, and is optimized for GTX 1050 Ti hardware.

## Components

- **B2TrainingInitializer:** Sets up the B2 model, dataloaders, and environment. Located at `src/core/kernel/b2_training_initializer.py`.
- **B2KnowledgeDistillationTrainer:** Orchestrates B2 knowledge distillation, curriculum, and evaluation. Located at `src/training/distillation/b2_knowledge_distillation_trainer.py`.
- **run_curriculum_distillation.py:** Entrypoint for running multi-stage curriculum distillation sessions.

## Key Features

- Uses B2 model and B2 embeddings (`F:/b2_embeddings`)
- B2-specific checkpoints, logs, and outputs
- Modular, extensible, and memory-optimized
- Fully documented and memlog-compliant

## Usage

1. Prepare B2 embeddings using `embed_b2_datasets.py`.
2. Run the curriculum distillation pipeline:

   ```bash
   export PYTHONPATH=./src
   python src/training/distillation/run_curriculum_distillation.py
   ```

3. Monitor progress and logs in `F:/impressioncore-b2-models/distillation/logs`.

## Architecture Diagram

``` text
[Teacher Models] → [B2KnowledgeDistillationTrainer] → [B2TrainingInitializer] → [B2 Model + Embeddings]
```

## Change Log

- 2025-07-01: Initial B2 pipeline refactor and documentation (by Copilot)
