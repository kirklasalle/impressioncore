#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/phase1_training_automation.py #training
**Category:** Core Implementation
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\phase1_training_automation.py #training
# Category:** Core Implementation
# Status:** Active

"""
Phase 1 Training Automation Script for ImpressionCore
Automates manifest validation, embedding existence check, and both initialization and optimization training runs for repeatability and integrity.
"""
import json
import subprocess
import sys
from pathlib import Path

# CONFIGURABLE PATHS
MANIFEST_DIR = Path("F:/b2_datasets/")
EMBEDDING_CATALOGUE = Path("F:/b2_embeddings/b2_embedding_catalogue.json")
EMBEDDING_ROOT = Path("F:/b2_embeddings/")
TRAIN_SCRIPT = Path("train_b2_enhanced_optimized.py")
PREPARE_SCRIPT = Path("prepare_raw_data.py")
PHASE1_INIT_CONFIG = Path("configs/phase1_init.yaml")  # Optional: adjust as needed
PHASE1_OPT_CONFIG = Path("configs/phase1_optimize.yaml")  # Optional: adjust as needed

# 1. Validate Manifest
print("\n[1/4] Validating manifest...")
subprocess.run([
    sys.executable, str(PREPARE_SCRIPT),
    "--output-dir", str(MANIFEST_DIR),
    "--validate"
], check=True)

# 2. Check Embedding Existence
print("\n[2/4] Checking embedding file existence...")
with open(MANIFEST_DIR / "train_manifest.json", encoding="utf-8") as f:
    train_samples = json.load(f)
with open(MANIFEST_DIR / "val_manifest.json", encoding="utf-8") as f:
    val_samples = json.load(f)
all_samples = train_samples + val_samples
missing = []
for s in all_samples:
    emb_path = Path(s["embedding_path"])
    if not emb_path.exists():
        missing.append(str(emb_path))
if missing:
    print(f"❌ Missing {len(missing)} embedding files:")
    for m in missing[:10]:
        print(f"   • {m}")
    if len(missing) > 10:
        print(f"   ...and {len(missing)-10} more.")
    sys.exit(1)
else:
    print("✅ All embedding files exist.")

# 3. Run Initialization/Embedding Training
print("\n[3/4] Running Phase 1 Initialization/Embedding Training...")
init_cmd = [sys.executable, str(TRAIN_SCRIPT)]
if PHASE1_INIT_CONFIG.exists():
    init_cmd += ["--config", str(PHASE1_INIT_CONFIG)]
subprocess.run(init_cmd, check=True)

# 4. Run Optimize Embedding Training
print("\n[4/4] Running Phase 1 Optimize Embedding Training...")
opt_cmd = [sys.executable, str(TRAIN_SCRIPT), "--mode", "optimize"]
if PHASE1_OPT_CONFIG.exists():
    opt_cmd += ["--config", str(PHASE1_OPT_CONFIG)]
subprocess.run(opt_cmd, check=True)

print("\n✅ Phase 1 automation complete. Both sessions ran successfully and are repeatable.")
