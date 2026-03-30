#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #command_line #cuda #memory_management #multimodal #python #source_code #src/interfaces/cli/high_school_training_cli.py #tokenization #training
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #command_line #cuda #memory_management #multimodal #python #source_code #src/interfaces/cli/high_school_training_cli.py #tokenization #training
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore High School Training CLI

File: src/interfaces/cli/high_school_training_cli.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-12
Modified: 2025-06-12
Version: 1.0.0

Description:
CLI interface for training ImpressionCore to high school graduate level conversation
using knowledge distillation. Provides easy access to training, evaluation, and
model management for achieving academic conversation competency.
"""

import argparse

# Add src to path for imports
import sys
from datetime import datetime
from pathlib import Path

import torch

sys.path.append(str(Path(__file__).parent.parent.parent))

from core.utils.rich_enhancements import create_rich_console
from core.utils.rich_logging import setup_rich_logging
from training.high_school_distillation_trainer import HighSchoolDistillationTrainer, HighSchoolTrainingConfig

console = create_rich_console()
logger = setup_rich_logging(__name__)

def create_training_config(args):
    """Create training configuration from CLI arguments"""
    config = HighSchoolTrainingConfig()

    # Update config with CLI arguments
    if args.batch_size:
        config.batch_size = args.batch_size
    if args.learning_rate:
        config.learning_rate = args.learning_rate
    if args.epochs:
        config.num_epochs = args.epochs
    if args.teacher_model:
        config.teacher_model = args.teacher_model
    if args.temperature:
        config.temperature = args.temperature
    if args.max_seq_length:
        config.max_seq_length = args.max_seq_length

    # Memory optimization settings
    if args.no_mixed_precision:
        config.mixed_precision = False
    if args.no_gradient_checkpointing:
        config.gradient_checkpointing = False
    if args.max_memory:
        config.max_memory_mb = args.max_memory

    return config

def train_command(args):
    """Execute training command"""
    console.print("\n🎓 [bold blue]ImpressionCore High School Graduate Training[/bold blue]")
    console.print("=" * 60)

    # Check system requirements
    if not torch.cuda.is_available() and not args.force_cpu:
        console.print("⚠️  [yellow]CUDA not available. Training will be slower on CPU.[/yellow]")
        console.print("Use --force-cpu to proceed anyway, or install CUDA for better performance.")
        return

    # Create configuration
    config = create_training_config(args)

    # Display configuration
    console.print("\n📋 [bold]Training Configuration[/bold]")
    console.print("  Target Level: High School Graduate")
    console.print(f"  Teacher Model: {config.teacher_model}")
    console.print(f"  Epochs: {config.num_epochs}")
    console.print(f"  Batch Size: {config.batch_size}")
    console.print(f"  Learning Rate: {config.learning_rate}")
    console.print(f"  Mixed Precision: {config.mixed_precision}")
    console.print(f"  Gradient Checkpointing: {config.gradient_checkpointing}")
    console.print(f"  Max Memory: {config.max_memory_mb}MB")

    if not args.yes:
        response = input("\nProceed with training? (y/N): ")
        if response.lower() != 'y':
            console.print("Training cancelled.")
            return

    # Start training
    try:
        trainer = HighSchoolDistillationTrainer(config)
        trainer.train()
        console.print("\n🎉 [bold green]Training completed successfully![/bold green]")
    except Exception as e:
        console.print(f"\n❌ [bold red]Training failed: {e}[/bold red]")
        logger.error(f"Training error: {e}", exc_info=True)

def evaluate_command(args):
    """Evaluate a trained model"""
    console.print("\n📊 [bold blue]High School Conversation Evaluation[/bold blue]")

    if not Path(args.model_path).exists():
        console.print(f"❌ [red]Model not found: {args.model_path}[/red]")
        return

    # Load model and evaluate
    try:
        checkpoint = torch.load(args.model_path, map_location='cpu')
        config = checkpoint.get('config', HighSchoolTrainingConfig())

        trainer = HighSchoolDistillationTrainer(config)
        trainer.student_model.load_state_dict(checkpoint['model_state_dict'])

        console.print(f"✅ Model loaded: {args.model_path}")
        console.print("🔍 Running conversation evaluation...")

        score = trainer._evaluate_conversation_skills(-1)

        console.print(f"\n📈 [bold green]Final Score: {score:.2f}/10[/bold green]")

        # Score interpretation
        if score >= 8.0:
            console.print("🏆 [bold green]Excellent! Model demonstrates strong high school level conversation skills.[/bold green]")
        elif score >= 6.0:
            console.print("✅ [bold yellow]Good! Model shows solid conversation abilities with room for improvement.[/bold yellow]")
        elif score >= 4.0:
            console.print("⚠️  [bold orange]Fair. Model has basic conversation skills but needs more training.[/bold orange]")
        else:
            console.print("❌ [bold red]Poor. Model needs significant additional training.[/bold red]")

    except Exception as e:
        console.print(f"❌ [bold red]Evaluation failed: {e}[/bold red]")
        logger.error(f"Evaluation error: {e}", exc_info=True)

def chat_command(args):
    """Interactive chat with trained model"""
    console.print("\n💬 [bold blue]High School Graduate Chat[/bold blue]")

    if not Path(args.model_path).exists():
        console.print(f"❌ [red]Model not found: {args.model_path}[/red]")
        return

    try:
        # Load model
        checkpoint = torch.load(args.model_path, map_location='cpu')
        config = checkpoint.get('config', HighSchoolTrainingConfig())

        trainer = HighSchoolDistillationTrainer(config)
        trainer.student_model.load_state_dict(checkpoint['model_state_dict'])
        trainer.student_model.eval()

        console.print("✅ Model loaded successfully!")
        console.print("💡 [dim]Type 'quit' to exit, 'help' for commands[/dim]")
        console.print("-" * 50)

        while True:
            try:
                user_input = input("\n🎓 You: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    console.print("\n📖 Available commands:")
                    console.print("  help - Show this help")
                    console.print("  quit/exit/q - Exit chat")
                    console.print("  clear - Clear conversation history")
                    console.print("\n💡 Try asking about:")
                    console.print("  • Academic subjects (literature, science, math, history)")
                    console.print("  • Current events and social issues")
                    console.print("  • College and career planning")
                    console.print("  • Study tips and learning strategies")
                    continue
                elif user_input.lower() == 'clear':
                    console.print("🧹 Conversation cleared!")
                    continue
                elif not user_input:
                    continue

                # Generate response
                console.print("🤖 ImpressionCore: ", end="")

                input_ids = trainer.tokenizer.encode(user_input, return_tensors='pt')

                with torch.no_grad():
                    outputs = trainer.student_model.generate(
                        input_ids,
                        max_length=input_ids.size(1) + 150,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=trainer.tokenizer.pad_token_id,
                        repetition_penalty=1.1
                    )

                response = trainer.tokenizer.decode(
                    outputs[0][input_ids.size(1):],
                    skip_special_tokens=True
                ).strip()

                console.print(response)

            except KeyboardInterrupt:
                console.print("\n👋 Goodbye!")
                break
            except Exception as e:
                console.print(f"\n❌ Error generating response: {e}")

    except Exception as e:
        console.print(f"❌ [bold red]Failed to load model: {e}[/bold red]")

def list_models_command(args):
    """List available trained models"""
    console.print("\n📋 [bold blue]Available High School Models[/bold blue]")

    models_dir = Path("src/models/production")
    checkpoints_dir = Path("src/models/checkpoints")

    found_models = []

    # Check production models
    if models_dir.exists():
        for model_file in models_dir.glob("impressioncore_high_school_graduate_*.pth"):
            found_models.append(("Production", model_file))

    # Check checkpoints
    if checkpoints_dir.exists():
        for model_file in checkpoints_dir.glob("high_school_model_epoch_*.pth"):
            found_models.append(("Checkpoint", model_file))

    if not found_models:
        console.print("📭 No trained models found.")
        console.print("💡 Run training first with: --train")
        return

    console.print(f"Found {len(found_models)} model(s):")
    console.print()

    for model_type, model_path in found_models:
        # Get model info
        try:
            checkpoint = torch.load(model_path, map_location='cpu')
            epoch = checkpoint.get('epoch', 'Unknown')

            file_size = model_path.stat().st_size / (1024 * 1024)  # MB
            mod_time = datetime.fromtimestamp(model_path.stat().st_mtime)

            console.print(f"📄 [bold]{model_type}[/bold]: {model_path.name}")
            console.print(f"   Path: {model_path}")
            console.print(f"   Size: {file_size:.1f} MB")
            console.print(f"   Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            if epoch != 'Unknown':
                console.print(f"   Epoch: {epoch + 1}")
            console.print()

        except Exception:
            console.print(f"📄 [bold]{model_type}[/bold]: {model_path.name} (corrupted)")
            console.print()

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="ImpressionCore High School Graduate Training CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start training with default settings
  python src/interfaces/cli/high_school_training_cli.py --train

  # Train with custom parameters
  python src/interfaces/cli/high_school_training_cli.py --train --epochs 15 --batch-size 2

  # Evaluate a trained model
  python src/interfaces/cli/high_school_training_cli.py --evaluate --model-path src/models/production/model.pth

  # Chat with trained model
  python src/interfaces/cli/high_school_training_cli.py --chat --model-path src/models/production/model.pth

  # List available models
  python src/interfaces/cli/high_school_training_cli.py --list-models
        """
    )

    # Commands
    parser.add_argument('--train', action='store_true', help='Start training')
    parser.add_argument('--evaluate', action='store_true', help='Evaluate trained model')
    parser.add_argument('--chat', action='store_true', help='Interactive chat with model')
    parser.add_argument('--list-models', action='store_true', help='List available models')

    # Training arguments
    parser.add_argument('--epochs', type=int, help='Number of training epochs (default: 10)')
    parser.add_argument('--batch-size', type=int, help='Training batch size (default: 4)')
    parser.add_argument('--learning-rate', type=float, help='Learning rate (default: 2e-5)')
    parser.add_argument('--teacher-model', type=str, help='Teacher model for distillation')
    parser.add_argument('--temperature', type=float, help='Distillation temperature (default: 4.0)')
    parser.add_argument('--max-seq-length', type=int, help='Maximum sequence length')

    # Memory optimization
    parser.add_argument('--no-mixed-precision', action='store_true', help='Disable mixed precision')
    parser.add_argument('--no-gradient-checkpointing', action='store_true', help='Disable gradient checkpointing')
    parser.add_argument('--max-memory', type=int, help='Maximum memory usage (MB)')
    parser.add_argument('--force-cpu', action='store_true', help='Force CPU training')

    # General arguments
    parser.add_argument('--model-path', type=str, help='Path to model for evaluation/chat')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompts')

    args = parser.parse_args()

    # Execute command
    if args.train:
        train_command(args)
    elif args.evaluate:
        if not args.model_path:
            console.print("❌ [red]--model-path required for evaluation[/red]")
            return
        evaluate_command(args)
    elif args.chat:
        if not args.model_path:
            console.print("❌ [red]--model-path required for chat[/red]")
            return
        chat_command(args)
    elif args.list_models:
        list_models_command(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
