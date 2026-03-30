#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #multimodal #python #source_code #src/scripts\run_embedding_and_training_pipeline.py #tokenization #training #transformer
**Category:** Source Code
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #multimodal #python #source_code #src\\scripts\\run_embedding_and_training_pipeline.py #tokenization #training #transformer
# Category:** Source Code
# Status:** Active

"""
ImpressionCore B3 Full Pipeline: Embedding Extraction and Training
=================================================================
This script orchestrates the entire B3 pipeline:
1. Extracts multimodal embeddings from the raw F:/datasets directory.
2. Launches the full 3B model training using the generated embeddings.
"""

import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

# Add src to path to allow for imports
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))

from transformers import AutoTokenizer

from core.models.impressioncore_b3_architecture import ImpressionCoreB3Model3B, run_full_embedding_extraction

console = Console()

def main():
    """Main pipeline execution"""
    console.print(Panel.fit(
        "[bold cyan]ImpressionCore B3 Full Pipeline Started[/bold cyan]",
        border_style="cyan"
    ))

    # --- Step 1: Embedding Extraction ---
    console.print(Panel.fit(
        "[bold green]Step 1: Running Full Embedding Extraction[/bold green]",
        border_style="green"
    ))
    try:
        model = ImpressionCoreB3Model3B()
        tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        run_full_embedding_extraction(model, tokenizer)
        console.print("[green]✅ Embedding extraction completed successfully.[/green]")
    except Exception as e:
        console.print(f"[red]❌ Embedding extraction failed: {e}[/red]")
        sys.exit(1)

    # --- Step 2: Launch Model Training ---
    console.print(Panel.fit(
        "[bold green]Step 2: Launching B3 3B Model Training[/bold green]",
        border_style="green"
    ))
    try:
        # Use subprocess to call the training script
        process = subprocess.run(
            [sys.executable, "run_b3_full_training.py"],
            capture_output=True,
            text=True,
            check=True  # This will raise a CalledProcessError if the script fails
        )
        console.print("[green]✅ Model training launched successfully.[/green]")
        console.print(f"Output from training script:\n{process.stdout}")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Model training script failed with exit code {e.returncode}[/red]")
        console.print(f"Stderr:\n{e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        console.print("[red]❌ Error: 'run_b3_full_training.py' not found. Make sure you are in the correct directory.[/red]")
        sys.exit(1)

    console.print(Panel.fit(
        "[bold cyan]ImpressionCore B3 Full Pipeline Finished[/bold cyan]",
        border_style="cyan"
    ))

if __name__ == "__main__":
    main()
