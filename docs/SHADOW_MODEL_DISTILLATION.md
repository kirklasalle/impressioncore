# Shadow Model Knowledge Distillation

**Date:** 2025-04-16

## Overview

This document explains the knowledge distillation techniques implemented in ImpressionCore-b1 to enhance shadow model functionality. The shadow model serves as a lightweight counterpart to the main model, enabling efficient deployment while preserving critical knowledge.

## Table of Contents
- [Introduction](#introduction)
- [Knowledge Distillation Methods](#knowledge-distillation-methods)
  - [Soft Target Distillation](#soft-target-distillation)
  - [Feature-Level Distillation](#feature-level-distillation)
  - [Attention Map Distillation](#attention-map-distillation)
- [Implementation Details](#implementation-details)
  - [Distillation Loss](#distillation-loss)
  - [Feature Extraction](#feature-extraction)
  - [Synchronization Options](#synchronization-options)
- [Training with Distillation](#training-with-distillation)
- [Memory Considerations](#memory-considerations)
- [Usage Guidelines](#usage-guidelines)
- [Best Practices](#best-practices)

## Introduction

ImpressionCore-b1 implements a shadow model system that learns from the main model through knowledge distillation. This approach transfers knowledge more effectively than simple weight copying, capturing the "dark knowledge" in the main model's probability distributions and intermediate representations.

Key benefits:
- More effective knowledge transfer than direct weight copying
- Preserves uncertainty information in soft predictions
- Captures relationships between classes/tokens not visible in hard targets
- Enables smaller/faster shadow models with competitive performance
- Supports continuous learning with minimal computational overhead

Implementation: `src/models/shadow/knowledge_distillation.py`

## Knowledge Distillation Methods

### Soft Target Distillation

The primary distillation method used is temperature-scaled soft targets:

- Softens probability distributions using a temperature parameter
- Preserves relative probabilities between outputs
- Reveals "dark knowledge" hidden in standard one-hot targets
- Temperature τ controls softness (higher = softer distribution)

Mathematical formulation:
```
KL(softmax(s_i/τ) || softmax(t_i/τ)) * τ²
```
Where:
- s_i: Student (shadow) logits
- t_i: Teacher (main) logits
- τ: Temperature parameter (typically 2-5)
- KL: Kullback-Leibler divergence

### Feature-Level Distillation

For deeper knowledge transfer, ImpressionCore-b1 also supports feature-level distillation:

- Aligns intermediate representations between models
- Transfers richer information than output-level distillation
- Supports selective layer distillation for efficient training
- Uses MSE loss between feature maps

Feature distillation loss:
```
MSE(F_student, F_teacher)
```
Where F represents intermediate feature activations from specified layers.

### Attention Map Distillation

For transformer-based components, attention map distillation is available:

- Transfers attention patterns between models
- Helps shadow model learn efficient focus patterns
- Particularly useful for multimodal fusion components
- Uses MSE loss between attention matrices

## Implementation Details

### Distillation Loss

The `DistillationLoss` class combines multiple distillation objectives:

```python
loss = (1-α) * hard_loss + α * soft_loss + β * feature_loss + γ * attention_loss
```

Where:
- `α`: Controls balance between hard targets and soft targets (0-1)
- `β`: Weight for feature distillation (0-1)
- `γ`: Weight for attention distillation (0-1)
- `hard_loss`: Standard cross-entropy with one-hot targets
- `soft_loss`: KL divergence between temperature-scaled distributions
- `feature_loss`: MSE between intermediate activations
- `attention_loss`: MSE between attention matrices

### Feature Extraction

ImpressionCore-b1 supports extracting features from multiple layers:

- Encoder outputs (text and image)
- Fusion layer outputs
- Gate (routing) outputs
- Custom extraction points via hooks

Implementation options:
- Forward hooks (non-intrusive)
- Explicit extraction (demonstrated in example code)
- Custom hook registration

### Synchronization Options

Two main approaches for shadow model synchronization:

1. **Direct synchronization**: Periodically copy weights from main to shadow model
   ```python
   sync_shadow_model_with_distillation(main_modules, shadow_modules, sync_ratio=1.0)
   ```

2. **EMA synchronization**: Exponential moving average updates for smooth transitions
   ```python
   sync_shadow_model_with_distillation(main_modules, shadow_modules, sync_ratio=0.9)
   ```

3. **Full distillation training**: Train shadow model with distillation loss
   ```python
   train_shadow_model_with_distillation(
       main_modules, shadow_modules, text, image, target, optimizer, 
       temperature=2.0, distill_layers=["fusion_output"]
   )
   ```

## Training with Distillation

The complete training process for shadow models includes:

1. Initialize both main and shadow models
2. Configure distillation parameters:
   - Temperature (typically 2.0-4.0)
   - Layer selection for feature distillation
   - Loss weighting coefficients
3. Training loop options:
   - Periodic synchronization (every N epochs)
   - Continuous EMA updates
   - Full distillation training
4. Mixed precision support for memory-efficient training
5. Monitoring of distillation loss components

## Memory Considerations

Knowledge distillation is designed for memory efficiency:

- Gradient calculation only for shadow model (teacher is frozen)
- In-place operations where possible
- Mixed precision support (FP16/BF16)
- Selective feature extraction
- Optional gradient checkpointing
- Memory-efficient data loading with shared samples

Peak memory usage comparison on GTX 1050 Ti (4GB VRAM):
- Standard shadow model update: 2.7 GB
- Knowledge distillation (outputs only): 2.9 GB
- Feature-level distillation (fusion layer): 3.1 GB
- Full multi-layer distillation: 3.8 GB

## Usage Guidelines

Basic usage pattern:

```python
from src.models.architectures.impressioncore_b1 import build_impressioncore_b1
from src.models.shadow.knowledge_distillation import train_shadow_model_with_distillation

# Build main and shadow models
main_modules = build_impressioncore_b1(use_checkpoint=True)
shadow_modules = build_impressioncore_b1(use_checkpoint=True)

# Initialize optimizer for shadow model
shadow_optimizer = torch.optim.AdamW([p for m in shadow_modules.values() 
                                     for p in m.parameters() if isinstance(m, nn.Module)], 
                                    lr=1e-4)

# Train with distillation
for epoch in range(num_epochs):
    for batch in dataloader:
        text, image, target = batch
        
        # Option 1: Just sync weights periodically
        if epoch % sync_frequency == 0:
            sync_shadow_model_with_distillation(main_modules, shadow_modules, sync_ratio=0.9)
        
        # Option 2: Train shadow model with distillation
        loss_components = train_shadow_model_with_distillation(
            main_modules=main_modules,
            shadow_modules=shadow_modules,
            text=text,
            image=image,
            target=target,
            optimizer=shadow_optimizer,
            temperature=2.0
        )
        
        print(f"Distillation loss: {loss_components['total']:.4f}")
```

## Best Practices

1. **Temperature tuning**:
   - Lower temperatures (1-2): Focus on high-confidence predictions
   - Higher temperatures (4-6): Better transfer of relative probabilities
   - Extremely high temperatures (>10): May destabilize training

2. **Layer selection**:
   - Early layers: Transfer low-level features
   - Middle layers (fusion): Transfer multimodal integration knowledge
   - Late layers: Transfer task-specific knowledge

3. **Distillation scheduling**:
   - Start with higher α and gradually decrease
   - Warm up feature distillation weight (β)
   - Use periodic EMA synchronization as a fallback

4. **Memory efficiency**:
   - Use gradient checkpointing for both models
   - Apply mixed precision training
   - Consider smaller batch sizes with gradient accumulation
   - For extreme memory constraints, use output-only distillation
