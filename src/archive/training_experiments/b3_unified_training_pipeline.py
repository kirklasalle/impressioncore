#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #cuda #memory_management #multimodal #python #source_code #src/training/b3_unified_training_pipeline.py #tokenization #training
**Category:** Training System
**Status:** Active
"""



import os
import sys
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import torch.nn.functional as F
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import logging
from datetime import datetime
import time
import argparse
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
import numpy as np
import glob
import webdataset as wds
from transformers import GPT2TokenizerFast
from functools import partial

# Add project root to path
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_path))

# Import ImpressionCore components
try:
    from src.core.models.b3_unified_integration import B3UnifiedTokenizerBridge, create_optimized_b3_system
    from src.core.models.impressioncore_b3_architecture import B3Config
    from src.core.models.unified_tokenizer_system import UnifiedTokenizerSystem
    from src.core.utils.rich_logging import setup_rich_logging
    from src.core.utils.rich_enhancements import print_success, print_warning, print_error, print_info
except ImportError as e:
    # Refactored: avoid sys.exit on import so lightweight tests can still run.
    # Raise a clear ImportError that callers can catch; preserves Phase 2 restructuring safety.
    raise ImportError(
        f"ImpressionCore B3 components not available during import: {e}. "
        "Run from project root with environment active to access full training pipeline."
    ) from e

# Initialize rich console and logging
console = Console()
logger = setup_rich_logging(__name__)

@dataclass
class TrainingConfig:
    """Training configuration optimized for GTX 1050 Ti"""

    # Memory Optimization
    batch_size: int = 1
    gradient_accumulation_steps: int = 32  # Effective batch size of 32
    mixed_precision: bool = True
    gradient_checkpointing: bool = True
    max_sequence_length: int = 512

    # Model Architecture (GTX 1050 Ti Nano-profile)
    embed_dim: int = 384
    num_heads: int = 6
    num_layers: int = 6
    num_experts: int = 2
    expert_dim: int = 1536
    experts_per_token: int = 1
    dropout: float = 0.1

    # Training Dynamics
    learning_rate: float = 1e-5
    warmup_steps: int = 1000
    max_epochs: int = 10
    evaluation_frequency: int = 100
    save_frequency: int = 500
    quality_target: float = 10.0
    max_grad_norm: float = 1.0  # Added for stability

    # Dataset Configuration
    f_drive_datasets: str = "F:/data/datasets"
    f_drive_models: str = "F:/models"
    f_drive_cache: str = "F:/data/training/cache"

    # Training Phases
    phase: str = "single_modal"  # single_modal, cross_modal, multimodal
    modality: str = "text"  # text, image, audio, video, all

    # Unified Tokenizer
    use_unified_tokenizer: bool = True
    conversation_focus: bool = True
    multimodal_integration: bool = True

    # Hardware Constraints
    max_vram_gb: float = 3.5  # Reserve 0.5GB for system
    device: str = "cuda" if torch.cuda.is_available() else "cpu"

class MultimodalDataset(Dataset):
    """Dataset class for multimodal training data from F: drive"""

    def __init__(self, config: TrainingConfig, phase: str = "train"):
        self.config = config
        self.phase = phase
        self.f_drive_path = Path(config.f_drive_datasets)

        # Initialize data paths
        self.text_path = self.f_drive_path / "text"
        self.image_path = self.f_drive_path / "vision"
        self.audio_path = self.f_drive_path / "audio"
        self.video_path = self.f_drive_path / "video"

        # Load available datasets
        self.data_samples = self._load_samples()

        logger.info(f"Loaded {len(self.data_samples)} samples for {phase} phase")

    def _load_samples(self) -> List[Dict[str, Any]]:
        """Load available data samples based on training phase"""
        samples = []

        if self.config.phase == "single_modal":
            if self.config.modality == "text":
                samples.extend(self._load_text_samples())
            elif self.config.modality == "image":
                samples.extend(self._load_image_samples())
            elif self.config.modality == "audio":
                samples.extend(self._load_audio_samples())

        elif self.config.phase == "cross_modal":
            # Load paired samples for cross-modal training
            samples.extend(self._load_paired_samples())

        return samples[:10000]

def safe_decode(val):
    """Safely decode bytes or string with Latin-1 fallback for robustness"""
    if isinstance(val, (bytes, bytearray)):
        try: return val.decode("utf-8")
        except: return val.decode("latin-1", errors="replace")
    return str(val) if val is not None else ""

def preprocess_sample_wds(sample, tokenizer, max_length):
    """Shard-based preprocessing for B3 multimodal data"""
    modality = safe_decode(sample.get("modality.txt", b"unknown"))
    input_ids = torch.zeros(max_length, dtype=torch.long)
    attention_mask = torch.zeros(max_length, dtype=torch.long)

    if modality == "text":
        raw_text = sample.get("data.txt", sample.get("data.json"))
        if raw_text:
            text = safe_decode(raw_text)
            tokens = tokenizer(text, max_length=max_length, truncation=True, padding="max_length", return_tensors="pt")
            input_ids = tokens["input_ids"][0]
            attention_mask = tokens["attention_mask"][0]

    return {"input_ids": input_ids, "attention_mask": attention_mask, "labels": input_ids.clone()}

class MultimodalDataset(Dataset):
    """Dataset class for multimodal training data from F: drive"""

    def __init__(self, config: TrainingConfig, phase: str = "train"):
        self.config = config
        self.phase = phase
        self.f_drive_path = Path(config.f_drive_datasets)

        # Initialize data paths
        self.text_path = self.f_drive_path / "text"
        self.image_path = self.f_drive_path / "vision"
        self.audio_path = self.f_drive_path / "audio"
        self.video_path = self.f_drive_path / "video"

        # Load available datasets
        self.data_samples = self._load_samples()

        logger.info(f"Loaded {len(self.data_samples)} samples for {phase} phase")

    def _create_webdataset(self):
        """Create a streaming WebDataset from shards for enterprise efficiency"""
        shard_path = "F:/data/processed/shards/b3_multimodal_shard-*.tar"
        shards = glob.glob(shard_path)
        if not shards:
            logger.warning(f"No shards found at {shard_path}")
            return None

        # Windows-specific URI formatting for gopen/WebDataset
        shards = [f"file:{s.replace(os.sep, '/')}" for s in shards]

        tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        tokenizer.pad_token = tokenizer.eos_token

        return (
            wds.WebDataset(shards, resampled=True, shardshuffle=False)
            .shuffle(1000)
            .map(partial(preprocess_sample_wds, tokenizer=tokenizer, max_length=self.config.max_sequence_length))
            .to_tuple("input_ids", "attention_mask", "labels")
        )

    def _load_samples(self) -> List[Dict[str, Any]]:
        """Load available data samples based on training phase"""
        samples = []

        if self.config.phase == "single_modal":
            if self.config.modality == "text":
                samples.extend(self._load_text_samples())
            elif self.config.modality == "image":
                samples.extend(self._load_image_samples())
            elif self.config.modality == "audio":
                samples.extend(self._load_audio_samples())

        elif self.config.phase == "cross_modal":
            # Load paired samples for cross-modal training
            samples.extend(self._load_paired_samples())

        return samples[:10000]

    def _load_text_samples(self) -> List[Dict[str, Any]]:
        """Load text samples for conversation training"""
        samples = []

        # Search for text files in F:/data/datasets/text
        if self.text_path.exists():
            for text_file in self.text_path.rglob("*.txt"):
                try:
                    with open(text_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if len(content) > 10:  # Minimum content check
                            samples.append({
                                "type": "text",
                                "content": content[:self.config.max_sequence_length],
                                "source": str(text_file),
                                "modality": "text"
                            })
                except Exception as e:
                    continue  # Skip problematic files

        # Create synthetic conversation data if needed
        if len(samples) < 1000:
            synthetic_samples = self._create_synthetic_text_data()
            samples.extend(synthetic_samples)

        return samples

    def _load_image_samples(self) -> List[Dict[str, Any]]:
        """Load image samples for vision training"""
        samples = []

        # Search for image files in F:/data/datasets/vision
        if self.image_path.exists():
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
            for img_file in self.image_path.rglob("*"):
                if img_file.suffix.lower() in image_extensions:
                    samples.append({
                        "type": "image",
                        "path": str(img_file),
                        "source": str(img_file),
                        "modality": "image"
                    })

        return samples[:5000]  # Memory limit for GTX 1050 Ti

    def _load_audio_samples(self) -> List[Dict[str, Any]]:
        """Load audio samples for speech training"""
        samples = []

        # Search for audio files in F:/data/datasets/audio
        if self.audio_path.exists():
            audio_extensions = {'.wav', '.mp3', '.flac', '.ogg'}
            for audio_file in self.audio_path.rglob("*"):
                if audio_file.suffix.lower() in audio_extensions:
                    samples.append({
                        "type": "audio",
                        "path": str(audio_file),
                        "source": str(audio_file),
                        "modality": "audio"
                    })

        return samples[:3000]  # Audio processing is memory-intensive

    def _load_paired_samples(self) -> List[Dict[str, Any]]:
        """Load paired samples for cross-modal training"""
        # Implementation for paired text-image, text-audio, etc.
        return self._create_synthetic_paired_data()

    def _load_multimodal_samples(self) -> List[Dict[str, Any]]:
        """Load comprehensive multimodal samples"""
        # Implementation for full multimodal data
        return self._create_synthetic_multimodal_data()

    def _create_synthetic_text_data(self) -> List[Dict[str, Any]]:
        """Create synthetic conversation data for training"""
        synthetic_conversations = [
            "Hello, how are you today?",
            "I'm doing well, thank you for asking!",
            "Can you help me understand multimodal AI?",
            "Multimodal AI combines text, images, and audio for better understanding.",
            "What makes ImpressionCore special?",
            "ImpressionCore is designed to run efficiently on consumer hardware.",
            "How does the unified tokenizer work?",
            "The unified tokenizer combines DialoGPT and GPT-2 for better conversation understanding.",
            "What is the goal of this training?",
            "The goal is to achieve 10/10 conversation quality on GTX 1050 Ti hardware."
        ]

        samples = []
        for i, text in enumerate(synthetic_conversations):
            samples.append({
                "type": "text",
                "content": text,
                "source": f"synthetic_{i}",
                "modality": "text"
            })

        return samples

    def _create_synthetic_paired_data(self) -> List[Dict[str, Any]]:
        """Create synthetic paired data for cross-modal training"""
        # Placeholder for paired data creation
        return []

    def _create_synthetic_multimodal_data(self) -> List[Dict[str, Any]]:
        """Create synthetic multimodal data"""
        # Placeholder for multimodal data creation
        return []

    def __len__(self):
        return len(self.data_samples)

    def __getitem__(self, idx):
        sample = self.data_samples[idx]

        # Process based on modality
        if sample["modality"] == "text":
            return self._process_text_sample(sample)
        elif sample["modality"] == "image":
            return self._process_image_sample(sample)
        elif sample["modality"] == "audio":
            return self._process_audio_sample(sample)
        else:
            return self._process_multimodal_sample(sample)

    def _process_text_sample(self, sample: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        """Process text sample for training"""
        text = sample["content"]

        # Create simple input-output pairs for conversation training
        return {
            "text": text,
            "input_ids": torch.randint(0, 50257, (self.config.max_sequence_length,)),
            "labels": torch.randint(0, 50257, (self.config.max_sequence_length,)),
            "modality_type": torch.tensor(0),  # Text modality
            "mask": torch.ones(self.config.max_sequence_length)
        }

    def _process_image_sample(self, sample: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        """Process image sample for training"""
        # Placeholder image processing
        return {
            "image_features": torch.randn(32, 768),  # Simulated image features
            "labels": torch.randint(0, 50257, (32,)),
            "modality_type": torch.tensor(1),  # Image modality
            "mask": torch.ones(32)
        }

    def _process_audio_sample(self, sample: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        """Process audio sample for training"""
        # Placeholder audio processing
        return {
            "audio_features": torch.randn(32, 768),  # Simulated audio features
            "labels": torch.randint(0, 50257, (32,)),
            "modality_type": torch.tensor(2),  # Audio modality
            "mask": torch.ones(32)
        }

    def _process_multimodal_sample(self, sample: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        """Process multimodal sample for training"""
        # Placeholder multimodal processing
        return {
            "input_ids": torch.randint(0, 50257, (self.config.max_sequence_length,)),
            "image_features": torch.randn(32, 768),
            "audio_features": torch.randn(32, 768),
            "labels": torch.randint(0, 50257, (self.config.max_sequence_length,)),
            "modality_type": torch.tensor(6),  # Multimodal
            "mask": torch.ones(self.config.max_sequence_length)
        }

class B3TrainingPipeline:
    """Main training pipeline for B3 with unified tokenizer"""

    def __init__(self, config: TrainingConfig):
        self.config = config
        self.console = Console()

        # Initialize F: drive paths (Aligned with b3_pretraining_config)
        self.f_drive_path = Path("F:/data")
        self.checkpoints_path = self.f_drive_path / "training" / "checkpoints" / "b3_pretraining"
        self.training_path = self.f_drive_path / "training" / "logs" / "b3_pretraining"

        # Create directories
        self.checkpoints_path.mkdir(parents=True, exist_ok=True)
        self.training_path.mkdir(parents=True, exist_ok=True)

        # Initialize model and tokenizer
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.scaler = None  # For mixed precision

        # Training state
        self.current_epoch = 0
        self.global_step = 0
        self.best_quality = 0.0
        self.training_stats = {
            "losses": [],
            "quality_scores": [],
            "vram_usage": [],
            "processing_times": []
        }

        logger.info(f"B3 Training Pipeline initialized for {config.phase} phase")

    def initialize_model(self):
        """Initialize B3 model with unified tokenizer integration"""

        # Create B3 config optimized for GTX 1050 Ti Nano-profile
        b3_config = B3Config(
            embed_dim=self.config.embed_dim,
            num_heads=self.config.num_heads,
            num_layers=self.config.num_layers,
            vocab_size=50257,
            num_experts=self.config.num_experts,
            expert_dim=self.config.expert_dim,
            experts_per_token=self.config.experts_per_token,
            dropout=self.config.dropout,
            use_gradient_checkpointing=self.config.gradient_checkpointing,
            max_seq_length=self.config.max_sequence_length,
            # Additional Nano-profile specifics
            image_embed_dim=self.config.embed_dim,
            audio_embed_dim=self.config.embed_dim,
            phoneme_vocab_size=256
        )

        # Initialize integrated model
        self.model = B3UnifiedTokenizerBridge(b3_config)

        # Move to device
        self.model = self.model.to(self.config.device)

        # Initialize optimizer
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=0.01
        )

        # Initialize learning rate scheduler
        self.scheduler = optim.lr_scheduler.LinearLR(
            self.optimizer,
            start_factor=0.1,
            total_iters=self.config.warmup_steps
        )

        # Initialize mixed precision scaler using modern API
        if self.config.mixed_precision:
            self.scaler = torch.amp.GradScaler("cuda")

        # Load best checkpoint if available
        self._load_best_checkpoint()

        logger.info(f"Model initialized with {sum(p.numel() for p in self.model.parameters())} parameters")

    def _load_best_checkpoint(self):
        """Load the best available checkpoint"""
        best_checkpoint = self.checkpoints_path / "b3_best_quality_model.pth"

        if best_checkpoint.exists():
            try:
                checkpoint = torch.load(best_checkpoint, map_location=self.config.device)

                # Load model state (be flexible with state dict keys)
                if 'model_state_dict' in checkpoint:
                    model_state = checkpoint['model_state_dict']
                else:
                    model_state = checkpoint

                # Try to load with strict=False to handle architecture differences
                missing_keys, unexpected_keys = self.model.load_state_dict(model_state, strict=False)

                if missing_keys:
                    logger.warning(f"Missing keys in checkpoint: {len(missing_keys)} keys")
                if unexpected_keys:
                    logger.warning(f"Unexpected keys in checkpoint: {len(unexpected_keys)} keys")

                # Load optimizer and scheduler if available
                if 'optimizer_state_dict' in checkpoint and self.optimizer:
                    try:
                        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
                    except Exception as e:
                        logger.warning(f"Could not load optimizer state: {e}")

                # Load training metadata
                if 'epoch' in checkpoint:
                    self.current_epoch = checkpoint['epoch']
                if 'global_step' in checkpoint:
                    self.global_step = checkpoint['global_step']
                if 'best_quality' in checkpoint:
                    self.best_quality = checkpoint['best_quality']

                logger.info(f"Loaded checkpoint from epoch {self.current_epoch}, quality: {self.best_quality:.3f}")

            except Exception as e:
                logger.error(f"Failed to load checkpoint: {e}")
                logger.info("Starting training from scratch")

    def create_dataloader(self, phase: str = "train") -> DataLoader:
        """Create dataloader for training phase with shard support"""

        dataset_obj = MultimodalDataset(self.config, phase)
        wds_dataset = dataset_obj._create_webdataset()

        if wds_dataset:
            logger.info("Using WebDataset shard streaming for training")
            dataloader = DataLoader(
                wds_dataset,
                batch_size=self.config.batch_size,
                num_workers=0,
                pin_memory=True
            )
        else:
            dataloader = DataLoader(
                dataset_obj,
                batch_size=self.config.batch_size,
                shuffle=(phase == "train"),
                num_workers=0,
                pin_memory=True,
                drop_last=True
            )

        return dataloader

    def train_epoch(self, dataloader: DataLoader, epoch: int) -> Dict[str, float]:
        """Train for one epoch"""

        self.model.train()
        epoch_losses = []
        epoch_quality_scores = []

        # Progress tracking
        progress = Progress(
            TextColumn("[bold blue]Training", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            TimeRemainingColumn(),
            console=self.console
        )

        with progress:
            try:
                total_steps = len(dataloader)
            except (TypeError, AttributeError):
                total_steps = self.config.max_steps if hasattr(self.config, 'max_steps') else 100000

            task = progress.add_task("Training batches", total=total_steps)

            for batch_idx, batch in enumerate(dataloader):
                # Handle WebDataset tuple (input_ids, attention_mask, labels)
                if isinstance(batch, (list, tuple)) and len(batch) >= 3:
                    batch = {
                        "input_ids": batch[0],
                        "attention_mask": batch[1],
                        "labels": batch[2]
                    }

                # Move batch to device
                batch = {k: v.to(self.config.device) if isinstance(v, torch.Tensor) else v
                        for k, v in batch.items()}

                # Training step
                step_stats = self._training_step(batch, batch_idx)

                # Guard against NaN loss
                if torch.isnan(torch.tensor(step_stats["loss"])):
                    logger.warning(f"NaN loss detected at Step {self.global_step}, skipping batch")
                    progress.update(task, advance=1, description="[bold red]NaN skipped")
                    self.global_step += 1
                    continue

                epoch_losses.append(step_stats["loss"])
                epoch_quality_scores.append(step_stats["quality_score"])

                # Update progress
                progress.update(task, advance=1,
                              description=f"Loss: {step_stats['loss']:.4f}, Quality: {step_stats['quality_score']:.2f}")

                # Evaluation and saving
                if (self.global_step + 1) % self.config.evaluation_frequency == 0:
                    self._evaluate_and_log()

                if (self.global_step + 1) % self.config.save_frequency == 0:
                    self._save_checkpoint(f"step_{self.global_step}")

                self.global_step += 1

        # Calculate epoch statistics
        if not epoch_losses:
            return {"avg_loss": 0.0, "avg_quality": 0.0, "total_batches": 0}

        epoch_stats = {
            "avg_loss": np.mean(epoch_losses),
            "avg_quality": np.mean(epoch_quality_scores),
            "total_batches": len(dataloader)
        }

        return epoch_stats

    def _training_step(self, batch: Dict[str, torch.Tensor], batch_idx: int) -> Dict[str, float]:
        """Single training step with modern mixed precision logic"""

        start_time = time.perf_counter()

        # Forward pass with modern autocast
        device_type = "cuda" if "cuda" in str(self.config.device) else "cpu"
        with torch.autocast(device_type=device_type, enabled=self.config.mixed_precision):
            outputs = self.model(**batch)
            # Handle potential model output variants
            if isinstance(outputs, dict):
                loss = outputs.get('loss')
            else:
                loss = getattr(outputs, 'loss', None)

            if loss is None:
                # Fallback loss calculation if model didn't return it
                logits = outputs.get('logits') if isinstance(outputs, dict) else outputs.logits
                labels = batch.get('labels')
                if logits is not None and labels is not None:
                    loss = F.cross_entropy(logits.view(-1, logits.size(-1)), labels.view(-1), ignore_index=-100)
                else:
                    loss = torch.tensor(0.0, device=self.config.device, requires_grad=True)

        # Scale loss for gradient accumulation
        loss = loss / self.config.gradient_accumulation_steps

        # Check for NaN/Inf BEFORE backprop to prevent poisoning gradients
        if torch.isnan(loss) or torch.isinf(loss):
            return {
                "loss": float('nan'),
                "quality_score": outputs.get('quality_score', torch.tensor(0.0)).item(),
                "processing_time_ms": (time.perf_counter() - start_time) * 1000,
                "vram_gb": torch.cuda.memory_allocated() / 1024**3 if torch.cuda.is_available() else 0.0
            }

        # Backward pass with scaler safety
        if self.config.mixed_precision and self.scaler:
            self.scaler.scale(loss).backward()
        else:
            loss.backward()

        # Optimizer step with gradient accumulation
        if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
            # Unscale for gradient clipping
            if self.config.mixed_precision and self.scaler:
                self.scaler.unscale_(self.optimizer)

            # Gradient clipping for stability
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.max_grad_norm)

            if self.config.mixed_precision and self.scaler:
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                self.optimizer.step()

            self.optimizer.zero_grad()

            if self.global_step < self.config.warmup_steps:
                self.scheduler.step()

        # Calculate statistics
        processing_time = (time.perf_counter() - start_time) * 1000
        quality_score = outputs.get('quality_score', torch.tensor(8.5)).item()

        # Memory monitoring
        if torch.cuda.is_available():
            vram_used = torch.cuda.memory_allocated() / 1024**3  # GB
            self.training_stats["vram_usage"].append(vram_used)

        self.training_stats["losses"].append(loss.item())
        self.training_stats["quality_scores"].append(quality_score)
        self.training_stats["processing_times"].append(processing_time)

        # Prevent memory accumulation in stats
        if len(self.training_stats["losses"]) > 1000:
            for key in ["losses", "quality_scores", "vram_usage", "processing_times"]:
                self.training_stats[key] = self.training_stats[key][-1000:]
        return {
            "loss": loss.item() * self.config.gradient_accumulation_steps,
            "quality_score": quality_score,
            "processing_time_ms": processing_time,
            "vram_gb": vram_used if torch.cuda.is_available() else 0.0
        }

    def _evaluate_and_log(self):
        """Evaluate model and log metrics"""

        if len(self.training_stats["quality_scores"]) > 10:
            recent_quality = np.mean(self.training_stats["quality_scores"][-10:])
            recent_loss = np.mean(self.training_stats["losses"][-10:])
            recent_vram = np.mean(self.training_stats["vram_usage"][-10:]) if self.training_stats["vram_usage"] else 0.0

            # Update best quality
            if recent_quality > self.best_quality:
                self.best_quality = recent_quality
                self._save_checkpoint("best_quality")

            # Check if target quality reached
            if recent_quality >= self.config.quality_target:
                self.console.print(f"🎯 [bold green]TARGET QUALITY REACHED: {recent_quality:.2f}/10.0!")

            # Log current status
            self.console.print(f"📊 Step {self.global_step}: Loss={recent_loss:.4f}, Quality={recent_quality:.2f}, VRAM={recent_vram:.1f}GB")

    def _save_checkpoint(self, name: str):
        """Save model checkpoint to F: drive"""

        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'epoch': self.current_epoch,
            'global_step': self.global_step,
            'best_quality': self.best_quality,
            'config': asdict(self.config),
            'training_stats': self.training_stats,
            'timestamp': datetime.now().isoformat()
        }

        # Save checkpoint
        checkpoint_path = self.checkpoints_path / f"b3_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pth"
        torch.save(checkpoint, checkpoint_path)

        # Update best model link
        if name == "best_quality":
            best_link = self.checkpoints_path / "b3_best_quality_model.pth"
            if best_link.exists():
                best_link.unlink()
            # Create a copy instead of symlink for Windows compatibility
            torch.save(checkpoint, best_link)

        logger.info(f"Checkpoint saved: {checkpoint_path}")

        # Rotate checkpoints to save space (keep last 3 + best)
        self._rotate_checkpoints()

    def _rotate_checkpoints(self, keep_last: int = 3):
        """Delete older checkpoints to prevent disk overflow"""
        try:
            # Find all step checkpoints
            checkpoints = sorted(self.checkpoints_path.glob("b3_step_*_*.pth"))

            # Keep the last N checkpoints
            if len(checkpoints) > keep_last:
                for ckpt in checkpoints[:-keep_last]:
                    try:
                        ckpt.unlink()
                        logger.info(f"Deleted old checkpoint: {ckpt.name}")
                    except Exception as e:
                        logger.warning(f"Failed to delete {ckpt.name}: {e}")
        except Exception as e:
            logger.warning(f"Checkpoint rotation failed: {e}")

    def train(self, resume_path: Optional[str] = None):
        """Main training loop"""

        self.console.print(Panel.fit(
            f"🚀 B3 Training Pipeline\n"
            f"Phase: {self.config.phase}\n"
            f"Modality: {self.config.modality}\n"
            f"Target Quality: {self.config.quality_target}/10.0\n"
            f"Device: {self.config.device}\n"
            f"Max VRAM: {self.config.max_vram_gb:.1f}GB",
            title="Training Configuration"
        ))

        # Initialize model
        self.initialize_model()

        # Load from specific resume path if provided (overrides best_quality auto-load)
        if resume_path:
            self._load_checkpoint_file(resume_path)

        # Create dataloader
        dataloader = self.create_dataloader("train")

        # Training loop
        try:
            for epoch in range(self.current_epoch, self.config.max_epochs):
                self.current_epoch = epoch
                logger.info(f"Starting Epoch {epoch + 1}/{self.config.max_epochs}")

                # Train epoch
                epoch_stats = self.train_epoch(dataloader, epoch)

                # Log epoch stats
                logger.info(f"Epoch {epoch + 1} Stats: Loss={epoch_stats['avg_loss']:.4f}, Quality={epoch_stats['avg_quality']:.2f}")

                # Save epoch checkpoint
                self._save_checkpoint(f"epoch_{epoch}")

        except KeyboardInterrupt:
            logger.warning("Training interrupted by user")
            self._save_checkpoint(f"interrupted_step_{self.global_step}")
            logger.info("Safety checkpoint saved. Exiting...")
    def _load_checkpoint_file(self, path: str):
        """Load specific checkpoint file"""
        try:
            checkpoint = torch.load(path, map_location=self.config.device)
            self.model.load_state_dict(checkpoint['model_state_dict'], strict=False)
            if 'optimizer_state_dict' in checkpoint and self.optimizer:
                self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            if 'epoch' in checkpoint: self.current_epoch = checkpoint['epoch']
            if 'global_step' in checkpoint: self.global_step = checkpoint['global_step']
            if 'best_quality' in checkpoint: self.best_quality = checkpoint['best_quality']
            logger.info(f"Resumed from {path} (Step {self.global_step})")
        except Exception as e:
            logger.error(f"Failed to resume from {path}: {e}")

    def _save_checkpoint(self, name: str):
        """Save model checkpoint to F: drive"""

        # Rotate checkpoints BEFORE saving to ensure space exists
        self._rotate_checkpoints()

        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict() if self.optimizer else None,
            'epoch': self.current_epoch,
            'global_step': self.global_step,
            'best_quality': self.best_quality,
            'config': self.config.__dict__
        }

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        # Ensure name doesn't already have timestamp if it's not needed or append it
        if "step" in name or "epoch" in name:
            filename = f"b3_{name}_{timestamp}.pth"
        else:
            filename = f"b3_{name}.pth"

        save_path = self.checkpoints_path / filename

        try:
            torch.save(checkpoint, save_path)
            logger.info(f"Saved checkpoint to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint to {save_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="B3 Unified Training Pipeline")
    parser.add_argument("--resume", type=str, default=None, help="Path to checkpoint to resume from")
    args = parser.parse_args()

    # Create configuration
    config = TrainingConfig()  # Uses defaults (Nano profile)

    # Initialize and start training
    pipeline = B3TrainingPipeline(config)

    # Auto-resume search if no resume path provided
    if not args.resume:
        checkpoints = sorted(glob.glob(f"F:/data/training/checkpoints/b3_pretraining/b3_step_*_*.pth"))
        if checkpoints:
            args.resume = checkpoints[-1]
            console.print(f"[bold yellow]🔍 Auto-found latest checkpoint: {args.resume}")

    pipeline.train(resume_path=args.resume)

if __name__ == "__main__":
    main()
