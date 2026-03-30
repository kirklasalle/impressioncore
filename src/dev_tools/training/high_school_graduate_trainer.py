#!/usr/bin/env python3
"""
ImpressionCore High School Graduate Training Launcher

File: high_school_graduate_trainer.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-12
Modified: 2025-06-12
Version: 1.0.0

Description:
Production-ready launcher for training ImpressionCore to achieve high school
graduate level text conversation capabilities through knowledge distillation.

Usage:
    python high_school_graduate_trainer.py [options]
"""

import sys
import os
from pathlib import Path
import argparse
import torch
from datetime import datetime

# Ensure we can import from src
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def setup_environment():
    """Setup the training environment"""
    print("🔧 Setting up ImpressionCore training environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ required")
        sys.exit(1)
    
    # Check for required directories
    required_dirs = [
        "src/training",
        "src/models",
        "src/core/utils",
        "src/interfaces/cli"
    ]
    
    for dir_path in required_dirs:
        if not (project_root / dir_path).exists():
            print(f"❌ Error: Required directory missing: {dir_path}")
            sys.exit(1)
    
    # Check CUDA availability
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        device_name = torch.cuda.get_device_name(0)
        memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✅ CUDA available: {device_name} ({memory_gb:.1f}GB)")
    else:
        print("⚠️  CUDA not available - will use CPU (slower training)")
    
    return cuda_available

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description="ImpressionCore High School Graduate Training Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎓 TRAINING OBJECTIVE:
Train ImpressionCore to achieve high school graduate level text conversation
through advanced knowledge distillation techniques.

🎯 TARGET COMPETENCIES:
- Academic discussion and reasoning
- Subject matter comprehension (literature, science, math, history)
- Peer-level conversation and collaboration
- Critical thinking and analysis
- Study guidance and learning support

💡 EXAMPLES:
  # Quick start with default settings
  python high_school_graduate_trainer.py
  
  # Custom training configuration
  python high_school_graduate_trainer.py --epochs 15 --batch-size 2 --learning-rate 1e-5
  
  # Evaluate existing model
  python high_school_graduate_trainer.py --evaluate --model models/my_model.pth
  
  # Interactive chat testing
  python high_school_graduate_trainer.py --chat --model models/my_model.pth

🔧 SYSTEM REQUIREMENTS:
- Python 3.8+
- PyTorch with CUDA support (recommended)
- 4GB+ GPU VRAM (GTX 1050 Ti optimized)
- 8GB+ system RAM
        """
    )
    
    # Main commands
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--train', action='store_true', default=True,
                      help='Start high school graduate training (default)')
    group.add_argument('--evaluate', action='store_true',
                      help='Evaluate trained model conversation skills')
    group.add_argument('--chat', action='store_true',
                      help='Interactive chat with trained model')
    group.add_argument('--list-models', action='store_true',
                      help='List available trained models')
    
    # Training parameters
    parser.add_argument('--epochs', type=int, default=10,
                       help='Number of training epochs (default: 10)')
    parser.add_argument('--batch-size', type=int, default=4,
                       help='Training batch size (default: 4, optimized for 4GB VRAM)')
    parser.add_argument('--learning-rate', type=float, default=2e-5,
                       help='Learning rate (default: 2e-5)')
    parser.add_argument('--temperature', type=float, default=4.0,
                       help='Distillation temperature (default: 4.0)')
    
    # Model configuration
    parser.add_argument('--teacher-model', type=str, default="microsoft/DialoGPT-medium",
                       help='Teacher model for knowledge distillation')
    parser.add_argument('--model', type=str,
                       help='Path to model file for evaluation/chat')
    
    # System optimization
    parser.add_argument('--cpu-only', action='store_true',
                       help='Force CPU-only training (not recommended)')
    parser.add_argument('--no-mixed-precision', action='store_true',
                       help='Disable mixed precision training')
    parser.add_argument('--max-memory', type=int, default=3500,
                       help='Maximum GPU memory usage in MB (default: 3500)')
    
    # Convenience options
    parser.add_argument('--quick', action='store_true',
                       help='Quick training mode (5 epochs, smaller batch)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Skip confirmation prompts')
    
    args = parser.parse_args()
    
    # Apply quick mode settings
    if args.quick:
        args.epochs = 5
        args.batch_size = 2
        print("⚡ Quick training mode enabled (5 epochs, batch size 2)")
    
    # Setup environment
    cuda_available = setup_environment()
    
    if args.cpu_only:
        os.environ['CUDA_VISIBLE_DEVICES'] = ''
        cuda_available = False
    
    # Display configuration
    print("\n🎓 ImpressionCore High School Graduate Training")
    print("=" * 60)
    print(f"Objective: Train to high school graduate conversation level")
    print(f"Method: Knowledge distillation with conversation focus")
    print(f"Target Hardware: GTX 1050 Ti (4GB VRAM)")
    print(f"Device: {'CUDA' if cuda_available else 'CPU'}")
    print()
    
    # Route to appropriate CLI module
    try:
        from interfaces.cli.high_school_training_cli import (
            train_command, evaluate_command, chat_command, list_models_command
        )
        
        # Convert args for CLI module
        if args.train or (not args.evaluate and not args.chat and not args.list_models):
            print("🚀 Starting high school graduate training...")
            train_command(args)
        elif args.evaluate:
            if not args.model:
                print("❌ Error: --model required for evaluation")
                return
            args.model_path = args.model
            evaluate_command(args)
        elif args.chat:
            if not args.model:
                print("❌ Error: --model required for chat")
                return
            args.model_path = args.model
            chat_command(args)
        elif args.list_models:
            list_models_command(args)
            
    except ImportError as e:
        print(f"❌ Error importing training modules: {e}")
        print("Make sure all ImpressionCore modules are properly installed.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Training error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
