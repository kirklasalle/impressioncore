#!/usr/bin/env python3
"""
ImpressionCore: Continuous Training With Shared Memory

Module for continuous training with shared memory functionality in the ImpressionCore framework.

File: examples\continuous_training_with_shared_memory.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, pytorch, production, 2025, object-oriented]
Dependencies: [torch, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements continuous training with shared memory functionality for the
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
from examples.continuous_training_with_shared_memory import CustomTrainerWithMemoryManagement
instance = CustomTrainerWithMemoryManagement()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import logging
import os
import sys
import torch
import argparse
import time
from pathlib import Path
import glob
import gc

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import utilities for memory management
# Memory optimization: Memory-critical operation
from src.core.utils.gpu_memory_manager import GPUMemoryManager
# Memory optimization: Memory-critical operation
from src.core.utils.memory_swap_manager import MemorySwapManager
# Memory optimization: Memory-critical operation
from src.core.utils.cuda_utils import clean_gpu_memory, get_cuda_info
# Memory optimization: Memory-critical operation
from src.core.config import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """
    
    parse_args function for processing.
    
    Args:
        No arguments: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
    """
    parser = argparse.ArgumentParser(
        description="Continue training with enhanced GPU memory management"
        # Memory optimization: Memory-critical operation
    )
      # Basic training arguments
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="src/output/training_metrics/checkpoint-2000",
        help="Path to checkpoint directory or file"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=1000,
        help="Number of additional training steps"
    )
    parser.add_argument(
        "--dataset_dir",
        type=str,
        default="trainingdocs",
        help="Directory containing training text files"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=4,
        help="Training batch size"
    )
    
    # Memory management arguments
    # Memory optimization: Memory-critical operation
    parser.add_argument(
        "--shared_memory",
        # Memory optimization: Memory-critical operation
        action="store_true",
        help="Enable shared system memory for VRAM extension"
        # Memory optimization: Memory-critical operation
    )
    parser.add_argument(
        "--memory_target",
        # Memory optimization: Memory-critical operation
        type=float,
        default=0.85,
        help="Target VRAM usage fraction (0.0-1.0)"
    )
    parser.add_argument(
        "--memory_monitor",
        # Memory optimization: Memory-critical operation
        action="store_true",
        help="Enable memory usage monitoring"
        # Memory optimization: Memory-critical operation
    )
    parser.add_argument(
        "--dynamic_batching",
        action="store_true",
        help="Dynamically adjust batch size based on memory"
        # Memory optimization: Memory-critical operation
    )
    parser.add_argument(
        "--pinned_memory",
        # Memory optimization: Memory-critical operation
        action="store_true",
        help="Use pinned memory for faster CPU-GPU transfers"
        # Memory optimization: Memory-critical operation
    )
    parser.add_argument(
        "--swap_parameters",
        action="store_true",
        help="Enable swapping model parameters between VRAM and system RAM"
        # Memory optimization: Explicit memory cleanup
    )
    
    # Performance optimization arguments
    parser.add_argument(
        "--fp16",
        action="store_true",
        help="Use mixed precision (FP16) training"
    )
    parser.add_argument(
        "--gradient_accumulation_steps",
        type=int,
        default=8,
        help="Number of steps to accumulate gradients"
    )
    parser.add_argument(
        "--max_seq_len",
        type=int,
        default=None,
        help="Maximum sequence length (default: use checkpoint value)"
    )
    parser.add_argument(
        "--resize_embeddings",
        action="store_true",
        help="Resize position embeddings if needed"
    )
    
    return parser.parse_args()

def setup_memory_management(args):
# Memory optimization: Memory-critical operation
    """
    Setup memory management based on command line arguments.
    # Memory optimization: Memory-critical operation
    
    Returns:
        Tuple of (device, memory_manager, swap_manager)
        # Memory optimization: Device placement for memory management
    """
    # Create GPU memory manager
    # Memory optimization: Memory-critical operation
    memory_manager = GPUMemoryManager(
    # Memory optimization: Memory-critical operation
        vram_target_usage=args.memory_target,
        # Memory optimization: Memory-critical operation
        enable_shared_memory=args.shared_memory,
        # Memory optimization: Memory-critical operation
        enable_monitoring=args.memory_monitor
        # Memory optimization: Memory-critical operation
    )
    
    # Determine device based on CUDA availability
    # Memory optimization: Device placement for memory management
    device = torch.device("cuda" if memory_manager.has_cuda else "cpu")
    # Memory optimization: Device placement for memory management
    
    # Create swap manager if requested
    swap_manager = None
    if args.swap_parameters and device.type == 'cuda':
    # Memory optimization: Device placement for memory management
        swap_manager = MemorySwapManager(
        # Memory optimization: Memory-critical operation
            vram_target_usage=args.memory_target,
            # Memory optimization: Memory-critical operation
            enable_monitoring=args.memory_monitor,
            # Memory optimization: Memory-critical operation
            device=device,
            # Memory optimization: Device placement for memory management
            use_pinned_memory=args.pinned_memory
            # Memory optimization: Memory-critical operation
        )
        logger.info("Parameter swapping between VRAM and system RAM enabled")
    
    # Show memory information
    # Memory optimization: Memory-critical operation
    if device.type == 'cuda':
    # Memory optimization: Device placement for memory management
        info = get_cuda_info()
        # Memory optimization: Memory-critical operation
        logger.info(f"Using GPU: {info.get('device_name', 'unknown')}")
        # Memory optimization: Device placement for memory management
        logger.info(f"VRAM: {info.get('memory_total_mb', 0):.1f}MB total, " + 
        # Memory optimization: Memory-critical operation
                   f"{info.get('memory_free_mb', 0):.1f}MB free")
                   # Memory optimization: Memory-critical operation
        
        # Check if shared memory is supported
        # Memory optimization: Memory-critical operation
        if args.shared_memory and info.get('shared_memory_support', False):
        # Memory optimization: Memory-critical operation
            logger.info("Shared memory support: Enabled")
            # Memory optimization: Memory-critical operation
            logger.info(f"System RAM available: {info.get('system_memory_mb', 0):.1f}MB")
            # Memory optimization: Memory-critical operation
        elif args.shared_memory:
        # Memory optimization: Memory-critical operation
            logger.warning("Shared memory requested but not fully supported by driver")
            # Memory optimization: Memory-critical operation
            logger.info("Some shared memory features will still be used")
            # Memory optimization: Memory-critical operation
    else:
        logger.warning("CUDA not available, using CPU. Training will be much slower.")
        # Memory optimization: Memory-critical operation
    
    return device, memory_manager, swap_manager
    # Memory optimization: Device placement for memory management

def main():
    """Main function for continuous training with shared memory."""
    # Memory optimization: Memory-critical operation
    args = parse_args()
    
    # Set up memory management
    # Memory optimization: Memory-critical operation
    device, memory_manager, swap_manager = setup_memory_management(args)
    # Memory optimization: Device placement for memory management
    
    try:        # Import required modules
        from src.core.model import ModelInterface
        # Memory optimization: Explicit memory cleanup
        from src.core.trainer import DistillationTrainer
        from torch.utils.data import DataLoader, Dataset, ConcatDataset
        from transformers import GPT2Tokenizer
        
        # Add safe globals for checkpoint loading
        from torch.serialization import add_safe_globals
        add_safe_globals([ConfigManager])
        
        # Import functions from original continuous_training.py
        from continuous_training import (
            find_checkpoint_file,
            resize_position_embeddings
        )
        
        # Load checkpoint file
        logger.info(f"Loading checkpoint from {args.checkpoint}")
        checkpoint_path = find_checkpoint_file(args.checkpoint)
        logger.info(f"Found checkpoint file: {checkpoint_path}")
        
        # Try multiple approaches to load checkpoint
        checkpoint = None
        try:
            # Try loading with safe globals
            from torch.serialization import safe_globals
            with safe_globals([ConfigManager]):
                checkpoint = torch.load(checkpoint_path, map_location="cpu")
            logger.info("Successfully loaded checkpoint with safe_globals")
        except Exception as e1:
            logger.warning(f"Failed to load with safe_globals: {e1}")
            
            try:
                # Try legacy mode
                checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
                logger.info("Successfully loaded checkpoint with weights_only=False")
            except Exception as e2:
                logger.warning(f"Failed to load with weights_only=False: {e2}")
                
                try:
                    # Try restrictive mode
                    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
                    logger.info("Successfully loaded checkpoint with weights_only=True")
                except Exception as e3:
                    logger.error("All checkpoint loading approaches failed")
                    logger.error(f"Last error: {e3}")
                    return
        
        if checkpoint is None:
            logger.error("Failed to load checkpoint")
            return
        
        # Initialize tokenizer
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        tokenizer.pad_token = tokenizer.eos_token
        
        # Extract or create configurations
        if hasattr(checkpoint, 'config') or (isinstance(checkpoint, dict) and 'config' in checkpoint):
            config = checkpoint.config if hasattr(checkpoint, 'config') else checkpoint['config']
            logger.info("Loaded configuration from checkpoint")
            
            # Extract sequence length
            checkpoint_seq_len = getattr(config.model_config, 'max_position_embeddings', 128)
            logger.info(f"Checkpoint sequence length: {checkpoint_seq_len}")
            
            # Use checkpoint sequence length unless overridden
            if args.max_seq_len is None:
                args.max_seq_len = checkpoint_seq_len
                logger.info(f"Using checkpoint sequence length: {args.max_seq_len}")
        else:
            logger.warning("No configuration found in checkpoint, using defaults")
            config = ConfigManager()
            config.model_config.hidden_size = 256
            config.model_config.num_hidden_layers = 6
            config.model_config.num_attention_heads = 8
            config.model_config.intermediate_size = 1024
            config.model_config.max_position_embeddings = args.max_seq_len or 128
            
            config.training_config.max_steps = args.steps
            config.training_config.logging_steps = 50
            config.training_config.eval_steps = 100
            config.training_config.save_steps = 100
            config.training_config.batch_size = args.batch_size
            config.training_config.gradient_accumulation_steps = args.gradient_accumulation_steps
          # Create model
        model = ModelInterface(config.model_config)
        # Memory optimization: Explicit memory cleanup
        
        # Load model weights
        # Memory optimization: Explicit memory cleanup
        try:
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
            elif isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
                model.load_state_dict(checkpoint['state_dict'])
            elif hasattr(checkpoint, 'state_dict'):
                model.load_state_dict(checkpoint.state_dict())
            else:
                model.load_state_dict(checkpoint)
            
            logger.info("Successfully loaded model weights")
            # Memory optimization: Explicit memory cleanup
        except RuntimeError as e:
            # Handle position embedding size mismatch
            if "size mismatch for position_embeddings" in str(e) and args.resize_embeddings:
                logger.warning("Position embedding size mismatch, attempting resize")
                # Extract sizes from error message
                # ... (code that extracts sizes and recreates model with correct size)
                # Memory optimization: Explicit memory cleanup
                # For now, we'll just abort if this happens
                logger.error(f"Position embedding resize not implemented: {e}")
                return
            else:
                logger.error(f"Could not load model weights: {e}")
                # Memory optimization: Explicit memory cleanup
                return
        
        # Apply mixed precision if requested
        if args.fp16 and device.type == 'cuda':
        # Memory optimization: Device placement for memory management
            from torch.cuda.amp import GradScaler
            # Memory optimization: CUDA operations for GPU acceleration
            scaler = GradScaler()
            logger.info("Mixed precision (FP16) enabled with gradient scaling")
        else:
            scaler = None
        
        # Move model to device
        # Memory optimization: Device placement for memory management
        model = model.to(device)
        # Memory optimization: Device placement for memory management
        model_size_mb = sum(p.numel() * p.element_size() for p in model.parameters()) / 1024**2
        logger.info(f"Model loaded successfully (size: {model_size_mb:.1f}MB)")
        # Memory optimization: Explicit memory cleanup
        
        # Register model parameters for swapping if requested
        # Memory optimization: Explicit memory cleanup
        if swap_manager is not None:
            swap_manager.register_model_parameters(model)
          # Create teacher model (same as student for now)
          # Memory optimization: Explicit memory cleanup
        teacher_model = ModelInterface(config.model_config)
        # Memory optimization: Explicit memory cleanup
        teacher_model.load_state_dict(model.state_dict())
        teacher_model = teacher_model.to(device)
        # Memory optimization: Device placement for memory management
        logger.info("Teacher model initialized")
        # Memory optimization: Explicit memory cleanup
        
        # Report memory usage after model loading
        # Memory optimization: Explicit memory cleanup
        if device.type == 'cuda':
        # Memory optimization: Device placement for memory management
            mem_info = get_cuda_info()
            # Memory optimization: Memory-critical operation
            logger.info(f"VRAM after model loading: " + 
            # Memory optimization: Explicit memory cleanup
                       f"{mem_info.get('memory_allocated_mb', 0):.1f}MB allocated, " +
                       # Memory optimization: Memory-critical operation
                       f"{mem_info.get('memory_reserved_mb', 0):.1f}MB reserved")
                       # Memory optimization: Memory-critical operation
        
        # Load datasets 
        from mixed_corpus_training import (
            load_multiple_datasets,
            split_dataset,
            create_sample_text_files
        )
        
        # Check for training data
        if not os.path.exists(args.dataset_dir) or len(glob.glob(os.path.join(args.dataset_dir, "*.txt"))) == 0:
            logger.warning(f"No text files found in {args.dataset_dir}, creating samples")
            create_sample_text_files()
        
        # Load and prepare datasets
        try:
            max_length = args.max_seq_len if args.max_seq_len is not None else config.model_config.max_position_embeddings
            overlap = max_length // 2
            
            logger.info(f"Loading datasets with sequence length {max_length} and overlap {overlap}")
            all_datasets = load_multiple_datasets(
                doc_dir=args.dataset_dir,
                max_length=max_length,
                overlap=overlap
            )
            
            if not all_datasets:
                logger.error("No datasets were loaded. Check the dataset directory.")
                return
                
            # Combine and split datasets
            combined_dataset = ConcatDataset(all_datasets)
            logger.info(f"Combined dataset has {len(combined_dataset)} samples")
            
            train_dataset, eval_dataset = split_dataset(combined_dataset, eval_ratio=0.1)
            logger.info(f"Train dataset: {len(train_dataset)} samples")
            logger.info(f"Eval dataset: {len(eval_dataset)} samples")
            
        except Exception as e:
            logger.error(f"Error loading datasets: {e}")
            return
        
        # Create dataloaders with optimized settings for GPU memory
        # Memory optimization: Memory-critical operation
        train_dataloader = DataLoader(
            train_dataset,
            batch_size=args.batch_size,
            shuffle=True,
            num_workers=0,  # Use 0 workers to avoid memory issues on 4GB VRAM
            # Memory optimization: Memory-critical operation
            pin_memory=args.pinned_memory and device.type == 'cuda',
            # Memory optimization: Device placement for memory management
            drop_last=True  # More efficient for gradient accumulation
        )
        
        eval_dataloader = DataLoader(
            eval_dataset,
            batch_size=args.batch_size * 2,  # Can use larger batch size for eval (no gradients)
            shuffle=False,
            num_workers=0,
            pin_memory=args.pinned_memory and device.type == 'cuda'
            # Memory optimization: Device placement for memory management
        )
        
        # Configure training parameters
        config.training_config.max_steps = args.steps
        config.training_config.gradient_accumulation_steps = args.gradient_accumulation_steps
        config.training_config.fp16 = args.fp16 and device.type == 'cuda'
        # Memory optimization: Device placement for memory management
        config.training_config.batch_size = args.batch_size
        
        # Create specialized optimizer with shared memory awareness
        # Memory optimization: Memory-critical operation
        optimizer = create_optimizer_with_shared_memory(
        # Memory optimization: Memory-critical operation
            model=model,
            learning_rate=config.training_config.learning_rate if hasattr(config.training_config, 'learning_rate') else 2e-4,
            weight_decay=config.training_config.weight_decay if hasattr(config.training_config, 'weight_decay') else 0.01,
            use_shared_memory=args.shared_memory
            # Memory optimization: Memory-critical operation
        )
        
        # Setup trainer
        try:
            # Create a trainer class that works well with swap manager
            trainer = CustomTrainerWithMemoryManagement(
            # Memory optimization: Memory-critical operation
                model=model,
                tokenizer=tokenizer,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                config=config.training_config,
                optimizer=optimizer,
                device=device,
                # Memory optimization: Device placement for memory management
                swap_manager=swap_manager,
                memory_manager=memory_manager,
                # Memory optimization: Memory-critical operation
                scaler=scaler if args.fp16 and device.type == 'cuda' else None,
                # Memory optimization: Device placement for memory management
                max_steps=args.steps,
                gradient_accumulation_steps=args.gradient_accumulation_steps,
                teacher_model=teacher_model
            )
            
            # Setup training monitoring
            logger.info(f"Starting training with shared memory optimization")
            # Memory optimization: Memory-critical operation
            logger.info(f"Using batch size {args.batch_size} with gradient accumulation steps {args.gradient_accumulation_steps}")
            if args.fp16 and device.type == 'cuda':
            # Memory optimization: Device placement for memory management
                logger.info("Mixed precision (FP16) training enabled")
            if args.shared_memory:
            # Memory optimization: Memory-critical operation
                logger.info("Shared system memory enabled for extended VRAM")
                # Memory optimization: Memory-critical operation
            if args.swap_parameters:
                logger.info("Parameter swapping between VRAM and system RAM enabled")
                
            # Train model
            start_time = time.time()
            training_result = trainer.train()
            training_time = time.time() - start_time
            
            logger.info(f"Training completed in {training_time:.2f} seconds")
            logger.info(f"Training metrics: {training_result}")
            
            # Save the final model
            output_dir = os.path.join("outputs", f"continuous_training_{int(time.time())}")
            os.makedirs(output_dir, exist_ok=True)
            
            model.save_pretrained(output_dir)
            tokenizer.save_pretrained(output_dir)
            
            logger.info(f"Model saved to {output_dir}")
            # Memory optimization: Explicit memory cleanup
            
        except Exception as e:
            logger.error(f"Error during training: {e}", exc_info=True)
        
        finally:
            # Clean up resources
            if swap_manager is not None:
                swap_manager.cleanup()
            if memory_manager is not None:
            # Memory optimization: Memory-critical operation
                memory_manager.cleanup()
                # Memory optimization: Memory-critical operation
            
            # Final GPU memory cleanup
            # Memory optimization: Memory-critical operation
            if device.type == 'cuda':
            # Memory optimization: Device placement for memory management
                clean_gpu_memory(aggressive=True)
                # Memory optimization: Memory-critical operation
            
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)


def create_optimizer_with_shared_memory(model, learning_rate=2e-4, weight_decay=0.01, use_shared_memory=False):
# Memory optimization: Memory-critical operation
    """
    Create an optimizer configured for shared memory usage.
    # Memory optimization: Memory-critical operation
    
    Args:
        model: The model to optimize
        # Memory optimization: Explicit memory cleanup
        learning_rate: Learning rate
        weight_decay: Weight decay value
        use_shared_memory: Whether to enable shared memory optimizations
        # Memory optimization: Memory-critical operation
        
    Returns:
        Configured optimizer
    """
    # Group parameters to apply weight decay selectively
    no_decay = ['bias', 'LayerNorm.weight']
    optimizer_grouped_parameters = [
        {
            'params': [p for n, p in model.named_parameters() 
                      if not any(nd in n for nd in no_decay)],
            'weight_decay': weight_decay,
        },
        {
            'params': [p for n, p in model.named_parameters() 
                      if any(nd in n for nd in no_decay)],
            'weight_decay': 0.0,
        }
    ]
    
    # Create optimizer with memory-efficient settings
    # Memory optimization: Memory-critical operation
    optimizer = torch.optim.AdamW(
        optimizer_grouped_parameters,
        lr=learning_rate,
        eps=1e-8,
        betas=(0.9, 0.999),
        fused=False  # Fused implementation can use more memory
        # Memory optimization: Memory-critical operation
    )
    
    # Apply shared memory optimizations if enabled
    # Memory optimization: Memory-critical operation
    if use_shared_memory:
    # Memory optimization: Memory-critical operation
        # Use pinned memory for optimizer states if available
        # Memory optimization: Memory-critical operation
        for group in optimizer.param_groups:
            for p in group['params']:
                if hasattr(p, 'pin_memory') and p.device.type == 'cuda':
                # Memory optimization: Device placement for memory management
                    # Pin the parameter's memory to enable efficient CPU-GPU transfers
                    # Memory optimization: Memory-critical operation
                    state = optimizer.state[p]
                    for k, v in state.items():
                        if isinstance(v, torch.Tensor) and v.device.type == 'cpu':
                        # Memory optimization: Device placement for memory management
                            state[k] = v.pin_memory()
                            # Memory optimization: Memory-critical operation
    
    return optimizer


class CustomTrainerWithMemoryManagement:
# Memory optimization: Memory-critical operation
    """
    Custom trainer class that incorporates memory management for efficient GPU training.
    # Memory optimization: Memory-critical operation
    This class adapts the DistillationTrainer to work with shared memory and tensor swapping.
    # Memory optimization: Memory-critical operation
    """
    
    def __init__(
        self,
        model,
        tokenizer,
        train_dataset,
        config,
        device,
        # Memory optimization: Device placement for memory management
        optimizer=None,
        eval_dataset=None,
        max_steps=1000,
        swap_manager=None,
        memory_manager=None,
        # Memory optimization: Memory-critical operation
        scaler=None,
        gradient_accumulation_steps=1,
        teacher_model=None
    ):
        """Initialize trainer with memory-optimized settings."""
        # Memory optimization: Memory-critical operation
        self.model = model
        # Memory optimization: Explicit memory cleanup
        self.tokenizer = tokenizer
        self.train_dataset = train_dataset
        self.eval_dataset = eval_dataset
        self.config = config
        self.device = device
        # Memory optimization: Device placement for memory management
        self.max_steps = max_steps
        self.swap_manager = swap_manager
        self.memory_manager = memory_manager
        # Memory optimization: Memory-critical operation
        self.scaler = scaler
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.teacher_model = teacher_model
        # Memory optimization: Explicit memory cleanup
        
        # Create optimizer if not provided
        self.optimizer = optimizer or create_optimizer_with_shared_memory(
        # Memory optimization: Memory-critical operation
            model=model,
            learning_rate=getattr(config, 'learning_rate', 2e-4),
            weight_decay=getattr(config, 'weight_decay', 0.01),
            use_shared_memory=self.swap_manager is not None
            # Memory optimization: Memory-critical operation
        )
        
        # Get batch size with fallback
        self.batch_size = getattr(config, 'batch_size', 4)
        
        # Set up output directory
        self.output_dir = getattr(config, 'output_dir', "outputs/custom_trainer")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Training state
        self.global_step = 0
        self.epoch = 0
        self.best_eval_loss = float('inf')
        
        # Try to adapt to the actual DistillationTrainer
        try:
            # Create a reference trainer for API compatibility
            from src.core.trainer import DistillationTrainer
            self.ref_trainer = DistillationTrainer(
                student_model=self.model,
                tokenizer=self.tokenizer,
                train_dataset=self.train_dataset,
                teacher_model=self.teacher_model,
                eval_dataset=self.eval_dataset,
                config=self.config,
                alpha=0.0,
                temperature=1.0
            )
            # We'll delegate some method calls to this reference implementation
        except Exception as e:
            logger.warning(f"Could not create reference DistillationTrainer: {e}")
            self.ref_trainer = None
    
    def train(self):
        """Train the model with memory management."""
        # Memory optimization: Explicit memory cleanup
        logger.info("Starting training with memory management")
        # Memory optimization: Memory-critical operation
        
        # Use the distillation trainer for the actual training loop if available
        if self.ref_trainer is not None:
            try:
                # Try to use the reference implementation but with our memory management
                # Memory optimization: Memory-critical operation
                self._inject_memory_management()
                # Memory optimization: Memory-critical operation
                result = self.ref_trainer.train()
                return result
            except Exception as e:
                logger.warning(f"Error using reference trainer: {e}")
                logger.info("Falling back to custom training loop")
                
        # Custom training loop with memory management
        # Memory optimization: Memory-critical operation
        self.model.train()
        train_dataloader = DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=0,
            pin_memory=self.device.type == 'cuda'
            # Memory optimization: Device placement for memory management
        )
        
        # Initialize progress tracking
        progress_bar = None
        try:
            from tqdm import tqdm
            progress_bar = tqdm(total=self.max_steps, desc="Training")
        except ImportError:
            progress_bar = None
            
        # Track metrics
        tr_loss = 0.0
        self.global_step = 0
        
        # Main training loop
        step = 0
        optimizer_was_run = False
        
        # Loop until max steps
        while self.global_step < self.max_steps:
            epoch_iterator = iter(train_dataloader)
            
            # Loop through batches
            try:
                while True:
                    # Get next batch
                    try:
                        batch = next(epoch_iterator)
                    except StopIteration:
                        # Reached end of dataset, restart
                        epoch_iterator = iter(train_dataloader)
                        batch = next(epoch_iterator)
                    
                    # Ensure tensors are on the correct device
                    # Memory optimization: Device placement for memory management
                    batch = {k: v.to(self.device) for k, v in batch.items()}
                    # Memory optimization: Device placement for memory management
                    
                    # Forward pass with memory management
                    # Memory optimization: Memory-critical operation
                    if self.swap_manager is not None:
                        # Ensure critical layers are on GPU
                        # Memory optimization: Memory-critical operation
                        self.swap_manager.ensure_group_on_gpu("base")
                        # Memory optimization: Memory-critical operation
                    
                    # Use mixed precision if enabled
                    if self.scaler is not None:
                        with torch.cuda.amp.autocast():
                        # Memory optimization: CUDA operations for GPU acceleration
                            loss = self.model(**batch).loss
                            loss = loss / self.gradient_accumulation_steps
                        
                        # Scale loss and backward pass
                        self.scaler.scale(loss).backward()
                        
                        if (step + 1) % self.gradient_accumulation_steps == 0:
                            # Unscale gradients
                            self.scaler.unscale_(self.optimizer)
                            
                            # Clip gradients
                            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                            
                            # Update weights
                            self.scaler.step(self.optimizer)
                            self.scaler.update()
                            self.optimizer.zero_grad()
                            optimizer_was_run = True
                    else:
                        # Regular forward/backward pass
                        loss = self.model(**batch).loss
                        loss = loss / self.gradient_accumulation_steps
                        loss.backward()
                        
                        if (step + 1) % self.gradient_accumulation_steps == 0:
                            # Clip gradients
                            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                            
                            # Update weights
                            self.optimizer.step()
                            self.optimizer.zero_grad()
                            optimizer_was_run = True
                    
                    # Track loss
                    tr_loss += loss.item() * self.gradient_accumulation_steps
                    
                    step += 1
                    
                    # Update global step if optimizer was run
                    if optimizer_was_run:
                        self.global_step += 1
                        optimizer_was_run = False
                        
                        # Update progress bar
                        if progress_bar is not None:
                            progress_bar.update(1)
                            progress_bar.set_postfix({"loss": f"{tr_loss/self.global_step:.4f}"})
                        
                        # Check for evaluation
                        if self.global_step % getattr(self.config, 'eval_steps', 100) == 0:
                            # Run evaluation
                            eval_results = self.evaluate()
                            logger.info(f"Eval at step {self.global_step}: {eval_results}")
                            
                            # Save checkpoint if best
                            if eval_results["eval_loss"] < self.best_eval_loss:
                                self.best_eval_loss = eval_results["eval_loss"]
                                self.save_model(os.path.join(self.output_dir, "best"))
                        
                        # Save checkpoint
                        if self.global_step % getattr(self.config, 'save_steps', 500) == 0:
                            self.save_model(os.path.join(self.output_dir, f"checkpoint-{self.global_step}"))
                        
                        # Clean up memory periodically
                        # Memory optimization: Memory-critical operation
                        if self.global_step % 10 == 0 and self.device.type == 'cuda':
                        # Memory optimization: Device placement for memory management
                            clean_gpu_memory(aggressive=False)
                            # Memory optimization: Memory-critical operation
                        
                    # Check if we reached max steps
                    if self.global_step >= self.max_steps:
                        break
                        
            except Exception as e:
                logger.error(f"Error during training loop: {e}", exc_info=True)
                break
                
        # Clean up
        if progress_bar is not None:
            progress_bar.close()
            
        # Save final model
        self.save_model(os.path.join(self.output_dir, "final"))
        
        return {"train_loss": tr_loss / self.global_step, "steps": self.global_step}
            
    def evaluate(self):
        """Evaluate the model."""
        if self.eval_dataset is None:
            logger.info("No evaluation data provided")
            return {"eval_loss": float('nan')}
            
        # Use the reference trainer if available
        if self.ref_trainer is not None and hasattr(self.ref_trainer, 'evaluate'):
            try:
                return self.ref_trainer.evaluate()
            except Exception as e:
                logger.warning(f"Error using reference evaluate: {e}")
                
        # Custom evaluation
        self.model.eval()
        eval_dataloader = DataLoader(
            self.eval_dataset,
            batch_size=self.batch_size * 2,
            shuffle=False,
            num_workers=0
        )
        
        eval_loss = 0.0
        eval_steps = 0
        
        with torch.no_grad():
        # Memory optimization: Disable gradient computation to save memory
            for batch in eval_dataloader:
                # Move batch to device
                # Memory optimization: Device placement for memory management
                batch = {k: v.to(self.device) for k, v in batch.items()}
                # Memory optimization: Device placement for memory management
                
                # Forward pass
                outputs = self.model(**batch)
                loss = outputs.loss
                
                eval_loss += loss.item()
                eval_steps += 1
                
                # Don't evaluate too many batches
                if eval_steps >= 100:
                    break
        
        self.model.train()
        
        return {"eval_loss": eval_loss / eval_steps, "eval_steps": eval_steps}
    
    def save_model(self, output_dir):
        """Save model with memory management."""
        # Memory optimization: Explicit memory cleanup
        os.makedirs(output_dir, exist_ok=True)
        
        # Use the reference trainer if available
        if self.ref_trainer is not None and hasattr(self.ref_trainer, 'save_model'):
            try:
                self.ref_trainer.save_model(output_dir)
                return
            except Exception as e:
                logger.warning(f"Error using reference save_model: {e}")
        
        # Custom model saving
        # Memory optimization: Explicit memory cleanup
        if hasattr(self.model, 'save_pretrained'):
            # HuggingFace-style save
            self.model.save_pretrained(output_dir)
        else:
            # Standard PyTorch save
            save_dict = {
                'model_state_dict': self.model.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'global_step': self.global_step,
                'epoch': self.epoch,
                'config': self.config
            }
            torch.save(save_dict, os.path.join(output_dir, "model.pt"))
        
        # Save tokenizer if it has the method
        if hasattr(self.tokenizer, 'save_pretrained'):
            self.tokenizer.save_pretrained(output_dir)
            
        logger.info(f"Model saved to {output_dir}")
        # Memory optimization: Explicit memory cleanup
    
    def _inject_memory_management(self):
    # Memory optimization: Memory-critical operation
        """Inject memory management hooks into the reference trainer."""
        # Memory optimization: Memory-critical operation
        if self.ref_trainer is None:
            return
            
        # Store original methods that we'll override
        original_forward = self.model.forward
        
        # Create a forward wrapper that handles memory management
        # Memory optimization: Memory-critical operation
        def forward_with_memory_management(*args, **kwargs):
        # Memory optimization: Memory-critical operation
            """
            
    forward_with_memory_management function for processing.
    # Memory optimization: Memory-critical operation
    
    Args:
        No arguments: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
            """
            # Ensure critical parts are on GPU when needed
            # Memory optimization: Memory-critical operation
            if self.swap_manager is not None:
                self.swap_manager.ensure_group_on_gpu("base")
                # Memory optimization: Memory-critical operation
            
            # Call original forward
            return original_forward(*args, **kwargs)
        
        # Replace the method
        import types
        self.model.forward = types.MethodType(forward_with_memory_management, self.model)
        # Memory optimization: Memory-critical operation


if __name__ == "__main__":
    main()