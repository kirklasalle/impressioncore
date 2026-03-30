"""
Launch Path A: Knowledge Distillation Training

This script starts the knowledge distillation process where B3-Hope (student)
learns conversation skills from DialoGPT-medium (teacher).

Created: October 6, 2025
Purpose: Path A Implementation - Transfer conversation knowledge to B3
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from training.b3_knowledge_distillation_trainer import KnowledgeDistillationTrainer
from rich.console import Console

console = Console()


def main():
    """Launch distillation training"""

    console.print("\n[bold cyan]" + "="*60)
    console.print("[bold cyan]PATH A: KNOWLEDGE DISTILLATION")
    console.print("[bold cyan]Teaching B3-Hope conversation skills from DialoGPT-medium")
    console.print("[bold cyan]" + "="*60 + "\n")

    console.print("[yellow]Teacher: microsoft/DialoGPT-medium (354M params, 147M Reddit convos)")
    console.print("[yellow]Student: B3-Hope (35.5M params)")
    console.print("[yellow]Method: KL Divergence knowledge distillation")
    console.print("[yellow]Dataset: 1,000 simple conversation pairs")
    console.print("[yellow]Training: 20 epochs, test every 5 epochs")
    console.print()

    # Create trainer
    trainer = KnowledgeDistillationTrainer(
        student_checkpoint="F:/models/checkpoints/b3/b3_massive_final.pth",
        teacher_name="microsoft/DialoGPT-medium",
        teacher_cache="F:/models/teachers/dialogpt_medium",
        output_dir="F:/models/checkpoints/b3/distillation"
    )

    # Start training
    trainer.train(
        num_epochs=20,
        batch_size=4,      # GTX 1050 Ti constraint
        temperature=2.0,   # Soft targets
        alpha=0.7          # 70% distillation, 30% hard labels
    )

    console.print("\n[bold green]✅ PATH A DISTILLATION COMPLETE!")
    console.print("\n[yellow]Next steps:")
    console.print("[yellow]1. Test distilled model: python test_final_model_conversation.py")
    console.print("[yellow]2. Compare to baseline quality (was 0.0/10.0 after Path C)")
    console.print("[yellow]3. If quality ≥7.5/10.0, proceed to production")
    console.print()


if __name__ == "__main__":
    main()
