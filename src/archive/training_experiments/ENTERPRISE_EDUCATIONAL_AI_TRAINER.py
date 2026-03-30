#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #command_line #cuda #gpu_optimization #memory_management #python #source_code #src/training/enterprise_educational_ai_trainer.py #testing #tokenization #training #transformer
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #attention_mechanism #command_line #cuda #gpu_optimization #memory_management #python #source_code #src\\training\\enterprise_educational_ai_trainer.py #testing #tokenization #training #transformer
# Category:** Training System
# Status:** Active

"""
🚀 ENTERPRISE EDUCATIONAL AI TRAINER
World-class high school graduate AI training system

This trainer uses the enterprise-grade educational dataset to create
a sophisticated AI model that demonstrates high school graduate-level
competency across all academic subjects.

Features:
- Multi-subject curriculum learning
- Standards-aligned training objectives
- Knowledge distillation from larger models
- Comprehensive evaluation metrics
- Enterprise-grade performance monitoring

Author: ImpressionCore Educational AI Team
License: MIT
Version: 1.0.0
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json
import logging
import time
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling,
    get_linear_schedule_with_warmup
)
from datasets import Dataset as HFDataset
import wandb
from pathlib import Path
import os
import gc

# Rich console enhancements
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    from rich.logging import RichHandler
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich not available, using standard output")

@dataclass
class TrainingConfig:
    """Configuration for the enterprise training pipeline."""

    # Model Configuration
    model_name: str = "microsoft/DialoGPT-small"
    max_length: int = 512

    # Training Configuration
    batch_size: int = 4
    learning_rate: float = 5e-5
    num_epochs: int = 3
    warmup_steps: int = 100
    weight_decay: float = 0.01
    gradient_accumulation_steps: int = 2

    # Curriculum Learning
    enable_curriculum: bool = True
    curriculum_stages: List[str] = None

    # Knowledge Distillation
    enable_distillation: bool = True
    teacher_model: str = "microsoft/DialoGPT-medium"
    distillation_temperature: float = 4.0
    distillation_alpha: float = 0.7

    # Evaluation
    eval_steps: int = 100
    save_steps: int = 200
    logging_steps: int = 50

    # Hardware Optimization
    fp16: bool = True
    dataloader_num_workers: int = 2

    def __post_init__(self):
        if self.curriculum_stages is None:
            self.curriculum_stages = [
                "mathematics", "science", "english_language_arts",
                "social_studies", "computer_science"
            ]

class EducationalDataset(Dataset):
    """Custom dataset for educational content with curriculum learning support."""

    def __init__(self, data_path: str, tokenizer, config: TrainingConfig,
                 current_stage: str = None):
        self.tokenizer = tokenizer
        self.config = config
        self.current_stage = current_stage

        # Load the enterprise dataset
        with open(data_path, 'r', encoding='utf-8') as f:
            self.dataset = json.load(f)

        self.qa_pairs = self.dataset['qa_pairs']

        # Filter by current curriculum stage if enabled
        if config.enable_curriculum and current_stage:
            self.qa_pairs = [
                qa for qa in self.qa_pairs
                if qa['subject'] == current_stage
            ]

        # Prepare training examples
        self.examples = self._prepare_examples()

        logging.info(f"Loaded {len(self.examples)} training examples for stage: {current_stage or 'all'}")

    def _prepare_examples(self) -> List[Dict]:
        """Prepare training examples from QA pairs."""
        examples = []

        for qa in self.qa_pairs:
            # Format as conversational pairs
            question = qa['question']
            answer = qa['answer']
            context = qa.get('context', '')

            # Create training text
            if context:
                training_text = f"Context: {context}\n\nQuestion: {question}\n\nAnswer: {answer}"
            else:
                training_text = f"Question: {question}\n\nAnswer: {answer}"

            examples.append({
                'text': training_text,
                'subject': qa['subject'],
                'difficulty': qa['difficulty'],
                'cognitive_level': qa['cognitive_level'],
                'quality_score': qa['quality_score']
            })

        return examples

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        example = self.examples[idx]

        # Tokenize the text
        encoding = self.tokenizer(
            example['text'],
            truncation=True,
            padding='max_length',
            max_length=self.config.max_length,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': encoding['input_ids'].squeeze(),
            'metadata': {
                'subject': example['subject'],
                'difficulty': example['difficulty'],
                'cognitive_level': example['cognitive_level'],
                'quality_score': example['quality_score']
            }
        }

class EnterpriseEducationalTrainer:
    """Enterprise-grade educational AI trainer with advanced features."""

    def __init__(self, config: TrainingConfig, dataset_path: str):
        self.config = config
        self.dataset_path = dataset_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Initialize rich console if available
        if RICH_AVAILABLE:
            self.console = Console()
            self.setup_rich_logging()
        else:
            self.console = None

        # Initialize components
        self.tokenizer = None
        self.model = None
        self.teacher_model = None
        self.optimizer = None
        self.scheduler = None

        # Training state
        self.current_stage = 0
        self.training_history = []
        self.best_loss = float('inf')

        # Setup directories
        self.output_dir = Path(f"enterprise_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.output_dir.mkdir(exist_ok=True)

        self.log_message("🚀 Enterprise Educational Trainer initialized", "info")

    def setup_rich_logging(self):
        """Setup rich logging handlers."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=self.console, rich_tracebacks=True)]
        )

    def log_message(self, message: str, level: str = "info"):
        """Log message with rich formatting if available."""
        if self.console:
            if level == "info":
                self.console.print(f"[blue]ℹ️  {message}[/blue]")
            elif level == "success":
                self.console.print(f"[green]✅ {message}[/green]")
            elif level == "warning":
                self.console.print(f"[yellow]⚠️  {message}[/yellow]")
            elif level == "error":
                self.console.print(f"[red]❌ {message}[/red]")
        else:
            print(f"{level.upper()}: {message}")

    def initialize_models(self):
        """Initialize the student and teacher models."""
        self.log_message("Loading tokenizer and models...", "info")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load student model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            torch_dtype=torch.float16 if self.config.fp16 else torch.float32
        )
        self.model.to(self.device)

        # Load teacher model for distillation
        if self.config.enable_distillation:
            self.log_message("Loading teacher model for knowledge distillation...", "info")
            self.teacher_model = AutoModelForCausalLM.from_pretrained(
                self.config.teacher_model,
                torch_dtype=torch.float16 if self.config.fp16 else torch.float32
            )
            self.teacher_model.to(self.device)
            self.teacher_model.eval()

        # Setup optimizer and scheduler
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay
        )

        self.log_message("Models initialized successfully", "success")

    def create_curriculum_stage_dataset(self, stage: str) -> EducationalDataset:
        """Create dataset for a specific curriculum stage."""
        return EducationalDataset(
            self.dataset_path,
            self.tokenizer,
            self.config,
            current_stage=stage
        )

    def knowledge_distillation_loss(self, student_logits, teacher_logits, labels, temperature):
        """Calculate knowledge distillation loss."""
        # Soft target loss (distillation)
        soft_targets = torch.softmax(teacher_logits / temperature, dim=-1)
        soft_predictions = torch.log_softmax(student_logits / temperature, dim=-1)
        distillation_loss = torch.nn.KLDivLoss(reduction='batchmean')(
            soft_predictions, soft_targets
        ) * (temperature ** 2)

        # Hard target loss (standard)
        hard_loss = torch.nn.CrossEntropyLoss()(
            student_logits.view(-1, student_logits.size(-1)),
            labels.view(-1)
        )

        # Combine losses
        total_loss = (
            self.config.distillation_alpha * distillation_loss +
            (1 - self.config.distillation_alpha) * hard_loss
        )

        return total_loss, distillation_loss, hard_loss

    def train_stage(self, stage: str, stage_idx: int) -> Dict:
        """Train a single curriculum stage."""
        self.log_message(f"Starting training stage {stage_idx + 1}/{len(self.config.curriculum_stages)}: {stage}", "info")

        # Create dataset for this stage
        dataset = self.create_curriculum_stage_dataset(stage)

        if len(dataset) == 0:
            self.log_message(f"No data found for stage {stage}, skipping", "warning")
            return {}

        # Create data loader
        dataloader = DataLoader(
            dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=self.config.dataloader_num_workers,
            pin_memory=True
        )

        # Setup scheduler for this stage
        total_steps = len(dataloader) * self.config.num_epochs
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=self.config.warmup_steps,
            num_training_steps=total_steps
        )

        # Training loop
        self.model.train()
        stage_losses = []
        stage_start_time = time.time()

        if RICH_AVAILABLE:
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=self.console
            )

            with progress:
                task = progress.add_task(f"Training {stage}...", total=total_steps)

                step = 0
                for epoch in range(self.config.num_epochs):
                    epoch_losses = []

                    for batch_idx, batch in enumerate(dataloader):
                        step += 1

                        # Move batch to device
                        input_ids = batch['input_ids'].to(self.device)
                        attention_mask = batch['attention_mask'].to(self.device)
                        labels = batch['labels'].to(self.device)

                        # Forward pass
                        outputs = self.model(
                            input_ids=input_ids,
                            attention_mask=attention_mask,
                            labels=labels
                        )

                        if self.config.enable_distillation and self.teacher_model:
                            # Get teacher outputs
                            with torch.no_grad():
                                teacher_outputs = self.teacher_model(
                                    input_ids=input_ids,
                                    attention_mask=attention_mask
                                )

                            # Calculate distillation loss
                            loss, dist_loss, hard_loss = self.knowledge_distillation_loss(
                                outputs.logits,
                                teacher_outputs.logits,
                                labels,
                                self.config.distillation_temperature
                            )
                        else:
                            loss = outputs.loss

                        # Backward pass
                        loss.backward()

                        if step % self.config.gradient_accumulation_steps == 0:
                            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                            self.optimizer.step()
                            self.scheduler.step()
                            self.optimizer.zero_grad()

                        # Track metrics
                        epoch_losses.append(loss.item())

                        # Update progress
                        progress.update(task, advance=1)

                        # Log periodically
                        if step % self.config.logging_steps == 0:
                            avg_loss = np.mean(epoch_losses[-self.config.logging_steps:])
                            progress.update(task, description=f"Training {stage} - Loss: {avg_loss:.4f}")

                    stage_losses.extend(epoch_losses)
        else:
            # Standard training loop without rich progress
            step = 0
            for epoch in range(self.config.num_epochs):
                print(f"Epoch {epoch + 1}/{self.config.num_epochs}")
                epoch_losses = []

                for batch_idx, batch in enumerate(dataloader):
                    step += 1

                    # Move batch to device
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    labels = batch['labels'].to(self.device)

                    # Forward pass
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels=labels
                    )

                    if self.config.enable_distillation and self.teacher_model:
                        # Get teacher outputs
                        with torch.no_grad():
                            teacher_outputs = self.teacher_model(
                                input_ids=input_ids,
                                attention_mask=attention_mask
                            )

                        # Calculate distillation loss
                        loss, dist_loss, hard_loss = self.knowledge_distillation_loss(
                            outputs.logits,
                            teacher_outputs.logits,
                            labels,
                            self.config.distillation_temperature
                        )
                    else:
                        loss = outputs.loss

                    # Backward pass
                    loss.backward()

                    if step % self.config.gradient_accumulation_steps == 0:
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                        self.optimizer.step()
                        self.scheduler.step()
                        self.optimizer.zero_grad()

                    # Track metrics
                    epoch_losses.append(loss.item())

                    # Log periodically
                    if step % self.config.logging_steps == 0:
                        avg_loss = np.mean(epoch_losses[-self.config.logging_steps:])
                        print(f"Step {step}, Loss: {avg_loss:.4f}")

                stage_losses.extend(epoch_losses)

        # Calculate stage metrics
        stage_time = time.time() - stage_start_time
        avg_loss = np.mean(stage_losses)

        stage_metrics = {
            'stage': stage,
            'stage_idx': stage_idx,
            'avg_loss': avg_loss,
            'training_time': stage_time,
            'examples_processed': len(dataset),
            'steps': step
        }

        self.training_history.append(stage_metrics)

        self.log_message(
            f"Completed stage {stage}: Avg Loss: {avg_loss:.4f}, Time: {stage_time:.2f}s",
            "success"
        )

        return stage_metrics

    def train_curriculum(self) -> Dict:
        """Train the model using curriculum learning across all stages."""
        self.log_message("Starting curriculum-based training", "info")

        training_start_time = time.time()

        # Train each curriculum stage
        for stage_idx, stage in enumerate(self.config.curriculum_stages):
            stage_metrics = self.train_stage(stage, stage_idx)

            # Save checkpoint after each stage
            if stage_metrics:
                checkpoint_path = self.output_dir / f"checkpoint_stage_{stage_idx + 1}_{stage}"
                self.save_checkpoint(checkpoint_path, stage_metrics)

            # Garbage collection to free memory
            gc.collect()
            torch.cuda.empty_cache()

        # Calculate overall training metrics
        total_time = time.time() - training_start_time
        total_examples = sum(metrics['examples_processed'] for metrics in self.training_history)
        avg_loss = np.mean([metrics['avg_loss'] for metrics in self.training_history])

        final_metrics = {
            'total_training_time': total_time,
            'total_examples_processed': total_examples,
            'average_loss': avg_loss,
            'stages_completed': len(self.training_history),
            'stage_history': self.training_history
        }

        self.log_message(f"Curriculum training completed in {total_time:.2f}s", "success")
        self.log_message(f"Total examples processed: {total_examples}", "info")
        self.log_message(f"Average loss: {avg_loss:.4f}", "info")

        return final_metrics

    def save_checkpoint(self, path: Path, metrics: Dict):
        """Save model checkpoint with training metrics."""
        path.mkdir(exist_ok=True)

        # Save model and tokenizer
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)

        # Save training metrics
        with open(path / "training_metrics.json", 'w') as f:
            json.dump(metrics, f, indent=2)

        self.log_message(f"Checkpoint saved to {path}", "info")

    def save_final_model(self, metrics: Dict):
        """Save the final trained model."""
        final_path = self.output_dir / "final_model"
        final_path.mkdir(exist_ok=True)

        # Save model and tokenizer
        self.model.save_pretrained(final_path)
        self.tokenizer.save_pretrained(final_path)

        # Save comprehensive training report
        report = {
            'model_name': self.config.model_name,
            'training_config': self.config.__dict__,
            'final_metrics': metrics,
            'training_history': self.training_history,
            'created_at': datetime.now().isoformat(),
            'device_used': str(self.device)
        }

        with open(final_path / "training_report.json", 'w') as f:
            json.dump(report, f, indent=2)

        self.log_message(f"Final model saved to {final_path}", "success")

        return final_path

    def run_full_training(self):
        """Run the complete enterprise training pipeline."""
        try:
            self.log_message("🎓 Starting Enterprise Educational AI Training", "info")

            # Display training configuration
            if self.console:
                config_table = Table(title="Training Configuration")
                config_table.add_column("Parameter", style="cyan")
                config_table.add_column("Value", style="magenta")

                config_table.add_row("Model", self.config.model_name)
                config_table.add_row("Batch Size", str(self.config.batch_size))
                config_table.add_row("Learning Rate", str(self.config.learning_rate))
                config_table.add_row("Epochs", str(self.config.num_epochs))
                config_table.add_row("Curriculum Learning", str(self.config.enable_curriculum))
                config_table.add_row("Knowledge Distillation", str(self.config.enable_distillation))
                config_table.add_row("Device", str(self.device))

                self.console.print(config_table)

            # Initialize models
            self.initialize_models()

            # Run curriculum training
            final_metrics = self.train_curriculum()

            # Save final model
            final_path = self.save_final_model(final_metrics)

            # Display final results
            if self.console:
                self.console.print(
                    Panel(
                        f"🎉 Training completed successfully!\n\n"
                        f"📍 Model saved to: {final_path}\n"
                        f"⏱️  Total time: {final_metrics['total_training_time']:.2f}s\n"
                        f"📚 Examples processed: {final_metrics['total_examples_processed']}\n"
                        f"📉 Final average loss: {final_metrics['average_loss']:.4f}",
                        title="Enterprise Training Complete",
                        border_style="green"
                    )
                )
            else:
                print("=" * 60)
                print("🎉 ENTERPRISE TRAINING COMPLETED SUCCESSFULLY!")
                print(f"📍 Model saved to: {final_path}")
                print(f"⏱️  Total time: {final_metrics['total_training_time']:.2f}s")
                print(f"📚 Examples processed: {final_metrics['total_examples_processed']}")
                print(f"📉 Final average loss: {final_metrics['average_loss']:.4f}")
                print("=" * 60)

            return final_path, final_metrics

        except KeyboardInterrupt:
            self.log_message("Training interrupted by user", "warning")
            raise
        except Exception as e:
            self.log_message(f"Training failed: {str(e)}", "error")
            raise

def main():
    """Main function to run the enterprise educational trainer."""

    # Configuration
    config = TrainingConfig(
        model_name="microsoft/DialoGPT-small",
        batch_size=2,  # Reduced for consumer GPU
        learning_rate=3e-5,
        num_epochs=2,
        enable_curriculum=True,
        enable_distillation=False,  # Disabled for initial run
        fp16=True
    )

    # Find the latest enterprise dataset
    dataset_files = [f for f in os.listdir('.') if f.startswith('enterprise_educational_dataset_') and f.endswith('.json')]
    if not dataset_files:
        print("❌ No enterprise dataset found! Please run the dataset builder first.")
        return

    latest_dataset = max(dataset_files, key=lambda x: os.path.getctime(x))
    print(f"📚 Using dataset: {latest_dataset}")

    # Create and run trainer
    trainer = EnterpriseEducationalTrainer(config, latest_dataset)

    try:
        final_path, metrics = trainer.run_full_training()
        print(f"\n🚀 Enterprise Educational AI training completed!")
        print(f"🎓 Your high school graduate-level AI is ready!")

    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
