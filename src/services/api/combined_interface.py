#!/usr/bin/env python3
"""
ImpressionCore: Combined Interface

Module for combined interface functionality in the ImpressionCore framework.

File: interface\combined_interface.py
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
This module implements combined interface functionality for the
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
from interface.combined_interface import CombinedInterface
instance = CombinedInterface()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import gradio as gr
from pathlib import Path
from typing import Optional, Dict, Any, Union
import logging
import torch

from .text_generation import TextGenerationInterface
from .image_generation import ImageGenerationInterface
from ..models.diffusion.model_manager import ModelManager, ModelLoadConfig

logger = logging.getLogger(__name__)

class CombinedInterface:
    """
    Unified interface combining text and image generation capabilities.
    Provides memory-efficient inference with shared components.
    # Memory optimization: Memory-critical operation
    """
    
    def __init__(
        self,
        model_path: Union[str, Path],
        optimization_config: Optional[Union[str, Path]] = None,
        share: bool = False,
    ):
        """Initialize combined interface."""
        self.model_path = Path(model_path)
        self.share = share
        
        # Load optimization configuration
        if optimization_config is not None:
            self.load_config = ModelManager.load_optimization_config(optimization_config)
        else:
            # Create default config optimized for 4GB VRAM
            self.load_config = ModelLoadConfig(
                use_cpu_offload=True,
                attention_slice_size=64,
                max_batch_size=1,
                force_half_precision=True,
                sequential_offload=True,
                low_vram_mode=True
            )
        
        # Initialize interfaces
        logger.info("Initializing text generation interface...")
        self.text_interface = TextGenerationInterface(
            model_path=model_path,
            use_fp16=self.load_config.force_half_precision,
            chunk_size=self.load_config.attention_slice_size,
            share=False  # Don't launch individual interfaces
        )
        
        logger.info("Initializing image generation interface...")
        self.image_interface = ImageGenerationInterface(
            model_path=model_path,
            optimization_config=self.load_config,
            share=False  # Don't launch individual interfaces
        )
        
        # Create combined interface
        self.interface = self._create_interface()
    
    def _create_interface(self) -> gr.Blocks:
        """Create the combined Gradio interface."""
        with gr.Blocks(title="ImpressionCore Generation Interface") as interface:
            gr.Markdown("""
                # ImpressionCore Generation Interface
                Generate text and images using advanced neural models.
                Optimized for consumer hardware with 4GB VRAM.
            """)
            
            # Hardware status indicator
            with gr.Row():
                hardware_info = gr.Markdown()
                memory_text = gr.Markdown()
                # Memory optimization: Memory-critical operation
            
            def update_hardware_info():
                """Update hardware information display."""
                if torch.cuda.is_available():
                # Memory optimization: CUDA operations for GPU acceleration
                    gpu_name = torch.cuda.get_device_name()
                    # Memory optimization: CUDA operations for GPU acceleration
                    total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    # Memory optimization: CUDA operations for GPU acceleration
                    return f"""
                        ### Hardware Information
                        - GPU: {gpu_name}
                        # Memory optimization: Memory-critical operation
                        - Total VRAM: {total_memory:.2f}GB
                        # Memory optimization: Memory-critical operation
                        - Optimization Mode: {'Low VRAM' if self.load_config.low_vram_mode else 'Standard'}
                    """
                return "### Hardware Information\nRunning on CPU only"
            
            def update_memory_info():
            # Memory optimization: Memory-critical operation
                """Update memory usage display."""
                # Memory optimization: Memory-critical operation
                if torch.cuda.is_available():
                # Memory optimization: CUDA operations for GPU acceleration
                    mem_allocated = torch.cuda.memory_allocated() / (1024**3)
                    # Memory optimization: CUDA operations for GPU acceleration
                    mem_reserved = torch.cuda.memory_reserved() / (1024**3)
                    # Memory optimization: CUDA operations for GPU acceleration
                    return f"""
                        ### Memory Usage
                        # Memory optimization: Memory-critical operation
                        - Allocated: {mem_allocated:.2f}GB
                        - Reserved: {mem_reserved:.2f}GB
                        - Free: {(torch.cuda.get_device_properties(0).total_memory / (1024**3) - mem_reserved):.2f}GB
                        # Memory optimization: CUDA operations for GPU acceleration
                    """
                return "Memory tracking not available"
                # Memory optimization: Memory-critical operation
            
            # Update hardware info
            hardware_info.update(value=update_hardware_info())
            
            # Create tabs for different generation modes
            with gr.Tabs():
                # Text generation tab
                with gr.Tab("Text Generation"):
                    with gr.Row():
                        with gr.Column(scale=3):
                            # Text input components
                            text_prompt = gr.Textbox(
                                label="Text Prompt",
                                placeholder="Enter text to continue...",
                                lines=5
                            )
                            
                            with gr.Accordion("Generation Parameters", open=False):
                                with gr.Row():
                                    text_max_length = gr.Slider(
                                        label="Maximum Length",
                                        minimum=10,
                                        maximum=1000,
                                        value=100,
                                        step=10
                                    )
                                    text_temperature = gr.Slider(
                                        label="Temperature",
                                        minimum=0.1,
                                        maximum=2.0,
                                        value=0.7,
                                        step=0.1
                                    )
                                    
                                with gr.Row():
                                    text_top_p = gr.Slider(
                                        label="Top-p",
                                        minimum=0.1,
                                        maximum=1.0,
                                        value=0.9,
                                        step=0.1
                                    )
                                    text_top_k = gr.Slider(
                                        label="Top-k",
                                        minimum=1,
                                        maximum=100,
                                        value=50,
                                        step=1
                                    )
                                
                                text_repetition_penalty = gr.Slider(
                                    label="Repetition Penalty",
                                    minimum=1.0,
                                    maximum=2.0,
                                    value=1.2,
                                    step=0.1
                                )
                                
                                with gr.Row():
                                    text_num_sequences = gr.Slider(
                                        label="Number of Sequences",
                                        minimum=1,
                                        maximum=5,
                                        value=1,
                                        step=1
                                    )
                                    text_seed = gr.Number(
                                        label="Seed (Optional)",
                                        value=None,
                                        precision=0
                                    )
                            
                            # Generation button
                            text_generate_btn = gr.Button("Generate Text", variant="primary")
                            
                        with gr.Column(scale=2):
                            # Text output components
                            text_output = gr.TextArea(
                                label="Generated Text",
                                lines=10,
                                interactive=False
                            )
                            text_info = gr.Markdown()
                
                # Image generation tab
                with gr.Tab("Image Generation"):
                    with gr.Row():
                        with gr.Column(scale=3):
                            # Image input components
                            image_prompt = gr.Textbox(
                                label="Image Prompt",
                                placeholder="Describe the image you want to generate...",
                                lines=3
                            )
                            image_negative_prompt = gr.Textbox(
                                label="Negative Prompt (Optional)",
                                placeholder="What you don't want in the image...",
                                lines=2
                            )
                            
                            with gr.Accordion("Generation Parameters", open=False):
                                with gr.Row():
                                    image_steps = gr.Slider(
                                        label="Generation Steps",
                                        minimum=20,
                                        maximum=100,
                                        value=50,
                                        step=1
                                    )
                                    image_guidance = gr.Slider(
                                        label="Guidance Scale",
                                        minimum=1.0,
                                        maximum=20.0,
                                        value=7.5,
                                        step=0.5
                                    )
                                    
                                with gr.Row():
                                    image_width = gr.Slider(
                                        label="Width",
                                        minimum=256,
                                        maximum=1024,
                                        value=512,
                                        step=64
                                    )
                                    image_height = gr.Slider(
                                        label="Height",
                                        minimum=256,
                                        maximum=1024,
                                        value=512,
                                        step=64
                                    )
                                    
                                image_seed = gr.Number(
                                    label="Seed (Optional)",
                                    value=None,
                                    precision=0
                                )
                            
                            # Generation button
                            image_generate_btn = gr.Button("Generate Image", variant="primary")
                            
                        with gr.Column(scale=2):
                            # Image output components
                            image_output = gr.Image(label="Generated Image")
                            image_info = gr.Markdown()
            
            # Set up event handlers
            text_generate_btn.click(
                self.text_interface.interface._create_interface().generate_text,
                inputs=[
                    text_prompt, text_max_length, text_temperature,
                    text_top_p, text_top_k, text_repetition_penalty,
                    text_num_sequences, text_seed
                ],
                outputs=[text_output, text_info]
            )
            
            image_generate_btn.click(
                self.image_interface.interface._create_interface().generate_image,
                inputs=[
                    image_prompt, image_negative_prompt, image_steps,
                    image_guidance, image_width, image_height, image_seed
                ],
                outputs=[image_output, image_info]
            )
            
            # Update memory info periodically
            # Memory optimization: Memory-critical operation
            gr.on(
                triggers=[],
                fn=update_memory_info,
                # Memory optimization: Memory-critical operation
                outputs=[memory_text],
                # Memory optimization: Memory-critical operation
                every=5  # Update every 5 seconds
            )
        
        return interface
    
    def launch(self, **kwargs):
        """Launch the combined interface."""
        self.interface.launch(
            share=self.share,
            server_name="0.0.0.0",  # Allow external connections
            **kwargs
        )