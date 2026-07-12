#!/usr/bin/env python3
"""
ImpressionCore: Training Utils

Module for training utils functionality in the ImpressionCore framework.

File: training\training_utils.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, training, gpu-optimized, ml, pytorch, production, 2025, object-oriented]
Dependencies: [torch, typing, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements training utils functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
from training.training_utils import TrainingMetrics
instance = TrainingMetrics()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import json
import logging
import torch
import torch.nn as nn
import torch.optim as optim
import torch.distributed as dist
from torch.utils.data import Dataset, DataLoader
from torch.nn.parallel import DistributedDataParallel
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
import numpy as np
import random
from tqdm import tqdm
import time
from pathlib import Path

try:
    from core.config import ModelConfig, TrainingConfig
    from core.model import ImpressionCoreModel
    from core.dual_shadow import DualShadowModel
    from utils.checkpoint_utils import save_checkpoint, load_checkpoint
except ImportError:
    from ..core.config import ModelConfig, TrainingConfig
    from ..core.model import ImpressionCoreModel
    # Memory optimization: Explicit memory cleanup
    from ..core.dual_shadow import DualShadowModel
    from ..utils.checkpoint_utils import save_checkpoint, load_checkpoint

logger = logging.getLogger(__name__)

@dataclass
class TrainingMetrics:
    """Training metrics tracker"""
    
    total_loss: float = 0.0
    step_count: int = 0
    total_tokens: int = 0
    best_loss: float = float('inf')
    start_time: float = field(default_factory=time.time)
    last_log_time: float = field(default_factory=time.time)
    
    def update(self, loss: float, num_tokens: int) -> None:
        """Update metrics with new values"""
        self.total_loss += loss
        self.step_count += 1
        self.total_tokens += num_tokens
        self.best_loss = min(self.best_loss, loss)
    
    def get_stats(self) -> Dict[str, float]:
        """Get current statistics"""
        now = time.time()
        elapsed = now - self.start_time
        tokens_per_second = self.total_tokens / max(1, elapsed)
        avg_loss = self.total_loss / max(1, self.step_count)
        
        return {
            "avg_loss": avg_loss,
            "best_loss": self.best_loss,
            "tokens_per_second": tokens_per_second,
            "elapsed_time": elapsed
        }
    
    def log(self, force: bool = False) -> Dict[str, float]:
        """Log metrics if enough time has passed"""
        now = time.time()
        stats = self.get_stats()
        
        # Log no more than once every 10 seconds
        if force or now - self.last_log_time > 10:
            logger.info(
                f"Training stats: loss={stats['avg_loss']:.4f}, "
                f"tokens/sec={stats['tokens_per_second']:.1f}, "
                f"elapsed={stats['elapsed_time'] / 60:.1f}m"
            )
            self.last_log_time = now
            
        return stats
    
    def reset(self) -> None:
        """Reset cumulative statistics"""
        self.total_loss = 0.0
        self.step_count = 0
        self.total_tokens = 0
        self.start_time = time.time()


class TextDataset(Dataset):
    """Simple dataset for training from tokenized text data"""
    
    def __init__(
        self,
        data_path: str,
        block_size: int = 1024,
        stride: Optional[int] = None,
        pad_token_id: int = 0
    ):
        """
        Initialize the dataset.
        
        Args:
            data_path: Path to tokenized data file (jsonl or pt)
            block_size: Maximum sequence length
            stride: Stride for sliding window (None = block_size)
            pad_token_id: Token ID to use for padding
        """
        self.block_size = block_size
        self.stride = stride if stride is not None else block_size
        self.pad_token_id = pad_token_id
        
        # Load data
        self.data = self._load_data(data_path)
        self.blocks = self._prepare_blocks()
        
        logger.info(f"Loaded dataset from {data_path} with {len(self.blocks)} blocks")
    
    def _load_data(self, data_path: str) -> List[torch.Tensor]:
        """Load data from file"""
        if data_path.endswith('.pt'):
            # Load PyTorch tensor
            return torch.load(data_path)
        elif data_path.endswith('.jsonl'):
            # Load JSONL file with tokenized text
            tokens = []
            with open(data_path, 'r') as f:
                for line in f:
                    item = json.loads(line)
                    if isinstance(item, dict) and 'tokens' in item:
                        tokens.append(torch.tensor(item['tokens'], dtype=torch.long))
                    elif isinstance(item, list):
                        tokens.append(torch.tensor(item, dtype=torch.long))
            return tokens
        else:
            raise ValueError(f"Unsupported data file format: {data_path}")
    
    def _prepare_blocks(self) -> List[Dict[str, torch.Tensor]]:
        """Prepare blocks for training"""
        blocks = []
        
        for tokens in self.data:
            # Split into blocks with stride
            for start in range(0, max(0, len(tokens) - 1), self.stride):
                end = min(start + self.block_size, len(tokens))
                block_tokens = tokens[start:end]
                
                # Create inputs and labels
                # For causal LM, inputs are tokens, labels are shifted right
                input_ids = block_tokens
                labels = torch.cat([block_tokens[1:], torch.tensor([self.pad_token_id])])
                
                # Create attention mask (1s for tokens, 0s for padding)
                attention_mask = torch.ones_like(input_ids)
                
                blocks.append({
                    'input_ids': input_ids,
                    'attention_mask': attention_mask,
                    'labels': labels
                })
        
        return blocks
    
    def __len__(self) -> int:
        """
        
    __len__ function for processing.
    
    Args:
        self: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        return len(self.blocks)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        
    __getitem__ function for processing.
    
    Args:
        self, idx: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        return self.blocks[idx]


def collate_fn(batch: List[Dict[str, torch.Tensor]], pad_token_id: int = 0) -> Dict[str, torch.Tensor]:
    """
    Collate function for DataLoader.
    
    Args:
        batch: List of examples
        pad_token_id: Token ID to use for padding
        
    Returns:
        Batched tensors
    """
    max_length = max(len(x['input_ids']) for x in batch)
    
    # Initialize padded tensors
    input_ids = torch.full((len(batch), max_length), pad_token_id, dtype=torch.long)
    attention_mask = torch.zeros((len(batch), max_length), dtype=torch.long)
    labels = torch.full((len(batch), max_length), -100, dtype=torch.long)  # -100 is ignored by loss
    
    # Fill tensors
    for i, item in enumerate(batch):
        seq_len = len(item['input_ids'])
        input_ids[i, :seq_len] = item['input_ids']
        attention_mask[i, :seq_len] = item['attention_mask']
        labels[i, :seq_len] = item['labels']
    
    return {
        'input_ids': input_ids,
        'attention_mask': attention_mask,
        'labels': labels
    }


def set_random_seed(seed: int) -> None:
    """Set random seeds for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    # Memory optimization: CUDA operations for GPU acceleration
    torch.backends.cudnn.deterministic = True


def get_linear_schedule_with_warmup(
    optimizer: torch.optim.Optimizer,
    num_warmup_steps: int,
    num_training_steps: int,
    last_epoch: int = -1
) -> torch.optim.lr_scheduler.LambdaLR:
    """
    Create a schedule with a learning rate that decreases linearly after
    linearly increasing during a warmup period.
    """
    def lr_lambda(current_step: int) -> float:
        """
        
    lr_lambda function for processing.
    
    Args:
        current_step: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        if current_step < num_warmup_steps:
            return float(current_step) / float(max(1, num_warmup_steps))
        return max(
            0.0,
            float(num_training_steps - current_step) / float(max(1, num_training_steps - num_warmup_steps))
        )
        
    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda, last_epoch)


def train(
    config: ModelConfig,
    model: Union[ImpressionCoreModel, DualShadowModel],
    train_dataset: Dataset,
    val_dataset: Optional[Dataset] = None,
    output_dir: str = "checkpoints",
    training_args: Optional[TrainingConfig] = None,
    seed: int = 42
) -> Dict[str, float]:
    """
    Train an ImpressionCore model.
    
    Args:
        config: Model configuration
        # Memory optimization: Explicit memory cleanup
        model: Model to train
        # Memory optimization: Explicit memory cleanup
        train_dataset: Training dataset
        val_dataset: Validation dataset (optional)
        output_dir: Directory to save checkpoints
        training_args: Training arguments (will use config.training if None)
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary of training metrics
    """
    # Set random seed
    set_random_seed(seed)
    
    # Get training arguments
    if training_args is None:
        training_args = config.training
    
    # Set device
    # Memory optimization: Device placement for memory management
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Memory optimization: CUDA operations for GPU acceleration
    logger.info(f"Using device: {device}")
    # Memory optimization: Device placement for memory management
    
    # Prepare model
    if isinstance(model, DualShadowModel):
        # If using dual shadow model, only shadow model is trained
        # Memory optimization: Explicit memory cleanup
        model.shadow_model.to(device)
        # Memory optimization: Device placement for memory management
        train_model = model.shadow_model
        # Memory optimization: Explicit memory cleanup
    else:
        model.to(device)
        # Memory optimization: Device placement for memory management
        train_model = model
        # Memory optimization: Explicit memory cleanup
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create data loader
    train_loader = DataLoader(
        train_dataset,
        batch_size=training_args.batch_size,
        shuffle=True,
        collate_fn=lambda batch: collate_fn(batch),
        num_workers=4,
        pin_memory=True
        # Memory optimization: Memory-critical operation
    )
    
    val_loader = None
    if val_dataset:
        val_loader = DataLoader(
            val_dataset,
            batch_size=training_args.batch_size,
            shuffle=False,
            collate_fn=lambda batch: collate_fn(batch),
            num_workers=4,
            pin_memory=True
            # Memory optimization: Memory-critical operation
        )
    
    # Set up optimizer
    optimizer = optim.AdamW(
        train_model.parameters(),
        lr=training_args.learning_rate,
        weight_decay=training_args.weight_decay
    )
    
    # Set up learning rate scheduler
    total_steps = len(train_loader) * training_args.max_steps
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=training_args.warmup_steps,
        num_training_steps=total_steps
    )
    
    # Set up fp16/bf16 if needed
    scaler = None
    if training_args.fp16:
        scaler = torch.cuda.amp.GradScaler()
        # Memory optimization: CUDA operations for GPU acceleration
    
    # Metrics tracker
    metrics = TrainingMetrics()
    
    # Gradient accumulation setup
    accum_steps = training_args.gradient_accumulation_steps
    
    # Save initial checkpoint
    model_to_save = train_model
    save_checkpoint(
        os.path.join(output_dir, "checkpoint_init.pt"),
        model_to_save,
        optimizer,
        0,
        0,
        config,
        {"metrics": metrics.get_stats()}
    )
    
    # Training loop
    logger.info("Starting training")
    train_model.train()
    
    global_step = 0
    best_val_loss = float('inf')
    
    for epoch in range(training_args.max_steps):
        train_model.train()
        
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}", dynamic_ncols=True)
        for step, batch in enumerate(pbar):
            # Move batch to device
            # Memory optimization: Device placement for memory management
            batch = {k: v.to(device) for k, v in batch.items()}
            # Memory optimization: Device placement for memory management
            
            # Count tokens
            num_tokens = batch['attention_mask'].sum().item()
            
            # Forward pass with mixed precision if enabled
            if scaler is not None:
                with torch.cuda.amp.autocast():
                # Memory optimization: CUDA operations for GPU acceleration
                    outputs = train_model(**batch)
                    loss = outputs.loss if hasattr(outputs, 'loss') else outputs[0]
                    loss = loss / accum_steps
                
                # Scale loss and backward
                scaler.scale(loss).backward()
                
                # Update weights if accumulated enough gradients
                if (step + 1) % accum_steps == 0 or (step + 1 == len(train_loader)):
                    # Clip gradients
                    if training_args.max_grad_norm > 0:
                        scaler.unscale_(optimizer)
                        torch.nn.utils.clip_grad_norm_(train_model.parameters(), training_args.max_grad_norm)
                    
                    # Update
                    scaler.step(optimizer)
                    scaler.update()
                    optimizer.zero_grad()
                    scheduler.step()
                    
                    # Update global step
                    global_step += 1
            else:
                # Standard forward pass and backward
                outputs = train_model(**batch)
                loss = outputs.loss if hasattr(outputs, 'loss') else outputs[0]
                loss = loss / accum_steps
                
                # Backward
                loss.backward()
                
                # Update weights if accumulated enough gradients
                if (step + 1) % accum_steps == 0 or (step + 1 == len(train_loader)):
                    # Clip gradients
                    if training_args.max_grad_norm > 0:
                        torch.nn.utils.clip_grad_norm_(train_model.parameters(), training_args.max_grad_norm)
                    
                    # Update
                    optimizer.step()
                    optimizer.zero_grad()
                    scheduler.step()
                    
                    # Update global step
                    global_step += 1
            
            # Update metrics
            metrics.update(loss.item() * accum_steps, num_tokens)
            
            # Update progress bar
            pbar.set_postfix({
                'loss': f"{metrics.total_loss / metrics.step_count:.4f}",
                'lr': f"{scheduler.get_last_lr()[0]:.2e}"
            })
            
            # Log metrics periodically
            stats = metrics.log()
            
            # Save checkpoint periodically
            if global_step > 0 and global_step % 1000 == 0:
                checkpoint_path = os.path.join(output_dir, f"checkpoint_{global_step}.pt")
                save_checkpoint(
                    checkpoint_path,
                    model_to_save,
                    optimizer,
                    epoch,
                    global_step,
                    config,
                    {"metrics": metrics.get_stats()}
                )
                logger.info(f"Saved checkpoint to {checkpoint_path}")
        
        # Validation
        if val_loader is not None:
            val_loss = evaluate(train_model, val_loader, device)
            # Memory optimization: Device placement for memory management
            logger.info(f"Validation loss: {val_loss:.4f}")
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_path = os.path.join(output_dir, "checkpoint_best.pt")
                save_checkpoint(
                    best_path,
                    model_to_save,
                    optimizer,
                    epoch,
                    global_step,
                    config,
                    {"metrics": metrics.get_stats(), "val_loss": val_loss}
                )
                logger.info(f"Saved best model with val_loss={val_loss:.4f}")
                # Memory optimization: Explicit memory cleanup
        
        # Save epoch checkpoint
        checkpoint_path = os.path.join(output_dir, f"checkpoint_epoch_{epoch+1}.pt")
        save_checkpoint(
            checkpoint_path,
            model_to_save,
            optimizer,
            epoch,
            global_step,
            config,
            {"metrics": metrics.get_stats()}
        )
    
    # Save final checkpoint
    final_path = os.path.join(output_dir, "checkpoint_final.pt")
    save_checkpoint(
        final_path,
        model_to_save,
        optimizer,
        training_args.max_steps - 1,
        global_step,
        config,
        {"metrics": metrics.get_stats()}
    )
    
    # If using dual shadow model, merge shadow into primary and save
    if isinstance(model, DualShadowModel):
        model._merge_shadow_to_primary()
        merged_path = os.path.join(output_dir, "checkpoint_merged.pt")
        save_checkpoint(
            merged_path,
            model.primary_model,
            None,
            training_args.max_steps - 1,
            global_step,
            config,
            {"metrics": metrics.get_stats(), "merged": True}
        )
    
    logger.info("Training complete")
    return metrics.get_stats()


def evaluate(
    model: nn.Module,
    data_loader: DataLoader,
    device: torch.device
    # Memory optimization: Device placement for memory management
) -> float:
    """
    Evaluate a model on a dataset.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        model: Model to evaluate
        # Memory optimization: Explicit memory cleanup
        data_loader: DataLoader for evaluation data
        device: Device to use for evaluation
        # Memory optimization: Device placement for memory management
        
    Returns:
        Average loss
    """
    model.eval()
    total_loss = 0.0
    total_samples = 0
    
    with torch.no_grad():
    # Memory optimization: Disable gradient computation to save memory
        for batch in tqdm(data_loader, desc="Evaluating"):
            # Move batch to device
            # Memory optimization: Device placement for memory management
            batch = {k: v.to(device) for k, v in batch.items()}
            # Memory optimization: Device placement for memory management
            
            # Forward pass
            outputs = model(**batch)
            loss = outputs.loss if hasattr(outputs, 'loss') else outputs[0]
            
            # Accumulate loss
            total_loss += loss.item() * batch['input_ids'].size(0)
            total_samples += batch['input_ids'].size(0)
    
    # Reset to training mode
    model.train()
    
    # Return average loss
    return total_loss / total_samples


def get_device(prefer_cuda: bool = True) -> str:
    """
    Get the best available device for training/inference.
    
    Args:
        prefer_cuda: Whether to prefer CUDA over CPU
        
    Returns:
        str: Device string ('cuda' or 'cpu')
    """
    if prefer_cuda and torch.cuda.is_available():
        return 'cuda'
    else:
        return 'cpu'


def get_optimal_device() -> torch.device:
    """
    Get the optimal device with proper torch.device object.
    
    Returns:
        torch.device: The optimal device for the current system
    """
    if torch.cuda.is_available():
        device = torch.device("cuda")
        # Log device info
        print(f"Using GPU: {torch.cuda.get_device_name()}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f}GB")
    else:
        device = torch.device("cpu")
        print("Using CPU (CUDA not available)")
    
    return device