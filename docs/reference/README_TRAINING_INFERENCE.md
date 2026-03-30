# Readme Training Inference

**Created:** February 25, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\README_TRAINING_INFERENCE.md #attention_mechanism #docs\reference\readme_training_inference.md #documentation #gpu_optimization #inference #memory_management #multimodal #performance #testing #training #transformer  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# ImpressionCore Training & Inference Guide

This guide provides instructions for running additional training sessions and inference tests with the ImpressionCore model.

## Project Overview

ImpressionCore is a transformer-based language model with the following features:

- Multimodal input support (text, visual, audio)
- Efficient attention mechanisms
- Support for continual training with new data
- Text generation capabilities with customizable parameters
- Model distillation capabilities

## Available Scripts

I've created several scripts to facilitate additional training and inference:

1. **continuous_training.py** - Continues training from a checkpoint using different data
2. **inference_tests.py** - Tests model generation with different parameters and benchmarks performance
3. **mixed_corpus_training.py** - Trains on multiple document types simultaneously
4. **run_training_pipeline.py** - Orchestrates the entire training and inference pipeline

## Running Additional Training Sessions

### Option 1: Complete Training Pipeline

The easiest way to run a full training sequence is using the pipeline script:

```bash
python examples/run_training_pipeline.py
```

This will:

1. Train a small model for quick iteration
2. Train on multiple documents to improve versatility
3. Continue training from a checkpoint to refine performance
4. Run inference tests to evaluate the model

### Option 2: Individual Training Scripts

For more granular control, run the individual scripts:

#### Basic Training

```bash
python examples/train_model.py
```

#### Small Model Training (Fast)

```bash
python examples/train_small.py
```

#### Continue Training from a Checkpoint

```bash
python examples/continuous_training.py
```

#### Mixed Corpus Training

```bash
python examples/mixed_corpus_training.py
```

## Running Inference Tests

To test the model's text generation capabilities:

```bash
python examples/inference_tests.py
```

This script:

- Tests generation with different temperature settings
- Benchmarks inference speed
- Tests multimodal inputs (if supported)
- Compares results from different checkpoints

For a quick generation test:

```bash
python examples/generate_text.py
```

## Training Parameters

You can modify the following parameters in each script for different training configurations:

### Model Architecture

- `hidden_size` - Size of hidden layers
- `num_hidden_layers` - Number of transformer layers
- `num_attention_heads` - Number of attention heads
- `intermediate_size` - Size of feed-forward layers

### Training Configuration

- `max_steps` - Number of training steps
- `learning_rate` - Learning rate for optimization
- `batch_size` - Batch size for training
- `weight_decay` - L2 regularization strength

### Inference Parameters

- `temperature` - Controls randomness (higher = more random)
- `top_k` - Limits vocabulary to top k tokens
- `top_p` - Nucleus sampling threshold
- `max_length` - Maximum generation length

## Checkpoints

The system stores checkpoints at regular intervals during training:

- `checkpoint_X.pt` - Saved at step X
- `best_model.pt` - Model with the lowest validation loss
- `final_model.pt` - Final state after training completes
- `interrupted_checkpoint.pt` - Created if training is interrupted

## Recommended Workflow

For optimal results, follow this workflow:

1. Start with a quick small model training for validation:

   ```bash
   python examples/train_small.py
   ```

2. Train on multiple document types to improve versatility:

   ```bash
   python examples/mixed_corpus_training.py
   ```

3. Fine-tune from the best checkpoint:

   ```bash
   python examples/continuous_training.py
   ```

4. Run inference tests to evaluate:

   ```bash
   python examples/inference_tests.py
   ```

## Tips for Better Results

- **Use larger models for final training**: Increase `hidden_size` and `num_hidden_layers` for better performance
- **Lower learning rate for fine-tuning**: Use learning rates around 1e-5 for fine-tuning from checkpoints
- **Experiment with different temperatures**: Lower temperatures (0.5-0.7) produce more focused text, while higher values produce more creative outputs
- **Monitor validation loss**: If validation loss increases, consider early stopping or reducing the learning rate
- **Train with diverse data**: For best generalization, include a variety of document types in training

## Troubleshooting

- **Out of memory errors**: Reduce batch size or model size, or enable gradient accumulation
- **Slow training**: Check GPU utilization, reduce sequence length, or use mixed precision training
- **Poor generation quality**: Try training longer, using more data, or adjusting generation parameters
