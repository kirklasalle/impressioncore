#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #deployment #multimodal #python #source_code #src/training/execute_distillation_training.py #testing #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #deployment #multimodal #python #source_code #src\\training\\execute_distillation_training.py #testing #training
# Category:** Training System
# Status:** Active

"""
Execute B1 Knowledge Distillation Training with Ollama

Quick execution script for knowledge distillation training using Ollama
as the teacher model to enhance our B1 model beyond 10/10 performance.

File: execute_distillation_training.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-28
Version: 1.0.0

Usage:
    python execute_distillation_training.py

Description:
Launches knowledge distillation training where our enhanced B1 model learns
from Ollama's high-quality responses to achieve even better performance.
"""

import sys
import time
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from src.training.b1_distillation_training_ollama import B1DistillationTrainer, DistillationConfig
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    # Try alternative import path
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from training.b1_distillation_training_ollama import B1DistillationTrainer, DistillationConfig
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        IMPORTS_SUCCESSFUL = True
    except ImportError as e2:
        print(f"Import error: {e}")
        print(f"Alternative import error: {e2}")
        IMPORTS_SUCCESSFUL = False

def check_ollama_availability():
    """Check if Ollama is available and running"""
    try:
        import ollama

        # Test connection
        models = ollama.list()

        # Handle Ollama ListResponse object
        if hasattr(models, 'models'):
            available_models = []
            for model in models.models:
                if hasattr(model, 'name'):
                    available_models.append(model.name)
                elif hasattr(model, 'model'):
                    available_models.append(model.model)
        else:
            # Fallback for other formats
            available_models = []

        print("✅ Ollama is available")
        print(f"📚 Available models: {available_models}")

        # Check for recommended models
        recommended = ["llama3.1:8b", "llama3:8b", "llama2:7b"]
        available_recommended = [m for m in recommended if m in available_models]

        if available_recommended:
            print(f"🎯 Recommended models available: {available_recommended}")
            return True, available_recommended[0]
        else:
            print("⚠️ No recommended models found. Attempting to pull llama3.1:8b...")
            try:
                ollama.pull("llama3.1:8b")
                return True, "llama3.1:8b"
            except Exception as e:
                print(f"❌ Failed to pull model: {e}")
                return False, None

    except ImportError:
        print("❌ Ollama not installed. Install with: pip install ollama")
        return False, None
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("Make sure Ollama is running: ollama serve")
        return False, None

def execute_distillation_training():
    """Execute the knowledge distillation training pipeline"""

    if not IMPORTS_SUCCESSFUL:
        print("❌ Failed to import required modules.")
        print("💡 Make sure you're in the project root directory.")
        return False

    console = Console()

    # Display execution banner
    banner_text = Text()
    banner_text.append("🎓 EXECUTING B1 KNOWLEDGE DISTILLATION\n", style="bold cyan")
    banner_text.append("👨‍🏫 Teacher: Ollama Model\n", style="bold yellow")
    banner_text.append("🎯 Student: Enhanced B1 (10/10 Baseline)\n", style="bold green")
    banner_text.append("📈 Target: Beyond 10/10 Performance\n", style="bold red")
    banner_text.append("💾 Hardware: GTX 1050 Ti Optimized\n", style="bold blue")
    banner_text.append("🛡️ Sacred Covenant: ACTIVE\n", style="bold green")

    panel = Panel(banner_text, title="Knowledge Distillation Training", border_style="bright_cyan")
    console.print(panel)

    try:
        # Check Ollama availability
        console.print("🔍 [bold yellow]Checking Ollama availability...[/bold yellow]")
        ollama_available, teacher_model = check_ollama_availability()

        if not ollama_available:
            console.print("❌ [bold red]Ollama not available. Please install and run Ollama first.[/bold red]")
            console.print("💡 [yellow]Install: https://ollama.ai[/yellow]")
            console.print("💡 [yellow]Run: ollama serve[/yellow]")
            return False

        # Create distillation configuration
        console.print("⚙️ [bold yellow]Creating distillation configuration...[/bold yellow]")
        config = DistillationConfig()
        config.teacher_model = teacher_model  # Use available model

        # Create distillation trainer
        console.print("🎓 [bold yellow]Initializing knowledge distillation trainer...[/bold yellow]")
        trainer = B1DistillationTrainer(config=config, enable_rich=True)

        # Phase 1: Component Initialization
        console.print("🔧 [bold cyan]Phase 1: Component Initialization[/bold cyan]")
        if not trainer.initialize_components():
            console.print("❌ [bold red]Component initialization failed[/bold red]")
            return False

        console.print("✅ [bold green]All components initialized successfully[/bold green]")

        # Phase 2: Knowledge Distillation Training
        console.print("🎓 [bold cyan]Phase 2: Knowledge Distillation Training[/bold cyan]")
        success = trainer.execute_distillation_training()

        if success:
            console.print("🏆 [bold green]KNOWLEDGE DISTILLATION COMPLETED SUCCESSFULLY![/bold green]")
            console.print(f"📊 Final Quality: {trainer.best_quality:.2f}/10.0")
            console.print(f"📈 Improvement: +{trainer.best_quality - config.baseline_quality:.2f} from baseline")
            console.print(f"👨‍🏫 Teacher Model: {config.teacher_model}")
            return True
        else:
            console.print("⚠️ [bold yellow]Distillation completed with partial success[/bold yellow]")
            return False

    except Exception as e:
        console.print(f"❌ [bold red]Distillation training execution failed: {str(e)}[/bold red]")
        return False

def main():
    """Main execution function"""
    start_time = time.time()

    print("🎓 B1 Knowledge Distillation Trainer - ImpressionCore")
    print("=" * 60)

    try:
        success = execute_distillation_training()

        execution_time = time.time() - start_time

        if success:
            print(f"\n✅ Knowledge distillation completed successfully in {execution_time:.1f} seconds")
            print("🎯 Model enhanced beyond 10/10 baseline performance")
            print("💾 Distilled model ready for deployment")
        else:
            print(f"\n⚠️ Knowledge distillation completed with issues in {execution_time:.1f} seconds")
            print("📊 Check training logs for details")

        return success

    except KeyboardInterrupt:
        print("\n🛑 Knowledge distillation interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Knowledge distillation failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
