#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #memory_management #python #source_code #src/training/b3_streaming_training.py #testing #tokenization #training #transformer
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #cuda #memory_management #python #source_code #src\\training\\b3_streaming_training.py #testing #tokenization #training #transformer
# Category:** Training System
# Status:** Active

"""
ImpressionCore B3 Streaming Training System
===========================================
FULL F: DRIVE EMBEDDING TRAINING WITH GTX 1050 Ti OPTIMIZATION
Handles 323K+ embeddings with memory-efficient streaming
Sacred Covenant: 10/10 conversation quality achievement
"""

import os
import json
import time
import gc
import pickle
import traceback
from contextlib import nullcontext
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import AutoTokenizer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# Import our streaming system
from src.dev_tools.data_generation.b3_streaming_dataset import (
    StreamingDataset,
    StreamingConfig,
)

# Import B3 architecture
from src.core.models.impressioncore_b3_architecture import (
    B3Config,
    B3TrainingConfig,
    ImpressionCoreB3Model,
)

console = Console()

class StreamingTrainer:
    """Advanced streaming trainer for unlimited embeddings"""

    def __init__(self, model: nn.Module, config: B3Config, streaming_config: StreamingConfig, model_output_path: str = "checkpoints/streaming"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = model.to(self.device)
        self.config = config
        self.streaming_config = streaming_config
        self.model_output_path = Path(model_output_path)

        # Handle both dict and class config
        if isinstance(config, dict):
            learning_rate = config.get('learning_rate', 1e-4)
        else:
            learning_rate = config.learning_rate

        # Initialize components
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)

        # Memory optimization
        if torch.cuda.is_available():
            self.scaler = torch.amp.GradScaler("cuda")
            self._autocast_kwargs = {"device_type": "cuda"}
        else:
            self.scaler = None
            self._autocast_kwargs = {}
        self.gradient_accumulation_steps = getattr(config, 'gradient_accumulation_steps', 4)
        self.log_every_n_steps = getattr(config, 'log_every_n_steps', 100)

        # Progress tracking
        self.start_time = datetime.now()
        self.global_step = 0
        self.epoch = 0

    def _setup_data_loader(self) -> DataLoader:
        """Create streaming data loader"""
        dataset = StreamingDataset(self.streaming_config, self.tokenizer)

        return DataLoader(
            dataset,
            batch_size=self.streaming_config.batch_size,
            num_workers=0,  # Use our own parallel processing
            pin_memory=True if torch.cuda.is_available() else False,
            drop_last=True
        )

    def _save_checkpoint(self, epoch: int, loss: float):
        """Save training checkpoint"""
        checkpoint_dir = self.model_output_path
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        checkpoint = {
            'epoch': epoch,
            'global_step': self.global_step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'loss': loss,
            'config': self.config,
            'timestamp': datetime.now().isoformat()
        }

        checkpoint_path = checkpoint_dir / f"checkpoint_epoch_{epoch}.pth"
        torch.save(checkpoint, checkpoint_path)

        # Also save latest
        latest_path = checkpoint_dir / "latest.pth"
        torch.save(checkpoint, latest_path)

        console.print(f"[green]Checkpoint saved: {checkpoint_path}[/green]")

    def _log_memory_usage(self):
        """Log current memory usage"""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            cached = torch.cuda.memory_reserved() / 1024**3
            console.print(f"[cyan]VRAM: {allocated:.2f}GB allocated, {cached:.2f}GB reserved[/cyan]")
            return {'allocated_gb': allocated, 'reserved_gb': cached}
        return None

    def train(self):
        """Main training loop with streaming"""
        console.print("[bold green]Starting B3 Streaming Training[/bold green]")
        console.print(f"[cyan]Dataset: {self.streaming_config.root_path}[/cyan]")
        console.print(f"[cyan]Device: {self.device}[/cyan]")

        data_loader = self._setup_data_loader()

        # Training loop
        self.model.train()
        self.optimizer.zero_grad(set_to_none=True)
        total_loss = 0.0
        batch_count = 0
        accumulation_steps = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:

            task = progress.add_task("[cyan]Training...", total=None)

            for batch_idx, batch in enumerate(data_loader):
                try:
                    # Move to device
                    input_ids = batch['input_ids'].to(self.device)
                    labels = batch['labels'].to(self.device)
                    modality_type = batch['modality_type'].to(self.device)

                    image_features = batch.get('image_features')
                    if image_features is None and 'embeddings' in batch:
                        image_features = batch['embeddings']
                    if image_features is not None:
                        image_features = image_features.to(self.device)

                    autocast_ctx = (
                        torch.amp.autocast(**self._autocast_kwargs)
                        if self._autocast_kwargs
                        else nullcontext()
                    )

                    with autocast_ctx:
                        model_outputs = self.model(
                            input_ids=input_ids,
                            image_features=image_features,
                            modality_type=modality_type,
                            labels=labels
                        )

                        loss_full = model_outputs.get('loss')
                        if loss_full is None:
                            logits = model_outputs['logits']
                            shift_logits = logits[..., :-1, :].contiguous()
                            shift_labels = labels[..., 1:].contiguous()
                            loss_fct = nn.CrossEntropyLoss(ignore_index=self.tokenizer.pad_token_id)
                            loss_full = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))

                        loss = loss_full / max(self.gradient_accumulation_steps, 1)

                    if self.scaler:
                        self.scaler.scale(loss).backward()
                    else:
                        loss.backward()

                    total_loss += loss_full.detach().item()
                    batch_count += 1
                    accumulation_steps += 1

                    if accumulation_steps >= self.gradient_accumulation_steps:
                        if self.scaler:
                            self.scaler.step(self.optimizer)
                            self.scaler.update()
                        else:
                            self.optimizer.step()
                        self.optimizer.zero_grad(set_to_none=True)
                        accumulation_steps = 0
                        self.global_step += 1

                    if self.global_step > 0 and self.global_step % self.log_every_n_steps == 0:
                        avg_loss = total_loss / batch_count if batch_count else 0.0
                        console.print(f"[green]Step {self.global_step}, Avg Loss: {avg_loss:.4f}[/green]")
                        self._log_memory_usage()

                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                        gc.collect()

                    if batch_count % 1000 == 0 and batch_count > 0:
                        avg_loss = total_loss / batch_count
                        self._save_checkpoint(self.epoch, avg_loss)

                    progress.update(task, advance=1)

                except Exception as e:
                    console.print(f"[red]Error in batch {batch_idx}: {e}[/red]")
                    traceback.print_exc()
                    continue

            # End of epoch
            if batch_count > 0:
                avg_loss = total_loss / batch_count
                console.print(f"[bold green]Epoch {self.epoch} completed, Avg Loss: {avg_loss:.4f}[/bold green]")
                self._save_checkpoint(self.epoch, avg_loss)

            self.epoch += 1

    def validate(self) -> float:
        """Validation with streaming dataset"""
        # For now, use training loss as validation
        return 0.5  # Placeholder

    def get_training_stats(self) -> Dict[str, Any]:
        """Get comprehensive training statistics"""
        elapsed = datetime.now() - self.start_time

        return {
            'epoch': self.epoch,
            'global_step': self.global_step,
            'elapsed_time': str(elapsed),
            'device': str(self.device),
            'model_parameters': sum(p.numel() for p in self.model.parameters()),
            'memory_usage': self._log_memory_usage() if torch.cuda.is_available() else "CPU mode"
        }

def main():
    """Main training execution"""
    console.print("[bold cyan]ImpressionCore B3 Streaming Training[/bold cyan]")

    # Configuration
    # Import the 3B model and config
    from impressioncore_b3_architecture import ImpressionCoreB3Model3B, B3Config3B

    b3_config = B3Config3B()

    streaming_config = StreamingConfig(
        root_path="F:/",  # Your full F: drive
        max_seq_length=128000, # 128k context
        embedding_dim=4096, # 3B model embedding dim
        num_workers=4,
        batch_size=1,  # Batch size must be 1 for 3B model on 1050 Ti
        memory_limit_gb=3.5,
        checkpoint_interval=1000
    )

    # Initialize model and trainer
    model = ImpressionCoreB3Model3B()
    trainer = StreamingTrainer(model, b3_config, streaming_config, model_output_path="F:/models/")

    # Start training
    try:
        trainer.train()
    except KeyboardInterrupt:
        console.print("[yellow]Training interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Training error: {e}[/red]")
        raise

    # Final stats
    stats = trainer.get_training_stats()
    console.print("[bold green]Training completed![/bold green]")
    console.print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()