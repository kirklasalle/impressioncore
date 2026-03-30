#!/usr/bin/env bash
# ImpressionCore B2 Enhanced/Optimized Training Launcher
# Phase 1 Step 2: Full-scale, config-driven training
# Date: 2025-07-06
# Author: GitHub Copilot

# Activate environment (Windows Bash)
source .venv310/Scripts/activate

# Run enhanced/optimized training
python src/training/train_b2.py \
  --config b2_phase1_enhanced_config.yaml \
  --output-dir F:/models/b2_enhanced_checkpoints \
  --embed-dir F:/b2_embeddings \
  --manifest-dir F:/b2_datasets
