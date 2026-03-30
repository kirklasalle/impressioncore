#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-24-2025
**Author:** Kirk LaSalle
**Tags:** #api #command_line #cuda #gpu_optimization #inference #memory_management #multimodal #python #source_code #src/main.py #training
**Category:** Source Code
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** Kirk LaSalle
# Tags:** #api #command_line #cuda #gpu_optimization #inference #memory_management #multimodal #python #source_code #src/main.py #training
# Category:** Source Code
# Status:** Active

"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: main.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-25
Modified: 2025-05-25
Version: 1.0.0

Authors:
- Kirk LaSalle & GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [script]
Dependencies: [] # TODO: Auto-detect or allow manual input
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
# TODO: Add a brief description of this file's purpose.

Design Philosophy:
# TODO: Add design philosophy if applicable.

Memory Considerations:
# TODO: Document any specific memory considerations for this file.

Examples:
# TODO: Provide usage examples if applicable.

Notes:
# TODO: Add any relevant notes.

Main entry point for ImpressionCore.

This script provides a command-line interface for ImpressionCore
capabilities including tokenization, model inference, and more.
"""

import argparse
import datetime  # Added for timestamps
import json  # Added for JSON logging
import logging
import os
import sys
import time  # Added for duration calculation
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parent.resolve()
# Always use the directory containing main.py as src_path
src_path = PROJECT_ROOT
# sys.path.insert(0, str(PROJECT_ROOT)) # Add project root to allow imports like from src.core...
# sys.path.insert(0, str(src_path)) # Add src to allow direct imports from modules within src

# Ensure src_path is at the beginning of sys.path if not already there
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# Debugging: Log the sys.path
_initial_logger = logging.getLogger("main_initial")
_initial_logger.info(f"Initial sys.path: {sys.path}")
_initial_logger.info(f"PROJECT_ROOT: {PROJECT_ROOT}")
_initial_logger.info(f"src_path: {src_path}")


# --- Structured JSONL Event Logging for main.py ---
MEMLOG_CLI_DIR = src_path / "memlog" / "cli"
MEMLOG_CLI_DIR.mkdir(parents=True, exist_ok=True)

LOG_ID_MAIN = f"main_cli_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
EVENT_LOG_FILE_MAIN = MEMLOG_CLI_DIR / f"{LOG_ID_MAIN}.jsonl"
file_event_logger_main = None

def setup_file_event_logger_main():
    global file_event_logger_main
    file_event_logger_main = logging.getLogger(f"FileEventLogger_Main_{LOG_ID_MAIN}")
    file_event_logger_main.setLevel(logging.INFO)
    file_event_logger_main.propagate = False # Prevent propagation to console logger

    for handler in file_event_logger_main.handlers[:]:
        file_event_logger_main.removeHandler(handler)
        handler.close()

    fh = logging.FileHandler(EVENT_LOG_FILE_MAIN)
    fh.setLevel(logging.INFO)
    file_event_logger_main.addHandler(fh)

def log_event_main(event_type, status, details=None, error_message=None, duration_ms=None):
    if file_event_logger_main is None:
        setup_file_event_logger_main() # Ensure logger is initialized

    log_entry = {
        "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "log_id": LOG_ID_MAIN,
        "source_script": "main.py",
        "event_type": event_type,
        "status": status, # "success", "failure", "progress", "info"
        "details": details or {},
    }
    if error_message:
        log_entry["error_message"] = error_message
    if duration_ms is not None:
        log_entry["duration_ms"] = duration_ms

    if file_event_logger_main:
        file_event_logger_main.info(json.dumps(log_entry))
    else:
        # Fallback if logger somehow isn't initialized
        with open(EVENT_LOG_FILE_MAIN, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

# --- End Structured JSONL Event Logging ---

# Debugging: Log the sys.path
logger = logging.getLogger(__name__) # This will be replaced by rich logger later
log_event_main("initialization", "progress", {"message": "Script started", "sys_path": sys.path})

# Debugging: Check if the 'src' directory exists
if not os.path.exists(src_path):
    logger.error(f"'src' directory not found at: {src_path}")
    logger.error("Please ensure the 'src' directory exists in the project root.")
    log_event_main("initialization", "failure", {"path_checked": str(src_path)}, error_message="'src' directory not found")
    sys.exit(1)
else:
    logger.info(f"'src' directory found at: {src_path}")
    log_event_main("initialization", "info", {"message": "'src' directory found", "path": str(src_path)})

# Debugging: List contents of the 'src' directory
try:
    src_contents = os.listdir(src_path)
    logger.info(f"Contents of 'src' directory: {src_contents}")
    log_event_main("initialization", "info", {"message": "Listed 'src' contents", "contents": src_contents})
except Exception as e:
    logger.error(f"Error accessing 'src' directory: {e}")
    log_event_main("initialization", "failure", {"path_accessed": str(src_path)}, error_message=f"Error accessing 'src' directory: {e}")
    sys.exit(1)


# --- Robust directory check for required subdirectories ---
from pathlib import Path

required_structure = ["core", "training"]
# Normalize src_contents to lower-case names for comparison, and check as Path objects
src_dir = Path(src_path)
src_entries = {}
for entry in src_dir.iterdir():
    entry_type = 'dir' if entry.is_dir() else 'file' if entry.is_file() else 'other'
    logger.info(f"[Debug] Entry: {entry.name} | Path: {entry.resolve()} | Type: {entry_type} | is_dir: {entry.is_dir()}")
    src_entries[entry.name.lower()] = entry
missing_structure = []
for req in required_structure:
    entry = src_entries.get(req.lower())
    if not entry:
        logger.error(f"[Debug] Required entry '{req}' not found in src_entries. Keys: {list(src_entries.keys())}")
        missing_structure.append(req)
    elif not entry.is_dir():
        logger.error(f"[Debug] Required entry '{req}' found but is not a directory. Path: {entry.resolve()} | is_dir: {entry.is_dir()}")
        missing_structure.append(req)

logger.info(f"[Robust Check] src/ entries found: {list(src_entries.keys())}")
if missing_structure:
    logger.error(f"[Robust Check] Missing required directories in 'src': {missing_structure}")
    logger.error("Please ensure the 'src' directory contains the required structure.")
    log_event_main("initialization", "failure", {"missing_structure": missing_structure, "src_entries": list(src_entries.keys())}, error_message="Missing required directories in 'src'")
    sys.exit(1)

# Check for models and tokenization in training directory
training_path = os.path.join(src_path, "training")
if os.path.exists(training_path):
    training_contents = os.listdir(training_path)
    if "models" not in training_contents:
        logger.warning("Models directory not found in training/")
    if "tokenization.py" not in training_contents:
        logger.warning("Tokenization module not found in training/")
else:
    logger.error("Training directory not found in src/")
    sys.exit(1)

# Check for required dependencies
try:
    import numpy as np
    import torch
    from PIL import Image
    log_event_main("dependency_check", "success", {"dependencies": ["torch", "numpy", "PIL"]})
except ImportError as e:
    logger.error(f"Missing required dependency: {e}")
    logger.error("Please install the required dependencies using 'pip install -r requirements.txt'.")
    log_event_main("dependency_check", "failure", {"dependency_error": str(e)}, error_message=f"Missing required dependency: {e}")
    sys.exit(1)

# Set up rich logging and enhancements
try:
    from core.utils.rich_enhancements import (  # noqa: F401
        create_header,
        print_error,
        print_info,
        print_success,
        print_warning,
    )
    from core.utils.rich_logging import setup_rich_logging
    logger = setup_rich_logging(__name__)
    create_header("ImpressionCore CLI")
    print_info("Rich logging and enhancements enabled.")
    log_event_main("rich_setup", "success", {"message": "Rich logging and enhancements enabled."})
except ImportError as e:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.warning(f"Rich logging/enhancements not available: {e}")
    log_event_main("rich_setup", "failure", {"message": "Rich logging/enhancements not available"}, error_message=str(e))

try:
    # Import core modules that are available in your project structure
    from core.brain.modal_engine import ModalityType  # noqa: F401
    from core.utils.hardware_detection import get_system_info, optimize_for_hardware  # noqa: F401
    from dev_tools.evaluation.core_evaluator import start_evaluation

    # from models.memory_controller import get_memory_controller # SystemMonitor/API might handle aspects of this
    from interfaces.cli.model_management import define_model_from_config
    from training.core_trainer import start_training
    # from core.api_instance import ImpressionCoreAPI # Import the actual API when available
    log_event_main("core_module_import", "success", {"modules": ["ModalityType", "hardware_detection", "model_management", "core_trainer", "core_evaluator"]})

    # --- Advanced Utilities Import (Optional) ---
    advanced_utils_available = False
    advanced_utils_error = None
    try:
        from core.ai.multimodal.core import AdvancedMultimodalEngine  # noqa: F401
        from core.ai.multimodal.dev_tools import AdvancedDevTools  # noqa: F401
        advanced_utils_available = True
        log_event_main("advanced_utilities_import", "success", {"modules": ["AdvancedMultimodalEngine", "AdvancedDevTools"]})
    except ImportError as e:
        advanced_utils_error = str(e)
        logger.warning(f"⚠️  Advanced utilities not available - using fallbacks: {e}")
        log_event_main("advanced_utilities_import", "failure", {"error": advanced_utils_error})

except ImportError as e:
    logger.error(f"Error importing dependencies: {e}")
    logger.error("Ensure the 'src' directory is correctly structured and contains the required modules.")
    log_event_main("core_module_import", "failure", {"import_error": str(e)}, error_message=f"Error importing dependencies: {e}")
    sys.exit(1)

class ImpressionCoreAPI:
    """Production-grade API for CLI interactions, wrapping UnifiedBrainTriad and utilities."""
    def __init__(self, config_path: str = "src/core/src/core/config/triad_config.json"):
        from src.orchestrator.system_logger import sys_logger
        from src.orchestrator.unified_triad import UnifiedBrainTriad

        self.triad = UnifiedBrainTriad(config_path)
        self.tokenizer = self.triad.tokenizer
        self.sys_logger = sys_logger
        logger.info("ImpressionCoreAPI initialized with UnifiedBrainTriad")

    def get_system_monitor(self):
        # The triad instance has hardware status methods
        return self.triad

    def get_project_root(self):
        return str(PROJECT_ROOT)

    def tokenize(self, content: Union[str, torch.Tensor], modality: str):
        """Tokenize content using the actual Triad tokenizer."""
        if modality == "text":
            if not isinstance(content, str):
                raise ValueError("Text modality requires string content")
            return self.tokenizer.encode(content)
        elif modality == "image":
            # For images, the Triad uses the Multimodal Processor
            if self.triad.processor:
                # We return a dummy list for CLI compatibility, but log the shape
                import torch
                if isinstance(content, torch.Tensor):
                    logger.info(f"Tokenizing image tensor of shape {content.shape}")
                return [0, 1, 2] # CLI expects a list
            raise ValueError("Multimodal processor not available for image tokenization")
        return []

    def detokenize(self, token_ids: list[int], modality: str):
        """Detokenize tokens back into human-readable format."""
        if modality == "text":
            return self.tokenizer.decode(token_ids, skip_special_tokens=True)
        return "Detokenization for non-text modalities not yet implemented in CLI."

def init_api(args):
    """Initialize the API based on command-line arguments."""
    log_event_main("api_initialization", "progress", {"args": vars(args)})
    start_time = time.perf_counter()

    # Instantiate the actual ImpressionCoreAPI
    # The API's constructor will initialize the SystemMonitor.
    # Project root is inferred by ImpressionCoreAPI if not provided.
    api_instance = ImpressionCoreAPI()

    # Log initial hardware info and resource usage via the API's system monitor
    system_monitor = api_instance.get_system_monitor()
    if system_monitor:
        system_monitor.get_hardware_info() # Logs internally
        system_monitor.log_resource_usage(force_log=True, context_message="CLI Initialization")

    # Arguments like --lite-engine or --disable-memory-optimizations
    # would ideally be handled by API config or methods.
    # For now, we rely on SystemMonitor's default behavior or its own config.
    # If specific CLI args need to influence SystemMonitor behavior not covered by its config,
    # we might need to add methods to ImpressionCoreAPI or SystemMonitor to adjust settings post-init.
    # Example:
    # if args.disable_memory_optimizations:
    #     logger.info("Memory optimizations explicitly disabled by CLI argument.")
    #     # Potentially: api_instance.get_system_monitor().configure_optimizations(enabled=False)

    duration_ms = (time.perf_counter() - start_time) * 1000
    log_event_main("api_initialization", "success",
                   {"api_class": type(api_instance).__name__,
                    "project_root": api_instance.get_project_root()},
                   duration_ms=duration_ms)
    return api_instance

def handle_tokenize(args, api):
    """Handle tokenize command.
    Args:
        args: Parsed command-line arguments.
        api: ImpressionCoreAPI instance.
    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    log_event_main("command_handle", "progress", {"command": "tokenize", "args": vars(args)})
    start_time = time.perf_counter()
    try:
        if args.modality == "text":
            # Read input
            if args.input_file:
                try:
                    with open(args.input_file, encoding='utf-8') as f:
                        content = f.read()
                    log_event_main("tokenize_text_input", "success", {"source": "file", "file_path": args.input_file, "content_length": len(content)})
                except Exception as e:
                    logger.error(f"Failed to read input file: {e}")
                    log_event_main("tokenize_text_input", "failure", {"source": "file", "file_path": args.input_file}, error_message=str(e), duration_ms=(time.perf_counter() - start_time) * 1000)
                    return 1
            else:
                content = args.content
                if not content:
                    logger.error("No content provided for text tokenization.")
                    log_event_main("tokenize_text_input", "failure", {"source": "argument"}, error_message="No content provided", duration_ms=(time.perf_counter() - start_time) * 1000)
                    return 1
                log_event_main("tokenize_text_input", "success", {"source": "argument", "content_length": len(content)})
            # Tokenize
            token_ids = api.tokenize(content, args.modality)
            # Output
            if args.output_file:
                try:
                    # Assuming core.ai.tokenization.converter is available
                    from core.ai.tokenization.converter import save_token_ids
                    save_token_ids(token_ids, args.output_file)
                    logger.info(f"Saved {len(token_ids)} tokens to {args.output_file}")
                    log_event_main("tokenize_text_output", "success", {"destination": "file", "file_path": args.output_file, "token_count": len(token_ids)})
                except Exception as e:
                    logger.error(f"Failed to save tokens: {e}")
                    log_event_main("tokenize_text_output", "failure", {"destination": "file", "file_path": args.output_file}, error_message=str(e))
                    # Continue to command failure log
            else:
                print(f"Tokens: {token_ids[:10]}... (total: {len(token_ids)})")
                log_event_main("tokenize_text_output", "success", {"destination": "console", "token_count": len(token_ids)})
        elif args.modality == "image":
            if not args.input_file:
                logger.error("Input file required for image tokenization")
                log_event_main("tokenize_image_input", "failure", error_message="Input file required", duration_ms=(time.perf_counter() - start_time) * 1000)
                return 1
            try:
                image = Image.open(args.input_file).convert("RGB")
                img_array = np.array(image)
                img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).float() / 255.0
                log_event_main("tokenize_image_input", "success", {"file_path": args.input_file, "image_size": image.size, "tensor_shape": list(img_tensor.shape)})
            except Exception as e:
                logger.error(f"Failed to load or process image: {e}")
                log_event_main("tokenize_image_input", "failure", {"file_path": args.input_file}, error_message=str(e), duration_ms=(time.perf_counter() - start_time) * 1000)
                return 1
            # Tokenize
            token_ids = api.tokenize(img_tensor, args.modality)
            # Output
            if args.output_file:
                try:
                    from core.ai.tokenization.converter import save_token_ids
                    save_token_ids(token_ids, args.output_file)
                    logger.info(f"Saved {len(token_ids)} tokens to {args.output_file}")
                    log_event_main("tokenize_image_output", "success", {"destination": "file", "file_path": args.output_file, "token_count": len(token_ids)})
                except Exception as e:
                    logger.error(f"Failed to save tokens: {e}")
                    log_event_main("tokenize_image_output", "failure", {"destination": "file", "file_path": args.output_file}, error_message=str(e))
                    # Continue to command failure log
            else:
                print(f"Tokens: {token_ids[:10]}... (total: {len(token_ids)})")
                log_event_main("tokenize_image_output", "success", {"destination": "console", "token_count": len(token_ids)})
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_event_main("command_handle", "success", {"command": "tokenize"}, duration_ms=duration_ms)
        return 0
    except Exception as e:
        logger.error(f"Unexpected error in handle_tokenize: {e}")
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_event_main("command_handle", "failure", {"command": "tokenize"}, error_message=str(e), duration_ms=duration_ms)
        return 1

def handle_detokenize(args, api):
    """Handle detokenize command.
    Args:
        args: Parsed command-line arguments.
        api: ImpressionCoreAPI instance.
    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    log_event_main("command_handle", "progress", {"command": "detokenize", "args": vars(args)})
    start_time = time.perf_counter()
    try:
        try:
            # Assuming core.ai.tokenization.converter is available
            from core.ai.tokenization.converter import load_token_ids
            token_ids = load_token_ids(args.input_file)
            log_event_main("detokenize_input", "success", {"file_path": args.input_file, "token_count": len(token_ids)})
        except Exception as e:
            logger.error(f"Failed to load token IDs: {e}")
            log_event_main("detokenize_input", "failure", {"file_path": args.input_file}, error_message=str(e), duration_ms=(time.perf_counter() - start_time) * 1000)
            return 1
        # Detokenize
        content = api.detokenize(token_ids, args.modality)
        if args.modality == "text":
            if args.output_file:
                try:
                    with open(args.output_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"Saved text to {args.output_file}")
                    log_event_main("detokenize_text_output", "success", {"destination": "file", "file_path": args.output_file})
                except Exception as e:
                    logger.error(f"Failed to save text: {e}")
                    log_event_main("detokenize_text_output", "failure", {"destination": "file", "file_path": args.output_file}, error_message=str(e))
                    # Continue to command failure log
            else:
                print("\nDetokenized text:")
                print(content)
                log_event_main("detokenize_text_output", "success", {"destination": "console"})
        elif args.modality == "image":
            if not args.output_file:
                logger.error("Output file required for image detokenization")
                log_event_main("detokenize_image_output", "failure", error_message="Output file required for image detokenization", duration_ms=(time.perf_counter() - start_time) * 1000)
                return 1
            try:
                image_array = (content.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
                image = Image.fromarray(image_array)
                image.save(args.output_file)
                logger.info(f"Saved image to {args.output_file}")
                log_event_main("detokenize_image_output", "success", {"destination": "file", "file_path": args.output_file})
            except Exception as e:
                logger.error(f"Failed to save image: {e}")
                log_event_main("detokenize_image_output", "failure", {"destination": "file", "file_path": args.output_file}, error_message=str(e))
                # Continue to command failure log
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_event_main("command_handle", "success", {"command": "detokenize"}, duration_ms=duration_ms)
        return 0
    except Exception as e:
        logger.error(f"Unexpected error in handle_detokenize: {e}")
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_event_main("command_handle", "failure", {"command": "detokenize"}, error_message=str(e), duration_ms=duration_ms)
        return 1

def main_cli_entry(): # Renamed to avoid conflict with module-level 'main' name if any confusion
    """Main function."""
    setup_file_event_logger_main() # Initialize file logger at the start of main
    log_event_main("script_execution", "progress", {"script_name": "main.py", "status": "started"})
    main_start_time = time.perf_counter()

    parser = argparse.ArgumentParser(description="ImpressionCore CLI")

    # Global options - these might influence API/SystemMonitor initialization or behavior
    parser.add_argument("--lite-engine", action="store_true",
                      help="Hint to use memory-efficient LiteModalEngine (if applicable in API)")
    parser.add_argument("--disable-memory-optimizations", action="store_true",
                      help="Hint to disable memory efficiency optimizations (if applicable in API/SystemMonitor)")

    # Subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Tokenize command
    tokenize_parser = subparsers.add_parser("tokenize", help="Tokenize content")
    tokenize_parser.add_argument("--modality", choices=["text", "image"], default="text",
                              help="Content modality")
    tokenize_parser.add_argument("--input-file", help="Input file (required for image)")
    tokenize_parser.add_argument("--output-file", help="Output file for tokens")
    tokenize_parser.add_argument("--content", help="Text content to tokenize")

    # Detokenize command
    detokenize_parser = subparsers.add_parser("detokenize", help="Detokenize tokens")
    detokenize_parser.add_argument("--modality", choices=["text", "image"], required=True,
                               help="Content modality")
    detokenize_parser.add_argument("--input-file", required=True,
                               help="Input file containing tokens")
    detokenize_parser.add_argument("--output-file",
                               help="Output file for content (required for image)")

    # Define Model command
    define_model_parser = subparsers.add_parser("define_model", help="Define/load a model architecture from a configuration file.")
    define_model_parser.add_argument("--config", required=True, help="Path to the model architecture YAML configuration file (e.g., configs/impressioncore_b1_arch.yaml)")

    # Train Model command
    train_model_parser = subparsers.add_parser("train_model", help="Train a model using a specified training configuration.")
    train_model_parser.add_argument("--config", required=True, help="Path to the training YAML configuration file (e.g., configs/impressioncore_b1_train.yaml)")

    # Evaluate Model command
    evaluate_model_parser = subparsers.add_parser("evaluate_model", help="Evaluate a trained model using a specified evaluation configuration and checkpoint.")
    evaluate_model_parser.add_argument("--config", required=True, help="Path to the evaluation YAML configuration file (e.g., configs/impressioncore_b1_eval.yaml)")
    evaluate_model_parser.add_argument("--checkpoint", help="Optional: Path to a specific model checkpoint (.pth file) to evaluate. Overrides checkpoint_path in config if provided.")


    # Parse arguments
    args = parser.parse_args()
    log_event_main("argument_parsing", "success", {"parsed_args": vars(args)})

    if not args.command:
        parser.print_help()
        log_event_main("script_execution", "info", {"message": "No command provided, printing help."}, duration_ms=(time.perf_counter() - main_start_time) * 1000)
        # Ensure logs are flushed before exiting
        if file_event_logger_main:
            for handler in file_event_logger_main.handlers[:]:
                handler.flush()
                handler.close()
                file_event_logger_main.removeHandler(handler)
        return 0

    # Initialize API - this now uses the new ImpressionCoreAPI
    api = init_api(args)
    system_monitor = api.get_system_monitor() if api else None

    # Execute command
    exit_code = 1 # Default to error
    if args.command == "tokenize":
        if system_monitor:
            system_monitor.log_resource_usage(force_log=True, context_message="Before Tokenize")
        exit_code = handle_tokenize(args, api)
        if system_monitor:
            system_monitor.log_resource_usage(force_log=True, context_message="After Tokenize")
    elif args.command == "detokenize":
        if system_monitor:
            system_monitor.log_resource_usage(force_log=True, context_message="Before Detokenize")
        exit_code = handle_detokenize(args, api)
        if system_monitor:
            system_monitor.log_resource_usage(force_log=True, context_message="After Detokenize")
    elif args.command == "define_model":
        log_event_main("command_handle", "progress", {"command": "define_model", "args": vars(args)})
        start_time = time.perf_counter()
        if system_monitor:
            system_monitor.log_resource_usage(force_log=True, context_message="Before Define Model")
        try:
            # Pass api instance for potential future use (e.g. path resolution, logging)
            model_config = define_model_from_config(args.config, api)
            if model_config:
                print_success(f"Model architecture '{model_config.get('model_name', 'Unknown Model')}' version {model_config.get('version', 'N/A')} processed.")
                duration_ms = (time.perf_counter() - start_time) * 1000
                log_event_main("command_handle", "success", {"command": "define_model", "config_path": args.config}, duration_ms=duration_ms)
                exit_code = 0
            else:
                print_error(f"Failed to process model architecture from {args.config}.")
                duration_ms = (time.perf_counter() - start_time) * 1000
                log_event_main("command_handle", "failure", {"command": "define_model", "config_path": args.config}, error_message="Failed to process model architecture", duration_ms=duration_ms)
                exit_code = 1
        except Exception as e:
            print_error(f"An unexpected error occurred during model definition: {e}")
            duration_ms = (time.perf_counter() - start_time) * 1000
            log_event_main("command_handle", "failure", {"command": "define_model", "config_path": args.config}, error_message=str(e), duration_ms=duration_ms)
            exit_code = 1
        if system_monitor:
            system_monitor.log_resource_usage(force_log=True, context_message="After Define Model")
    elif args.command == "train_model":
        log_event_main("command_handle", "progress", {"command": "train_model", "args": vars(args)})
        start_time = time.perf_counter()
        if system_monitor:
            system_monitor.log_resource_usage(force_log=True, context_message="Before Train Model")
            # VRAM check could be done here if config implies GPU usage
            # For now, start_training itself will read its config and can perform detailed checks
            # Example: Check if config specifies GPU and then call:
            # with open(args.config, 'r') as f_cfg: train_cfg = yaml.safe_load(f_cfg)
            # if train_cfg.get("device", "cpu") == "cuda":
            #     if not system_monitor.check_vram_availability(required_gb=train_cfg.get("system_oversight",{}).get("adaptive_memory_management_threshold_gb", 2.0)):
            #         print_error("Insufficient VRAM for training based on config. Aborting.")
            #         # log and exit
            #         # ...
            pass # Placeholder for more detailed pre-check based on train_config

        try:
            success = start_training(args.config, api) # Pass the actual api instance
            if success:
                duration_ms = (time.perf_counter() - start_time) * 1000
                log_event_main("command_handle", "success", {"command": "train_model", "config_path": args.config}, duration_ms=duration_ms)
                exit_code = 0
            else:
                duration_ms = (time.perf_counter() - start_time) * 1000
                log_event_main("command_handle", "failure", {"command": "train_model", "config_path": args.config}, error_message="Training process reported failure.", duration_ms=duration_ms)
                exit_code = 1
        except FileNotFoundError as e:
            print_error(f"Configuration file not found: {e.filename}")
            duration_ms = (time.perf_counter() - start_time) * 1000
            log_event_main("command_handle", "failure", {"command": "train_model", "config_path": args.config}, error_message=f"Configuration file not found: {e.filename}", duration_ms=duration_ms)
            exit_code = 1
        except yaml.YAMLError as e:
            print_error(f"Error parsing YAML configuration file {args.config}: {e}")
            duration_ms = (time.perf_counter() - start_time) * 1000
            log_event_main("command_handle", "failure", {"command": "train_model", "config_path": args.config}, error_message=f"YAML parsing error: {e}", duration_ms=duration_ms)
            exit_code = 1
        except Exception as e:
            print_error(f"An unexpected error occurred during model training: {e}")
            duration_ms = (time.perf_counter() - start_time) * 1000
            log_event_main("command_handle", "failure", {"command": "train_model", "config_path": args.config}, error_message=str(e), duration_ms=duration_ms)
            exit_code = 1
        if system_monitor:
            system_monitor.log_resource_usage(force_log=True, context_message="After Train Model")
    elif args.command == "evaluate_model":
        log_event_main("command_handle", "progress", {"command": "evaluate_model", "args": vars(args)})
        start_time = time.perf_counter()
        if system_monitor:
            system_monitor.log_resource_usage(force_log=True, context_message="Before Evaluate Model")
            # Similar VRAM check as in train_model could be added here based on eval_config

        eval_config_path = args.config
        # Handle checkpoint override from CLI
        # The start_evaluation function expects the API and the config path.
        # If a checkpoint is overridden, we need to load the eval_config, modify it,
        # and then pass the path to this (potentially temporary) modified config,
        # or pass the modified config dict directly if start_evaluation supports it.
        # For now, start_evaluation takes a config_path. Let's assume it handles checkpoint internally or via its config.
        # If args.checkpoint is provided, we'd ideally inform start_evaluation.
        # A simple way is for start_evaluation to also accept an optional checkpoint_override path.
        # Let's modify start_evaluation call to reflect this potential need.
        # For now, the `core_evaluator.py` `start_evaluation` takes `config_path` and `api`.
        # The `args.checkpoint` is not directly used by it.
        # We will pass the api instance. If checkpoint override is critical,
        # start_evaluation in core_evaluator.py would need an update, or we modify the config dict here.

        try:
            # The current start_evaluation in core_evaluator.py takes (config_path, api)
            # The previous call in main.py was (args.config, args.checkpoint, api_instance)
            # We need to reconcile this. For now, I'll pass what core_evaluator.py expects.
            # If args.checkpoint needs to be used, core_evaluator.py's start_evaluation
            # or this block needs to handle it (e.g. by loading eval_config, updating checkpoint_path, then calling).

            # For now, let's assume start_evaluation will use the checkpoint from its config file.
            # The CLI --checkpoint arg is currently not plumbed through to start_evaluation.
            # This will be addressed if start_evaluation is modified or if we modify the config dict here.

            results = start_evaluation(config_path=eval_config_path, api=api) # Pass api instance

            if results: # Assuming start_evaluation returns results or True on success
                duration_ms = (time.perf_counter() - start_time) * 1000
                log_event_main("command_handle", "success", {"command": "evaluate_model", "config_path": args.config, "checkpoint_override_status": "CLI arg not currently plumbed"}, duration_ms=duration_ms)
                exit_code = 0
            else:
                duration_ms = (time.perf_counter() - start_time) * 1000
                log_event_main("command_handle", "failure", {"command": "evaluate_model", "config_path": args.config}, error_message="Evaluation process reported failure or no results.", duration_ms=duration_ms)
                exit_code = 1
        except FileNotFoundError as e:
            print_error(f"Configuration or checkpoint file not found: {e.filename}")
            duration_ms = (time.perf_counter() - start_time) * 1000
            log_event_main("command_handle", "failure", {"command": "evaluate_model", "config_path": args.config}, error_message=f"File not found: {e.filename}", duration_ms=duration_ms)
            exit_code = 1
        except yaml.YAMLError as e:
            print_error(f"Error parsing YAML configuration file {args.config}: {e}")
            duration_ms = (time.perf_counter() - start_time) * 1000
            log_event_main("command_handle", "failure", {"command": "evaluate_model", "config_path": args.config}, error_message=f"YAML parsing error: {e}", duration_ms=duration_ms)
            exit_code = 1
        except Exception as e:
            print_error(f"An unexpected error occurred during model evaluation: {e}")
            duration_ms = (time.perf_counter() - start_time) * 1000
            log_event_main("command_handle", "failure", {"command": "evaluate_model", "config_path": args.config}, error_message=str(e), duration_ms=duration_ms)
            exit_code = 1
        if system_monitor:
            system_monitor.log_resource_usage(force_log=True, context_message="After Evaluate Model")

    # Ensure logs are flushed before exiting
    if file_event_logger_main:
        for handler in file_event_logger_main.handlers[:]:
            handler.flush()
            handler.close()
            file_event_logger_main.removeHandler(handler)
    return exit_code

if __name__ == "__main__":
    exit_status = 1 # Default to error
    try:
        exit_status = main_cli_entry()
    except Exception as e:
        # This is a top-level catch for unexpected errors not caught within main_cli_entry
        # _initial_logger can be used here if `logger` itself failed to initialize
        _initial_logger.error(f"Unhandled exception in __main__: {e}", exc_info=True)
        # Attempt to log with the main event logger if it was set up
        log_event_main("script_execution", "failure",
                       {"script_name": "main.py", "status": "unhandled_exception_toplevel"},
                       error_message=str(e))
    finally:
        # Final attempt to flush logs, especially if an error occurred before normal flushing
        if file_event_logger_main:
            for handler in file_event_logger_main.handlers[:]:
                try:
                    handler.flush()
                    handler.close()
                    file_event_logger_main.removeHandler(handler)
                except Exception as eh_final_flush:
                    _initial_logger.error(f"Error during final log flush: {eh_final_flush}")
        sys.exit(exit_status)
