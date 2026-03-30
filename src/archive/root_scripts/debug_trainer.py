"""
Debug script to trace trainer startup issues.
Run this with: python -u debug_trainer.py
"""
import sys
print("DEBUG [1/10]: Script started", flush=True)

print("DEBUG [2/10]: Importing os, sys, pathlib...", flush=True)
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
print(f"DEBUG [3/10]: Project root: {PROJECT_ROOT}", flush=True)

print("DEBUG [4/10]: Importing torch...", flush=True)
import torch
print(f"DEBUG [4/10]: Torch version: {torch.__version__}, CUDA: {torch.cuda.is_available()}", flush=True)

print("DEBUG [5/10]: Importing transformers...", flush=True)
from transformers import AutoTokenizer
print("DEBUG [5/10]: Transformers imported successfully", flush=True)

print("DEBUG [6/10]: Importing rich...", flush=True)
try:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    print("DEBUG [6/10]: Rich imported successfully", flush=True)
except ImportError as e:
    print(f"DEBUG [6/10]: Rich not available: {e}", flush=True)
    console = None

print("DEBUG [7/10]: Importing DiverseCurriculumLoader...", flush=True)
try:
    from src.training.data.diverse_curriculum_loader import DiverseCurriculumLoader, CurriculumConfig
    print("DEBUG [7/10]: DiverseCurriculumLoader imported", flush=True)
except Exception as e:
    print(f"DEBUG [7/10]: ERROR importing DiverseCurriculumLoader: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("DEBUG [8/10]: Importing B3 model architecture...", flush=True)
try:
    from src.core.models.impressioncore_b3_architecture import ImpressionCoreB3Model, B3Config
    print("DEBUG [8/10]: B3 architecture imported", flush=True)
except Exception as e:
    print(f"DEBUG [8/10]: ERROR importing B3 architecture: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("DEBUG [9/10]: Checking checkpoint path...", flush=True)
checkpoint_path = Path("F:/models/checkpoints/kd_sft_phase2/step_5000.pt")
if checkpoint_path.exists():
    print(f"DEBUG [9/10]: Checkpoint exists: {checkpoint_path}", flush=True)
    ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    print(f"DEBUG [9/10]: Checkpoint keys: {list(ckpt.keys())}", flush=True)
    print(f"DEBUG [9/10]: global_step: {ckpt.get('global_step', 'N/A')}", flush=True)
else:
    print(f"DEBUG [9/10]: Checkpoint NOT FOUND: {checkpoint_path}", flush=True)

print("DEBUG [10/10]: Checking output directory...", flush=True)
output_dir = Path("F:/models/checkpoints/diverse_curriculum_mhc_ultra")
try:
    os.makedirs(output_dir, exist_ok=True)
    print(f"DEBUG [10/10]: Output dir ok: {output_dir}", flush=True)
except Exception as e:
    print(f"DEBUG [10/10]: ERROR with output dir: {e}", flush=True)

print("\n" + "="*60, flush=True)
print("All imports and checks passed!", flush=True)
print("="*60, flush=True)

print("\nNow importing the full trainer module...", flush=True)
try:
    from src.training.pipelines import diverse_curriculum_trainer
    print("Trainer module imported successfully!", flush=True)

    print("\nCreating config...", flush=True)
    config = diverse_curriculum_trainer.DiverseTrainingConfig()
    print(f"Config created: output_dir={config.output_dir}", flush=True)

    print("\nConfig details:", flush=True)
    print(f"  - base_checkpoint_path: {config.base_checkpoint_path}", flush=True)
    print(f"  - use_mhc: {config.use_mhc}", flush=True)
    print(f"  - b3_ultra: {config.b3_ultra}", flush=True)
    print(f"  - max_steps: {config.max_steps}", flush=True)
    print(f"  - global_step would start at: 0 (or from checkpoint)", flush=True)

except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60, flush=True)
print("DEBUG COMPLETE - All checks passed!", flush=True)
print("="*60, flush=True)
print("\nTo run the actual trainer, use:", flush=True)
print("  python -u src/training/pipelines/diverse_curriculum_trainer.py", flush=True)
