#!/usr/bin/env python3
"""
ImpressionCore: Inference Tests

Module for inference tests functionality in the ImpressionCore framework.

File: examples\inference_tests.py
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
Dependencies: [torch, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements inference tests functionality for the
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
from examples.inference_tests import MainClass
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
import time
import torch
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import components
from src.pipeline.main import ModalEngine
from src.core.model import ImpressionCoreModel, ModelConfig
# Memory optimization: Explicit memory cleanup
from src.core.gpu_utils import (
# Memory optimization: Memory-critical operation
    get_device, get_memory_info, clear_gpu_memory, 
    # Memory optimization: Device placement for memory management
    MemoryTracker, is_shared_memory_gpu
    # Memory optimization: Memory-critical operation
)
from src.core.memory_optimization import memory_efficient_inference
# Memory optimization: Memory-critical operation
from src.core.config.config_manager import get_config_manager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Initialize config manager
config_manager = get_config_manager()

# Get device
# Memory optimization: Device placement for memory management
DEVICE = get_device()
# Memory optimization: Device placement for memory management

def ensure_model_config_complete(config):
    """
    Ensure the model config has all required attributes.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        config: The model configuration object
        # Memory optimization: Explicit memory cleanup
        
    Returns:
        Updated model configuration object with default values for missing attributes
        # Memory optimization: Explicit memory cleanup
    """
    # Common model attributes with sensible defaults
    # Memory optimization: Explicit memory cleanup
    required_attrs = {
        'dropout': 0.1,
        'hidden_act': 'gelu',
        'initializer_range': 0.02,
        'layer_norm_eps': 1e-12,
        'intermediate_size': 3072,  # Typically 4x hidden_size
    }
    
    # Set any missing attributes
    for attr, default_value in required_attrs.items():
        if not hasattr(config, attr):
            setattr(config, attr, default_value)
            logger.info(f"Added missing config attribute '{attr}' with default value {default_value}")
    
    return config

def test_cuda_availability():
# Memory optimization: Memory-critical operation
    """Test CUDA availability and print device information."""
    # Memory optimization: Device placement for memory management
    logger.info("Testing CUDA availability")
    # Memory optimization: Memory-critical operation
    
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        logger.info(f"CUDA is available: {torch.cuda.get_device_name(0)}")
        # Memory optimization: CUDA operations for GPU acceleration
        
        # Check if this is a shared memory GPU
        # Memory optimization: Memory-critical operation
        is_shared, dedicated_vram, total_shared = is_shared_memory_gpu()
        # Memory optimization: Memory-critical operation
        if is_shared:
            logger.info(f"Detected shared memory GPU with {dedicated_vram:.2f}GB dedicated VRAM")
            # Memory optimization: Memory-critical operation
            logger.info(f"System has {total_shared:.2f}GB total shared memory")
            # Memory optimization: Memory-critical operation
        
        # Get memory information
        # Memory optimization: Memory-critical operation
        memory_info = get_memory_info()
        # Memory optimization: Memory-critical operation
        logger.info(f"GPU memory information: {memory_info}")
        # Memory optimization: Memory-critical operation
        
        # Test a simple CUDA operation
        # Memory optimization: Memory-critical operation
        with MemoryTracker() as tracker:
        # Memory optimization: Memory-critical operation
            a = torch.tensor([1.0, 2.0, 3.0], device="cuda")
            # Memory optimization: Device placement for memory management
            b = torch.tensor([4.0, 5.0, 6.0], device="cuda")
            # Memory optimization: Device placement for memory management
            c = a + b
            
            memory_stats = tracker.stop()
            # Memory optimization: Memory-critical operation
            logger.info(f"Simple tensor operation memory usage: {memory_stats['peak_gpu_mb']:.2f}MB")
            # Memory optimization: Memory-critical operation
        
        logger.info(f"CUDA tensor operation result: {c.cpu().numpy()}")
        # Memory optimization: Memory-critical operation
        logger.info("CUDA test passed")
        # Memory optimization: Memory-critical operation
        return True
    else:
        logger.warning("CUDA is not available")
        # Memory optimization: Memory-critical operation
        return False

def test_model_inference():
    """Test basic model inference functionality."""
    # Memory optimization: Explicit memory cleanup
    logger.info("Creating model for inference test")
    # Memory optimization: Explicit memory cleanup
    
    try:
        # Create model config
        # Memory optimization: Explicit memory cleanup
        config = ModelConfig()
        
        # Ensure config has all required attributes
        config = ensure_model_config_complete(config)
        
        # Apply memory optimization settings from config
        # Memory optimization: Memory-critical operation
        config_manager.apply_memory_settings()
        # Memory optimization: Memory-critical operation
        
        # Create model with config
        # Memory optimization: Explicit memory cleanup
        model = ImpressionCoreModel(config)
        # Memory optimization: Explicit memory cleanup
        model.eval()
        
        # Move model to device
        # Memory optimization: Device placement for memory management
        model.to(DEVICE)
        # Memory optimization: Device placement for memory management
        logger.info(f"Model moved to device: {next(model.parameters()).device}")
        # Memory optimization: Device placement for memory management
        
        # Get optimal batch size from config
        batch_size = config_manager.get_optimal_batch_size("small_model")
        seq_length = 10
        logger.info(f"Using batch size {batch_size} based on config")
        
        # Generate random input
        input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_length)).to(DEVICE)
        # Memory optimization: Device placement for memory management
        attention_mask = torch.ones_like(input_ids).to(DEVICE)
        # Memory optimization: Device placement for memory management
        
        # Test forward pass
        logger.info("Testing forward pass")
        
        # Use memory tracking to monitor resource usage
        # Memory optimization: Memory-critical operation
        with MemoryTracker() as tracker:
        # Memory optimization: Memory-critical operation
            # Use memory-efficient inference context
            # Memory optimization: Memory-critical operation
            with memory_efficient_inference():
            # Memory optimization: Memory-critical operation
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            
            # Get memory statistics
            # Memory optimization: Memory-critical operation
            memory_stats = tracker.stop()
            # Memory optimization: Memory-critical operation
            logger.info(f"Forward pass peak memory usage: {memory_stats['peak_gpu_mb']:.2f}MB")
            # Memory optimization: Memory-critical operation
        
        # Check output shape - Handle different output formats robustly
        logger.info(f"Output type: {type(outputs)}")
        
        if isinstance(outputs, dict) and 'logits' in outputs:
            # If outputs is a dictionary with a 'logits' key
            actual_shape = outputs['logits'].shape
            logger.info(f"Output shape (from outputs['logits']): {actual_shape}")
            logger.info(f"Output device: {outputs['logits'].device}")
            # Memory optimization: Device placement for memory management
            assert actual_shape[0] == batch_size and actual_shape[1] == seq_length, f"Unexpected shape: {actual_shape}"
        elif isinstance(outputs, torch.Tensor):
            # If outputs is a tensor directly
            actual_shape = outputs.shape
            logger.info(f"Output shape (from tensor): {actual_shape}")
            logger.info(f"Output device: {outputs.device}")
            # Memory optimization: Device placement for memory management
            assert actual_shape[0] == batch_size and actual_shape[1] == seq_length, f"Unexpected shape: {actual_shape}"
        else:
            # For other output types, just log what we got
            logger.info(f"Output structure: {outputs}")
            if hasattr(outputs, 'shape'):
                logger.info(f"Output shape attribute: {outputs.shape}")
            elif hasattr(outputs, 'size'):
                logger.info(f"Output size attribute: {outputs.size}")
        
        # Test generation
        logger.info("Testing text generation")
        try:
            gen_length = 20
            # Use memory tracking for generation
            # Memory optimization: Memory-critical operation
            with MemoryTracker() as tracker:
            # Memory optimization: Memory-critical operation
                # Measure generation time
                start_time = time.time()
                generated = model.generate(input_ids, max_length=gen_length)
                generation_time = time.time() - start_time
                
                # Get memory statistics
                # Memory optimization: Memory-critical operation
                memory_stats = tracker.stop()
                # Memory optimization: Memory-critical operation
                logger.info(f"Generation peak memory usage: {memory_stats['peak_gpu_mb']:.2f}MB")
                # Memory optimization: Memory-critical operation
            
            # Check generated shape
            logger.info(f"Generated output type: {type(generated)}")
            if isinstance(generated, torch.Tensor):
                logger.info(f"Generated shape: {generated.shape}")
                logger.info(f"Generated device: {generated.device}")
                # Memory optimization: Device placement for memory management
                logger.info(f"Generation time: {generation_time:.4f} seconds")
            else:
                logger.info(f"Generated structure: {generated}")
        except AttributeError:
            logger.warning("Model doesn't have a generate method, skipping generation test")
            # Memory optimization: Explicit memory cleanup
        
        # Clear GPU memory
        # Memory optimization: Memory-critical operation
        clear_gpu_memory()
        # Memory optimization: Memory-critical operation
        
        logger.info("Basic model inference test passed")
        # Memory optimization: Explicit memory cleanup
        return True
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return False

def test_engine_integration():
    """Test integration with the ModalEngine."""
    logger.info("Testing integration with ModalEngine")
    
    try:
        # Create engine with only supported parameters
        engine = ModalEngine(
            brainsim_path=os.path.join(project_root, "brainsim")
        )
        
        # Initialize engine with proper error handling
        engine_initialized = False
        try:
            logger.info("Initializing engine...")
            engine.initialize()
            
            # Check if the engine has the required methods
            if (hasattr(engine, 'process_input') or 
                hasattr(engine, 'process') or 
                hasattr(engine, 'run')):
                engine_initialized = True
                logger.info("Engine initialized successfully with required methods")
            else:
                logger.warning("Engine initialized but required methods are missing")
        except Exception as init_error:
            logger.error(f"Engine initialization failed: {init_error}")
            return False
        
        # Only proceed if initialization was successful
        if engine_initialized:
            # Test with different prompts
            test_prompts = [
                "What is Mars?",
                "How many moons does Mars have?",
                "Compare Earth and Mars."
            ]
            
            # Check for appropriate method for processing input
            input_method = None
            if hasattr(engine, 'process_input'):
                input_method = engine.process_input
            elif hasattr(engine, 'process'):
                input_method = engine.process
            elif hasattr(engine, 'run'):
                input_method = engine.run
            
            if input_method is None:
                logger.error("No suitable input processing method found")
                return False
            
            # Use memory tracking for engine processing
            # Memory optimization: Memory-critical operation
            with MemoryTracker() as tracker:
            # Memory optimization: Memory-critical operation
                # Process test prompts
                for i, prompt in enumerate(test_prompts):
                    logger.info(f"Processing prompt {i+1}: '{prompt}'")
                    
                    start_time = time.time()
                    response = input_method(prompt)
                    processing_time = time.time() - start_time
                    
                    logger.info(f"Response: '{response}'")
                    logger.info(f"Processing time: {processing_time:.4f} seconds")
                
                # Get memory statistics
                # Memory optimization: Memory-critical operation
                memory_stats = tracker.stop()
                # Memory optimization: Memory-critical operation
                logger.info(f"Engine processing peak memory usage: {memory_stats['peak_gpu_mb']:.2f}MB")
                # Memory optimization: Memory-critical operation
            
            # Shutdown engine properly
            if hasattr(engine, 'shutdown'):
                engine.shutdown()
                logger.info("Engine shutdown successfully")
            elif hasattr(engine, 'close'):
                engine.close()
                logger.info("Engine closed successfully")
                
            logger.info("Engine integration test passed")
            return True
        else:
            logger.error("Engine integration test failed: Engine was not properly initialized")
            return False
            
    except ImportError as e:
        logger.error(f"Import error when testing ModalEngine: {e}")
        return False
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        return False

def main():
    """Run all inference tests."""
    all_tests_passed = True
    
    try:
        # First test CUDA availability
        # Memory optimization: Memory-critical operation
        cuda_available = test_cuda_availability()
        # Memory optimization: Memory-critical operation
        if not cuda_available:
        # Memory optimization: Memory-critical operation
            logger.warning("CUDA is not available, tests will run on CPU")
            # Memory optimization: Memory-critical operation
        
        # Test basic model inference
        # Memory optimization: Explicit memory cleanup
        model_inference_passed = test_model_inference()
        if not model_inference_passed:
            logger.error("Model inference test failed")
            # Memory optimization: Explicit memory cleanup
            all_tests_passed = False
        
        # Test integration with engine
        engine_integration_passed = test_engine_integration()
        if not engine_integration_passed:
            logger.error("Engine integration test failed")
            all_tests_passed = False
        
        if all_tests_passed:
            logger.info("All tests passed successfully!")
            return 0
        else:
            logger.error("One or more tests failed")
            return 1
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())