#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #python #source_code #src/brainsim/memory/debug_individual_items.py #tokenization
**Category:** Source Code
**Status:** Active
"""









# Debug Individual Items

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #memory_management #python #source_code #src\\brainsim\\memory\\debug_individual_items.py #tokenization
# Category:** Source Code
# Status:** Active

"""
Processes each item from the isolated batch individually to pinpoint the source of the MemoryError.
This script will load the batch, initialize models, and then loop through each item,
calling the embedding functions within a try-except block to catch the exact item
that causes a crash.
"""
import logging
import os
import pickle
import sys

from rich.console import Console
from rich.progress import Progress

# Add src to path to allow for imports from other project modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from src.core.utils.rich_logging import setup_logging
    from src.data.tokenization.tokenizer import initialize_models, tokenize
except ImportError as e:
    print(f"Error importing modules: {e}")
    # Fallback path insertion for robustness in different execution environments
    if sys.path[0] != os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')):
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
        from src.core.utils.rich_logging import setup_logging
        from src.data.tokenization.tokenizer import initialize_models, tokenize

# Setup logging and console
setup_logging()
logger = logging.getLogger("debug_individual_items")
console = Console()

BATCH_FILE_PATH = "F:/impressioncore-b1-uks-output/first_batch_for_inspection.pkl"
PROBLEM_ITEM_OUTPUT_PATH = "F:/impressioncore-b1-uks-output/problematic_item_{index}.pkl"

def main():
    """
    Main function to orchestrate the individual item debugging process.
    """
    logger.info("Starting individual item debugging process to find the source of MemoryError.")

    try:
        with open(BATCH_FILE_PATH, "rb") as f:
            batch_data = pickle.load(f)
        logger.info(f"Successfully loaded {len(batch_data)} items from {BATCH_FILE_PATH}")
    except FileNotFoundError:
        logger.error(f"Debug batch file not found at '{BATCH_FILE_PATH}'.")
        logger.error("Please run 'inspect_first_batch.py' to generate the required file.")
        return
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading the batch file: {e}")
        return

    logger.info("Initializing embedding models. This may take a moment...")
    try:
        text_tokenizer, image_model, image_preprocessor = initialize_models()
        if not all((text_tokenizer, image_model, image_preprocessor)):
            logger.error("Failed to initialize one or more models. Aborting.")
            return
        logger.info("Models initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize models: {e}")
        return

    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Processing items...", total=len(batch_data))

        for i, item in enumerate(batch_data):
            progress.update(task, advance=1, description=f"[cyan]Processing item {i+1}/{len(batch_data)}")
            try:
                # The 'item' dictionary is the prompt, containing text and/or image_path
                _ = tokenize(item, text_tokenizer, image_model, image_preprocessor)

            except Exception as e:
                logger.critical(f"!!! CATASTROPHIC ERROR at item index {i} !!!")
                logger.critical(f"Error Type: {type(e).__name__}")
                logger.critical(f"Error Message: {e}")
                logger.error("--- Problematic Item Data ---")
                console.print(item)

                # Save the single problematic item for isolated analysis
                problem_item_path = PROBLEM_ITEM_OUTPUT_PATH.format(index=i)
                try:
                    with open(problem_item_path, "wb") as f_out:
                        pickle.dump(item, f_out)
                    logger.info(f"Successfully saved the problematic item to '{problem_item_path}'")
                except Exception as save_e:
                    logger.error(f"Failed to save problematic item: {save_e}")

                logger.info("Execution stopped to focus on the identified critical error.")
                return

    logger.info("Successfully processed all items in the batch without any critical errors.")

if __name__ == "__main__":
    main()
