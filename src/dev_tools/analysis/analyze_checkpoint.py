#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/dev_tools/analysis/analyze_checkpoint.py
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\dev_tools\\analysis\\analyze_checkpoint.py
# Category:** Development Tools
# Status:** Active

"""
Checkpoint Analysis - Understand the structure of the trained model

File: analyze_checkpoint.py
Created: 2025-06-29
"""

from pathlib import Path

import torch
from rich.console import Console

console = Console()

def analyze_checkpoint():
    """Analyze the checkpoint structure"""
    model_path = Path("src/models/production/impressioncore_b1_distilled_v12.30/model_production.pt")

    console.print("[cyan]Loading checkpoint for analysis...[/cyan]")
    checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)

    console.print(f"[green]Checkpoint keys: {list(checkpoint.keys())}[/green]")

    for key, value in checkpoint.items():
        if isinstance(value, dict):
            console.print(f"\n[blue]{key}:[/blue] (dict with {len(value)} items)")
            if len(value) <= 10:  # Show if small
                for k, v in value.items():
                    if isinstance(v, torch.Tensor):
                        console.print(f"  {k}: tensor {v.shape}")
                    else:
                        console.print(f"  {k}: {type(v)} = {v}")
            else:
                console.print(f"  First 5 keys: {list(value.keys())[:5]}")
        elif isinstance(value, torch.Tensor):
            console.print(f"\n[blue]{key}:[/blue] tensor {value.shape}")
        else:
            console.print(f"\n[blue]{key}:[/blue] {type(value)} = {value}")

if __name__ == "__main__":
    analyze_checkpoint()
