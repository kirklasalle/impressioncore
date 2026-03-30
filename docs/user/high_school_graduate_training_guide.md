# ImpressionCore High School Graduate Training Guide

**Created:** June 12, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\user\high_school_graduate_training_guide.md #attention_mechanism #command_line #cuda #documentation #gpu_optimization #inference #memory_management #pytorch #testing #training  
**Category:** User Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## 🎯 Training Objective

Train the ImpressionCore model to achieve **high school graduate level text conversation** capabilities through advanced knowledge distillation techniques. This training focuses on:

- **Academic conversation skills** (literature, science, math, history)
- **Critical thinking and analysis** 
- **Peer-level communication**
- **Study guidance and learning support**
- **Subject matter comprehension**

## 🚀 Quick Start

### 1. Basic Training (Recommended)

```bash
# Navigate to project root
cd "d:\Projects\impressioncore"

# Start training with optimal settings
python high_school_graduate_trainer.py
```

### 2. Quick Test Training (5 epochs)

```bash
# Fast training for testing
python high_school_graduate_trainer.py --quick
```

### 3. Custom Training Configuration

```bash
# Advanced configuration
python high_school_graduate_trainer.py --epochs 15 --batch-size 2 --learning-rate 1e-5
```

## 📋 Training Options

### Core Training Parameters

- `--epochs N` - Number of training epochs (default: 10)
- `--batch-size N` - Training batch size (default: 4, optimized for 4GB VRAM)
- `--learning-rate F` - Learning rate (default: 2e-5)
- `--temperature F` - Distillation temperature (default: 4.0)

### Teacher Model Selection

- `--teacher-model MODEL` - Teacher model for distillation (default: microsoft/DialoGPT-medium)

### Memory Optimization

- `--max-memory N` - Maximum GPU memory in MB (default: 3500)
- `--no-mixed-precision` - Disable mixed precision training
- `--cpu-only` - Force CPU training (not recommended)

### Convenience Options

- `--quick` - Quick mode (5 epochs, smaller batch)
- `--verbose` - Detailed output
- `--yes` - Skip confirmations

## 🎓 Understanding the Training Process

### Knowledge Distillation Approach

The training uses **knowledge distillation** to transfer conversation skills from a larger teacher model to the compact ImpressionCore model:

1. **Teacher Model**: microsoft/DialoGPT-medium (conversation-focused)
2. **Student Model**: ImpressionCore-B1 (optimized for 4GB VRAM)
3. **Distillation Loss**: Transfers "soft knowledge" from teacher predictions
4. **Task Loss**: Direct learning from high school conversation examples

### High School Curriculum Focus

Training data includes conversations across key areas:

- **Literature**: Shakespeare, classic novels, poetry analysis
- **Science**: Biology, chemistry, physics, environmental science
- **Mathematics**: Algebra, geometry, statistics, problem-solving
- **History**: World history, American history, current events
- **Social Studies**: Government, economics, social issues
- **Study Skills**: Learning strategies, test preparation, time management

### Memory Optimization Features

- **Chunked Attention**: Processes long sequences efficiently
- **Gradient Checkpointing**: Reduces memory usage during training
- **Mixed Precision**: Uses FP16 for faster training with less memory
- **Batch Size Optimization**: Automatically optimized for 4GB VRAM

## 📊 Training Progress Monitoring

During training, you'll see:

- **Real-time progress bars** showing epoch and batch progress
- **Loss metrics** (total loss, distillation loss, task loss)
- **Memory usage monitoring** to prevent VRAM overflow
- **Conversation skill evaluation** every few epochs
- **Sample conversations** showing model improvement

## 🔍 Model Evaluation

### Evaluate Trained Model

```bash
# Evaluate conversation skills
python high_school_graduate_trainer.py --evaluate --model "src/models/production/model.pth"
```

### Interactive Testing

```bash
# Chat with trained model
python high_school_graduate_trainer.py --chat --model "src/models/production/model.pth"
```

### List Available Models

```bash
# See all trained models
python high_school_graduate_trainer.py --list-models
```

## 📈 Expected Results

### Training Metrics

- **Loss Reduction**: Expect 15-25% loss reduction over training
- **Conversation Score**: Target 7.0+/10.0 for high school level
- **Training Time**: ~2-4 hours for 10 epochs (depending on hardware)
- **Model Size**: ~2-5MB final model (highly compressed)

### Conversation Quality Indicators

- **Academic Vocabulary**: Uses appropriate subject-specific terms
- **Reasoning Skills**: Shows logical thinking and analysis
- **Question Asking**: Engages with follow-up questions
- **Example Usage**: Provides relevant examples and explanations
- **Peer-Level Tone**: Appropriate formality for high school context

## 🛠️ Advanced Usage

### Custom Teacher Models

```bash
# Use different teacher model
python high_school_graduate_trainer.py --teacher-model "facebook/blenderbot-400M-distill"
```

### Memory-Constrained Training

```bash
# For 3GB VRAM or less
python high_school_graduate_trainer.py --batch-size 1 --max-memory 2500
```

### Extended Training

```bash
# Longer training for better results
python high_school_graduate_trainer.py --epochs 20 --learning-rate 1e-5
```

## 🔧 System Requirements

### Recommended

- **GPU**: NVIDIA GTX 1050 Ti (4GB VRAM) or better
- **RAM**: 8GB+ system memory
- **Storage**: 5GB free space
- **Python**: 3.8+ with PyTorch CUDA support

### Minimum

- **CPU**: Multi-core processor (training will be slower)
- **RAM**: 6GB+ system memory
- **Storage**: 3GB free space
- **Python**: 3.8+ with PyTorch CPU

## 📂 Output Files

### Training Outputs

- `src/models/checkpoints/high_school_model_epoch_N_TIMESTAMP.pth` - Epoch checkpoints
- `src/models/production/impressioncore_high_school_graduate_TIMESTAMP.pth` - Final model

### Logs and Reports

- Training progress logs in console
- Memory usage monitoring
- Conversation evaluation results

## ❗ Troubleshooting

### CUDA Out of Memory

```bash
# Reduce batch size
python high_school_graduate_trainer.py --batch-size 1

# Or use CPU training
python high_school_graduate_trainer.py --cpu-only
```

### Import Errors

```bash
# Ensure you're in the project root directory
cd "d:\Projects\impressioncore"

# Check Python path includes src/
python -c "import sys; print('src' in str(sys.path))"
```

### Slow Training

- Enable mixed precision (default)
- Use CUDA instead of CPU
- Ensure sufficient system RAM

## 🎉 Success Indicators

### Training Complete

- ✅ All epochs completed without errors
- ✅ Loss steadily decreased
- ✅ Final model saved successfully
- ✅ Conversation score 7.0+/10.0

### Ready for Production

- ✅ Model loads correctly
- ✅ Inference time <100ms
- ✅ Responses show high school level reasoning
- ✅ Memory usage within limits

## 📞 Next Steps

After successful training:

1. **Test Extensively**: Use `--chat` mode for comprehensive testing
2. **Integrate**: Add model to your ImpressionCore CLI system
3. **Deploy**: Use trained model in production applications
4. **Iterate**: Fine-tune based on real-world usage

---

**Note**: This training system builds on ImpressionCore's proven production pipeline that has already achieved excellent results with 749K+ embeddings and optimized performance on GTX 1050 Ti hardware.
