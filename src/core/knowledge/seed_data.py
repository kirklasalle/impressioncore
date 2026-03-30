#!/usr/bin/env python3
"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: src\knowledge\seed_data.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-25
Modified: 2025-05-25
Version: 1.0.0

Authors:
- Kirk LaSalle & GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [knowledge]
Dependencies: [] # TODO: Auto-detect or allow manual input
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
# TODO: Add a brief description of this file's purpose.

Design Philosophy:
# TODO: Add design philosophy if applicable.

Memory Considerations:
# TODO: Document any specific memory considerations for this file.

Examples:
# TODO: Provide usage examples if applicable.

Notes:
# TODO: Add any relevant notes.
"""
\n\n """
Seed data for the Universal Knowledge Store.
"""

from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.core.knowledge.uks import UniversalKnowledgeStore, KnowledgeNode  # Corrected import path
from rich.console import Console
from rich.progress import Progress
from rich.logging import RichHandler
import logging

# Initialize rich console and logging
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console)]
)
logger = logging.getLogger("rich")

def create_astronomy_knowledge():
    """Create knowledge about astronomy topics."""
    uks = UniversalKnowledgeStore()

    # Example: Adding a celestial body node
    celestial_body = KnowledgeNode(name="Mars", attributes={"type": "planet", "has_water": False})
    uks.add_node(celestial_body)

    # Add more nodes as needed
    return uks

def seed_knowledge_store():
    """Create and return seeded knowledge store."""
    # Start with astronomy knowledge
    uks = create_astronomy_knowledge()
    
    # Could add more domains here
    # uks.merge(create_biology_knowledge())
    # uks.merge(create_geography_knowledge())
    
    return uks

# Update the save_seed_knowledge function to include progress animations
def save_seed_knowledge(output_path=None):
    """Create and save seed knowledge to file."""
    if output_path is None:
        output_path = project_root / "data" / "knowledge" / "seed_knowledge.json"

    # Create the knowledge store
    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Seeding knowledge store...", total=100)

        uks = seed_knowledge_store()
        progress.update(task, advance=50)

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to file
        success = uks.save_to_file(output_path)
        progress.update(task, advance=50)

        if success:
            console.log(f"[green]Seed knowledge saved to {output_path}")
        else:
            console.log(f"[red]Failed to save seed knowledge to {output_path}")

    return uks

# Run this script to generate seed knowledge
if __name__ == "__main__":
    uks = save_seed_knowledge()

    # Print summary of created knowledge
    console.print(f"[bold cyan]Created knowledge store with {len(uks.nodes)} nodes:[/bold cyan]")
    for label, node in uks.nodes.items():
        attr_count = len(node.attributes)
        rel_count = len(node.relations)
        console.print(f"- [bold]{label}[/bold]: {attr_count} attributes, {rel_count} relations")
