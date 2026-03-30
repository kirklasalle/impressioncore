#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #multimodal #python #source_code #src/training/execute_enhanced_training.py #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #multimodal #python #source_code #src\\training\\execute_enhanced_training.py #training
# Category:** Training System
# Status:** Active

"""
Execute Enhanced B1 Training

Quick execution script for the enhanced B1 training system targeting 10/10
conversation quality. This script provides a streamlined interface to launch
the enhanced training pipeline.

File: execute_enhanced_training.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-28
Version: 1.0.0

Usage:
    python execute_enhanced_training.py

Description:
Direct execution script for enhanced B1 training using the prepared enhanced
dataset. Builds upon the proven 7.07/10.0 baseline toward 10/10 quality target.
"""

import sys
import time
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from src.training.b1_enhanced_training_executor import B1EnhancedTrainingExecutor, EnhancedTrainingConfig
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    # Try alternative import path
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from training.b1_enhanced_training_executor import B1EnhancedTrainingExecutor, EnhancedTrainingConfig
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        IMPORTS_SUCCESSFUL = True
    except ImportError as e2:
        print(f"Import error: {e}")
        print(f"Alternative import error: {e2}")
        IMPORTS_SUCCESSFUL = False

def execute_enhanced_training():
    """Execute the enhanced B1 training pipeline"""

    if not IMPORTS_SUCCESSFUL:
        print("❌ Failed to import required modules. Please ensure dependencies are installed.")
        return False

    console = Console()

    # Display execution banner
    banner_text = Text()
    banner_text.append("🚀 EXECUTING ENHANCED B1 TRAINING\n", style="bold cyan")
    banner_text.append("🎯 Target: 10/10 Conversation Quality\n", style="bold red")
    banner_text.append("📊 Baseline: 7.07/10.0 (Proven Success)\n", style="bold green")
    banner_text.append("⚡ Enhanced Dataset: LOADED\n", style="bold yellow")
    banner_text.append("🛡️ Sacred Covenant: ACTIVE\n", style="bold green")

    panel = Panel(banner_text, title="Enhanced Training Execution", border_style="bright_cyan")
    console.print(panel)

    try:
        # Initialize enhanced training configuration
        console.print("🔧 [bold yellow]Initializing enhanced training configuration...[/bold yellow]")
        config = EnhancedTrainingConfig()

        # Create enhanced training executor
        console.print("🤖 [bold yellow]Creating enhanced training executor...[/bold yellow]")
        executor = B1EnhancedTrainingExecutor(config=config, enable_rich=True)

        # Phase 1: Model and Data Initialization
        console.print("📚 [bold cyan]Phase 1: Model & Data Initialization[/bold cyan]")
        if not executor.initialize_model_and_data():
            console.print("❌ [bold red]Model initialization failed[/bold red]")
            return False

        console.print("✅ [bold green]Model and data initialization complete[/bold green]")

        # Phase 2: Enhanced Training Execution
        console.print("🚀 [bold cyan]Phase 2: Enhanced Training Execution[/bold cyan]")
        success = executor.execute_enhanced_training()

        if success:
            console.print("🏆 [bold green]ENHANCED TRAINING COMPLETED SUCCESSFULLY![/bold green]")
            console.print(f"📊 Final Quality: {executor.best_quality:.2f}/10.0")
            console.print(f"📈 Improvement: +{executor.best_quality - 7.07:.2f} from baseline")
            return True
        else:
            console.print("⚠️ [bold yellow]Training completed with partial success[/bold yellow]")
            return False

    except Exception as e:
        console.print(f"❌ [bold red]Enhanced training execution failed: {str(e)}[/bold red]")
        return False

def main():
    """Main execution function"""
    start_time = time.time()

    print("🤖 Enhanced B1 Training Executor - ImpressionCore")
    print("=" * 50)

    try:
        success = execute_enhanced_training()

        execution_time = time.time() - start_time

        if success:
            print(f"\n✅ Enhanced training completed successfully in {execution_time:.1f} seconds")
            print("🎯 Ready for 10/10 conversation quality validation")
        else:
            print(f"\n⚠️ Enhanced training completed with issues in {execution_time:.1f} seconds")
            print("📊 Check training logs for details")

        return success

    except KeyboardInterrupt:
        print("\n🛑 Enhanced training interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Enhanced training failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
