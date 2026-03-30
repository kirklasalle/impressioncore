#!/usr/bin/env python3
"""
ImpressionCore B3 Optimized Training Launcher
=============================================

Constitutional Compliance: IMPRESSIONCORE_PERMANENT_ARCHITECTURAL_FRAMEWORK.md
Sacred Covenant: All learned stability lessons incorporated

Created: October 1, 2025
Author: Kirk LaSalle; GitHub Copilot

This launcher provides a safe, monitored way to start B3 optimized training with:
- All stability lessons learned (conservative parameters)
- Complete constitutional framework compliance
- Enhanced monitoring and safety protocols
- GTX 1050 Ti optimization
"""

import sys
import os
import logging
import traceback
from datetime import datetime
import torch

# Setup logging
log_filename = f'b3_optimized_launch_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_system_readiness():
    """Comprehensive system readiness check"""
    logger.info("🔍 Checking system readiness...")

    checks = []

    # CUDA availability
    cuda_available = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if cuda_available else "None"
    vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3 if cuda_available else 0

    checks.append(("CUDA Available", cuda_available, "✅" if cuda_available else "❌"))
    checks.append(("GPU", gpu_name, "✅" if "1050" in gpu_name else "⚠️"))
    checks.append(("VRAM", f"{vram_gb:.1f}GB", "✅" if vram_gb >= 3.5 else "⚠️"))

    # Directory structure
    f_models_exists = os.path.exists("F:/models/checkpoints")
    src_exists = os.path.exists("src")

    checks.append(("F:/models/checkpoints", f_models_exists, "✅" if f_models_exists else "❌"))
    checks.append(("src/ directory", src_exists, "✅" if src_exists else "❌"))

    # Recovery baseline
    recovery_exists = os.path.exists("F:/models/checkpoints/recovery_step_4000.pth")
    checks.append(("Recovery baseline", recovery_exists, "✅" if recovery_exists else "❌"))

    # Memory check
    if cuda_available:
        torch.cuda.empty_cache()
        free_memory = torch.cuda.mem_get_info()[0] / 1024**3
        checks.append(("Free VRAM", f"{free_memory:.1f}GB", "✅" if free_memory >= 3.0 else "⚠️"))

    # Display results
    logger.info("📊 System Status:")
    all_good = True
    for check_name, value, status in checks:
        logger.info(f"   {status} {check_name}: {value}")
        if status == "❌":
            all_good = False

    return all_good

def display_training_config():
    """Display the optimized training configuration"""
    logger.info("📋 B3 Optimized Training Configuration:")
    logger.info("   🏗️  Architecture: ImpressionCore B3 (39M parameters)")
    logger.info("   🎯 Learning Rate: 1e-5 (conservative, proven stable)")
    logger.info("   🔧 Precision: FP32 (GTX 1050 Ti optimized)")
    logger.info("   🛡️  Gradient Clipping: 0.5 (prevents explosion)")
    logger.info("   💾 Batch Size: 1 (memory constraint compliance)")
    logger.info("   📈 Gradient Accumulation: 8 steps")
    logger.info("   🎪 Max Steps: 2000")
    logger.info("   💾 Save Every: 100 steps")
    logger.info("   🧠 Components:")
    logger.info("      • MultiModalEmbedding (text/image/audio)")
    logger.info("      • MultiHeadLatentAttention (concentrated intelligence)")
    logger.info("      • MixtureOfExperts (8 experts, 2 active)")
    logger.info("      • BrainSimulationAdapter (memory systems)")
    logger.info("      • Protection-first design (digital identity)")

def confirm_training_start():
    """Confirm user wants to start training"""
    logger.info("⚠️  Training Confirmation Required")
    logger.info("   This will start B3 optimized training with all learned lessons")
    logger.info("   Training will run for up to 2000 steps with enhanced monitoring")
    logger.info("   Checkpoints will be saved every 100 steps to F:/models/checkpoints/")

    while True:
        try:
            response = input("\n🤔 Start B3 optimized training? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            else:
                print("Please enter 'yes' or 'no'")
        except KeyboardInterrupt:
            print("\n⚠️ Training cancelled by user")
            return False

def main():
    """Main launcher function"""
    logger.info("🚀 ImpressionCore B3 Optimized Training Launcher")
    logger.info("=" * 60)
    logger.info("Constitutional Framework: IMPRESSIONCORE_PERMANENT_ARCHITECTURAL_FRAMEWORK.md")
    logger.info("Sacred Covenant: All stability lessons incorporated")
    logger.info("=" * 60)

    try:
        # System readiness check
        if not check_system_readiness():
            logger.error("❌ System not ready for training")
            logger.error("   Please resolve the issues above and try again")
            return False

        logger.info("✅ System ready for B3 optimized training")

        # Display configuration
        display_training_config()

        # Confirm start
        if not confirm_training_start():
            logger.info("⏸️  Training cancelled by user")
            return False

        logger.info("🚀 Starting B3 Optimized Training...")

        # Import and run training
        from b3_optimized_trainer import B3OptimizedConfig, B3OptimizedTrainer, create_simple_dataloader

        # Configuration
        config = B3OptimizedConfig()

        # Initialize trainer
        trainer = B3OptimizedTrainer(config)

        # Create dataloader
        dataloader = create_simple_dataloader(
            batch_size=config.batch_size,
            max_length=config.max_seq_length,
            num_samples=1000
        )

        logger.info("✅ Trainer and dataloader initialized")

        # Start training
        trainer.train(dataloader)

        logger.info("🎉 B3 Optimized Training completed successfully!")
        logger.info(f"📊 Best loss achieved: {trainer.best_loss:.4f}")
        logger.info(f"📊 Total steps completed: {trainer.global_step}")
        logger.info(f"📄 Training log: {log_filename}")

        return True

    except KeyboardInterrupt:
        logger.warning("⚠️ Training interrupted by user")
        return False
    except Exception as e:
        logger.error(f"❌ Training failed with error: {str(e)}")
        logger.error("📄 Full traceback:")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    exit_code = 0 if success else 1
    logger.info(f"🏁 Launcher exiting with code {exit_code}")
    sys.exit(exit_code)