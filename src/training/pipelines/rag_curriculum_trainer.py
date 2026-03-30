"""
ImpressionCore B3 RAG Curriculum Trainer

Created: December 23, 2025
Tags: #training #b3 #rag #specialized_training
Category: Training Infrastructure
Status: Beta

This trainer uses the RAGCurriculumLoader to perform "Specialized Training".
It retrieves training samples based on a list of "Concept Queries" rather than random sampling.
This allows the model to be fine-tuned on specific behaviors (e.g. "empathy", "reasoning").
"""

import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import torch

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model
from src.training.data.rag_curriculum_loader import RAGCurriculumLoader

# Rich console
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RAGTrainingConfig:
    output_dir: str = "F:/models/checkpoints/rag_specialized"
    base_checkpoint_path: str = "F:/models/checkpoints/diverse_curriculum/step_5000.pt"

    # Curriculum Concepts to focus on
    concept_queries: list[str] = None

    # Hyperparameters
    batch_size: int = 2
    gradient_accumulation_steps: int = 16
    learning_rate: float = 1e-5 # Lower LR for fine-tuning
    max_steps: int = 2000 # Short burst training
    save_every: int = 500

    def __post_init__(self):
        if self.concept_queries is None:
            # Default "Conversational Foundation" curriculum
            self.concept_queries = [
                "empathy and understanding feelings",
                "logical reasoning and step-by-step thinking",
                "helpful assistant behavior",
                "complex problem solving"
            ]

class RAGCurriculumTrainer:
    def __init__(self, config: RAGTrainingConfig):
        self.config = config
        if not torch.cuda.is_available():
            logger.warning("CUDA not found! Training will be extremely slow on CPU.")
            self.device = torch.device("cpu")
        else:
            self.device = torch.device("cuda")
            logger.info(f"Training on GPU: {torch.cuda.get_device_name(0)}")

        # Initialize RAG Loader
        self.loader = RAGCurriculumLoader()

        # Initialize Tokenizer (GPT-2 base for B3)
        from transformers import AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load Model
        self._load_model()

        # Setup Optimizer
        from transformers.optimization import Adafactor
        self.optimizer = Adafactor(
            self.model.parameters(),
            lr=config.learning_rate,
            scale_parameter=False,
            relative_step=False,
            warmup_init=False
        )

        os.makedirs(config.output_dir, exist_ok=True)
        self.global_step = 0
        self.loss_history = []

    def _load_model(self):
        if RICH_AVAILABLE:
            console.print(f"[yellow]Loading model from {self.config.base_checkpoint_path}...[/yellow]")

        checkpoint = torch.load(self.config.base_checkpoint_path, map_location="cpu")

        # Handle config
        model_config = B3Config.from_dict(checkpoint["config"]) if "config" in checkpoint else B3Config()

        self.model = ImpressionCoreB3Model(model_config)

        # Load state dict
        if "model_state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["model_state_dict"], strict=False)
        elif "state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["state_dict"], strict=False)

        self.model.to(self.device)
        self.model.train()

        # Enable gradient checkpointing
        self.model.gradient_checkpointing_enable()

    def train(self):
        if RICH_AVAILABLE:
            console.print(Panel(f"[bold green]Starting Specialized Training on: {self.config.concept_queries}[/bold green]"))

        accumulation_loss = 0.0

        # Training Loop
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Specialized Training", total=self.config.max_steps)

            while self.global_step < self.config.max_steps:
                # 1. RAG Retrieval Step
                # Cycle through concepts
                concept = self.config.concept_queries[self.global_step % len(self.config.concept_queries)]

                # Retrieve relevant samples
                samples = self.loader.get_batch_by_query(concept, batch_size=self.config.batch_size)

                if not samples:
                    continue

                # 2. Prepare Batch
                batch_inputs = []
                for s in samples:
                    text = f"User: {s.get('prompt', '')}\nAssistant: {s.get('response', '')}<|endoftext|>"
                    batch_inputs.append(text)

                # Tokenize
                encodings = self.tokenizer(
                    batch_inputs,
                    truncation=True,
                    padding="max_length",
                    max_length=512,
                    return_tensors="pt"
                )

                input_ids = encodings["input_ids"].to(self.device)
                attention_mask = encodings["attention_mask"].to(self.device)

                labels = input_ids.clone()
                labels[attention_mask == 0] = -100

                # 3. Forward Pass
                outputs = self.model(
                    input_ids=input_ids,
                    mask=attention_mask,
                    labels=labels
                )

                loss = outputs['loss'] / self.config.gradient_accumulation_steps
                loss.backward()

                accumulation_loss += loss.item()

                # 4. Optimizer Step
                if (self.global_step + 1) % self.config.gradient_accumulation_steps == 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    self.optimizer.step()
                    self.optimizer.zero_grad()

                    self.loss_history.append(accumulation_loss)
                    progress.update(task, advance=1, description=f"[cyan]Step {self.global_step} | Loss: {accumulation_loss:.4f} | Concept: {concept[:20]}...")
                    accumulation_loss = 0.0

                    # Save Checkpoint
                    if self.global_step % self.config.save_every == 0:
                        self._save_checkpoint()

                self.global_step += 1

            # Final Save
            self._save_checkpoint(final=True)

    def _save_checkpoint(self, final=False):
        path = f"{self.config.output_dir}/step_{self.global_step}.pt"
        if final:
            path = f"{self.config.output_dir}/final.pt"

        torch.save({
            "global_step": self.global_step,
            "model_state_dict": self.model.state_dict(),
            "config": self.model.config.to_dict(),
            "loss_history": self.loss_history
        }, path)
        if RICH_AVAILABLE:
            console.print(f"[green]Saved checkpoint to {path}[/green]")

if __name__ == "__main__":
    # Smoke Test Mode
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run in test mode (no GPU req)")
    args = parser.parse_args()

    config = RAGTrainingConfig()

    if args.test:
        config.max_steps = 10
        config.batch_size = 1
        print("Running Trainer Smoke Test...")

        # Mocking for environment without full setup
        try:
            trainer = RAGCurriculumTrainer(config)
            # Just verify initialization worked
            print("Trainer initialized successfully.")
        except Exception as e:
            print(f"Trainer init failed (Expected if no model/data): {e}")
    else:
        trainer = RAGCurriculumTrainer(config)
        trainer.train()
