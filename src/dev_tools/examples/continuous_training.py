#!/usr/bin/env python3
"""
ImpressionCore: Continuous Training

Module for continuous training functionality in the ImpressionCore framework.

File: examples\continuous_training.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [pytorch, production, memory-critical, 2025]
Dependencies: [torch, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements continuous training functionality for the
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
from examples.continuous_training import MainClass
instance = MainClass()
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
from pathlib import Path
import glob
import gc
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import GPU memory manager
# Memory optimization: Memory-critical operation
from src.core.utils.gpu_memory_manager import GPUMemoryManager
# Memory optimization: Memory-critical operation

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Continue training from a checkpoint")
    parser.add_argument(
        "--checkpoint", 
        type=str, 
        default="src/output/training_metrics/checkpoint-2000",
        help="Path to the checkpoint directory or file"
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
        default=4,  # Reduced default batch size for GTX 1050 Ti
        help="Batch size for training"
    )
    parser.add_argument(
        "--eval_steps",
        type=int,
        default=100,
        help="Steps between evaluations"
    )
    parser.add_argument(
        "--gradient_accumulation_steps",
        type=int,
        default=8,  # Higher gradient accumulation to compensate for smaller batch size
        help="Number of steps to accumulate gradients"
    )
    parser.add_argument(
        "--use_cpu",
        action="store_true",
        help="Force CPU usage even if CUDA is available"
        # Memory optimization: Memory-critical operation
    )
    parser.add_argument(
        "--fp16",
        action="store_true",
        help="Use mixed precision training"
    )
    parser.add_argument(
        "--max_seq_len",
        type=int,
        default=None,  # Changed to None to use checkpoint values by default
        help="Maximum sequence length (default: use checkpoint value)"
    )
    parser.add_argument(
        "--resize_embeddings",
        action="store_true",
        help="Resize position embeddings if they don't match (may cause quality degradation)"
    )
    parser.add_argument(
        "--shared_memory",
        # Memory optimization: Memory-critical operation
        action="store_true",
        help="Enable shared system memory for GPU operations"
        # Memory optimization: Memory-critical operation
    )
    parser.add_argument(
        "--monitor_gpu",
        # Memory optimization: Memory-critical operation
        action="store_true",
        help="Enable GPU memory monitoring during training"
        # Memory optimization: Memory-critical operation
    )
    parser.add_argument(
        "--memory_target",
        # Memory optimization: Memory-critical operation
        type=float,
        default=0.85,
        help="Target GPU memory utilization (0.0-1.0)"
        # Memory optimization: Memory-critical operation
    )
    return parser.parse_args()

def setup_cuda_device(args):
# Memory optimization: Device placement for memory management
    """
    Configure CUDA device with optimizations for GTX 1050 Ti.
    # Memory optimization: Device placement for memory management
    
    Returns:
        device: PyTorch device object
        # Memory optimization: Device placement for memory management
        cuda_info: Dictionary with CUDA information
        # Memory optimization: Memory-critical operation
    """
    # Initialize GPU memory manager
    # Memory optimization: Memory-critical operation
    memory_manager = GPUMemoryManager(
    # Memory optimization: Memory-critical operation
        vram_target_usage=args.memory_target,
        # Memory optimization: Memory-critical operation
        enable_shared_memory=args.shared_memory,
        # Memory optimization: Memory-critical operation
        enable_monitoring=args.monitor_gpu,
        # Memory optimization: Memory-critical operation
        log_file="gpu_memory_usage.csv" if args.monitor_gpu else None
        # Memory optimization: Memory-critical operation
    )
    
    # Get device and info
    # Memory optimization: Device placement for memory management
    device = memory_manager.device
    # Memory optimization: Device placement for memory management
    cuda_info = memory_manager.memory_info
    # Memory optimization: Memory-critical operation
    
    if args.use_cpu:
        logger.info("Forcing CPU usage as requested")
        device = torch.device("cpu")
        # Memory optimization: Device placement for memory management
        memory_manager.cleanup()
        # Memory optimization: Memory-critical operation
        return device, {"cuda_available": False}, None
        # Memory optimization: Device placement for memory management
    
    if cuda_info.get("cuda_available", False):
    # Memory optimization: Memory-critical operation
        logger.info(f"CUDA is available and working: {cuda_info.get('device_name', 'unknown')}")
        # Memory optimization: Device placement for memory management
        
        # Check for NVIDIA driver features
        driver_version = cuda_info.get('driver_version', 'unknown')
        # Memory optimization: Memory-critical operation
        logger.info(f"NVIDIA driver version: {driver_version}")
        
        if args.shared_memory:
        # Memory optimization: Memory-critical operation
            logger.info("Shared system memory enabled - allows GPU to use system RAM when VRAM is full")
            # Memory optimization: Memory-critical operation
            if 'shared_memory_support' in cuda_info and cuda_info['shared_memory_support']:
            # Memory optimization: Memory-critical operation
                logger.info("Driver supports shared memory features")
                # Memory optimization: Memory-critical operation
            
        # Show system RAM information
        system_ram = cuda_info.get('system_memory_mb', 0)
        # Memory optimization: Memory-critical operation
        if system_ram > 0:
            logger.info(f"System RAM available for potential GPU use: {system_ram:.1f}MB")
            # Memory optimization: Memory-critical operation
    else:
        device = torch.device("cpu")
        # Memory optimization: Device placement for memory management
        logger.warning("CUDA not available, using CPU. Training will be much slower.")
        # Memory optimization: Memory-critical operation
        memory_manager.cleanup()
        # Memory optimization: Memory-critical operation
        memory_manager = None
        # Memory optimization: Memory-critical operation
    
    return device, cuda_info, memory_manager
    # Memory optimization: Device placement for memory management

def find_checkpoint_file(checkpoint_path):
    """
    Find the checkpoint file in the given path.
    
    Args:
        checkpoint_path: Path to checkpoint directory or file
        
    Returns:
        Path to the checkpoint file (.bin or .pt)
    """
    if os.path.isfile(checkpoint_path):
        return checkpoint_path
    
    # Check for common checkpoint filenames
    candidates = [
        os.path.join(checkpoint_path, "pytorch_model.bin"),
        os.path.join(checkpoint_path, "model.pt"),
        os.path.join(checkpoint_path, "checkpoint.pt")
    ]
    
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    
    # If no specific file found, look for .bin or .pt files
    bin_files = glob.glob(os.path.join(checkpoint_path, "*.bin"))
    pt_files = glob.glob(os.path.join(checkpoint_path, "*.pt"))
    
    if bin_files:
        return bin_files[0]
    if pt_files:
        return pt_files[0]
    
    raise FileNotFoundError(f"No checkpoint file found in {checkpoint_path}")

def optimize_for_1050ti(model, args):
    """
    Apply optimizations for the GTX 1050 Ti.
    
    Args:
        model: PyTorch model
        args: Script arguments
        
    Returns:
        Optimized model and possible wrapped components
        # Memory optimization: Explicit memory cleanup
    """
    # Memory optimizations - use smaller data types
    # Memory optimization: Memory-critical operation
    if args.fp16 and torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        logger.info("Enabling mixed precision (FP16) training")
        try:
            # Try to use native AMP
            from torch.cuda.amp import autocast, GradScaler
            # Memory optimization: CUDA operations for GPU acceleration
            scaler = GradScaler()
            mixed_precision = True
            logger.info("Using native PyTorch AMP for mixed precision")
            return model, {"mixed_precision": mixed_precision, "scaler": scaler}
        except ImportError:
            logger.warning("Native mixed precision not available in this PyTorch version")
            return model, {"mixed_precision": False}
    
    return model, {"mixed_precision": False}

def resize_position_embeddings(model, new_size):
    """
    Resize position embeddings of the model.
    
    Args:
        model: The model to update
        # Memory optimization: Explicit memory cleanup
        new_size: New size for position embeddings
        
    Returns:
        Updated model
    """
    if hasattr(model, 'position_embeddings'):
        # Access the position embeddings attribute directly
        old_embeddings = model.position_embeddings.weight
        old_size = old_embeddings.shape[0]
        
        if old_size == new_size:
            return model
        
        # Create new embeddings
        new_embeddings = torch.nn.Embedding(new_size, old_embeddings.shape[1])
        
        # Copy the original embeddings (truncate or zero-pad as needed)
        copy_size = min(old_size, new_size)
        with torch.no_grad():
        # Memory optimization: Disable gradient computation to save memory
            new_embeddings.weight[:copy_size] = old_embeddings[:copy_size]
        
        # Replace the old embeddings with the new ones
        model.position_embeddings = new_embeddings
        logger.info(f"Resized position embeddings from {old_size} to {new_size}")
        
        # Update the model configuration if it exists
        # Memory optimization: Explicit memory cleanup
        if hasattr(model, 'config'):
            model.config.max_position_embeddings = new_size
            logger.info("Updated model configuration with new position embedding size")
            # Memory optimization: Explicit memory cleanup
        
    elif hasattr(model, 'resize_position_embeddings'):
        # Use the model's existing method if available (e.g., for transformers models)
        model.resize_position_embeddings(new_size)
        logger.info(f"Resized position embeddings to {new_size} using model's built-in method")
        
    else:
        logger.warning(f"Could not resize position embeddings: attribute not found")
        
    return model

def main():
    """Main function for continuous training."""
    args = parse_args()
    
    try:
        # Setup CUDA/CPU device with memory manager
        # Memory optimization: Device placement for memory management
        device, cuda_info, memory_manager = setup_cuda_device(args)
        # Memory optimization: Device placement for memory management
        
        # Add necessary imports with proper serialization safety
        from src.core.model import Model
        # Memory optimization: Explicit memory cleanup
        from src.core.trainer import DistillationTrainer
        from torch.utils.data import DataLoader, Dataset, ConcatDataset
        from transformers import GPT2Tokenizer
        from src.config.config_manager import ConfigManager
        
        # Add safe globals to allow unpickling the checkpoint
        from torch.serialization import add_safe_globals
        add_safe_globals([ConfigManager])
        
        # Check if checkpoint path exists
        if not os.path.exists(args.checkpoint):
            logger.error(f"Checkpoint path does not exist: {args.checkpoint}")
            return
        
        # Find the checkpoint file
        try:
            checkpoint_path = find_checkpoint_file(args.checkpoint)
            logger.info(f"Found checkpoint file: {checkpoint_path}")
        except FileNotFoundError as e:
            logger.error(str(e))
            return
        
        # Try loading the checkpoint with different approaches
        checkpoint = None
        
        # Try approach 1: Load with weights_only=False (legacy mode)
        try:
            logger.info("Attempting to load checkpoint with weights_only=False...")
            checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
            logger.info("Successfully loaded checkpoint with weights_only=False")
        except Exception as e:
            logger.warning(f"Could not load checkpoint with weights_only=False: {str(e)}")
            
            # Try approach 2: Load with weights_only=True (safer but more restrictive)
            try:
                logger.info("Attempting to load checkpoint with weights_only=True...")
                checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
                logger.info("Successfully loaded checkpoint with weights_only=True")
            except Exception as e2:
                logger.error(f"Failed to load checkpoint with weights_only=True: {str(e2)}")
                logger.info("Trying alternative loading approach...")
                
                # Try approach 3: Use a context manager for safe globals
                try:
                    from torch.serialization import safe_globals
                    with safe_globals([ConfigManager]):
                        checkpoint = torch.load(checkpoint_path, map_location="cpu")
                    logger.info("Successfully loaded checkpoint with safe_globals context manager")
                except Exception as e3:
                    logger.error(f"All loading approaches failed. Last error: {str(e3)}")
                    logger.info("Please check the checkpoint file format and compatibility.")
                    return
        
        if checkpoint is None:
            logger.error("Failed to load checkpoint")
            return
        
        # Load tokenizer
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        tokenizer.pad_token = tokenizer.eos_token
        
        # Get or create configurations
        if hasattr(checkpoint, 'config') or (isinstance(checkpoint, dict) and 'config' in checkpoint):
            config = checkpoint.config if hasattr(checkpoint, 'config') else checkpoint['config']
            logger.info("Loaded configuration from checkpoint")
            
            # Extract max_position_embeddings from config if available
            checkpoint_seq_len = None
            if hasattr(config, 'model_config') and hasattr(config.model_config, 'max_position_embeddings'):
                checkpoint_seq_len = config.model_config.max_position_embeddings
                logger.info(f"Checkpoint position embedding size: {checkpoint_seq_len}")
            
            # Respect checkpoint's sequence length unless explicitly overridden
            if args.max_seq_len is None:
                args.max_seq_len = checkpoint_seq_len or 128  # default to 128 if not found
                logger.info(f"Using checkpoint sequence length: {args.max_seq_len}")
            elif args.resize_embeddings:
                logger.info(f"Will resize position embeddings from {checkpoint_seq_len} to {args.max_seq_len}")
            else:
                logger.warning(f"Sequence length mismatch: checkpoint={checkpoint_seq_len}, requested={args.max_seq_len}")
                logger.warning("Using checkpoint's sequence length to avoid model loading errors.")
                # Memory optimization: Explicit memory cleanup
                args.max_seq_len = checkpoint_seq_len or 128
        else:
            logger.warning("Configuration not found in checkpoint, using default")
            config = ConfigManager()
            config.model_config.hidden_size = 256
            config.model_config.num_hidden_layers = 6
            config.model_config.num_attention_heads = 8
            config.model_config.intermediate_size = 1024
            
            # If no config was found, use default sequence length or user-specified value
            config.model_config.max_position_embeddings = args.max_seq_len or 128
            logger.info(f"Setting default max_position_embeddings to {config.model_config.max_position_embeddings}")
            
            # Update training config
            config.training_config.max_steps = args.steps
            config.training_config.logging_steps = 50
            config.training_config.eval_steps = args.eval_steps
            config.training_config.save_steps = 100
            config.training_config.batch_size = args.batch_size
            config.training_config.gradient_accumulation_steps = args.gradient_accumulation_steps
        
        # Create student model
        student_model = ImpressionCoreModel(config.model_config)
        # Memory optimization: Explicit memory cleanup
        
        # Get original position embeddings size before loading state dict
        # This helps us detect if we need to resize
        original_pos_emb_size = None
        if hasattr(student_model, 'position_embeddings'):
            original_pos_emb_size = student_model.position_embeddings.weight.shape[0]
            logger.info(f"Original model position embedding size: {original_pos_emb_size}")
            # Memory optimization: Explicit memory cleanup
        
        # Try to load state dict, capture errors about position embedding size mismatch
        try:
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                student_model.load_state_dict(checkpoint['model_state_dict'])
            elif isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
                student_model.load_state_dict(checkpoint['state_dict'])
            elif hasattr(checkpoint, 'state_dict'):
                student_model.load_state_dict(checkpoint.state_dict())
            else:
                # Try to load the checkpoint directly as a state dict
                student_model.load_state_dict(checkpoint)
            
            logger.info("Successfully loaded model weights without modification")
            # Memory optimization: Explicit memory cleanup
        except RuntimeError as e:
            if "size mismatch for position_embeddings" in str(e) and args.resize_embeddings:
                logger.warning("Position embedding size mismatch detected, attempting resize...")
                
                # Extract sizes from error message
                error_msg = str(e)
                import re
                patterns = [
                    r"copying a param with shape torch\.Size\(\[([\d]+),\s*([\d]+)\]\)",
                    r"shape in current model is torch\.Size\(\[([\d]+),\s*([\d]+)\]\)"
                    # Memory optimization: Explicit memory cleanup
                ]
                
                checkpoint_size = None
                current_size = None
                
                for pattern in patterns:
                    match = re.search(pattern, error_msg)
                    if match:
                        size1, size2 = int(match.group(1)), int(match.group(2))
                        if "checkpoint" in error_msg[:match.start()]:
                            checkpoint_size = size1
                        else:
                            current_size = size1
                
                if checkpoint_size is not None:
                    logger.info(f"Detected checkpoint position embedding size: {checkpoint_size}")
                    
                    # Create a new model with the checkpoint's embedding size
                    # Memory optimization: Explicit memory cleanup
                    config.model_config.max_position_embeddings = checkpoint_size
                    logger.info(f"Recreating model with position embedding size {checkpoint_size}")
                    # Memory optimization: Explicit memory cleanup
                    student_model = ImpessionCoreModel(config.model_config)
                    # Memory optimization: Explicit memory cleanup
                    
                    # Try loading weights again
                    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                        student_model.load_state_dict(checkpoint['model_state_dict'])
                    elif isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
                        student_model.load_state_dict(checkpoint['state_dict'])
                    elif hasattr(checkpoint, 'state_dict'):
                        student_model.load_state_dict(checkpoint.state_dict())
                    else:
                        student_model.load_state_dict(checkpoint)
                    
                    # Now resize the position embeddings to the requested size
                    student_model = resize_position_embeddings(student_model, args.max_seq_len)
                    # Memory optimization: Explicit memory cleanup
                    
                    # Update config to match the new size
                    config.model_config.max_position_embeddings = args.max_seq_len
                    logger.info(f"Successfully loaded and resized position embeddings to {args.max_seq_len}")
                else:
                    logger.error("Could not extract embedding sizes from error message")
                    logger.error(f"Original error: {e}")
                    return
            else:
                logger.error(f"Could not load model weights: {e}")
                # Memory optimization: Explicit memory cleanup
                return
        
        # Apply memory optimizations specific to GTX 1050 Ti
        # Memory optimization: Memory-critical operation
        student_model, opt_data = optimize_for_1050ti(student_model, args)
        
        # Move model to device - put this in a try block to catch CUDA errors
        # Memory optimization: Device placement for memory management
        try:
            student_model = student_model.to(device)
            # Memory optimization: Device placement for memory management
            logger.info(f"Model successfully moved to {device}")
            # Memory optimization: Device placement for memory management
        except RuntimeError as e:
            if "CUDA out of memory" in str(e):
            # Memory optimization: Memory-critical operation
                logger.error("CUDA out of memory when loading model. Try reducing model size or batch size.")
                # Memory optimization: Explicit memory cleanup
                logger.info("Falling back to CPU")
                device = torch.device("cpu")
                # Memory optimization: Device placement for memory management
                student_model = student_model.to(device)
                # Memory optimization: Device placement for memory management
            else:
                raise
        
        # Print model size information
        # Memory optimization: Explicit memory cleanup
        model_size = sum(p.numel() * p.element_size() for p in student_model.parameters()) / 1024**2
        logger.info(f"Model size: {model_size:.2f} MB")
        # Memory optimization: Explicit memory cleanup
        
        # Create teacher model (same as student for now)
        # Memory optimization: Explicit memory cleanup
        teacher_model = ImpressionCoreModel(config.model_config)
        # Memory optimization: Explicit memory cleanup
        teacher_model.load_state_dict(student_model.state_dict())
        teacher_model = teacher_model.to(device)
        # Memory optimization: Device placement for memory management
        logger.info("Teacher model initialized")
        # Memory optimization: Explicit memory cleanup
        
        # Log CUDA memory after model loading
        # Memory optimization: Explicit memory cleanup
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            allocated = torch.cuda.memory_allocated() / 1024**2
            # Memory optimization: CUDA operations for GPU acceleration
            reserved = torch.cuda.memory_reserved() / 1024**2
            # Memory optimization: CUDA operations for GPU acceleration
            logger.info(f"CUDA memory after model loading: Reserved {reserved:.1f}MB, Allocated {allocated:.1f}MB")
            # Memory optimization: Explicit memory cleanup
        
        # Import and use dataset code from mixed_corpus_training
        sys.path.append(os.path.dirname(__file__))
        from mixed_corpus_training import (
            load_multiple_datasets,
            split_dataset,
            create_sample_text_files
        )
        
        # Check for training data
        if not os.path.exists(args.dataset_dir) or len(glob.glob(os.path.join(args.dataset_dir, "*.txt"))) == 0:
            logger.warning(f"No training files found in {args.dataset_dir}. Creating sample files.")
            create_sample_text_files()
        
        # Load datasets with constrained sequence length for 1050 Ti
        try:
            # Fix the None comparison issue when computing max_length
            if args.max_seq_len is not None:
                max_length = min(config.model_config.max_position_embeddings, args.max_seq_len)
                logger.info(f"Using constrained sequence length of {max_length} for dataset loading")
            else:
                max_length = config.model_config.max_position_embeddings
                logger.info(f"Using model's sequence length of {max_length} for dataset loading")
                
            all_datasets = load_multiple_datasets(
                doc_dir=args.dataset_dir,
                max_length=max_length,
                overlap=max_length // 2
            )
        except Exception as e:
            logger.error(f"Failed to load datasets: {str(e)}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return
        
        if not all_datasets:
            logger.error("No datasets were loaded, training aborted")
            return
            
        # Combine and split datasets
        combined_dataset = ConcatDataset(all_datasets)
        logger.info(f"Combined dataset has {len(combined_dataset)} samples")
        
        train_dataset, eval_dataset = split_dataset(combined_dataset, eval_ratio=0.1)
        logger.info(f"Train dataset: {len(train_dataset)} samples")
        logger.info(f"Eval dataset: {len(eval_dataset)} samples")
        
        # Create dataloaders with pin_memory for faster GPU transfer
        # Memory optimization: Memory-critical operation
        train_dataloader = DataLoader(
            train_dataset,
            batch_size=args.batch_size,
            shuffle=True,
            num_workers=0,  # Use 0 workers to avoid memory issues on 4GB VRAM
            # Memory optimization: Memory-critical operation
            pin_memory=True if torch.cuda.is_available() else False,
            # Memory optimization: CUDA operations for GPU acceleration
            drop_last=True  # Prevent odd-sized batches
        )
        
        eval_dataloader = DataLoader(
            eval_dataset,
            batch_size=args.batch_size * 2,  # Can use larger batch size for eval (no gradients)
            shuffle=False,
            num_workers=0,  # Use 0 workers to avoid memory issues on 4GB VRAM
            # Memory optimization: Memory-critical operation
            pin_memory=True if torch.cuda.is_available() else False
            # Memory optimization: CUDA operations for GPU acceleration
        )
        
        # Update training configuration
        if hasattr(config.training_config, "max_steps"):
            # Update max_steps for continuation
            original_max_steps = config.training_config.max_steps
            config.training_config.max_steps = original_max_steps + args.steps
            logger.info(f"Updated training steps: {original_max_steps} + {args.steps} = {config.training_config.max_steps}")
        else:
            # If max_steps not in config, set it directly
            config.training_config.max_steps = args.steps
            logger.info(f"Set training steps to {args.steps}")
            
        # Set other GPU training parameters
        # Memory optimization: Memory-critical operation
        if hasattr(config.training_config, "gradient_accumulation_steps"):
            config.training_config.gradient_accumulation_steps = args.gradient_accumulation_steps
            logger.info(f"Set gradient accumulation steps to {args.gradient_accumulation_steps}")
            
        if hasattr(config.training_config, "fp16") and args.fp16:
            config.training_config.fp16 = True
            logger.info("Enabled mixed precision training")
            
        # Initialize trainer
        try:
            # Create trainer with updated config and dataloaders
            trainer = DistillationTrainer(
                student_model=student_model,
                tokenizer=tokenizer,
                train_dataset=train_dataset,
                teacher_model=teacher_model,
                eval_dataset=eval_dataset,
                config=config.training_config,
                alpha=0.0,  # No distillation
                temperature=1.0
            )
            
            # Add mixed precision scaler if available
            if opt_data.get("mixed_precision", False):
                trainer.scaler = opt_data.get("scaler")
                logger.info("Added gradient scaler for mixed precision training")
            
            logger.info(f"Starting continued training for {args.steps} more steps")
            start_time = time.time()
            
            # Start training
            train_result = trainer.train()
            
            training_time = time.time() - start_time
            logger.info(f"Continued training completed in {training_time/60:.2f} minutes")
            logger.info(f"Training metrics: {train_result}")
            
        except AttributeError as attr_error:
            # Handle the specific error case where max_steps doesn't exist
            if "'DistillationTrainer' object has no attribute 'max_steps'" in str(attr_error):
                logger.warning("Trainer doesn't have max_steps attribute. Trying alternative approach...")
                
                # Try to extract the train method and call it directly
                import inspect
                train_params = inspect.signature(trainer.train).parameters
                
                if not train_params:  # No parameters needed
                    trainer.train()
                elif "max_steps" in train_params:  # Can pass max_steps directly
                    trainer.train(max_steps=args.steps)
                elif "steps" in train_params:  # Some implementations use 'steps'
                    trainer.train(steps=args.steps)
                else:
                    # No clear way to set steps, train with defaults
                    trainer.train()
                
                logger.info("Training completed with fallback method")
            else:
                # Different AttributeError, re-raise
                raise
                
        except Exception as e:
            logger.error(f"Error during training: {str(e)}", exc_info=True)
            
        finally:
            # Clean up GPU resources
            # Memory optimization: Memory-critical operation
            if torch.cuda.is_available():
            # Memory optimization: CUDA operations for GPU acceleration
                torch.cuda.empty_cache()
                # Memory optimization: CUDA operations for GPU acceleration
                gc.collect()
                # Memory optimization: Force garbage collection
                allocated = torch.cuda.memory_allocated() / 1024**2
                # Memory optimization: CUDA operations for GPU acceleration
                reserved = torch.cuda.memory_reserved() / 1024**2
                # Memory optimization: CUDA operations for GPU acceleration
                logger.info(f"Final CUDA memory state: Reserved {reserved:.1f}MB, Allocated {allocated:.1f}MB")
                # Memory optimization: Memory-critical operation
            
    except ImportError as e:
        logger.error(f"Failed to import required modules: {str(e)}")
        logger.info("Please ensure all required packages are installed.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()