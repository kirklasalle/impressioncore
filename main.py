"""
Main entry point for ImpressionCore.

This script provides a command-line interface for ImpressionCore
capabilities including tokenization, model inference, and more.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Set 'src' as the program root
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, src_path)

# Debugging: Log the sys.path
logger = logging.getLogger(__name__)
logger.info(f"sys.path: {sys.path}")

# Debugging: Check if the 'src' directory exists
if not os.path.exists(src_path):
    logger.error(f"'src' directory not found at: {src_path}")
    logger.error("Please ensure the 'src' directory exists in the project root.")
    sys.exit(1)
else:
    logger.info(f"'src' directory found at: {src_path}")

# Debugging: List contents of the 'src' directory
try:
    src_contents = os.listdir(src_path)
    logger.info(f"Contents of 'src' directory: {src_contents}")
except Exception as e:
    logger.error(f"Error accessing 'src' directory: {e}")
    sys.exit(1)

# Check for required subdirectories and modules
required_structure = ["core", "models", "tokenization"]
missing_structure = [item for item in required_structure if item not in src_contents]

if missing_structure:
    logger.error(f"Missing required directories or modules in 'src': {missing_structure}")
    logger.error("Please ensure the 'src' directory contains the required structure.")
    sys.exit(1)

# Check for required dependencies
try:
    import torch
    import numpy as np
    from PIL import Image
except ImportError as e:
    logger.error(f"Missing required dependency: {e}")
    logger.error("Please install the required dependencies using 'pip install -r requirements.txt'.")
    sys.exit(1)

# Set up rich logging and enhancements
try:
    from core.utils.rich_logging import setup_rich_logging
    from core.utils.rich_enhancements import print_info, print_success, print_warning, print_error, create_header
    logger = setup_rich_logging(__name__)
    create_header("ImpressionCore CLI")
    print_info("Rich logging and enhancements enabled.")
except ImportError as e:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.warning(f"Rich logging/enhancements not available: {e}")

try:
    # Import core modules that are available in your project structure
    from core.modal_engine import ModalityType
    from core.utils.hardware_detection import get_system_info, optimize_for_hardware
    from models.memory_controller import get_memory_controller
    
    # Define a temporary API class since it doesn't exist yet
    class ImpressionCoreAPI:
        """
        Temporary implementation of the ImpressionCore API.
        
        This class serves as a placeholder until the actual implementation
        is complete. It provides minimal functionality for the CLI to work.
        """
        def __init__(self, use_lite_engine=False, memory_efficient=True, recommended_precision=None):
            self.use_lite_engine = use_lite_engine
            self.memory_efficient = memory_efficient
            self.precision = recommended_precision
            logger.info("Initializing temporary ImpressionCoreAPI implementation")
        
        def tokenize(self, content, modality):
            """Tokenize content based on modality."""
            logger.info(f"Tokenizing {modality} content (placeholder implementation)")
            return [1, 2, 3, 4, 5]  # Placeholder token IDs
            
        def detokenize(self, token_ids, modality):
            """Detokenize token IDs based on modality."""
            logger.info(f"Detokenizing {modality} content (placeholder implementation)")
            if modality == "text":
                return "Placeholder detokenized text"
            else:
                import torch
                import numpy as np
                # Return a small placeholder image tensor
                return torch.zeros(3, 32, 32)  # RGB image of 32x32 pixels
    
    def get_api():
        """Get the API instance."""
        return ImpressionCoreAPI()
            
except ImportError as e:
    logger.error(f"Error importing dependencies: {e}")
    logger.error("Ensure the 'src' directory is correctly structured and contains the required modules.")
    sys.exit(1)

def init_api(args):
    """Initialize the API based on command-line arguments."""
    # Get hardware-specific settings
    hw_settings = optimize_for_hardware()
    
    # Use hardware detection to apply appropriate optimizations
    memory_efficient_value = not args.disable_memory_optimizations and hw_settings["is_low_vram"]
    
    # Initialize memory controller if using memory optimization
    if memory_efficient_value:
        logger.info("Initializing memory controller for low VRAM operation")
        memory_controller = get_memory_controller()
    
    logger.info(f"Initializing API with memory_efficient={memory_efficient_value}")
    
    # Pass hardware-optimized settings to API
    return ImpressionCoreAPI(
        use_lite_engine=args.lite_engine or hw_settings["is_low_vram"], 
        memory_efficient=memory_efficient_value,
        recommended_precision=hw_settings["recommended_precision"] if not args.disable_memory_optimizations else torch.float32
    )

def handle_tokenize(args, api):
    """Handle tokenize command.
    Args:
        args: Parsed command-line arguments.
        api: ImpressionCoreAPI instance.
    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    try:
        if args.modality == "text":
            # Read input
            if args.input_file:
                try:
                    with open(args.input_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    logger.error(f"Failed to read input file: {e}")
                    return 1
            else:
                content = args.content
                if not content:
                    logger.error("No content provided for text tokenization.")
                    return 1
            # Tokenize
            token_ids = api.tokenize(content, args.modality)
            # Output
            if args.output_file:
                try:
                    from src.tokenization.converter import save_token_ids
                    save_token_ids(token_ids, args.output_file)
                    logger.info(f"Saved {len(token_ids)} tokens to {args.output_file}")
                except Exception as e:
                    logger.error(f"Failed to save tokens: {e}")
                    return 1
            else:
                print(f"Tokens: {token_ids[:10]}... (total: {len(token_ids)})")
        elif args.modality == "image":
            if not args.input_file:
                logger.error("Input file required for image tokenization")
                return 1
            try:
                image = Image.open(args.input_file).convert("RGB")
                img_array = np.array(image)
                img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).float() / 255.0
            except Exception as e:
                logger.error(f"Failed to load or process image: {e}")
                return 1
            # Tokenize
            token_ids = api.tokenize(img_tensor, args.modality)
            # Output
            if args.output_file:
                try:
                    from src.tokenization.converter import save_token_ids
                    save_token_ids(token_ids, args.output_file)
                    logger.info(f"Saved {len(token_ids)} tokens to {args.output_file}")
                except Exception as e:
                    logger.error(f"Failed to save tokens: {e}")
                    return 1
            else:
                print(f"Tokens: {token_ids[:10]}... (total: {len(token_ids)})")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error in handle_tokenize: {e}")
        return 1

def handle_detokenize(args, api):
    """Handle detokenize command.
    Args:
        args: Parsed command-line arguments.
        api: ImpressionCoreAPI instance.
    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    try:
        try:
            from src.tokenization.converter import load_token_ids
            token_ids = load_token_ids(args.input_file)
        except Exception as e:
            logger.error(f"Failed to load token IDs: {e}")
            return 1
        # Detokenize
        content = api.detokenize(token_ids, args.modality)
        if args.modality == "text":
            if args.output_file:
                try:
                    with open(args.output_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"Saved text to {args.output_file}")
                except Exception as e:
                    logger.error(f"Failed to save text: {e}")
                    return 1
            else:
                print("\nDetokenized text:")
                print(content)
        elif args.modality == "image":
            if not args.output_file:
                logger.error("Output file required for image detokenization")
                return 1
            try:
                image_array = (content.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
                image = Image.fromarray(image_array)
                image.save(args.output_file)
                logger.info(f"Saved image to {args.output_file}")
            except Exception as e:
                logger.error(f"Failed to save image: {e}")
                return 1
        return 0
    except Exception as e:
        logger.error(f"Unexpected error in handle_detokenize: {e}")
        return 1

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="ImpressionCore CLI")
    
    # Global options
    parser.add_argument("--lite-engine", action="store_true", 
                      help="Use memory-efficient LiteModalEngine")
    parser.add_argument("--disable-memory-optimizations", action="store_true",
                      help="Disable memory efficiency optimizations")
    
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
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
        
    # Initialize API
    api = init_api(args)
    
    # Execute command
    if args.command == "tokenize":
        return handle_tokenize(args, api)
    elif args.command == "detokenize":
        return handle_detokenize(args, api)
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
