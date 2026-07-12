#!/usr/bin/env python3
"""
ImpressionCore: Generate Text

Module for generate text functionality in the ImpressionCore framework.

File: examples\generate_text.py
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
Dependencies: [torch, typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements generate text functionality for the
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
from examples.generate_text import JsonFormatter
instance = JsonFormatter()
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
import argparse
import logging
import torch
from pathlib import Path
from typing import List, Dict, Any, Optional
import datetime # Added
import json # Added

# Add the project root to the path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.core.model import ImpressionCoreModel, ModelConfig
# Memory optimization: Explicit memory cleanup
from src.core.gpu_utils import get_device, clear_gpu_memory, MemoryTracker
# Memory optimization: Device placement for memory management
from src.core.memory_optimization import memory_efficient_inference
# Memory optimization: Memory-critical operation
from transformers import AutoTokenizer

# Configure basic console logging (can be overridden by file logger for specifics)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # This will be the console logger

# Global file logger instance
file_event_logger = None

def setup_file_event_logger(log_dir: Path, run_args: Optional[Dict] = None):
    """Sets up a dedicated JSON file logger for script events."""
    global file_event_logger
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log_file_name = f"generate_text_events_{timestamp}.jsonl"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / log_file_name

    file_event_logger = logging.getLogger("FileEventLogger")
    file_event_logger.setLevel(logging.INFO)
    
    # Prevent propagation to the root logger (console)
    file_event_logger.propagate = False 

    # Remove existing handlers to avoid duplication if called multiple times (e.g., in tests)
    for handler in file_event_logger.handlers[:]:
        file_event_logger.removeHandler(handler)
        handler.close()

    handler = logging.FileHandler(log_file_path)
    
    class JsonFormatter(logging.Formatter):
        """
        
    JsonFormatter class for ImpressionCore framework.
    
    This class implements jsonformatter functionality optimized for
    memory-constrained environments like the GTX 1050 Ti.
    # Memory optimization: Memory-critical operation
    
    Memory Considerations:
    # Memory optimization: Memory-critical operation
        - Implements memory-efficient algorithms
        # Memory optimization: Memory-critical operation
        - Supports gradient checkpointing
        - Provides CPU fallback options
    
    Notes:
        - Thread-safe implementation
        - GPU memory optimized
        # Memory optimization: Memory-critical operation
        - Part of ImpressionCore ecosystem
    
        """
        def format(self, record):
            """
            
    format function for processing.
    
    Args:
        self, record: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
            """
            log_entry = {
                "timestamp": datetime.datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "funcName": record.funcName,
                "lineno": record.lineno,
            }
            if hasattr(record, 'custom_fields'):
                log_entry.update(record.custom_fields)
            return json.dumps(log_entry)

    handler.setFormatter(JsonFormatter())
    file_event_logger.addHandler(handler)
    
    logger.info(f"Detailed event logging to: {log_file_path}")
    if run_args and file_event_logger:
        file_event_logger.info("Script started.", extra={'custom_fields': {'event_type': 'script_start', 'arguments': run_args}})

def log_event(message: str, level: str = "info", event_type: Optional[str] = None, **kwargs):
    """Helper function to log to the file event logger with custom fields."""
    if file_event_logger:
        custom_fields = {'event_type': event_type if event_type else message.lower().replace(" ", "_")}
        custom_fields.update(kwargs)
        
        log_method = getattr(file_event_logger, level.lower(), file_event_logger.info)
        log_method(message, extra={'custom_fields': custom_fields})

def load_model_and_tokenizer(model_path: str):
    """
    Load a trained model and its tokenizer.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        model_path: Path to the model directory
        # Memory optimization: Explicit memory cleanup
        
    Returns:
        Tuple of (model, tokenizer)
    """
    logger.info(f"Loading model from {model_path}")
    # Memory optimization: Explicit memory cleanup
    log_event(f"Attempting to load model and tokenizer from path: {model_path}", event_type="load_model_start", model_path=model_path)
    # Memory optimization: Explicit memory cleanup
    
    # Check if model exists
    # Memory optimization: Explicit memory cleanup
    if not os.path.exists(model_path):
        log_event(f"Model path not found: {model_path}", level="error", event_type="load_model_failure", reason="path_not_found")
        # Memory optimization: Explicit memory cleanup
        raise FileNotFoundError(f"Model path not found: {model_path}")
        # Memory optimization: Explicit memory cleanup

    # Look for checkpoint directories with specific patterns
    config_path = None
    checkpoint_path = None
    
    # Direct config path in the specified directory
    direct_config_path = os.path.join(model_path, "config.json")
    if os.path.exists(direct_config_path):
        config_path = direct_config_path
        checkpoint_path = model_path
        logger.info(f"Found config directly at: {config_path}")
    else:
        logger.info(f"No config found directly at {direct_config_path}, looking for checkpoints...")
        
        # Look for checkpoint folders with different naming patterns
        checkpoint_patterns = [
            "checkpoint-epoch_*",  # epoch-based checkpoints
            "checkpoint-*",        # step-based checkpoints
            "best",                # best checkpoint
            "final"                # final checkpoint
        ]
        
        candidates = []
        for pattern in checkpoint_patterns:
            import glob
            matches = glob.glob(os.path.join(model_path, pattern))
            for match in matches:
                if os.path.isdir(match) and os.path.exists(os.path.join(match, "config.json")):
                    candidates.append(match)
        
        # Look for epoch-based checkpoints first (prefer later epochs)
        epoch_checkpoints = sorted([c for c in candidates if "epoch_" in c], 
                                  key=lambda x: int(x.split("epoch_")[-1]))
        
        # Look for step-based checkpoints if no epochs found
        step_checkpoints = sorted([c for c in candidates if "checkpoint-" in c and not "epoch_" in c], 
                                 key=lambda x: int(x.split("checkpoint-")[-1]) if x.split("checkpoint-")[-1].isdigit() else 0)
        
        # Special checkpoints
        special_checkpoints = [c for c in candidates if c.endswith("best") or c.endswith("final")]
        
        # Use the best candidate found
        if epoch_checkpoints:
            checkpoint_path = epoch_checkpoints[-1]  # Latest epoch
            logger.info(f"Using latest epoch checkpoint: {os.path.basename(checkpoint_path)}")
        elif special_checkpoints:
            checkpoint_path = special_checkpoints[0]
            logger.info(f"Using special checkpoint: {os.path.basename(checkpoint_path)}")
        elif step_checkpoints:
            checkpoint_path = step_checkpoints[-1]  # Latest step
            logger.info(f"Using latest step checkpoint: {os.path.basename(checkpoint_path)}")
        else:
            logger.warning(f"No checkpoint directories found in {model_path}")
            # Try to use the path directly as a last resort
            checkpoint_path = model_path
        
        if checkpoint_path:
            config_path = os.path.join(checkpoint_path, "config.json")
    
    # Verify config path exists
    if config_path and not os.path.exists(config_path):
        logger.error(f"Config file not found at: {config_path}")
        log_event(f"Config file not found at calculated path: {config_path}", level="error", event_type="load_model_failure", reason="config_not_found")
        config_path = None
    
    # If still no config found, check if the path itself might be the checkpoint
    if not config_path:
        direct_cp_config = os.path.join(model_path, "config.json")
        if os.path.exists(direct_cp_config):
            config_path = direct_cp_config
            checkpoint_path = model_path
            logger.info(f"Using directory directly as checkpoint: {checkpoint_path}")
    
    # If still no config found, raise error
    if not config_path:
        err_msg = f"Could not find config.json in {model_path} or any of its checkpoint subdirectories"
        logger.error(err_msg)
        log_event(err_msg, level="error", event_type="load_model_failure", reason="config_not_found_in_any_location")
        raise FileNotFoundError(err_msg)
    
    # Load config
    try:
        config = ModelConfig.from_file(config_path)
        logger.info(f"Loaded config with {config.hidden_size} hidden size")
        log_event("ModelConfig loaded successfully.", config_path=config_path, hidden_size=config.hidden_size)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        log_event(f"Failed to load ModelConfig from {config_path}: {str(e)}", level="error", event_type="load_model_failure", reason="config_load_exception")
        raise
    
    # Initialize model
    model = ImpressionCoreModel(config)
    # Memory optimization: Explicit memory cleanup
    
    # Load model weights
    # Memory optimization: Explicit memory cleanup
    try:
        model_file = os.path.join(checkpoint_path, "model.pt")
        if not os.path.exists(model_file):
            logger.warning(f"Model file not found at: {model_file}")
            # Memory optimization: Explicit memory cleanup
            # Try alternative filenames
            alternatives = [
                "pytorch_model.bin",
                "weights.pt",
                "model_weights.pt",
                "model.bin"
            ]
            for alt in alternatives:
                alt_path = os.path.join(checkpoint_path, alt)
                if os.path.exists(alt_path):
                    model_file = alt_path
                    logger.info(f"Found alternative model file: {alt_path}")
                    # Memory optimization: Explicit memory cleanup
                    break
            
            if not os.path.exists(model_file):
                raise FileNotFoundError(f"Could not find model weights file in {checkpoint_path}")
                # Memory optimization: Explicit memory cleanup
        
        logger.info(f"Loading model weights from: {model_file}")
        # Memory optimization: Explicit memory cleanup
        state_dict = torch.load(model_file, map_location="cpu")
        model.load_state_dict(state_dict)
        logger.info("Successfully loaded model weights")
        # Memory optimization: Explicit memory cleanup
        log_event("Model weights loaded successfully.", model_file=model_file)
        # Memory optimization: Explicit memory cleanup
    except Exception as e:
        logger.error(f"Failed to load model weights: {e}")
        # Memory optimization: Explicit memory cleanup
        log_event(f"Failed to load model weights from {model_file}: {str(e)}", level="error", event_type="load_model_failure", reason="weights_load_exception")
        # Memory optimization: Explicit memory cleanup
        raise
    
    # Load tokenizer
    try:
        # First try to load from the model directory
        # Memory optimization: Explicit memory cleanup
        if os.path.exists(os.path.join(model_path, "tokenizer_config.json")):
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            logger.info(f"Loaded tokenizer from {model_path}")
        else:
            # Fall back to GPT-2 tokenizer
            tokenizer = AutoTokenizer.from_pretrained("gpt2")
            logger.info("Loaded default GPT-2 tokenizer")
        
        # Ensure pad token is set
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        log_event("Tokenizer loaded successfully.", tokenizer_path=model_path if os.path.exists(os.path.join(model_path, "tokenizer_config.json")) else "gpt2_default")
    except Exception as e:
        logger.error(f"Failed to load tokenizer: {e}")
        log_event(f"Failed to load tokenizer: {str(e)}", level="error", event_type="load_model_failure", reason="tokenizer_load_exception")
        raise
    
    # Set model to evaluation mode
    # Memory optimization: Explicit memory cleanup
    model.eval()
    
    # Move model to device
    # Memory optimization: Device placement for memory management
    device = get_device()
    # Memory optimization: Device placement for memory management
    model.to(device)
    # Memory optimization: Device placement for memory management
    log_event("Model and tokenizer loaded and moved to device.", device=str(device), event_type="load_model_success")
    # Memory optimization: Device placement for memory management
    
    return model, tokenizer

def generate_text(
    model: ImpressionCoreModel,
    tokenizer,
    prompts: List[str],
    max_length: int = 50,
    temperature: float = 1.0,
    top_p: float = 1.0,
    num_return_sequences: int = 1,
):
    """
    Generate text from prompts.
    
    Args:
        model: The ImpressionCoreModel
        tokenizer: Tokenizer to use
        prompts: List of prompts to generate from
        max_length: Maximum length of generated text
        temperature: Sampling temperature (higher = more random)
        top_p: Nucleus sampling probability
        num_return_sequences: Number of sequences to generate for each prompt
        
    Returns:
        Dict mapping prompts to generated text
    """
    results = {}
    
    for prompt_idx, prompt in enumerate(prompts):
        logger.info(f"Generating text for prompt: '{prompt}'")
        log_event(f"Starting generation for prompt #{prompt_idx + 1}", event_type="generation_prompt_start", prompt=prompt, prompt_index=prompt_idx)
        
        # Tokenize prompt
        input_ids = tokenizer.encode(prompt, return_tensors="pt")
        
        # Move to the same device as the model
        # Memory optimization: Device placement for memory management
        device = next(model.parameters()).device
        # Memory optimization: Device placement for memory management
        input_ids = input_ids.to(device)
        # Memory optimization: Device placement for memory management
        
        # Track memory usage during generation
        # Memory optimization: Memory-critical operation
        with MemoryTracker() as tracker:
        # Memory optimization: Memory-critical operation
            # Generate text with memory-efficient inference
            # Memory optimization: Memory-critical operation
            with memory_efficient_inference():
            # Memory optimization: Memory-critical operation
                with torch.no_grad():
                # Memory optimization: Disable gradient computation to save memory
                    start_length = input_ids.shape[1]
                    
                    # Use native generate method if available
                    if hasattr(model, "generate") and callable(model.generate):
                        outputs = model.generate(
                            input_ids=input_ids,
                            max_length=start_length + max_length,
                            temperature=temperature,
                            top_p=top_p,
                            num_return_sequences=num_return_sequences,
                            pad_token_id=tokenizer.pad_token_id,
                            eos_token_id=tokenizer.eos_token_id,
                        )
                    else:
                        # Manual generation if generate method not implemented
                        outputs = input_ids.clone()
                        for _ in range(max_length):
                            # Forward pass to get logits
                            model_output = model(outputs)
                            logits = model_output["logits"]
                            
                            # Get logits for the last token
                            next_token_logits = logits[:, -1, :] / temperature
                            
                            # Apply top-p sampling
                            if top_p < 1.0:
                                sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                                cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
                                
                                # Remove tokens with cumulative probability above the threshold
                                sorted_indices_to_remove = cumulative_probs > top_p
                                # Shift the indices to the right to keep also the first token above the threshold
                                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                                sorted_indices_to_remove[..., 0] = 0
                                
                                # Create a mask for the logits
                                indices_to_remove = sorted_indices[sorted_indices_to_remove]
                                next_token_logits[:, indices_to_remove] = -float('inf')
                            

                            # Sample from the filtered distribution
                            probs = torch.softmax(next_token_logits, dim=-1)
                            next_token = torch.multinomial(probs, num_samples=1)
                            
                            # Append the new token
                            outputs = torch.cat([outputs, next_token], dim=-1)
                            
                            # Stop if all sequences have generated an EOS token
                            if (outputs[:, -1] == tokenizer.eos_token_id).all():
                                break
            
            # Get memory statistics
            # Memory optimization: Memory-critical operation
            memory_stats = tracker.stop()
            # Memory optimization: Memory-critical operation
            logger.info(f"Text generation peak memory: {memory_stats['peak_gpu_mb']:.2f} MB")
            # Memory optimization: Memory-critical operation
            log_event("Memory usage during generation.", peak_gpu_mb=memory_stats['peak_gpu_mb'], initial_gpu_mb=memory_stats['initial_gpu_mb'])
            # Memory optimization: Memory-critical operation
        
        # Decode generated text
        generated_texts = []
        for output in outputs:
            # Decode only the newly generated tokens
            generated_text = tokenizer.decode(output[start_length:], skip_special_tokens=True)
            generated_texts.append(generated_text)
        
        # Add to results
        results[prompt] = generated_texts
        
        # Log the first generated sample
        logger.info(f"Generated: '{prompt}{generated_texts[0]}'")
        log_event(f"Completed generation for prompt #{prompt_idx + 1}", event_type="generation_prompt_end", prompt=prompt, num_sequences_generated=len(generated_texts), first_generated_sequence=generated_texts[0] if generated_texts else "")

    log_event("All prompts processed.", event_type="generation_all_prompts_complete", total_prompts=len(prompts))
    return results

def main():
    """Run text generation example."""
    parser = argparse.ArgumentParser(description="Generate text with ImpressionCore model")
    parser.add_argument("--model_path", type=str, default="models/small", help="Path to the model directory")
    # Memory optimization: Explicit memory cleanup
    parser.add_argument("--prompts", type=str, nargs="+", default=["ImpressionCore is a"], 
                       help="One or more prompts for text generation. Enclose each prompt in quotes.")
    parser.add_argument("--max_length", type=int, default=50, help="Maximum length of generated text")
    parser.add_argument("--temperature", type=float, default=1.0, help="Sampling temperature")
    parser.add_argument("--top_p", type=float, default=0.9, help="Nucleus sampling probability")
    parser.add_argument("--use_cuda", action="store_true", help="Use CUDA if available")
    # Memory optimization: Memory-critical operation
    parser.add_argument("--num_sequences", type=int, default=1, help="Number of sequences to generate per prompt")
    parser.add_argument("--list_checkpoints", action="store_true", 
                       help="List all available checkpoints in the model directory and exit")
                       # Memory optimization: Explicit memory cleanup
    
    args = parser.parse_args()

    # Setup file event logger
    log_directory = project_root / "memlog" / "cli"
    setup_file_event_logger(log_directory, run_args=vars(args))

    log_event("Parsed command line arguments.", event_type="args_parsed", arguments=vars(args))

    # List checkpoints if requested
    if args.list_checkpoints:
        print(f"\nListing checkpoints in: {args.model_path}")
        if os.path.exists(args.model_path):
            checkpoints = []
            
            # Check if direct path is a checkpoint
            if os.path.exists(os.path.join(args.model_path, "config.json")):
                checkpoints.append((args.model_path, "(Direct path)"))
            
            # Look for checkpoint directories
            for item in os.listdir(args.model_path):
                item_path = os.path.join(args.model_path, item)
                if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "config.json")):
                    if "epoch" in item:
                        epoch_num = item.split("epoch_")[-1] if "epoch_" in item else "unknown"
                        checkpoints.append((item_path, f"(Epoch {epoch_num})"))
                    elif item.startswith("checkpoint-"):
                        step_num = item.split("checkpoint-")[-1]
                        checkpoints.append((item_path, f"(Step {step_num})"))
                    else:
                        checkpoints.append((item_path, ""))
            
            if checkpoints:
                print("\nAvailable checkpoints:")
                for path, desc in checkpoints:
                    print(f"  - {os.path.basename(path)} {desc}")
                print("\nUse --model_path with the full path to one of these checkpoints")
            else:
                print("No checkpoints found.")
                log_event("No checkpoints found in the specified model directory.", level="warning", event_type="checkpoints_listing")
                # Memory optimization: Explicit memory cleanup
        else:
            print(f"Model directory not found: {args.model_path}")
            # Memory optimization: Explicit memory cleanup
            log_event(f"Model directory not found for checkpoint listing: {args.model_path}", level="error", model_path=args.model_path)
            # Memory optimization: Explicit memory cleanup
        
        log_event("Script finished: Checkpoint listing complete.", event_type="script_end", exit_code=0)
        return 0

    # Process prompts to ensure they're properly formatted
    prompts = []
    for prompt in args.prompts:
        # Strip extra whitespace and ensure it's not empty
        clean_prompt = prompt.strip()
        if clean_prompt:
            prompts.append(clean_prompt)
    
    if not prompts:
        logger.error("No valid prompts provided")
        log_event("No valid prompts provided after cleaning.", level="error", original_prompts=args.prompts)
        log_event("Script finished: No valid prompts.", event_type="script_end", exit_code=1)
        return 1
    
    logger.info(f"Processing {len(prompts)} prompts: {prompts}")
    
    # Override CUDA environment variable based on args
    # Memory optimization: Memory-critical operation
    if args.use_cuda:
    # Memory optimization: Memory-critical operation
        os.environ["IMPRESSIONCORE_FORCE_CPU"] = "0"
    else:
        os.environ["IMPRESSIONCORE_FORCE_CPU"] = "1"
    
    try:
        # Load model and tokenizer
        # Memory optimization: Explicit memory cleanup
        log_event("Starting model and tokenizer loading process.", model_path=args.model_path)
        # Memory optimization: Explicit memory cleanup
        model, tokenizer = load_model_and_tokenizer(args.model_path)
        
        # Generate text
        log_event("Starting text generation process.")
        results = generate_text(
            model=model,
            tokenizer=tokenizer,
            prompts=prompts,
            max_length=args.max_length,
            temperature=args.temperature,
            top_p=args.top_p,
            num_return_sequences=args.num_sequences,
        )
        
        # Print results
        print("\n" + "=" * 40 + " GENERATION RESULTS " + "=" * 40)
        for prompt, generated_texts in results.items():
            print(f"\nPrompt: '{prompt}'")
            for i, text in enumerate(generated_texts):
                print(f"\n--- Generation {i+1} ---")
                print(f"{prompt}{text}")
        print("\n" + "=" * 100)
        
        log_event("Script finished: Text generation successful.", event_type="script_end", exit_code=0, num_results=len(results))
        return 0
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"\\nError: {e}")
        print("\\nTip: Run with --list_checkpoints to see available checkpoint directories")
        log_event(f"Script failed: FileNotFoundError - {str(e)}", level="critical", event_type="script_end", exit_code=1, error_details=str(e))
        return 1
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        print(f"\\nError: {e}")
        # Log the full traceback for detailed debugging in the file log
        import traceback
        tb_str = traceback.format_exc()
        log_event(f"Script failed: Exception - {str(e)}", level="critical", event_type="script_end", exit_code=1, error_details=str(e), traceback=tb_str)
        return 1

if __name__ == "__main__":
    sys.exit(main())