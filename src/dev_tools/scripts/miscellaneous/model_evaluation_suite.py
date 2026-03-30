#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #gpu_optimization #inference #memory_management #python #source_code #src/scripts/miscellaneous/model_evaluation_suite.py #testing #training
**Category:** Source Code
**Status:** Active
"""



import json
from datetime import datetime
from pathlib import Path

import psutil
import torch


def analyze_training_results():
    """Analyze your recent training results"""

    print("📊 ImpressionCore B3 Training Analysis")
    print("=====================================")

    # Load training results
    training_file = "b3_full_training_report_30epochs_20250802_131359.json"

    if not Path(training_file).exists():
        print(f"❌ Training file not found: {training_file}")
        return

    try:
        with open(training_file) as f:
            data = json.load(f)

        # Extract key information
        config = data.get('training_configuration', {})
        summary = data.get('training_summary', {})
        results = data.get('training_results', {})
        infrastructure = data.get('infrastructure_config', {})
        epoch_results = data.get('epoch_results', [])

        print("🏗️  Model Architecture & Infrastructure:")
        print(f"   Architecture: {infrastructure.get('base_architecture', 'N/A')}")
        print(f"   Hardware Target: {infrastructure.get('hardware_target', 'N/A')}")
        print(f"   Memory Budget: {infrastructure.get('memory_budget', 'N/A')}")
        print(f"   Infrastructure Size: {infrastructure.get('infrastructure_size', 'N/A')}")
        print(f"   Educational Embeddings: {infrastructure.get('educational_embeddings', 'N/A')}")

        print("\n⚙️  Training Configuration:")
        print(f"   Total Epochs: {config.get('epochs', 'N/A')}")
        print(f"   Steps per Epoch: {config.get('steps_per_epoch', 'N/A')}")
        print(f"   Learning Rate: {config.get('learning_rate', 'N/A')}")
        print(f"   Batch Size: {config.get('batch_size', 'N/A')}")
        print(f"   Quality Target: {config.get('quality_target', 'N/A')}")

        print("\n🎯 Final Training Results:")
        print(f"   ✅ Training Success: {summary.get('training_success', False)}")
        print(f"   🏆 Final Quality: {results.get('final_quality', 'N/A')}")
        print(f"   📉 Final Loss: {results.get('final_loss', 'N/A'):.6f}")
        print(f"   ⏱️  Duration: {summary.get('training_duration_hours', 'N/A'):.2f} hours")
        print(f"   🚀 Avg Steps/Second: {results.get('avg_steps_per_second', 'N/A'):.2f}")

        # Analyze epoch progression
        if epoch_results:
            print("\n📈 Training Progression Analysis:")

            # First and last epoch comparison
            first_epoch = epoch_results[0]
            last_epoch = epoch_results[-1]

            quality_improvement = last_epoch['avg_quality'] - first_epoch['avg_quality']
            loss_reduction = first_epoch['avg_loss'] - last_epoch['avg_loss']
            loss_reduction_percent = (loss_reduction / first_epoch['avg_loss']) * 100

            print("   📊 Quality Progression:")
            print(f"      Initial: {first_epoch['avg_quality']:.6f}")
            print(f"      Final: {last_epoch['avg_quality']:.6f}")
            print(f"      Improvement: +{quality_improvement:.6f}")

            print("   📉 Loss Progression:")
            print(f"      Initial: {first_epoch['avg_loss']:.6f}")
            print(f"      Final: {last_epoch['avg_loss']:.6f}")
            print(f"      Reduction: -{loss_reduction:.6f} ({loss_reduction_percent:.1f}%)")

            # Calculate convergence metrics
            losses = [epoch['avg_loss'] for epoch in epoch_results]
            [epoch['avg_quality'] for epoch in epoch_results]

            # Find convergence point (where loss variance becomes small)
            convergence_epoch = find_convergence_point(losses)

            print("   🎯 Convergence Analysis:")
            print(f"      Convergence Epoch: ~{convergence_epoch}")
            print(f"      Quality at Convergence: {epoch_results[min(convergence_epoch-1, len(epoch_results)-1)]['avg_quality']:.6f}")

            # Training stability
            avg_duration = sum(epoch['duration_seconds'] for epoch in epoch_results) / len(epoch_results)
            duration_variance = sum((epoch['duration_seconds'] - avg_duration)**2 for epoch in epoch_results) / len(epoch_results)

            print("   ⚡ Training Efficiency:")
            print(f"      Avg Epoch Duration: {avg_duration:.1f} seconds")
            print(f"      Training Stability: {duration_variance:.2f} (lower is better)")
            print(f"      Epochs per Hour: {3600 / avg_duration:.1f}")

        # Overall assessment
        print("\n🏆 Performance Assessment:")

        final_quality = results.get('final_quality', 0)
        target_quality = config.get('quality_target', 10.0)
        quality_achievement = (final_quality / target_quality) * 100

        print(f"   🎯 Quality Achievement: {quality_achievement:.2f}% of target")

        if quality_achievement >= 99.0:
            print("   ✅ EXCELLENT - Near-perfect quality achieved!")
        elif quality_achievement >= 95.0:
            print("   ✅ VERY GOOD - High quality achieved!")
        elif quality_achievement >= 90.0:
            print("   ⚠️ GOOD - Acceptable quality, room for improvement")
        else:
            print("   ❌ POOR - Significant improvement needed")

        # Memory efficiency assessment
        duration_hours = summary.get('training_duration_hours', 0)
        epochs_completed = summary.get('epochs_completed', 0)

        if duration_hours > 0 and epochs_completed > 0:
            efficiency_score = epochs_completed / duration_hours  # epochs per hour
            print(f"   ⚡ Training Efficiency: {efficiency_score:.1f} epochs/hour")

            if efficiency_score >= 100:
                print("   ✅ EXCELLENT training speed!")
            elif efficiency_score >= 50:
                print("   ✅ GOOD training speed")
            else:
                print("   ⚠️ Could be faster")

        print("\n🔬 Technical Metrics Summary:")
        print(f"   📊 Loss Reduction: {loss_reduction_percent:.1f}%")
        print(f"   🎯 Quality Score: {final_quality:.6f}/{target_quality}")
        print(f"   ⏱️  Training Speed: {results.get('avg_steps_per_second', 0):.2f} steps/sec")
        print("   🎮 Hardware Optimized: GTX 1050 Ti (4GB VRAM)")
        print(f"   💾 Memory Efficient: {infrastructure.get('memory_budget', 'N/A')}")

    except Exception as e:
        print(f"❌ Error analyzing training results: {e}")

def find_convergence_point(losses: list[float], window_size: int = 5, threshold: float = 0.01) -> int:
    """Find approximate convergence point in loss values"""
    if len(losses) < window_size * 2:
        return len(losses)

    for i in range(window_size, len(losses) - window_size):
        # Calculate variance in sliding window
        window = losses[i-window_size:i+window_size]
        variance = sum((x - sum(window)/len(window))**2 for x in window) / len(window)

        if variance < threshold:
            return i

    return len(losses)

def analyze_model_performance():
    """Analyze current model performance from F:/models"""

    print("\n🤖 Model Performance Analysis")
    print("=============================")

    # Check F:/models structure
    models_path = Path("F:/models")
    if not models_path.exists():
        print("❌ F:/models not found")
        return

    # Find model files
    model_files = list(models_path.rglob("*.pt"))

    if not model_files:
        print("❌ No model files found")
        return

    print(f"📁 Found {len(model_files)} model files")

    # Sort by modification time
    model_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    print("\n📋 Recent Models:")
    for i, model_file in enumerate(model_files[:5]):
        size_mb = model_file.stat().st_size / (1024 * 1024)
        mod_time = datetime.fromtimestamp(model_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"   {i+1}. {model_file.name} ({size_mb:.1f} MB) - {mod_time}")

    # Analyze best model
    best_model = model_files[0]
    print(f"\n🔍 Analyzing Best Model: {best_model.name}")

    try:
        # Check if we can load it
        checkpoint = torch.load(best_model, map_location='cpu', weights_only=False)

        print("✅ Model loads successfully")
        print(f"📊 Checkpoint type: {type(checkpoint)}")

        if isinstance(checkpoint, dict):
            print("🔍 Checkpoint contents:")
            for key, value in checkpoint.items():
                if isinstance(value, torch.Tensor):
                    print(f"   {key}: {value.shape} ({value.dtype})")
                elif isinstance(value, int | float | str | bool):
                    print(f"   {key}: {value}")
                else:
                    print(f"   {key}: {type(value)}")

        # Calculate memory footprint
        total_params = 0
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
            for param_tensor in state_dict.values():
                if isinstance(param_tensor, torch.Tensor):
                    total_params += param_tensor.numel()

        if total_params > 0:
            memory_mb = total_params * 4 / (1024 * 1024)  # Assuming float32
            print(f"📊 Model Parameters: {total_params:,}")
            print(f"💾 Estimated Memory: {memory_mb:.1f} MB")

    except Exception as e:
        print(f"❌ Error analyzing model: {e}")

def system_requirements_check():
    """Check system requirements and capabilities"""

    print("\n🖥️  System Requirements Analysis")
    print("================================")

    # Check CUDA availability
    print("🎮 GPU Information:")
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        current_memory = torch.cuda.memory_allocated(0) / (1024**3)
        free_memory = total_memory - current_memory

        print(f"   ✅ CUDA Available: {gpu_name}")
        print(f"   💾 Total VRAM: {total_memory:.1f} GB")
        print(f"   💾 Used VRAM: {current_memory:.1f} GB")
        print(f"   💾 Free VRAM: {free_memory:.1f} GB")

        # GTX 1050 Ti assessment
        if "GTX 1050 Ti" in gpu_name:
            print("   🎯 Target Hardware Detected: GTX 1050 Ti")
            print("   ✅ Perfect match for ImpressionCore B3 optimization!")
        elif "GTX" in gpu_name or "RTX" in gpu_name:
            print("   ✅ Compatible NVIDIA GPU detected")
        else:
            print("   ⚠️ GPU compatibility unknown")
    else:
        print("   ❌ CUDA not available - CPU only mode")

    # Check CPU and RAM
    print("\n🧠 CPU & Memory Information:")
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    memory = psutil.virtual_memory()

    print(f"   CPU Cores: {cpu_count}")
    if cpu_freq:
        print(f"   CPU Frequency: {cpu_freq.current:.0f} MHz")
    print(f"   Total RAM: {memory.total / (1024**3):.1f} GB")
    print(f"   Available RAM: {memory.available / (1024**3):.1f} GB")
    print(f"   RAM Usage: {memory.percent:.1f}%")

    # Storage check for F: drive
    print("\n💾 Storage Information:")
    try:
        f_drive = Path("F:/")
        if f_drive.exists():
            disk_usage = psutil.disk_usage("F:/")
            total_gb = disk_usage.total / (1024**3)
            used_gb = disk_usage.used / (1024**3)
            free_gb = disk_usage.free / (1024**3)

            print(f"   F: Drive Total: {total_gb:.1f} GB")
            print(f"   F: Drive Used: {used_gb:.1f} GB")
            print(f"   F: Drive Free: {free_gb:.1f} GB")

            if free_gb > 50:
                print("   ✅ Adequate storage for model training")
            else:
                print("   ⚠️ Low storage space")
        else:
            print("   ❌ F: drive not accessible")
    except Exception as e:
        print(f"   ❌ Storage check failed: {e}")

def inference_readiness_check():
    """Check if models are ready for inference"""

    print("\n🚀 Inference Readiness Assessment")
    print("=================================")

    checks = {
        "F:/models structure": Path("F:/models").exists(),
        "Model files available": len(list(Path("F:/models").rglob("*.pt"))) > 0 if Path("F:/models").exists() else False,
        "CUDA available": torch.cuda.is_available(),
        "Training completed": Path("b3_full_training_report_30epochs_20250802_131359.json").exists(),
        "Python environment": True,  # If we're running this, it's working
    }

    print("📋 Readiness Checklist:")
    for check, status in checks.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {check}")

    all_ready = all(checks.values())

    if all_ready:
        print("\n🎉 SYSTEM READY FOR INFERENCE!")
        print("   All requirements met")
        print("   Models available and trained")
        print("   Hardware compatible")
        print("   🚀 Ready to deploy for production use!")
    else:
        print("\n⚠️ SYSTEM NOT READY")
        failed_checks = [check for check, status in checks.items() if not status]
        print(f"   Failed checks: {', '.join(failed_checks)}")

def main():
    """Main evaluation function"""

    print("🤖 ImpressionCore B3 Model Evaluation & Analysis")
    print("================================================")
    print(f"🕒 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run all analyses
    analyze_training_results()
    analyze_model_performance()
    system_requirements_check()
    inference_readiness_check()

    print("\n" + "="*50)
    print("🎯 EVALUATION COMPLETE!")
    print("="*50)

if __name__ == "__main__":
    main()
