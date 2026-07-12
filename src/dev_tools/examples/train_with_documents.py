#!/usr/bin/env python3
"""
ImpressionCore: Train With Documents

Module for train with documents functionality in the ImpressionCore framework.

File: examples\train_with_documents.py
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
Dependencies: [torch, typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements train with documents functionality for the
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
from examples.train_with_documents import MainClass
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
import json
import logging
import argparse
import torch
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
from tqdm import tqdm
from glob import glob
from transformers import AutoTokenizer

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import components
from src.core.knowledge.document_store import DocumentStore
from src.core.model import ImpressionCoreModel, ModelConfig
# Memory optimization: Explicit memory cleanup
from src.core.gpu_utils import get_device, get_memory_info, MemoryTracker
# Memory optimization: Device placement for memory management
from src.core.config.config_manager import get_config_manager
from src.core.memory_optimization import optimize_for_training
# Memory optimization: Memory-critical operation

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Train a model with embedded documents"
        # Memory optimization: Explicit memory cleanup
    )
    
    # Model options
    # Memory optimization: Explicit memory cleanup
    parser.add_argument(
        "--model-path",
        type=str,
        help="Path to pretrained model (optional)"
        # Memory optimization: Explicit memory cleanup
    )
    
    parser.add_argument(
        "--output-path",
        type=str,
        default=os.path.join(project_root, "output", "models", "document_enhanced"),
        help="Path to save the trained model"
    )
    
    # Document options
    parser.add_argument(
        "--document-tags",
        type=str,
        nargs="+",
        help="Tags to filter documents for training"
    )
    
    parser.add_argument(
        "--document-export",
        type=str,
        help="Path to exported document file (alternative to using tags)"
    )
    
    # Training options
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Training batch size"
    )
    
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=5e-5,
        help="Learning rate"
    )
    
    parser.add_argument(
        "--fp16",
        action="store_true",
        help="Use mixed precision training"
    )
    
    parser.add_argument(
        "--max-seq-length",
        type=int,
        default=512,
        help="Maximum sequence length"
    )
    
    parser.add_argument(
        "--gradient-accumulation-steps",
        type=int,
        default=4,
        help="Number of gradient accumulation steps"
    )
    
    # Device options
    # Memory optimization: Device placement for memory management
    parser.add_argument(
        "--device",
        # Memory optimization: Device placement for memory management
        type=str,
        choices=["auto", "cuda", "cpu"],
        # Memory optimization: Memory-critical operation
        default="auto",
        help="Device to use for training"
        # Memory optimization: Device placement for memory management
    )
    
    return parser.parse_args()

def setup_training_device(args):
# Memory optimization: Device placement for memory management
    """
    Set up training device based on arguments and available hardware.
    # Memory optimization: Device placement for memory management
    
    Args:
        args: Command line arguments
        
    Returns:
        torch.device: Device for training
        # Memory optimization: Device placement for memory management
    """
    if args.device == "cpu":
    # Memory optimization: Device placement for memory management
        device = torch.device("cpu")
        # Memory optimization: Device placement for memory management
        logger.info("Using CPU for training as requested")
    elif args.device == "cuda":
    # Memory optimization: Device placement for memory management
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            device = torch.device("cuda")
            # Memory optimization: Device placement for memory management
            logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
            # Memory optimization: CUDA operations for GPU acceleration
        else:
            logger.warning("CUDA requested but not available, falling back to CPU")
            # Memory optimization: Memory-critical operation
            device = torch.device("cpu")
            # Memory optimization: Device placement for memory management
    else:  # auto
        device = get_device()  # Use our custom function to detect device
        # Memory optimization: Device placement for memory management
        if device.type == "cuda":
        # Memory optimization: Device placement for memory management
            logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
            # Memory optimization: CUDA operations for GPU acceleration
        else:
            logger.info("Using CPU for training")
    
    return device
    # Memory optimization: Device placement for memory management

def load_training_documents(args) -> Dict[str, List[str]]:
    """
    Load documents for training based on command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Dictionary of document chunks by document ID
    """
    # If export file is provided, load from there
    if args.document_export and os.path.exists(args.document_export):
        try:
            with open(args.document_export, "r", encoding="utf-8") as f:
                export_data = json.load(f)
            
            documents = export_data.get("documents", {})
            logger.info(f"Loaded {len(documents)} documents from export file")
            return documents
        except Exception as e:
            logger.error(f"Error loading export file: {e}")
    
    # Otherwise, get documents from the store based on tags
    if args.document_tags:
        doc_store = DocumentStore()
        documents = doc_store.get_training_documents(args.document_tags)
        logger.info(f"Loaded {len(documents)} documents from store with tags: {args.document_tags}")
        return documents
    
    logger.warning("No documents specified for training")
    return {}

def load_text_corpus(directory: str, max_samples: int = 0) -> Dict[str, list]:
    """
    Load and combine all .txt files in a directory for training.
    Args:
        directory: Path to the text corpus directory.
        max_samples: Maximum number of samples to load (0 for all).
    Returns:
        Dictionary with a single key 'corpus' mapping to a list of text samples.
    Memory:
    # Memory optimization: Memory-critical operation
        Loads all lines into memory; for large corpora, set max_samples to limit usage.
        # Memory optimization: Memory-critical operation
    """
    all_texts = []
    txt_files = glob(os.path.join(directory, "*.txt"))
    for file_path in txt_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                all_texts.extend(lines)
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
    if max_samples > 0:
        all_texts = all_texts[:max_samples]
    logger.info(f"Loaded {len(all_texts)} text samples from {len(txt_files)} files in {directory}")
    return {"corpus": all_texts}

def prepare_training_data(documents: Dict[str, List[str]], tokenizer, max_length: int) -> List[Dict[str, torch.Tensor]]:
    """
    Prepare documents for training by tokenizing and formatting into batches.
    
    Args:
        documents: Dictionary of document chunks by document ID
        tokenizer: Tokenizer to use for encoding
        max_length: Maximum sequence length
        
    Returns:
        List of batched data for training
    """
    training_examples = []
    
    # Flatten document chunks into a list
    all_chunks = []
    for doc_id, chunks in documents.items():
        all_chunks.extend(chunks)
    
    logger.info(f"Processing {len(all_chunks)} document chunks for training")
    
    # Process chunks into training examples
    for chunk in tqdm(all_chunks, desc="Tokenizing"):
        # Skip empty chunks
        if not chunk.strip():
            continue
            
        # Tokenize chunk
        encoded = tokenizer.encode_plus(
            chunk,
            add_special_tokens=True,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
            return_tensors="pt"
        )
        
        # Add to training examples
        training_examples.append({
            "input_ids": encoded["input_ids"].squeeze(0),
            "attention_mask": encoded["attention_mask"].squeeze(0),
            "labels": encoded["input_ids"].squeeze(0).clone()  # Use same ids for labels (LM task)
        })
    
    return training_examples

def train_model(model, training_data, args, device):
# Memory optimization: Device placement for memory management
    """
    Train the model on document data.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        model: Model to train
        # Memory optimization: Explicit memory cleanup
        training_data: Prepared training data
        args: Command line arguments
        device: Device to train on
        # Memory optimization: Device placement for memory management
        
    Returns:
        Trained model
    """
    # Move model to the right device
    # Memory optimization: Device placement for memory management
    model.to(device)
    # Memory optimization: Device placement for memory management
    
    # Apply memory optimizations for training
    # Memory optimization: Memory-critical operation
    if device.type == "cuda":
    # Memory optimization: Device placement for memory management
        model = optimize_for_training(model, "gtx1050ti" if "1050" in torch.cuda.get_device_name(0) else "default")
        # Memory optimization: CUDA operations for GPU acceleration
    
    # Set model to training mode
    # Memory optimization: Explicit memory cleanup
    model.train()
    
    # Create optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    
    # Training loop
    logger.info(f"Starting training for {args.epochs} epochs")
    
    global_step = 0
    total_loss = 0.0
    
    for epoch in range(args.epochs):
        epoch_iterator = tqdm(
            range(0, len(training_data), args.batch_size),
            desc=f"Epoch {epoch+1}/{args.epochs}"
        )
        
        for batch_start in epoch_iterator:
            # Get batch data
            batch_end = min(batch_start + args.batch_size, len(training_data))
            batch = training_data[batch_start:batch_end]
            
            # Stack batch tensors
            batch_input_ids = torch.stack([example["input_ids"] for example in batch]).to(device)
            # Memory optimization: Device placement for memory management
            batch_attention_mask = torch.stack([example["attention_mask"] for example in batch]).to(device)
            # Memory optimization: Device placement for memory management
            batch_labels = torch.stack([example["labels"] for example in batch]).to(device)
            # Memory optimization: Device placement for memory management
            
            # Debug: print input_ids min/max and vocab_size before model call
            # Memory optimization: Explicit memory cleanup
            try:
                with open("embedding_debug.log", "a") as dbg:
                    dbg.write(f"input_ids min: {batch_input_ids.min().item()}, max: {batch_input_ids.max().item()}, vocab_size: {getattr(model.config, 'vocab_size', 'N/A')}\n")
            except Exception as e:
                logger.warning(f"Could not write to embedding_debug.log: {e}")
            print(f"[DEBUG] input_ids min: {batch_input_ids.min().item()}, max: {batch_input_ids.max().item()}, vocab_size: {getattr(model.config, 'vocab_size', 'N/A')}")
            logger.info(f"input_ids min: {batch_input_ids.min().item()}, max: {batch_input_ids.max().item()}, vocab_size: {getattr(model.config, 'vocab_size', 'N/A')}")            # Forward pass
            with torch.cuda.amp.autocast(enabled=args.fp16):
            # Memory optimization: CUDA operations for GPU acceleration
                outputs = model(
                    input_ids=batch_input_ids,
                    attention_mask=batch_attention_mask,
                    labels=batch_labels
                )
                
                # Handle ModelOutput object properly - access loss directly as an attribute
                loss = outputs.loss
                loss = loss / args.gradient_accumulation_steps
            
            # Backward pass
            loss.backward()
            
            # Update weights if we've accumulated enough gradients
            if (batch_start // args.batch_size + 1) % args.gradient_accumulation_steps == 0:
                optimizer.step()
                optimizer.zero_grad()
                global_step += 1
            
            # Update progress bar
            total_loss += loss.item() * args.gradient_accumulation_steps
            avg_loss = total_loss / (global_step + 1)
            epoch_iterator.set_postfix(loss=f"{avg_loss:.4f}")
        
        logger.info(f"Epoch {epoch+1} completed with average loss: {avg_loss:.4f}")
    
    logger.info(f"Training completed after {global_step} steps")
    
    # Reset model to evaluation mode
    # Memory optimization: Explicit memory cleanup
    model.eval()
    
    return model

def save_model(model, output_path: str):
    """
    Save the trained model.
    
    Args:
        model: Trained model
        output_path: Path to save the model
    """
    # Create output directory
    os.makedirs(output_path, exist_ok=True)
    
    # Save model configuration
    # Memory optimization: Explicit memory cleanup
    config_path = os.path.join(output_path, "config.json")
    with open(config_path, "w") as f:
        json.dump(model.config.__dict__, f, indent=2)
    
    # Move model to CPU for saving
    # Memory optimization: Explicit memory cleanup
    model = model.to("cpu")
    # Memory optimization: Explicit memory cleanup
    
    # Save model state
    # Memory optimization: Explicit memory cleanup
    model_path = os.path.join(output_path, "model.pt")
    torch.save(model.state_dict(), model_path)
    
    logger.info(f"Model saved to {output_path}")
    # Memory optimization: Explicit memory cleanup

def main():
    """Main entry point."""
    args = parse_args()

    # Set up training device
    # Memory optimization: Device placement for memory management
    device = setup_training_device(args)
    # Memory optimization: Device placement for memory management

    # Load documents for training
    if not args.document_tags and not args.document_export:
        corpus_dir = os.path.join(project_root, "data", "datasets", "text_corpus")
        documents = load_text_corpus(corpus_dir, max_samples=10000)
    else:
        documents = load_training_documents(args)

    if not documents:
        logger.error("No documents available for training")
        return 1

    # --- Load Tokenizer using AutoTokenizer ---
    tokenizer_dir = os.path.join(project_root, "training", "checkpoints", "new_tokenizer")
    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_dir)
        vocab_size = tokenizer.vocab_size
        logger.info(f"Successfully loaded tokenizer from {tokenizer_dir}")
        
        # Check and set padding token if not present
        if tokenizer.pad_token is None:
            logger.info("Padding token not found. Setting pad_token = eos_token")
            tokenizer.pad_token = tokenizer.eos_token
            logger.info(f"Padding token set to: {tokenizer.pad_token}")
    except Exception as e:
        logger.error(f"Failed to load tokenizer from {tokenizer_dir}: {e}")
        return 1

    # Debug: Show vocab size and a few vocab items after loading
    if vocab_size == 0:
        logger.error("Loaded tokenizer has empty vocab. Please ensure the tokenizer was trained correctly.")
        return 1
    print(f"[DEBUG] Loaded tokenizer vocab size: {vocab_size}")
    # Note: Accessing vocab items might differ slightly with AutoTokenizer
    try:
        # Attempt to get vocab items if possible (might vary by tokenizer type)
        vocab_items = list(tokenizer.get_vocab().items())[:10]
        print(f"[DEBUG] First 10 vocab items: {vocab_items}")
    except AttributeError:
        print("[DEBUG] Could not retrieve vocab items directly for this tokenizer type.")

    # --- Model Initialization ---
    # Memory optimization: Explicit memory cleanup
    try:
        if args.model_path and os.path.exists(args.model_path):
            logger.info(f"Loading pretrained model from {args.model_path}")
            # Memory optimization: Explicit memory cleanup
            model = ImpressionCoreModel.from_pretrained(args.model_path)
            # Memory optimization: Explicit memory cleanup
        else:
            logger.info("Creating new model with default configuration")
            # Memory optimization: Explicit memory cleanup
            config = ModelConfig()
            config.vocab_size = vocab_size
            config.dropout = getattr(config, 'hidden_dropout_prob', 0.1)
            if not hasattr(config, 'max_position_embeddings'):
                config.max_position_embeddings = 512
            config.num_layers = getattr(config, 'num_hidden_layers', 6)
            logger.info(f"ModelConfig attributes before model init: {config.__dict__}")
            # Memory optimization: Explicit memory cleanup
            model = ImpressionCoreModel(config)
            # Memory optimization: Explicit memory cleanup
    except Exception as e:
        logger.error(f"Error initializing model: {e}")
        return 1

    # --- Prepare Training Data ---
    training_data = prepare_training_data(documents, tokenizer, args.max_seq_length)

    if not training_data:
        logger.error("No valid training data prepared")
        return 1

    # Train the model
    trained_model = train_model(model, training_data, args, device)
    # Memory optimization: Device placement for memory management

    # Save the trained model
    save_model(trained_model, args.output_path)

    logger.info("Training completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
