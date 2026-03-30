"""
ImpressionCore B3 Foundation Model - Training Pipeline

Created: October 11, 2025
Updated: October 11, 2025
Author: Kirk LaSalle; GitHub Copilot
Tags: #b3_foundation #training #multimodal #gtx1050ti
Category: Training Infrastructure
Status: Active

This module provides the training pipeline for B3 Foundation Model:
- Multimodal data loading (text, image, audio)
- Mixed precision training (FP16/FP32)
- Gradient checkpointing and accumulation
- MoE load balancing loss
- Performance monitoring
- Checkpoint saving/loading
- Memory optimization for GTX 1050 Ti

Constitutional Compliance: Trains 39M parameter target model.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import time
import json
from dataclasses import dataclass, asdict

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Handle imports
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.core.utils.amp_utils import create_grad_scaler, autocast_context
except ImportError:
    from core.utils.amp_utils import create_grad_scaler, autocast_context  # type: ignore[import]

try:
    from src.core.models.b3_foundation_architecture import B3FoundationConfig
    from src.core.models.b3_foundation_integrated import B3FoundationIntegrated
except ImportError:
    from core.models.b3_foundation_architecture import B3FoundationConfig
    from core.models.b3_foundation_integrated import B3FoundationIntegrated


@dataclass
class TrainingConfig:
    """Training configuration for B3 Foundation Model."""

    # Model
    model_name: str = "B3-Foundation"
    checkpoint_dir: str = "checkpoints/b3_foundation"

    # Training
    num_epochs: int = 1
    batch_size: int = 1  # Small for GTX 1050 Ti
    gradient_accumulation_steps: int = 8  # Effective batch = 8
    learning_rate: float = 1e-5
    weight_decay: float = 0.01
    max_grad_norm: float = 0.5
    warmup_steps: int = 100

    # Mixed precision
    use_mixed_precision: bool = True

    # MoE
    load_balancing_loss_weight: float = 0.01

    # Logging
    log_interval: int = 10
    save_interval: int = 100
    eval_interval: int = 50

    # Memory optimization
    max_seq_length: int = 128  # Reduced for memory
    gradient_checkpointing: bool = True

    # Device
    device: str = "cuda" if torch.cuda.is_available() else "cpu"

    # Modalities
    enable_text: bool = True
    enable_image: bool = False  # Disable for Phase 1
    enable_audio: bool = False  # Disable for Phase 1


class DummyMultimodalDataset(Dataset):
    """
    Dummy dataset for testing training pipeline.

    In production, this would load real multimodal data:
    - Text: Tokenized sequences
    - Image: RGB images (224x224)
    - Audio: Raw waveforms (16kHz)
    """

    def __init__(
        self,
        num_samples: int = 1000,
        vocab_size: int = 50257,
        seq_length: int = 128,
        enable_text: bool = True,
        enable_image: bool = False,
        enable_audio: bool = False
    ):
        self.num_samples = num_samples
        self.vocab_size = vocab_size
        self.seq_length = seq_length
        self.enable_text = enable_text
        self.enable_image = enable_image
        self.enable_audio = enable_audio

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        sample = {}

        if self.enable_text:
            # Random token IDs (in production: real tokenized text)
            sample['input_ids'] = torch.randint(0, self.vocab_size, (self.seq_length,))
            sample['labels'] = sample['input_ids'].clone()  # Next token prediction

        if self.enable_image:
            # Random images (in production: real images from dataset)
            sample['pixel_values'] = torch.randn(3, 224, 224)

        if self.enable_audio:
            # Random audio (in production: real audio waveforms)
            sample['audio_values'] = torch.randn(16000)  # 1 second at 16kHz

        return sample


class B3Trainer:
    """
    Training orchestrator for B3 Foundation Model.

    Features:
    - Mixed precision training (FP16/FP32)
    - Gradient accumulation for larger effective batch size
    - MoE load balancing loss integration
    - Checkpoint saving/loading
    - Performance monitoring (loss, VRAM, speed)
    """

    def __init__(
        self,
        model: B3FoundationIntegrated,
        config: TrainingConfig,
        train_dataset: Dataset,
        val_dataset: Optional[Dataset] = None
    ):
        self.model = model
        self.config = config
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset

        # Move model to device
        self.model.to(config.device)
        logger.info(f"✅ Model moved to {config.device}")

        # Data loaders (needed before scheduler)
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=config.batch_size,
            shuffle=True,
            num_workers=0,  # 0 for Windows compatibility
            pin_memory=True if config.device == "cuda" else False
        )
        logger.info(f"✅ Train DataLoader created (batch_size={config.batch_size})")

        if val_dataset:
            self.val_loader = DataLoader(
                val_dataset,
                batch_size=config.batch_size,
                shuffle=False,
                num_workers=0,
                pin_memory=True if config.device == "cuda" else False
            )
            logger.info(f"✅ Validation DataLoader created")
        else:
            self.val_loader = None

        # Optimizer
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay
        )
        logger.info(f"✅ AdamW optimizer initialized (lr={config.learning_rate})")

        # Learning rate scheduler (warmup + cosine decay)
        self.scheduler = self._create_scheduler()
        logger.info(f"✅ Learning rate scheduler initialized (warmup={config.warmup_steps})")

        # Mixed precision scaler
        device_string = str(self.config.device)
        self.amp_device_type = "cuda"
        amp_requested = config.use_mixed_precision and device_string.startswith("cuda")

        self.scaler = create_grad_scaler(
            enabled=amp_requested,
            device_type=self.amp_device_type
        )
        self.amp_enabled = self.scaler is not None
        if self.amp_enabled:
            logger.info("✅ Mixed precision training enabled (FP16/FP32)")
        elif config.use_mixed_precision and device_string.startswith("cuda"):
            logger.warning(
                "⚠️ Mixed precision requested but unavailable; proceeding in full precision"
            )
        elif config.use_mixed_precision:
            logger.warning(
                "⚠️ Mixed precision requested on non-CUDA device; proceeding in full precision"
            )

        # Training state
        self.global_step = 0
        self.epoch = 0
        self.best_val_loss = float('inf')

        # Checkpoint directory
        os.makedirs(config.checkpoint_dir, exist_ok=True)
        logger.info(f"✅ Checkpoint directory: {config.checkpoint_dir}")

    def _create_scheduler(self):
        """Create learning rate scheduler with warmup."""
        total_steps = len(self.train_loader) * self.config.num_epochs

        def lr_lambda(step):
            if step < self.config.warmup_steps:
                return step / self.config.warmup_steps
            else:
                progress = (step - self.config.warmup_steps) / (total_steps - self.config.warmup_steps)
                return 0.5 * (1 + np.cos(np.pi * progress))

        return torch.optim.lr_scheduler.LambdaLR(self.optimizer, lr_lambda)

    def train_epoch(self):
        """Train for one epoch."""
        self.model.train()
        epoch_loss = 0.0
        epoch_ce_loss = 0.0
        epoch_lb_loss = 0.0

        start_time = time.time()

        for batch_idx, batch in enumerate(self.train_loader):
            # Move batch to device
            batch = {k: v.to(self.config.device) if isinstance(v, torch.Tensor) else v
                    for k, v in batch.items()}

            # Forward pass with mixed precision
            if self.amp_enabled:
                with autocast_context(
                    enabled=self.amp_enabled,
                    device_type=self.amp_device_type
                ):
                    loss, metrics = self._forward_step(batch)
            else:
                loss, metrics = self._forward_step(batch)

            # Scale loss for gradient accumulation
            loss = loss / self.config.gradient_accumulation_steps

            # Backward pass
            if self.amp_enabled:
                self.scaler.scale(loss).backward()
            else:
                loss.backward()

            # Update weights every N accumulation steps
            if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                # Gradient clipping
                if self.amp_enabled:
                    self.scaler.unscale_(self.optimizer)

                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.max_grad_norm
                )

                # Optimizer step
                if self.amp_enabled:
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    self.optimizer.step()

                self.scheduler.step()
                self.optimizer.zero_grad()

                self.global_step += 1

            # Accumulate losses
            epoch_loss += loss.item() * self.config.gradient_accumulation_steps
            epoch_ce_loss += metrics['ce_loss']
            epoch_lb_loss += metrics['lb_loss']

            # Logging
            if (batch_idx + 1) % self.config.log_interval == 0:
                self._log_progress(
                    batch_idx,
                    len(self.train_loader),
                    metrics,
                    start_time
                )

            # Save checkpoint
            if self.global_step % self.config.save_interval == 0 and self.global_step > 0:
                self.save_checkpoint(f"step_{self.global_step}")

            # Validation
            if self.val_loader and self.global_step % self.config.eval_interval == 0 and self.global_step > 0:
                val_loss = self.validate()
                self.model.train()

                # Save best model
                if val_loss < self.best_val_loss:
                    self.best_val_loss = val_loss
                    self.save_checkpoint("best_model")
                    logger.info(f"✅ New best model saved (val_loss={val_loss:.4f})")

        # Epoch statistics
        num_batches = len(self.train_loader)
        avg_loss = epoch_loss / num_batches
        avg_ce_loss = epoch_ce_loss / num_batches
        avg_lb_loss = epoch_lb_loss / num_batches

        return {
            'loss': avg_loss,
            'ce_loss': avg_ce_loss,
            'lb_loss': avg_lb_loss
        }

    def _forward_step(self, batch):
        """Forward pass and loss computation."""
        # Extract inputs
        input_ids = batch.get('input_ids', None)
        pixel_values = batch.get('pixel_values', None)
        audio_values = batch.get('audio_values', None)
        labels = batch.get('labels', None)

        # Forward pass
        logits, aux_outputs = self.model(
            input_ids=input_ids,
            pixel_values=pixel_values,
            audio_values=audio_values,
            return_aux_outputs=True
        )

        # Cross-entropy loss (next token prediction)
        if labels is not None:
            ce_loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),
                labels.view(-1)
            )
        else:
            ce_loss = torch.tensor(0.0, device=logits.device)

        # Load balancing loss (MoE)
        lb_loss = aux_outputs['load_balancing_loss'] * self.config.load_balancing_loss_weight

        # Total loss
        total_loss = ce_loss + lb_loss

        metrics = {
            'ce_loss': ce_loss.item(),
            'lb_loss': lb_loss.item(),
            'total_loss': total_loss.item()
        }

        return total_loss, metrics

    def _log_progress(self, batch_idx, num_batches, metrics, start_time):
        """Log training progress."""
        elapsed = time.time() - start_time
        batches_done = batch_idx + 1
        eta = elapsed / batches_done * (num_batches - batches_done)

        lr = self.scheduler.get_last_lr()[0]

        # Memory stats
        if torch.cuda.is_available():
            mem_allocated = torch.cuda.memory_allocated() / 1024**2
            mem_reserved = torch.cuda.memory_reserved() / 1024**2
            mem_str = f"GPU: {mem_allocated:.0f}MB / {mem_reserved:.0f}MB"
        else:
            mem_str = "CPU"

        logger.info(
            f"Epoch {self.epoch} | "
            f"Step {self.global_step} | "
            f"Batch {batches_done}/{num_batches} | "
            f"Loss: {metrics['total_loss']:.4f} "
            f"(CE: {metrics['ce_loss']:.4f}, LB: {metrics['lb_loss']:.6f}) | "
            f"LR: {lr:.2e} | "
            f"{mem_str} | "
            f"ETA: {eta/60:.1f}m"
        )

    @torch.no_grad()
    def validate(self):
        """Run validation."""
        if not self.val_loader:
            return float('inf')

        self.model.eval()
        total_loss = 0.0
        num_batches = 0

        for batch in self.val_loader:
            batch = {k: v.to(self.config.device) if isinstance(v, torch.Tensor) else v
                    for k, v in batch.items()}

            with autocast_context(
                enabled=self.amp_enabled,
                device_type=self.amp_device_type
            ):
                _, metrics = self._forward_step(batch)
            total_loss += metrics['total_loss']
            num_batches += 1

        avg_loss = total_loss / num_batches
        logger.info(f"📊 Validation Loss: {avg_loss:.4f}")

        return avg_loss

    def save_checkpoint(self, name: str):
        """Save model checkpoint."""
        checkpoint_path = Path(self.config.checkpoint_dir) / f"{name}.pt"

        checkpoint = {
            'epoch': self.epoch,
            'global_step': self.global_step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'config': asdict(self.config),
            'best_val_loss': self.best_val_loss
        }

        if self.scaler:
            checkpoint['scaler_state_dict'] = self.scaler.state_dict()

        torch.save(checkpoint, checkpoint_path)
        logger.info(f"💾 Checkpoint saved: {checkpoint_path}")

    def load_checkpoint(self, checkpoint_path: str):
        """Load model checkpoint."""
        checkpoint = torch.load(checkpoint_path, map_location=self.config.device)

        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

        if self.scaler and 'scaler_state_dict' in checkpoint:
            self.scaler.load_state_dict(checkpoint['scaler_state_dict'])

        self.epoch = checkpoint['epoch']
        self.global_step = checkpoint['global_step']
        self.best_val_loss = checkpoint['best_val_loss']

        logger.info(f"✅ Checkpoint loaded from: {checkpoint_path}")
        logger.info(f"   Epoch: {self.epoch}, Step: {self.global_step}")

    def train(self):
        """Main training loop."""
        logger.info("=" * 80)
        logger.info("🚀 Starting B3 Foundation Training")
        logger.info("=" * 80)
        logger.info(f"Epochs: {self.config.num_epochs}")
        logger.info(f"Batch size: {self.config.batch_size}")
        logger.info(f"Gradient accumulation: {self.config.gradient_accumulation_steps}")
        logger.info(f"Effective batch size: {self.config.batch_size * self.config.gradient_accumulation_steps}")
        logger.info(f"Learning rate: {self.config.learning_rate}")
        logger.info(f"Device: {self.config.device}")
        logger.info("=" * 80)

        for epoch in range(self.config.num_epochs):
            self.epoch = epoch

            logger.info(f"\n📈 Epoch {epoch + 1}/{self.config.num_epochs}")
            logger.info("-" * 80)

            epoch_metrics = self.train_epoch()

            logger.info("-" * 80)
            logger.info(f"📊 Epoch {epoch + 1} Summary:")
            logger.info(f"   Average Loss: {epoch_metrics['loss']:.4f}")
            logger.info(f"   CE Loss: {epoch_metrics['ce_loss']:.4f}")
            logger.info(f"   LB Loss: {epoch_metrics['lb_loss']:.6f}")

            # Save epoch checkpoint
            self.save_checkpoint(f"epoch_{epoch + 1}")

        logger.info("=" * 80)
        logger.info("✅ Training completed!")
        logger.info("=" * 80)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN TRAINING SCRIPT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Main training script for B3 Foundation Model.

    Usage:
        python train_b3_foundation.py
    """

    print("\n" + "=" * 80)
    print("B3 Foundation Model - Training Pipeline")
    print("=" * 80)

    # Load configurations
    model_config = B3FoundationConfig()
    train_config = TrainingConfig()

    logger.info("✅ Configurations loaded")
    logger.info(f"   Model: {model_config.model_name}")
    logger.info(f"   Device: {train_config.device}")
    logger.info(f"   Mixed Precision: {train_config.use_mixed_precision}")

    # Create datasets
    logger.info("\n" + "=" * 80)
    logger.info("Creating Datasets")
    logger.info("=" * 80)

    train_dataset = DummyMultimodalDataset(
        num_samples=1000,
        vocab_size=model_config.vocab_size,
        seq_length=train_config.max_seq_length,
        enable_text=train_config.enable_text,
        enable_image=train_config.enable_image,
        enable_audio=train_config.enable_audio
    )

    val_dataset = DummyMultimodalDataset(
        num_samples=100,
        vocab_size=model_config.vocab_size,
        seq_length=train_config.max_seq_length,
        enable_text=train_config.enable_text,
        enable_image=train_config.enable_image,
        enable_audio=train_config.enable_audio
    )

    logger.info(f"✅ Train dataset: {len(train_dataset)} samples")
    logger.info(f"✅ Val dataset: {len(val_dataset)} samples")

    # Create model
    logger.info("\n" + "=" * 80)
    logger.info("Creating Model")
    logger.info("=" * 80)

    model = B3FoundationIntegrated(
        model_config,
        enable_text=train_config.enable_text,
        enable_image=train_config.enable_image,
        enable_audio=train_config.enable_audio
    )

    # Create trainer
    logger.info("\n" + "=" * 80)
    logger.info("Creating Trainer")
    logger.info("=" * 80)

    trainer = B3Trainer(
        model=model,
        config=train_config,
        train_dataset=train_dataset,
        val_dataset=val_dataset
    )

    # Start training
    logger.info("\n")
    trainer.train()

    # Final memory report
    if torch.cuda.is_available():
        logger.info("\n" + "=" * 80)
        logger.info("Final Memory Report")
        logger.info("=" * 80)

        allocated = torch.cuda.memory_allocated() / 1024**2
        reserved = torch.cuda.memory_reserved() / 1024**2
        max_allocated = torch.cuda.max_memory_allocated() / 1024**2

        logger.info(f"Current allocated: {allocated:.1f} MB")
        logger.info(f"Current reserved: {reserved:.1f} MB")
        logger.info(f"Peak allocated: {max_allocated:.1f} MB")
        logger.info(f"Target: <3.5 GB for training on GTX 1050 Ti")

        if max_allocated < 3584:  # 3.5 GB in MB
            logger.info(f"✅ Memory target MET ({max_allocated:.1f} MB < 3584 MB)")
        else:
            logger.info(f"⚠️  Memory target EXCEEDED ({max_allocated:.1f} MB > 3584 MB)")

    logger.info("\n" + "=" * 80)
    logger.info("🎉 Training pipeline execution complete!")
    logger.info("=" * 80)
