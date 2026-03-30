# ImpressionCore B2 Phase 1 Hyperparameters and Training Configuration

**Created:** July 06, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\B2_PHASE1_HYPERPARAMETERS.md #command_line #deployment #docs\b2_phase1_hyperparameters.md #documentation #memory_management #multimodal #training #transformer  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Overview

This document details the hyperparameters and configuration used for Phase 1 (initialization) training of the ImpressionCore B2 multimodal model. All values are based on state-of-the-art research, including Assembly of Experts (AoE), DeepSeek Chimera, Mixture of Experts (MoE), and best practices for efficient multimodal LLMs on consumer hardware (GTX 1050 Ti, 4GB VRAM).

## Key Hyperparameters (SOTA-Inspired)

| Parameter                | Value         | Rationale/Notes                                                      |
|-------------------------|--------------|---------------------------------------------------------------------|
| embed_dim               | 768          | Standard for GPT2/CLIP/Wav2Vec2 compatibility                       |
| vocab_size              | 50257        | GPT2/BPE vocabulary size                                            |
| img_dim                 | 256          | CLIP ViT-B/32 compatible                                            |
| audio_dim               | 16000        | Wav2Vec2 compatible                                                 |
| num_layers              | 12           | Transformer depth, memory-optimized                                 |
| num_heads               | 12           | Transformer width, memory-optimized                                 |
| max_seq_len             | 128000       | Large context for multimodal tasks                                  |
| n_experts               | 4            | MoE: 4 experts, 2 active per token                                  |
| dropout                 | 0.18         | Heads (MoE/Chimera: 0.15-0.25)                                     |
| core_dropout            | 0.12         | Transformer backbone                                                |
| lr                      | 2e-4         | Backbone learning rate                                              |
| head_lr_multiplier      | 5.0          | Heads/expert routers                                                |
| batch_size              | 2            | Dynamic, increase if VRAM allows                                    |
| epochs                  | 18           | With early stopping                                                 |
| loss_weight_sentiment   | 0.4          | SOTA for auxiliary heads                                            |
| loss_weight_intent      | 0.4          | SOTA for auxiliary heads                                            |
| loss_weight_quality     | 0.15         | SOTA for auxiliary heads                                            |
| curriculum_epochs       | 4            | Backbone only, then unfreeze heads                                  |
| gradient_clip           | 1.0          | Prevents exploding gradients                                        |
| early_stopping_patience | 6            | Robust early stopping                                               |
| precision               | amp          | Mixed precision (autocast, GradScaler)                              |
| quantization            | 8bit         | For deployment                                                      |

## Data and Paths

- **embedding_dir:** F:/b2_embeddings
- **output_dir:** F:/models/b2_checkpoints
- **train_manifest:** data/raw_multimodal/train_manifest.json
- **val_manifest:** data/raw_multimodal/val_manifest.json

## References

- [B2_NEXT_GENERATION_MULTIMODAL_ARCHITECTURE_DESIGN.md](B2_NEXT_GENERATION_MULTIMODAL_ARCHITECTURE_DESIGN.md)
- [B2_DISTILLATION_PIPELINE.md](B2_DISTILLATION_PIPELINE.md)
- [logic_concept_cache.md](logic_concept_cache.md)
- arXiv:2506.14794 (AoE, DeepSeek Chimera, MoE)

## Notes

- All values are hardware-optimized for GTX 1050 Ti (4GB VRAM).
- For further details, see the config file: `b2_phase1_init_config.yaml`.
- For experiment tracking and grid search, see `aggregate_grid_search_results.py` and TensorBoard logs.

---
*This file is auto-generated and maintained by ImpressionCore Copilot. Do not edit manually.*
