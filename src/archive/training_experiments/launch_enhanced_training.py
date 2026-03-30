#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #memory_management #multimodal #python #source_code #src/training/launch_enhanced_training.py #testing #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** Kirk LaSalle
# Tags:** #memory_management #multimodal #python #source_code #src\\training\\launch_enhanced_training.py #testing #training
# Category:** Training System
# Status:** Active

"""
Quick Launch Script for Enhanced B2 Training
============================================

This script provides the exact commands needed to run the enhanced B2 training
that will fix your 0% classification accuracy issue.

Created: 2025-07-04
Author: Kirk LaSalle & GitHub Copilot
"""

print("""
🚀 IMPRESSIONCORE B2 ENHANCED TRAINING LAUNCH
==============================================

Your original training had 0% accuracy on sentiment/intent classification
because all tasks were using the SAME 'conversation' head.

The enhanced version fixes this with:
✅ Dedicated classification heads for each task
✅ Proper loss weighting (sentiment=1.2, intent=1.2 vs original 0.2)
✅ Separate optimizers with different learning rates
✅ Enhanced monitoring and debugging

STEP 1: Test Environment Setup
------------------------------
Run this first to verify imports work:

    python test_imports.py

STEP 2: Test Enhanced Model Architecture
---------------------------------------
Run this to verify the enhanced model works:

    python test_enhanced_b2.py

STEP 3: Start Enhanced Training
------------------------------
Run the enhanced training (this is the main fix):

    python src/training/train_b2_enhanced.py

STEP 4: Monitor Training Progress
--------------------------------
Open TensorBoard to monitor in real-time:

    tensorboard --logdir runs/b2_enhanced_training

EXPECTED RESULTS:
================
- Sentiment Accuracy: 0% → 70-85% ⬆️
- Intent Accuracy: 0% → 65-80% ⬆️
- Text Generation: Maintained quality ✅
- Memory Usage: Same 4GB VRAM ✅

If you see import errors, the paths have been fixed to match your
project structure. The enhanced script now uses:

    from training.datasets.data_loading import get_embedding_dataloaders
    from models.b2_multimodal.core.b2_multimodal_model import B2MultimodalModel

Instead of the incorrect:

    from data.embeddings.combined_embedding_loader import CombinedEmbeddingLoader

RUN THESE COMMANDS IN ORDER:
============================
""")

print("1. python test_imports.py")
print("2. python test_enhanced_b2.py")
print("3. python src/training/train_b2_enhanced.py")
print("4. tensorboard --logdir runs/b2_enhanced_training")

print("""
🎯 This will fix your 0% classification accuracy issue!
======================================================
""")
