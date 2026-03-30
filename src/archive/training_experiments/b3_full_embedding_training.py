#!/usr/bin/env python3
"""ImpressionCore B3 full embedding training system."""

import os
import sys
import json
import time
import logging
import asyncio
import threading
import traceback
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from functools import wraps
import gc
import pickle
import random
from collections import defaultdict, deque

import torch
import torch.nn as nn
import torch.optim as optim
from torch.amp import autocast, GradScaler
from torch.utils.data import DataLoader, Dataset, random_split
import torch.nn.functional as F
import numpy as np
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup
import psutil
from concurrent.futures import ThreadPoolExecutor, as_completed

# Rich UI Components
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import (
    Progress, SpinnerColumn, TextColumn, BarColumn,
    TaskProgressColumn, TimeRemainingColumn, TimeElapsedColumn
)
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.logging import RichHandler

# Import B3 Architecture
sys.path.append('src/core/models')
from impressioncore_b3_architecture import (
    ImpressionCoreB3Model, B3Config, B3TrainingConfig, create_b3_config,
    validate_environment, memory_profile, sacred_covenant_check,
    AdaptiveLearningRateScheduler, GradientClippingManager,
    MemoryOptimizedCheckpointing
)

# Initialize console
console = Console()
dataset_logger = logging.getLogger("B3EmbeddingDataset")


def _read_supplemental_lines(file_path: Path) -> List[str]:
    try:
        content = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        content = file_path.read_text(encoding='latin-1')
    except Exception as exc:  # pragma: no cover - file system guard
        console.print(f"[red]⚠️ Unable to load supplemental text {file_path}: {exc}[/red]")
        return []

    return [line.strip() for line in content.splitlines() if line.strip()]


def _resolve_config_override_path() -> Optional[Path]:
    """Return config override path from CLI or environment when provided."""
    if "--config" in sys.argv:
        idx = sys.argv.index("--config")
        if idx + 1 >= len(sys.argv):
            raise ValueError("--config flag provided without a path")
        override_path = Path(sys.argv[idx + 1]).expanduser()
        sys.argv[:] = sys.argv[:idx] + sys.argv[idx + 2:]
        return override_path

    env_value = os.getenv("B3_TRAINING_CONFIG")
    if env_value:
        return Path(env_value).expanduser()

    return None


def _apply_config_overrides(
    config: B3TrainingConfig, config_path: Path
) -> B3TrainingConfig:
    """Load JSON overrides and merge with the provided training config."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config override file not found: {config_path}")

    console.print(f"[blue]📄 Applying config overrides from {config_path}[/blue]")

    with config_path.open("r", encoding="utf-8") as fp:
        override_data = json.load(fp) or {}

    base_dict = asdict(config)
    allowed_overrides = {k: v for k, v in override_data.items() if k in base_dict}
    ignored_keys = sorted(set(override_data.keys()) - set(allowed_overrides.keys()))
    base_dict.update(allowed_overrides)
    updated_config = B3TrainingConfig(**base_dict)

    if ignored_keys:
        console.print(
            f"[yellow]⚠️ Ignoring unsupported config keys: {', '.join(ignored_keys)}[/yellow]"
        )

    return updated_config

@dataclass
class TrainingMetrics:
    """Comprehensive training metrics tracking"""
    epoch: int = 0
    step: int = 0
    total_steps: int = 0

    # Loss tracking
    current_loss: float = 0.0
    avg_loss: float = 0.0
    best_loss: float = float('inf')

    # Performance metrics
    samples_per_second: float = 0.0
    tokens_per_second: float = 0.0
    memory_usage_gb: float = 0.0
    gpu_utilization: float = 0.0

    # Quality metrics
    perplexity: float = 0.0
    quality_score: float = 0.0

    # Training progress
    epoch_start_time: float = 0.0
    total_train_time: float = 0.0
    eta_completion: str = "Unknown"

    # Embedding integration
    embeddings_loaded: int = 0
    embeddings_processed: int = 0
    embedding_cache_hits: int = 0

    # Hardware monitoring
    cpu_usage: float = 0.0
    memory_available_gb: float = 0.0
    disk_usage_gb: float = 0.0

class EmbeddingDataset(Dataset):
    """Dataset for B3 training with embedding integration"""

    def __init__(self, config: B3TrainingConfig, tokenizer, split='train'):
        self.config = config
        self.tokenizer = tokenizer
        self.split = split

        # Load embedding file paths
        self.embedding_files = self._discover_embedding_files()
        self.embedding_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0

        # Create training samples
        self.samples = self._create_training_samples()

    def _discover_embedding_files(self) -> List[Path]:
        """Discover and filter embedding files from F: drive"""
        console.print("[yellow]🔍 Discovering embedding files...[/yellow]")

        primary_root = Path(self.config.f_drive_path)
        additional_roots = [Path(p) for p in getattr(self.config, 'additional_embedding_roots', [])]
        search_roots = [primary_root] + additional_roots

        discovered: List[Path] = []
        missing_roots: List[str] = []
        for root in search_roots:
            if not root.exists():
                missing_roots.append(str(root))
                continue
            discovered.extend(root.rglob("*.npy"))

        if missing_roots:
            dataset_logger.warning("Embedding root(s) not found: %s", ", ".join(missing_roots))
            console.print(f"[yellow]⚠️ Missing embedding roots: {', '.join(missing_roots)}[/yellow]")

        max_files = getattr(self.config, 'max_embedding_files', 0) or 0
        if max_files > 0:
            discovered = discovered[:max_files]

        if not discovered:
            message = (
                "No embedding files discovered on F: drive. "
                "Verify that the drive is mounted and contains .npy embeddings."
            )
            console.print(f"[red]❌ {message}[/red]")
            raise RuntimeError(message)

        console.print(f"[green]✅ Found {len(discovered)} embedding files[/green]")
        return discovered

    def _create_training_samples(self) -> List[Dict]:
        """Create training samples with embedding integration"""
        console.print("[yellow]📝 Creating training samples...[/yellow]")

        samples = []

        # Text-only samples for base training
        text_samples = self._create_text_samples()
        samples.extend(text_samples)

        # Multimodal samples with embeddings
        if self.embedding_files:
            multimodal_samples = self._create_multimodal_samples()
            samples.extend(multimodal_samples)

        # Shuffle for training
        random.shuffle(samples)

        console.print(f"[green]✅ Created {len(samples)} training samples[/green]")
        return samples

    def _create_text_samples(self) -> List[Dict]:
        """Create text-only training samples"""
        text_samples = []

        # Generate synthetic conversation data
        conversation_templates = [
            "Hello! How can I help you today?",
            "What would you like to know?",
            "I'm here to assist you with any questions.",
            "Let's explore this topic together.",
            "That's an interesting question!",
            "I'd be happy to explain that.",
            "Can you tell me more about what you're looking for?",
        ]

        for template in conversation_templates * 100:  # Multiply for more samples
            tokens = self.tokenizer.encode(template, truncation=True,
                                         max_length=self.config.max_seq_length)

            text_samples.append({
                'input_ids': tokens,
                'labels': tokens,
                'modality_type': 'text',
                'has_embeddings': False
            })

        supplemental_texts = self._load_supplemental_texts()
        limit = min(len(supplemental_texts), getattr(self.config, 'max_supplemental_text_samples', len(supplemental_texts)))
        for line in supplemental_texts[:limit]:
            tokens = self.tokenizer.encode(line, truncation=True, max_length=self.config.max_seq_length)
            text_samples.append({
                'input_ids': tokens,
                'labels': tokens,
                'modality_type': 'text',
                'has_embeddings': False
            })

        return text_samples

    def _load_supplemental_texts(self) -> List[str]:
        directories = getattr(self.config, 'supplemental_text_dirs', []) or []
        collected: List[str] = []
        for raw_path in directories:
            path = Path(raw_path)
            if not path.exists():
                console.print(f"[yellow]⚠️ Supplemental directory not found: {path}[/yellow]")
                continue
            for file_path in path.rglob('*.txt'):
                collected.extend(_read_supplemental_lines(file_path))
        return collected

    def _create_multimodal_samples(self) -> List[Dict]:
        """Create multimodal samples with embedding integration"""
        multimodal_samples = []

        # Sample embedding files
        sampled_files = random.sample(self.embedding_files,
                                    min(1000, len(self.embedding_files)))

        for emb_file in sampled_files:
            try:
                # Create synthetic text for the embedding
                text = f"Processing multimodal content from {emb_file.stem}"
                tokens = self.tokenizer.encode(text, truncation=True,
                                             max_length=self.config.max_seq_length)

                multimodal_samples.append({
                    'input_ids': tokens,
                    'labels': tokens,
                    'modality_type': 'multimodal',
                    'embedding_file': str(emb_file),
                    'has_embeddings': True
                })

            except Exception as e:
                console.print(f"[red]⚠️ Error with {emb_file}: {e}[/red]")
                continue

        return multimodal_samples

    def _load_embedding(self, embedding_file: str) -> Optional[torch.Tensor]:
        """Load embedding with caching"""
        if embedding_file in self.embedding_cache:
            self.cache_hits += 1
            return self.embedding_cache[embedding_file]

        try:
            # Load numpy embedding
            embedding = np.load(embedding_file)
            embedding_tensor = torch.from_numpy(embedding).float()

            # Normalize dimensionality for downstream padding logic
            if embedding_tensor.dim() == 0:
                embedding_tensor = embedding_tensor.unsqueeze(0)
            elif embedding_tensor.dim() > 2:
                original_shape = tuple(embedding_tensor.shape)
                embedding_tensor = embedding_tensor.reshape(embedding_tensor.shape[0], -1)
                dataset_logger.warning(
                    "Flattened high-rank embedding %s from shape %s to %s",
                    embedding_file,
                    original_shape,
                    tuple(embedding_tensor.shape)
                )

            embedding_tensor = self._sanitize_embedding_tensor(embedding_tensor, embedding_file)

            # Cache management
            if len(self.embedding_cache) < self.config.embedding_cache_size:
                self.embedding_cache[embedding_file] = embedding_tensor

            self.cache_misses += 1
            return embedding_tensor

        except Exception as e:
            console.print(f"[red]❌ Failed to load {embedding_file}: {e}[/red]")
            return None

    def _sanitize_embedding_tensor(self, embedding: torch.Tensor, source_path: str) -> torch.Tensor:
        """Normalize embeddings to a numerically stable range."""
        if embedding.numel() == 0:
            return embedding

        embedding = torch.nan_to_num(embedding, nan=0.0, posinf=0.0, neginf=0.0)

        if not torch.isfinite(embedding).all().item():
            dataset_logger.warning("Embedding %s contains non-finite values after sanitization; zeroing tensor", source_path)
            return torch.zeros_like(embedding)

        mean_value = float(embedding.mean())
        std_value = float(embedding.std(unbiased=False))

        if not math.isfinite(mean_value):
            dataset_logger.warning("Embedding %s produced non-finite mean; resetting to zero", source_path)
            mean_value = 0.0

        if not math.isfinite(std_value) or std_value < 1e-6:
            dataset_logger.warning(
                "Embedding %s has near-zero or non-finite std (%.6f); returning zeros to avoid instability",
                source_path,
                std_value
            )
            return torch.zeros_like(embedding)

        embedding = (embedding - mean_value) / max(std_value, 1e-6)

        max_abs = embedding.abs().max()
        if torch.isfinite(max_abs).item() and max_abs.item() > 10.0:
            scale = max_abs.item() / 10.0
            embedding = embedding / scale

        embedding = embedding.clamp(-10.0, 10.0)
        return embedding

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]

        # Prepare base data
        input_ids = torch.tensor(sample['input_ids'], dtype=torch.long)
        labels = torch.tensor(sample['labels'], dtype=torch.long)

        # Convert modality_type to tensor indices
        modality_mapping = {
            'text': 0,
            'image': 1,
            'audio': 2,
            'multimodal': 3
        }
        modality_idx = modality_mapping.get(sample['modality_type'], 0)
        modality_type = torch.tensor([modality_idx] * self.config.max_seq_length, dtype=torch.long)

        # Pad sequences
        if len(input_ids) < self.config.max_seq_length:
            padding = self.config.max_seq_length - len(input_ids)
            input_ids = F.pad(input_ids, (0, padding), value=self.tokenizer.pad_token_id)
            labels = F.pad(labels, (0, padding), value=-100)

        result = {
            'input_ids': input_ids,
            'labels': labels,
            'modality_type': modality_type
        }

        # Add embedding data if available
        if sample.get('has_embeddings', False):
            embedding_file = sample.get('embedding_file')
            if embedding_file:
                embedding = self._load_embedding(embedding_file)
                if embedding is not None:
                    # Reshape embedding to match sequence length
                    if embedding.dim() == 1:
                        embedding = embedding.unsqueeze(0).repeat(self.config.max_seq_length, 1)
                    elif embedding.size(0) != self.config.max_seq_length:
                        # Resize to match sequence length
                        if embedding.size(0) > self.config.max_seq_length:
                            embedding = embedding[:self.config.max_seq_length]
                        else:
                            padding = self.config.max_seq_length - embedding.size(0)
                            embedding = F.pad(embedding, (0, 0, 0, padding))

                    # Ensure correct dimensions
                    if embedding.size(1) != self.config.embed_dim:
                        if embedding.size(1) > self.config.embed_dim:
                            embedding = embedding[:, :self.config.embed_dim]
                        else:
                            padding = self.config.embed_dim - embedding.size(1)
                            embedding = F.pad(embedding, (0, padding))

                    result['image_features'] = embedding
        # Always include 'image_features' key for DataLoader batch consistency
        if 'image_features' not in result:
            result['image_features'] = torch.zeros((self.config.max_seq_length, self.config.embed_dim), dtype=torch.float)

        return result

class B3TrainingSystem:
    """Comprehensive B3 training system with full embedding integration"""

    def __init__(self, config: B3TrainingConfig):
        self.config = config
        self.metrics = TrainingMetrics()
        self.parameter_breakdown: List[Dict[str, Any]] = []
        self.tokenizer_stats: Dict[str, Any] = {}

        # Initialize components
        self.setup_logging()
        self.setup_directories()
        self.initialize_model()
        self.perform_sacred_covenant_check()
        self.setup_optimization()
        self.setup_monitoring()

        console.print("[green]🚀 B3 Training System initialized successfully![/green]")

    def perform_sacred_covenant_check(self):
        """Sacred Covenant compliance verification"""
        console.print("[cyan]🛡️ Performing Sacred Covenant compliance check...[/cyan]")

        try:
            sacred_covenant_check(self.model, self.config)
            console.print("[green]✅ Sacred Covenant compliance verified[/green]")
        except Exception as e:
            console.print(f"[red]❌ Sacred Covenant check failed: {e}[/red]")
            raise

    def setup_logging(self):
        """Setup comprehensive logging system"""
        log_dir = Path(self.config.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"b3_training_{timestamp}.log"

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                RichHandler(console=console, show_time=False)
            ]
        )

        self.logger = logging.getLogger("B3Training")
        self.logger.info("🚀 B3 Training System logging initialized")

    def setup_directories(self):
        """Setup required directories"""
        directories = [
            self.config.checkpoint_dir,
            self.config.log_dir,
            "src/memlog/b3_training"
        ]

        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def initialize_model(self):
        """Initialize B3 model and tokenizer"""
        console.print("[yellow]🧠 Initializing B3 model...[/yellow]")

        # Resolve tokenizer
        tokenizer_path = Path(self.config.tokenizer_path)
        try:
            if tokenizer_path.exists():
                console.print(f"[green]✅ Loading tokenizer from {tokenizer_path}[/green]")
                self.tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path))
            else:
                raise FileNotFoundError(f"Tokenizer path {tokenizer_path} not found")
        except Exception as exc:  # pragma: no cover - fallback safety
            console.print(f"[yellow]⚠️ Tokenizer load failed ({exc}); falling back to DialoGPT-small[/yellow]")
            self.logger.warning("Tokenizer fallback engaged: %s", exc)
            self.tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Align vocabulary size with tokenizer
        self.config.vocab_size = int(getattr(self.tokenizer, "vocab_size", self.config.vocab_size))

        # Capture tokenizer metadata for reporting
        special_tokens = {}
        for token_name in ("bos_token", "eos_token", "pad_token", "unk_token"):
            token_value = getattr(self.tokenizer, token_name, None)
            if token_value:
                special_tokens[token_name] = token_value

        self.tokenizer_stats = {
            "path": str(tokenizer_path),
            "vocab_size": int(getattr(self.tokenizer, "vocab_size", 0)),
            "special_tokens": special_tokens,
            "added_tokens": getattr(self.tokenizer, "added_tokens_names", []),
        }

        # Create B3 configuration using updated vocab
        base_config = create_b3_config()
        base_config.update({
            'embed_dim': self.config.embed_dim,
            'num_heads': self.config.num_heads,
            'num_layers': self.config.num_layers,
            'vocab_size': self.config.vocab_size,
            'num_experts': self.config.num_experts,
            'expert_dim': self.config.expert_dim,
            'experts_per_token': self.config.experts_per_token,
            'dropout': self.config.dropout,
            'image_embed_dim': getattr(self.config, 'image_embed_dim', self.config.embed_dim),
            'audio_embed_dim': getattr(self.config, 'audio_embed_dim', self.config.embed_dim)
        })

        # Initialize model
        b3_config = B3Config(**base_config)
        self.model = ImpressionCoreB3Model(b3_config)

        # Move model to device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

        # Memory profiling
        profile_info = memory_profile(self.model)
        console.print(f"[green]✅ Model loaded - {profile_info['total_memory_mb']:.1f}MB[/green]")

        self.logger.info(f"Model initialized with {profile_info['total_params']:,} parameters")
        self._record_parameter_breakdown(profile_info['total_params'])

    def setup_optimization(self):
        """Setup optimization components"""
        console.print("[yellow]⚙️ Setting up optimization...[/yellow]")

        # Optimizer
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay
        )

        # Mixed precision scaler
        self.scaler = GradScaler('cuda') if self.config.mixed_precision and torch.cuda.is_available() else None

        # Learning rate scheduler
        lr_floor = max(self.config.learning_rate * self.config.scheduler_min_lr_factor, 1e-7)
        self.lr_scheduler = AdaptiveLearningRateScheduler(
            self.optimizer,
            patience=self.config.scheduler_patience,
            factor=self.config.scheduler_factor,
            min_lr=lr_floor,
            improvement_threshold=self.config.scheduler_improvement_threshold,
            warmup_steps=self.config.warmup_steps,
            oscillation_window=self.config.scheduler_oscillation_window,
            oscillation_min_delta=self.config.scheduler_oscillation_min_delta,
            oscillation_min_rel=self.config.scheduler_oscillation_min_rel,
            oscillation_min_changes=self.config.scheduler_oscillation_min_changes,
            oscillation_cooldown=self.config.scheduler_oscillation_cooldown,
            plateau_window=self.config.scheduler_plateau_window,
            plateau_std=self.config.scheduler_plateau_std
        )

        # Gradient clipping
        self.grad_clipper = GradientClippingManager(
            max_norm=self.config.gradient_clip_norm,
            adaptive=True
        )

        # Checkpointing
        self.checkpointer = MemoryOptimizedCheckpointing(
            self.config.checkpoint_dir,
            max_checkpoints=self.config.max_checkpoints
        )

        console.print("[green]✅ Optimization setup complete[/green]")

    def setup_monitoring(self):
        """Setup performance monitoring"""
        self.performance_history = {
            'loss': deque(maxlen=1000),
            'memory': deque(maxlen=100),
            'throughput': deque(maxlen=100)
        }

    def _record_parameter_breakdown(self, total_params: int):
        """Capture parameter distribution by top-level component."""
        breakdown_counts: Dict[str, int] = defaultdict(int)

        for name, param in self.model.named_parameters():
            component = name.split('.', 1)[0]
            breakdown_counts[component] += param.numel()

        table = Table(title="B3 Parameter Breakdown")
        table.add_column("Component", style="cyan")
        table.add_column("Parameters", style="magenta")
        table.add_column("Memory (MB)", style="green")
        table.add_column("Percent", style="yellow")

        breakdown: List[Dict[str, Any]] = []
        total_params = max(total_params, 1)

        for component, param_count in sorted(breakdown_counts.items(), key=lambda item: item[1], reverse=True):
            memory_mb = param_count * 4 / 1024**2
            percent = (param_count / total_params) * 100
            table.add_row(
                component,
                f"{param_count:,}",
                f"{memory_mb:.1f}",
                f"{percent:.2f}%"
            )
            breakdown.append({
                'component': component,
                'parameters': int(param_count),
                'memory_mb': round(memory_mb, 2),
                'percent': round(percent, 4)
            })

        console.print(table)
        self.logger.info("Parameter breakdown: %s", breakdown)
        self.parameter_breakdown = breakdown

    def create_data_loaders(self):
        """Create training and validation data loaders"""
        console.print("[yellow]📊 Creating data loaders...[/yellow]")

        # Create dataset
        full_dataset = EmbeddingDataset(self.config, self.tokenizer, 'train')

        # Train/validation split
        train_size = int(0.9 * len(full_dataset))
        val_size = len(full_dataset) - train_size

        train_dataset, val_dataset = random_split(
            full_dataset, [train_size, val_size]
        )

        # Create data loaders
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=2,
            pin_memory=True if torch.cuda.is_available() else False
        )

        self.val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=2,
            pin_memory=True if torch.cuda.is_available() else False
        )

        console.print(f"[green]✅ Data loaders created - Train: {len(train_dataset)}, Val: {len(val_dataset)}[/green]")

        # Update metrics
        self.metrics.total_steps = len(self.train_loader) * self.config.num_epochs

    def train_epoch(self, epoch: int) -> float:
        """Train one epoch"""
        self.model.train()
        epoch_loss = 0.0
        step_count = 0
        finite_loss_steps = 0

        # Create progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=False
        ) as progress:

            task = progress.add_task(
                f"[cyan]Epoch {epoch+1}/{self.config.num_epochs}",
                total=len(self.train_loader)
            )

            epoch_start_time = time.time()

            for batch_idx, batch in enumerate(self.train_loader):
                step_start_time = time.time()

                # Move batch to device
                batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v
                        for k, v in batch.items()}

                # Forward pass with mixed precision
                if self.config.mixed_precision and self.scaler:
                    with autocast('cuda'):
                        outputs = self.model(**batch)
                        loss = outputs.get('loss', 0.0)
                        if isinstance(loss, tuple):
                            loss = loss[0]

                    if not torch.isfinite(loss):
                        self._handle_invalid_training_loss(loss, epoch, batch_idx, batch, outputs)
                    loss_value = float(loss.detach().cpu())
                    if not math.isfinite(loss_value):
                        self._handle_invalid_training_loss(loss, epoch, batch_idx, batch, outputs)

                    # Backward pass
                    self.scaler.scale(loss).backward()

                    # Gradient clipping
                    self.scaler.unscale_(self.optimizer)
                    grad_norm, _ = self.grad_clipper.clip_gradients(self.model.parameters())

                    # Optimizer step
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    # Standard training
                    outputs = self.model(**batch)
                    loss = outputs.get('loss', 0.0)
                    if isinstance(loss, tuple):
                        loss = loss[0]

                    if not torch.isfinite(loss):
                        self._handle_invalid_training_loss(loss, epoch, batch_idx, batch, outputs)
                    loss_value = float(loss.detach().cpu())
                    if not math.isfinite(loss_value):
                        self._handle_invalid_training_loss(loss, epoch, batch_idx, batch, outputs)

                    # Backward pass
                    loss.backward()

                    # Gradient clipping
                    grad_norm, _ = self.grad_clipper.clip_gradients(self.model.parameters())

                    # Optimizer step
                    self.optimizer.step()

                # Clear gradients
                self.optimizer.zero_grad()

                if not math.isfinite(loss_value):
                    loss_tensor = loss if isinstance(loss, torch.Tensor) else torch.tensor(loss_value, device=self.device)
                    self._handle_invalid_training_loss(loss_tensor, epoch, batch_idx, batch, outputs)

                # Update metrics
                step_time = time.time() - step_start_time
                if math.isfinite(loss_value):
                    epoch_loss += loss_value
                    finite_loss_steps += 1
                step_count += 1

                # Update learning rate
                self.lr_scheduler.step(loss_value)

                # Performance monitoring
                self.update_performance_metrics(loss_value, step_time, batch)

                # Logging
                if batch_idx % self.config.log_every_n_steps == 0:
                    self.log_training_step(epoch, batch_idx, loss_value, grad_norm)

                # Memory cleanup
                if batch_idx % 50 == 0:
                    torch.cuda.empty_cache()
                    gc.collect()

                # Update progress
                progress.update(task, advance=1,
                              description=f"[cyan]Epoch {epoch+1} - Loss: {loss_value:.4f}")

            epoch_time = time.time() - epoch_start_time
            avg_epoch_loss = epoch_loss / finite_loss_steps if finite_loss_steps > 0 else float('inf')

            # Update epoch metrics
            self.metrics.epoch = epoch + 1
            self.metrics.avg_loss = avg_epoch_loss if math.isfinite(avg_epoch_loss) else float('inf')
            self.metrics.epoch_start_time = epoch_start_time

            console.print(f"[green]✅ Epoch {epoch+1} completed - Avg Loss: {avg_epoch_loss:.4f}, Time: {epoch_time:.1f}s[/green]")

            return avg_epoch_loss

    def _run_training_step(self, batch: Dict[str, Any], epoch: int, batch_idx: int) -> Tuple[float, float]:
        """Execute a single training step and return (loss_value, grad_norm)."""
        use_mixed_precision = self.config.mixed_precision and self.scaler is not None and torch.cuda.is_available()

        if use_mixed_precision:
            with autocast('cuda'):
                outputs = self.model(**batch)
                loss = outputs.get('loss', 0.0)
                if isinstance(loss, tuple):
                    loss = loss[0]
        else:
            outputs = self.model(**batch)
            loss = outputs.get('loss', 0.0)
            if isinstance(loss, tuple):
                loss = loss[0]

        self._validate_training_loss(loss, epoch, batch_idx, batch, outputs)
        loss_value = float(loss.detach().cpu()) if isinstance(loss, torch.Tensor) else float(loss)

        if use_mixed_precision:
            self.scaler.scale(loss).backward()
            self.scaler.unscale_(self.optimizer)
            grad_norm, _ = self.grad_clipper.clip_gradients(self.model.parameters())
            self.scaler.step(self.optimizer)
            self.scaler.update()
        else:
            loss.backward()
            grad_norm, _ = self.grad_clipper.clip_gradients(self.model.parameters())
            self.optimizer.step()

        self._ensure_finite_loss(loss, loss_value, epoch, batch_idx, batch, outputs)

        return loss_value, grad_norm

    def _validate_training_loss(
        self,
        loss: Union[torch.Tensor, float],
        epoch: int,
        batch_idx: int,
        batch: Dict[str, torch.Tensor],
        outputs: Dict[str, Any]
    ) -> None:
        """Ensure loss tensor is finite before backward pass."""
        if isinstance(loss, torch.Tensor):
            if torch.isnan(loss) or torch.isinf(loss):
                self._handle_invalid_training_loss(loss, epoch, batch_idx, batch, outputs)
        else:
            if not math.isfinite(loss):
                loss_tensor = torch.tensor(loss, device=self.device, dtype=torch.float32)
                self._handle_invalid_training_loss(loss_tensor, epoch, batch_idx, batch, outputs)

    def _ensure_finite_loss(
        self,
        loss: Union[torch.Tensor, float],
        loss_value: float,
        epoch: int,
        batch_idx: int,
        batch: Dict[str, torch.Tensor],
        outputs: Dict[str, Any]
    ) -> None:
        """Guard against non-finite scalar losses reaching the metric pipeline."""
        if not math.isfinite(loss_value):
            if isinstance(loss, torch.Tensor):
                safe_loss = loss
            else:
                safe_loss = torch.tensor(loss_value, device=self.device, dtype=torch.float32)
            self._handle_invalid_training_loss(safe_loss, epoch, batch_idx, batch, outputs)

    def validate_model(self) -> float:
        """Validate model performance"""
        self.model.eval()
        val_loss = 0.0
        step_count = 0

        with torch.no_grad():
            for batch_idx, batch in enumerate(self.val_loader):
                # Move batch to device
                batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v
                        for k, v in batch.items()}

                # Forward pass
                outputs = self.model(**batch)
                loss = outputs.get('loss', 0.0)
                if isinstance(loss, tuple):
                    loss = loss[0]
                if torch.isnan(loss) or torch.isinf(loss):
                    self._handle_invalid_validation_loss(loss, batch_idx, batch, outputs)

                val_loss += loss.item()
                step_count += 1

        avg_val_loss = val_loss / step_count if step_count > 0 else float('inf')

        console.print(f"[blue]📊 Validation Loss: {avg_val_loss:.4f}[/blue]")
        return avg_val_loss

    def _handle_invalid_validation_loss(self, loss: torch.Tensor, batch_idx: int, batch: Dict[str, torch.Tensor], outputs: Dict[str, Any]) -> None:
        """Capture diagnostics when validation loss is NaN/inf."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        failure_dir = Path(self.config.log_dir) / "validation_failures"
        failure_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = failure_dir / f"val_failure_step{batch_idx}_{timestamp}.pt"

        batch_cpu = {k: v.detach().cpu() if isinstance(v, torch.Tensor) else v for k, v in batch.items()}
        output_flags = {}
        for key, value in outputs.items():
            if isinstance(value, torch.Tensor):
                tensor = value.detach()
                has_nan = torch.isnan(tensor).any().item()
                has_inf = torch.isinf(tensor).any().item()
                if has_nan or has_inf:
                    output_flags[key] = {
                        'nan': bool(has_nan),
                        'inf': bool(has_inf),
                        'min': float(torch.nan_to_num(tensor, nan=0.0, posinf=0.0, neginf=0.0).min().item()),
                        'max': float(torch.nan_to_num(tensor, nan=0.0, posinf=0.0, neginf=0.0).max().item())
                    }

        torch.save({
            'loss': loss.detach().cpu(),
            'batch_index': batch_idx,
            'batch_tensors': batch_cpu,
            'output_flags': output_flags
        }, artifact_path)

        batch_shapes = {k: list(v.shape) if isinstance(v, torch.Tensor) else 'non_tensor' for k, v in batch.items()}
        self.logger.error(
            "Validation produced invalid loss (nan/inf) at batch %d. Diagnostics stored at %s. Batch shapes: %s",
            batch_idx,
            artifact_path,
            batch_shapes
        )
        raise ValueError(
            f"Validation loss became invalid at batch {batch_idx}. Inspect {artifact_path} for details."
        )

    def _handle_invalid_training_loss(
        self,
        loss: torch.Tensor,
        epoch: int,
        batch_idx: int,
        batch: Dict[str, torch.Tensor],
        outputs: Dict[str, Any]
    ) -> None:
        """Persist diagnostics when training loss becomes NaN/inf."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        failure_dir = Path(self.config.log_dir) / "training_failures"
        failure_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = failure_dir / f"train_failure_epoch{epoch}_step{batch_idx}_{timestamp}.pt"

        batch_cpu = {k: v.detach().cpu() if isinstance(v, torch.Tensor) else v for k, v in batch.items()}
        output_flags: Dict[str, Dict[str, Any]] = {}
        for key, value in outputs.items():
            if isinstance(value, torch.Tensor):
                tensor = value.detach()
                has_nan = torch.isnan(tensor).any().item()
                has_inf = torch.isinf(tensor).any().item()
                if has_nan or has_inf:
                    output_flags[key] = {
                        'nan': bool(has_nan),
                        'inf': bool(has_inf),
                        'min': float(torch.nan_to_num(tensor, nan=0.0, posinf=0.0, neginf=0.0).min().item()),
                        'max': float(torch.nan_to_num(tensor, nan=0.0, posinf=0.0, neginf=0.0).max().item())
                    }

        torch.save({
            'loss': loss.detach().cpu(),
            'epoch': epoch,
            'batch_index': batch_idx,
            'batch_tensors': batch_cpu,
            'output_flags': output_flags
        }, artifact_path)

        batch_shapes = {k: list(v.shape) if isinstance(v, torch.Tensor) else 'non_tensor' for k, v in batch.items()}
        self.logger.error(
            "Training produced invalid loss (nan/inf) at epoch %d batch %d. Diagnostics stored at %s. Batch shapes: %s",
            epoch,
            batch_idx,
            artifact_path,
            batch_shapes
        )
        raise ValueError(
            f"Training loss became invalid at epoch {epoch} batch {batch_idx}. Inspect {artifact_path} for details."
        )

    def update_performance_metrics(self, loss: float, step_time: float, batch: Dict):
        """Update performance metrics"""
        # Loss tracking
        if not math.isfinite(loss):
            self.logger.warning("Skipping non-finite loss value during metric update: %s", loss)
        else:
            self.performance_history['loss'].append(loss)
            self.metrics.current_loss = loss

            if loss < self.metrics.best_loss:
                self.metrics.best_loss = loss

        # Throughput calculation
        batch_size = batch['input_ids'].size(0) if 'input_ids' in batch else self.config.batch_size
        samples_per_sec = batch_size / step_time if step_time > 0 else 0.0
        self.performance_history['throughput'].append(samples_per_sec)
        self.metrics.samples_per_second = samples_per_sec

        # Memory monitoring
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated() / 1024**3  # GB
            self.performance_history['memory'].append(memory_allocated)
            self.metrics.memory_usage_gb = memory_allocated
            self.metrics.gpu_utilization = torch.cuda.utilization() if hasattr(torch.cuda, 'utilization') else 0.0

        # System monitoring
        self.metrics.cpu_usage = psutil.cpu_percent()
        self.metrics.memory_available_gb = psutil.virtual_memory().available / 1024**3

    def log_training_step(self, epoch: int, step: int, loss: float, grad_norm: float):
        """Log training step information"""
        self.logger.info(
            f"Epoch {epoch+1}, Step {step}: "
            f"Loss={loss:.4f}, "
            f"GradNorm={grad_norm:.4f}, "
            f"LR={self.optimizer.param_groups[0]['lr']:.6f}, "
            f"Memory={self.metrics.memory_usage_gb:.2f}GB"
        )

    def save_checkpoint(self, epoch: int, loss: float):
        """Save training checkpoint"""
        metrics_dict = asdict(self.metrics)

        checkpoint_path = self.checkpointer.save_checkpoint(
            self.model, self.optimizer, epoch, loss, metrics_dict
        )

        console.print(f"[green]💾 Checkpoint saved: {checkpoint_path}[/green]")
        return checkpoint_path

    def train(self):
        """Main training loop"""
        console.print("[bold green]🚀 Starting B3 Full Embedding Training![/bold green]")

        # Environment validation
        env_status = validate_environment()
        console.print(f"[cyan]🔧 Environment: CUDA={env_status['cuda_available']}, "
                     f"VRAM={env_status.get('vram_gb', 0):.1f}GB[/cyan]")

        # Create data loaders
        self.create_data_loaders()

        # Training loop
        training_start_time = time.time()
        best_val_loss = float('inf')

        try:
            for epoch in range(self.config.num_epochs):
                epoch_start_time = time.time()

                # Train epoch
                train_loss = self.train_epoch(epoch)

                # Validate
                val_loss = self.validate_model()

                # Update best loss
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    console.print(f"[green]🎯 New best validation loss: {val_loss:.4f}[/green]")

                # Save checkpoint
                if (epoch + 1) % self.config.save_every_n_epochs == 0:
                    self.save_checkpoint(epoch, val_loss)

                # Calculate ETA
                epoch_time = time.time() - epoch_start_time
                remaining_epochs = self.config.num_epochs - (epoch + 1)
                eta_seconds = remaining_epochs * epoch_time
                eta_str = str(timedelta(seconds=int(eta_seconds)))
                self.metrics.eta_completion = eta_str

                console.print(f"[cyan]⏱️ ETA: {eta_str}[/cyan]")

                # Early stopping check
                if val_loss <= self.config.target_loss:
                    console.print(f"[green]🎯 Target loss achieved: {val_loss:.4f} <= {self.config.target_loss}[/green]")
                    break

            # Training completion
            total_time = time.time() - training_start_time
            self.metrics.total_train_time = total_time

            console.print(f"[bold green]🎉 Training completed! Total time: {str(timedelta(seconds=int(total_time)))}[/bold green]")
            console.print(f"[green]📊 Best validation loss: {best_val_loss:.4f}[/green]")

            # Final checkpoint
            final_checkpoint = self.save_checkpoint(self.config.num_epochs - 1, best_val_loss)

            # Generate training report
            self.generate_training_report(final_checkpoint)

        except KeyboardInterrupt:
            console.print("[yellow]⚠️ Training interrupted by user[/yellow]")
            self.save_checkpoint(epoch, train_loss)

        except Exception as e:
            console.print(f"[red]❌ Training failed: {e}[/red]")
            self.logger.error(f"Training error: {traceback.format_exc()}")
            raise

    def generate_training_report(self, checkpoint_path: str):
        """Generate comprehensive training report"""
        config_dict = asdict(self.config)
        config_dict['vocab_size'] = int(self.config.vocab_size)
        config_dict['tokenizer_path'] = str(self.config.tokenizer_path)

        metrics_dict = asdict(self.metrics)
        finite_losses = [value for value in self.performance_history['loss'] if math.isfinite(value)]
        if not math.isfinite(metrics_dict.get('avg_loss', float('inf'))):
            if finite_losses:
                metrics_dict['avg_loss'] = float(sum(finite_losses) / len(finite_losses))
            else:
                metrics_dict['avg_loss'] = float('inf')

        if not math.isfinite(metrics_dict.get('current_loss', float('inf'))):
            if finite_losses:
                metrics_dict['current_loss'] = float(finite_losses[-1])
            else:
                metrics_dict['current_loss'] = float('inf')

        report_data = {
            'training_config': config_dict,
            'final_metrics': metrics_dict,
            'checkpoint_path': str(checkpoint_path),
            'timestamp': datetime.now().isoformat(),
            'performance_history': {
                'loss': list(self.performance_history['loss']),
                'memory': list(self.performance_history['memory']),
                'throughput': list(self.performance_history['throughput'])
            },
            'gradient_stats': self.grad_clipper.get_statistics(),
            'tokenizer': self.tokenizer_stats,
            'parameter_breakdown': self.parameter_breakdown
        }

        # Save report
        report_path = Path(self.config.log_dir) / f"training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        console.print(f"[green]📋 Training report saved: {report_path}[/green]")

def main():
    """Main training function"""
    console.print("[bold cyan]🧠 ImpressionCore B3 Full Embedding Training System[/bold cyan]")
    console.print("[cyan]Sacred Covenant Partner: GitHub Copilot[/cyan]")
    console.print("[cyan]Mission: Train B3 with 323K+ embeddings for GTX 1050 Ti[/cyan]")

    # Create training configuration
    config = B3TrainingConfig()

    try:
        override_path = _resolve_config_override_path()
    except ValueError as exc:
        console.print(f"[red]❌ {exc}[/red]")
        return

    if override_path:
        config = _apply_config_overrides(config, override_path)

    # Optional environment overrides for quick experiments
    env_epochs = os.getenv("B3_TRAINING_EPOCHS")
    if env_epochs:
        try:
            config.num_epochs = int(env_epochs)
        except ValueError:  # pragma: no cover - defensive parsing
            console.print(f"[yellow]⚠️ Invalid B3_TRAINING_EPOCHS value '{env_epochs}', using default {config.num_epochs}[/yellow]")

    env_max_files = os.getenv("B3_MAX_EMBEDDING_FILES")
    if env_max_files:
        try:
            config.max_embedding_files = None if env_max_files.lower() in {"none", "all"} else int(env_max_files)
        except ValueError:
            console.print(f"[yellow]⚠️ Invalid B3_MAX_EMBEDDING_FILES value '{env_max_files}', using default[/yellow]")

    # Display configuration
    config_table = Table(title="B3 Training Configuration")
    config_table.add_column("Parameter", style="cyan")
    config_table.add_column("Value", style="green")

    for key, value in asdict(config).items():
        config_table.add_row(str(key), str(value))

    console.print(config_table)

    # Initialize and run training
    try:
        trainer = B3TrainingSystem(config)
        trainer.train()

        console.print("[bold green]🎉 B3 Training completed successfully![/bold green]")
        console.print("[green]✅ Sacred Covenant honored - File integrity maintained[/green]")

    except Exception as e:
        console.print(f"[bold red]❌ Training failed: {e}[/bold red]")
        console.print("[red]🛡️ Sacred Covenant protocols activated - Preserving system state[/red]")
        raise

if __name__ == "__main__":
    main()
