# ImpressionCore-B1 Quick Start Guide

**Created:** June 11, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\bulletproof_training_quick_start.md #cuda #documentation #gpu_optimization #memory_management #multimodal #testing #training  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

🚀 **Get your bulletproof multimodal AI training system running in 5 minutes!**

## Prerequisites

- Windows 10/11
- NVIDIA GPU with CUDA support (GTX 1050 Ti or better)
- Python 3.10+

## Quick Setup

### 1. Navigate to Project

```bash
cd "d:\Projects\impressioncore"
```

### 2. Activate Environment

```bash
.venv310\Scripts\activate
```

### 3. Verify CUDA

```bash
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

### 4. Run Training

```bash
python bulletproof_training_launcher.py
```

That's it! Your multimodal AI training will start immediately.

## What You'll See

1. **Hardware Validation** - System checks your CUDA setup
2. **Dataset Discovery** - Finds and validates real training data
3. **Model Initialization** - Sets up ImpressionCore-B1 (101K parameters)
4. **Training Progress** - Beautiful real-time monitoring
5. **Checkpoint Saving** - Automatic model preservation

## Expected Output

``` text
🚀 ImpressionCore-B1 Production Launcher
✅ CUDA device detected: cuda:0
🚀 GPU: NVIDIA GeForce GTX 1050 Ti (4.0GB VRAM)
📊 Discovered Datasets: 5 text, 10 images, 20 audio files
🧠 Model initialized: 101,386 parameters
⚡ Training started...
```

## Training Results

- **Speed**: ~1-3 seconds per epoch
- **Memory**: <100MB VRAM usage
- **Output**: Trained model + checkpoints
- **Location**: `src/training/checkpoints/`

## Command Options

```bash
# Extended training
python bulletproof_training_launcher.py --epochs 50

# Test only (no training)
python bulletproof_training_launcher.py --test-only

# Verbose output
python bulletproof_training_launcher.py --verbose
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No CUDA" | Install/update NVIDIA drivers + CUDA toolkit |
| "Dataset not found" | Run `python create_minimal_images.py` and `python create_minimal_audio.py` |
| "Import error" | Run `pip install -r requirements.txt` |
| "Memory error" | Reduce batch size in config or free GPU memory |

## Success Indicators

✅ Hardware validation passes  
✅ All datasets discovered  
✅ Model initializes (101,386 params)  
✅ Training completes all epochs  
✅ Checkpoints saved successfully  

## Next Steps

1. Check training logs in console
2. Examine saved models in `src/training/checkpoints/`
3. Experiment with different epochs/batch sizes
4. Scale up with larger datasets

---
**Need Help?** Check the full documentation: `docs/bulletproof_training_system_documentation.md`
