#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #cuda #memory_management #multimodal #python #source_code #src/training/b3/b3_training_quickstart.py #testing #training
**Category:** Training System
**Status:** Active
"""



import argparse
import os
import sys
from pathlib import Path

import torch
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

console = Console()

def check_cuda_compatibility():
    """Check CUDA availability and compatibility"""

    console.print("🔍 [bold blue]Checking CUDA compatibility...")

    if not torch.cuda.is_available():
        console.print("❌ [bold red]CUDA not available! Training will use CPU (very slow)")
        return False

    device_count = torch.cuda.device_count()
    device_name = torch.cuda.get_device_name(0)
    memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3

    console.print("✅ [bold green]CUDA available!")
    console.print(f"   Device: {device_name}")
    console.print(f"   Memory: {memory_total:.1f} GB")
    console.print(f"   Device Count: {device_count}")

    # Check if it's GTX 1050 Ti or similar
    if "1050" in device_name:
        console.print("🎯 [bold cyan]GTX 1050 Ti detected - using optimized settings")
    elif memory_total < 6.0:
        console.print("⚠️ [bold yellow]Low VRAM detected - using conservative settings")

    return True

def fix_device_compatibility():
    """Fix device compatibility issues in B3 integration"""

    console.print("🔧 [bold blue]Fixing device compatibility...")

    try:
        # Import and test B3 integration
        from core.models.b3_unified_integration import create_optimized_b3_system

        # Create system and test device placement
        with console.status("Creating optimized B3 system..."):
            system = create_optimized_b3_system()

        # Test basic functionality
        with console.status("Testing device compatibility..."):
            # Move all components to the same device
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

            # Ensure model is on correct device
            system = system.to(device)

            # Test with a simple input
            test_input = "Hello, this is a device compatibility test."
            try:
                system.process_text_only(test_input)
                console.print("✅ [bold green]Device compatibility fixed!")
                return True
            except RuntimeError as e:
                if "device" in str(e).lower():
                    console.print(f"⚠️ [bold yellow]Device mismatch detected: {e}")
                    console.print("🔄 [bold blue]Attempting automatic fix...")

                    # Force all tensors to same device
                    for _name, param in system.named_parameters():
                        if param.device != device:
                            param.data = param.data.to(device)

                    # Test again
                    system.process_text_only(test_input)
                    console.print("✅ [bold green]Device compatibility fixed with tensor migration!")
                    return True
                else:
                    raise e from e

    except Exception as e:
        console.print(f"❌ [bold red]Device compatibility fix failed: {e}")
        return False

def verify_f_drive_infrastructure():
    """Verify F: drive training infrastructure"""

    console.print("📁 [bold blue]Verifying F: drive infrastructure...")

    required_paths = {
        "F:/data/datasets": "Training datasets",
        "F:/models": "Model storage",
        "F:/models/checkpoints": "Model checkpoints",
        "F:/models/training": "Training artifacts"
    }

    issues = []

    for path_str, description in required_paths.items():
        path = Path(path_str)
        if path.exists():
            console.print(f"   ✅ {description}: {path}")
        else:
            console.print(f"   ❌ {description}: {path} [bold red](MISSING)")
            issues.append((path, description))

    if issues:
        console.print("\n🔧 [bold blue]Creating missing directories...")
        for path, _description in issues:
            path.mkdir(parents=True, exist_ok=True)
            console.print(f"   ✅ Created: {path}")

    # Check disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage("F:/")
        free_gb = free / 1024**3

        console.print(f"💾 [bold blue]F: drive space: {free_gb:.1f} GB available")

        if free_gb < 10:
            console.print("⚠️ [bold yellow]Warning: Low disk space on F: drive")
        else:
            console.print("✅ [bold green]Sufficient disk space available")

    except Exception as e:
        console.print(f"⚠️ [bold yellow]Could not check F: drive space: {e}")

    return len(issues) == 0

def check_model_availability():
    """Check for available models and checkpoints"""

    console.print("🤖 [bold blue]Checking model availability...")

    models_path = Path("F:/models")
    checkpoints_path = models_path / "checkpoints" / "b3"

    if not checkpoints_path.exists():
        console.print("📁 [bold blue]Creating checkpoints directory...")
        checkpoints_path.mkdir(parents=True, exist_ok=True)

    # Look for existing checkpoints
    checkpoints = list(checkpoints_path.glob("*.pth"))

    if checkpoints:
        console.print(f"✅ [bold green]Found {len(checkpoints)} existing checkpoints")

        # Check for best model
        best_model = checkpoints_path / "b3_best_quality_model.pth"
        if best_model.exists():
            console.print("🏆 [bold cyan]Best quality model available for resume training")
        else:
            console.print("📋 [bold blue]Multiple checkpoints available")
    else:
        console.print("📝 [bold blue]No existing checkpoints - will start training from scratch")

    return True

def prepare_training_environment():
    """Prepare the complete training environment"""

    console.print(Panel.fit(
        "🚀 Preparing ImpressionCore B3 Training Environment",
        title="Environment Setup"
    ))

    steps = [
        ("CUDA Compatibility", check_cuda_compatibility),
        ("Device Fix", fix_device_compatibility),
        ("F: Drive Infrastructure", verify_f_drive_infrastructure),
        ("Model Availability", check_model_availability)
    ]

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]"),
        console=console
    )

    all_success = True

    with progress:
        for step_name, step_func in steps:
            task = progress.add_task(f"Checking {step_name}...", total=None)

            try:
                success = step_func()
                if success:
                    progress.update(task, description=f"✅ {step_name}")
                else:
                    progress.update(task, description=f"❌ {step_name}")
                    all_success = False
            except Exception as e:
                progress.update(task, description=f"❌ {step_name}: {e}")
                all_success = False

    return all_success

def start_training(phase: str, modality: str, epochs: int, quality_target: float):
    """Start the training pipeline"""

    console.print("\n🎯 [bold green]Starting B3 Training Pipeline")
    console.print(f"   Phase: {phase}")
    console.print(f"   Modality: {modality}")
    console.print(f"   Epochs: {epochs}")
    console.print(f"   Quality Target: {quality_target}/10.0")

    # Import training pipeline
    try:
        from training.b3_unified_training_pipeline import B3TrainingPipeline, TrainingConfig

        # Create training configuration
        config = TrainingConfig(
            phase=phase,
            modality=modality,
            max_epochs=epochs,
            quality_target=quality_target,
            batch_size=8,  # GTX 1050 Ti optimized
            gradient_accumulation_steps=4,
            mixed_precision=True,
            gradient_checkpointing=True
        )

        # Initialize and start training
        pipeline = B3TrainingPipeline(config)
        pipeline.train()

        return True

    except Exception as e:
        console.print(f"❌ [bold red]Training failed to start: {e}")
        console.print("🔍 [bold blue]Troubleshooting suggestions:")
        console.print("   1. Ensure you're in the correct directory")
        console.print("   2. Check that all dependencies are installed")
        console.print("   3. Verify CUDA drivers are up to date")
        console.print("   4. Try running with --cpu-only flag")
        return False

def main():
    """Main quick start function"""

    parser = argparse.ArgumentParser(description="B3 Training Quick Start")
    parser.add_argument("--phase", choices=["single_modal", "cross_modal", "multimodal"],
                       default="single_modal", help="Training phase")
    parser.add_argument("--modality", choices=["text", "image", "audio", "video", "all"],
                       default="text", help="Target modality for single_modal phase")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--quality-target", type=float, default=10.0, help="Target quality score")
    parser.add_argument("--skip-checks", action="store_true", help="Skip environment checks")
    parser.add_argument("--cpu-only", action="store_true", help="Force CPU-only training")

    args = parser.parse_args()

    # Force CPU if requested
    if args.cpu_only:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    console.print("[bold cyan]🤖 ImpressionCore B3 Training Quick Start")
    console.print(f"[bold blue]Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Environment preparation
    if not args.skip_checks and not prepare_training_environment():
        console.print("\n❌ [bold red]Environment preparation failed!")
        console.print("🔧 [bold blue]Try running with --skip-checks to bypass checks")
        return 1

    console.print("\n✅ [bold green]Environment ready for training!")

    # Start training
    success = start_training(args.phase, args.modality, args.epochs, args.quality_target)

    if success:
        console.print("\n🎉 [bold green]Training completed successfully!")
        console.print("📊 [bold blue]Check F:/models/training/ for logs and reports")
        console.print("🏆 [bold cyan]Best model saved to F:/models/checkpoints/b3/b3_best_quality_model.pth")
        return 0
    else:
        console.print("\n❌ [bold red]Training failed!")
        return 1

if __name__ == "__main__":
    from datetime import datetime
    sys.exit(main())
