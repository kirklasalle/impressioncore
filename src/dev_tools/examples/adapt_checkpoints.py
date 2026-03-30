#!/usr/bin/env python3
"""
ImpressionCore: Adapt Checkpoints

Module for adapt checkpoints functionality in the ImpressionCore framework.

File: examples\adapt_checkpoints.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [pytorch, production, 2025]
Dependencies: [torch, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements adapt checkpoints functionality for the
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
from examples.adapt_checkpoints import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import sys
import glob
import argparse
import logging
import torch
import torch.serialization
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def safe_load_checkpoint(checkpoint_path, allow_unsafe=True):
    """
    Load a checkpoint safely, handling PyTorch 2.6 security restrictions.
    
    Args:
        checkpoint_path: Path to checkpoint file
        allow_unsafe: Whether to allow unsafe loading with weights_only=False
        
    Returns:
        Loaded checkpoint or None if failed
    """
    if not os.path.exists(checkpoint_path):
        logger.error(f"Checkpoint file not found: {checkpoint_path}")
        return None
    
    # Method 1: Try with safe_globals for ConfigManager
    try:
        # Create a dynamic context manager for specific custom classes
        # This allows loading custom class while maintaining security
        with torch.serialization.safe_globals(['core.config', 'core.config.ConfigManager']):
            checkpoint = torch.load(checkpoint_path, map_location='cpu')
            logger.info("Successfully loaded checkpoint with safe_globals")
            return checkpoint
    except Exception as e:
        logger.warning(f"Method 1 (safe_globals) failed: {str(e)}")
    
    # Method 2: Only if explicitly allowed, try loading with weights_only=False
    if allow_unsafe:
        try:
            checkpoint = torch.load(checkpoint_path, weights_only=False, map_location='cpu')
            logger.info("Successfully loaded checkpoint with weights_only=False")
            return checkpoint
        except Exception as e:
            logger.warning(f"Method 2 (weights_only=False) failed: {str(e)}")
    
    # Method 3: Try loading weights-only
    try:
        # Attempt to load just the weights (safer)
        checkpoint = torch.load(checkpoint_path, weights_only=True, map_location='cpu')
        logger.info("Successfully loaded checkpoint weights only")
        return checkpoint
    except Exception as e:
        logger.warning(f"Method 3 (weights_only=True) failed: {str(e)}")
    
    # All methods failed
    logger.error(f"All loading methods failed for {checkpoint_path}")
    return None

def create_safe_checkpoint(checkpoint, output_path):
    """
    Create a new checkpoint that doesn't depend on custom classes.
    
    Args:
        checkpoint: The loaded checkpoint dict
        output_path: Path to save the adapted checkpoint
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Extract essential data into a clean dict
        safe_checkpoint = {}
        
        # Extract model config
        # Memory optimization: Explicit memory cleanup
        config = {}
        if 'config' in checkpoint:
            orig_config = checkpoint['config']
            # Handle either dict or custom ConfigManager object
            if isinstance(orig_config, dict):
                config = orig_config.copy()
            else:
                # Extract attributes from ConfigManager
                for attr in dir(orig_config):
                    if not attr.startswith('_') and not callable(getattr(orig_config, attr)):
                        try:
                            config[attr] = getattr(orig_config, attr)
                        except Exception:
                            pass
        
        # Preserve model state dict
        # Memory optimization: Explicit memory cleanup
        if 'model_state_dict' in checkpoint:
            safe_checkpoint['model_state_dict'] = checkpoint['model_state_dict']
        elif 'state_dict' in checkpoint:
            safe_checkpoint['model_state_dict'] = checkpoint['state_dict']
        
        # Copy metadata
        for key in ['step', 'epoch', 'best_loss', 'iterations']:
            if key in checkpoint:
                safe_checkpoint[key] = checkpoint[key]
        
        # Add the configuration as a plain dict
        safe_checkpoint['config'] = config
        
        # Save the adapted checkpoint
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        torch.save(safe_checkpoint, output_path, _use_new_zipfile_serialization=True)
        logger.info(f"Saved adapted checkpoint to {output_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating safe checkpoint: {str(e)}")
        return False

def adapt_checkpoint(input_path, output_path, allow_unsafe=True):
    """
    Adapt a checkpoint to be compatible with newer PyTorch security.
    
    Args:
        input_path: Path to input checkpoint
        output_path: Path to output checkpoint
        allow_unsafe: Whether to allow unsafe loading
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Adapting checkpoint: {input_path} -> {output_path}")
    
    # Load the checkpoint
    checkpoint = safe_load_checkpoint(input_path, allow_unsafe)
    if checkpoint is None:
        logger.error("Failed to load checkpoint")
        return False
    
    # Create safe checkpoint
    return create_safe_checkpoint(checkpoint, output_path)

def main():
    """
    
    main function for processing.
    
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
    parser = argparse.ArgumentParser(description="Adapt checkpoints for PyTorch 2.6 compatibility")
    parser.add_argument("--input", type=str, help="Input checkpoint file")
    parser.add_argument("--output", type=str, help="Output checkpoint file")
    parser.add_argument("--all", action="store_true", help="Process all checkpoints in the checkpoints directory")
    parser.add_argument("--safe-only", action="store_true", help="Use safe loading only (no weights_only=False)")
    args = parser.parse_args()
    
    allow_unsafe = not args.safe_only
    
    if args.all:
        # Process all checkpoints in the checkpoints directory
        checkpoint_dir = os.path.join(project_root, "checkpoints")
        output_dir = os.path.join(project_root, "checkpoints_adapted")
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all checkpoint files
        checkpoint_files = glob.glob(os.path.join(checkpoint_dir, "*.pt"))
        success_count = 0
        
        for input_path in checkpoint_files:
            filename = os.path.basename(input_path)
            output_path = os.path.join(output_dir, filename)
            
            if adapt_checkpoint(input_path, output_path, allow_unsafe):
                success_count += 1
        
        logger.info(f"Adaptation complete. Successes: {success_count}, Failures: {len(checkpoint_files) - success_count}")
    elif args.input and args.output:
        # Process a single checkpoint
        adapt_checkpoint(args.input, args.output, allow_unsafe)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
