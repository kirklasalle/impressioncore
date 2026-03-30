#!/usr/bin/env python3
"""
ImpressionCore High School Training Demo Script

File: demo_high_school_training.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-12
Version: 1.0.0

Description:
Demonstration script showing how to use the ImpressionCore High School Graduate
training system. Provides examples and walkthroughs for training and testing.
"""

import sys
import os
from pathlib import Path
import subprocess

def print_header():
    """Print demo header"""
    print("🎓" + "=" * 70)
    print("   ImpressionCore High School Graduate Training Demonstration")
    print("=" * 72)
    print("   Build AI that can hold high school level academic conversations")
    print("   through advanced knowledge distillation techniques")
    print("=" * 72)

def check_system():
    """Check system readiness"""
    print("\n🔧 SYSTEM CHECK")
    print("-" * 30)
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"✅ Python Version: {python_version}")
    
    # Check if we're in the right directory
    if not Path("src/training").exists():
        print("❌ Error: Please run from ImpressionCore root directory")
        print("   Expected directory structure with src/training")
        return False
    
    print("✅ Directory: ImpressionCore root found")
    
    # Check for key files
    key_files = [
        "src/training/high_school_distillation_trainer.py",
        "src/interfaces/cli/high_school_training_cli.py",
        "high_school_graduate_trainer.py"
    ]
    
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            return False
    
    return True

def demo_quick_training():
    """Demonstrate quick training"""
    print("\n🚀 DEMO 1: QUICK TRAINING (5 EPOCHS)")
    print("-" * 40)
    print("This demonstrates a quick training run to test the system:")
    print()
    print("Command to run:")
    print("  python high_school_graduate_trainer.py --quick")
    print()
    print("What this does:")
    print("  • Trains for 5 epochs (faster than full 10)")
    print("  • Uses batch size 2 (memory efficient)")
    print("  • Shows real-time training progress")
    print("  • Evaluates conversation skills")
    print("  • Saves trained model")
    print()
    
    response = input("Run quick training demo? (y/N): ")
    if response.lower() == 'y':
        try:
            print("\n⚡ Starting quick training...")
            subprocess.run([
                sys.executable, "high_school_graduate_trainer.py", "--quick", "--yes"
            ], check=True)
            print("✅ Quick training completed!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Training failed: {e}")
        except FileNotFoundError:
            print("❌ Training script not found. Ensure you're in the project root.")

def demo_evaluation():
    """Demonstrate model evaluation"""
    print("\n📊 DEMO 2: MODEL EVALUATION")
    print("-" * 32)
    print("This shows how to evaluate a trained model's conversation skills:")
    print()
    
    # Look for available models
    models_dir = Path("src/models/production")
    checkpoint_dir = Path("src/models/checkpoints")
    
    model_files = []
    if models_dir.exists():
        model_files.extend(models_dir.glob("impressioncore_high_school_graduate_*.pth"))
    if checkpoint_dir.exists():
        model_files.extend(checkpoint_dir.glob("high_school_model_epoch_*.pth"))
    
    if model_files:
        print("Available models:")
        for i, model_path in enumerate(model_files):
            print(f"  {i+1}. {model_path}")
        print()
        
        choice = input("Select model number to evaluate (or 'n' to skip): ")
        if choice.isdigit() and 1 <= int(choice) <= len(model_files):
            selected_model = model_files[int(choice) - 1]
            print(f"\nEvaluation command:")
            print(f"  python high_school_graduate_trainer.py --evaluate --model \"{selected_model}\"")
            
            response = input("\nRun evaluation? (y/N): ")
            if response.lower() == 'y':
                try:
                    subprocess.run([
                        sys.executable, "high_school_graduate_trainer.py", 
                        "--evaluate", "--model", str(selected_model)
                    ], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"❌ Evaluation failed: {e}")
    else:
        print("No trained models found. Train a model first with:")
        print("  python high_school_graduate_trainer.py --quick")

def demo_chat():
    """Demonstrate interactive chat"""
    print("\n💬 DEMO 3: INTERACTIVE CHAT")
    print("-" * 28)
    print("This shows how to chat with a trained model:")
    print()
    
    # Look for available models
    models_dir = Path("src/models/production")
    checkpoint_dir = Path("src/models/checkpoints")
    
    model_files = []
    if models_dir.exists():
        model_files.extend(models_dir.glob("impressioncore_high_school_graduate_*.pth"))
    if checkpoint_dir.exists():
        model_files.extend(checkpoint_dir.glob("high_school_model_epoch_*.pth"))
    
    if model_files:
        print("Available models:")
        for i, model_path in enumerate(model_files):
            print(f"  {i+1}. {model_path}")
        print()
        
        choice = input("Select model number to chat with (or 'n' to skip): ")
        if choice.isdigit() and 1 <= int(choice) <= len(model_files):
            selected_model = model_files[int(choice) - 1]
            print(f"\nChat command:")
            print(f"  python high_school_graduate_trainer.py --chat --model \"{selected_model}\"")
            print()
            print("In chat mode, try asking:")
            print("  • 'Explain the main theme of Romeo and Juliet'")
            print("  • 'How does photosynthesis work?'")
            print("  • 'What factors should I consider for college?'")
            print("  • 'Help me understand quadratic equations'")
            print()
            
            response = input("Start interactive chat? (y/N): ")
            if response.lower() == 'y':
                try:
                    subprocess.run([
                        sys.executable, "high_school_graduate_trainer.py", 
                        "--chat", "--model", str(selected_model)
                    ], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"❌ Chat failed: {e}")
    else:
        print("No trained models found. Train a model first with:")
        print("  python high_school_graduate_trainer.py --quick")

def demo_full_training():
    """Demonstrate full training"""
    print("\n🎯 DEMO 4: FULL TRAINING (10 EPOCHS)")
    print("-" * 38)
    print("This demonstrates full high school graduate training:")
    print()
    print("Command to run:")
    print("  python high_school_graduate_trainer.py")
    print()
    print("What this does:")
    print("  • Trains for 10 epochs (full training)")
    print("  • Uses optimal batch size for your hardware")
    print("  • Knowledge distillation from DialoGPT-medium")
    print("  • Comprehensive conversation evaluation")
    print("  • Saves production-ready model")
    print()
    print("Expected results:")
    print("  • Training time: 2-4 hours (depending on hardware)")
    print("  • Final conversation score: 7.0+/10.0")
    print("  • Model size: 2-5MB (compressed)")
    print("  • Memory usage: <4GB VRAM (GTX 1050 Ti compatible)")
    print()
    
    response = input("Run full training? (y/N): ")
    if response.lower() == 'y':
        try:
            print("\n🎓 Starting full high school graduate training...")
            print("This will take 2-4 hours. You can stop with Ctrl+C if needed.")
            subprocess.run([
                sys.executable, "high_school_graduate_trainer.py", "--yes"
            ], check=True)
            print("✅ Full training completed!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Training failed: {e}")
        except KeyboardInterrupt:
            print("\n⚠️ Training interrupted by user")

def show_advanced_options():
    """Show advanced training options"""
    print("\n⚙️  ADVANCED OPTIONS")
    print("-" * 20)
    print("For advanced users, additional options are available:")
    print()
    print("Custom Configuration:")
    print("  python high_school_graduate_trainer.py --epochs 15 --batch-size 2")
    print()
    print("Memory Optimization:")
    print("  python high_school_graduate_trainer.py --max-memory 2500 --cpu-only")
    print()
    print("Different Teacher Model:")
    print("  python high_school_graduate_trainer.py --teacher-model facebook/blenderbot-400M-distill")
    print()
    print("List All Available Models:")
    print("  python high_school_graduate_trainer.py --list-models")
    print()
    print("For complete options, run:")
    print("  python high_school_graduate_trainer.py --help")

def main():
    """Main demo function"""
    print_header()
    
    if not check_system():
        print("\n❌ System check failed. Please fix issues and try again.")
        return
    
    print("\n✅ System ready for high school graduate training!")
    
    while True:
        print("\n📋 AVAILABLE DEMONSTRATIONS")
        print("-" * 28)
        print("1. Quick Training Demo (5 epochs)")
        print("2. Model Evaluation Demo")
        print("3. Interactive Chat Demo")
        print("4. Full Training Demo (10 epochs)")
        print("5. Show Advanced Options")
        print("6. Exit")
        print()
        
        choice = input("Select demo (1-6): ").strip()
        
        if choice == '1':
            demo_quick_training()
        elif choice == '2':
            demo_evaluation()
        elif choice == '3':
            demo_chat()
        elif choice == '4':
            demo_full_training()
        elif choice == '5':
            show_advanced_options()
        elif choice == '6':
            print("\n👋 Thank you for trying ImpressionCore!")
            print("For more information, see: docs/user/high_school_graduate_training_guide.md")
            break
        else:
            print("Invalid choice. Please select 1-6.")

if __name__ == "__main__":
    main()
