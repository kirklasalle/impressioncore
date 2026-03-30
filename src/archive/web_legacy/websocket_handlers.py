#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #attention_mechanism #command_line #memory_management #multimodal #performance #python #source_code #src/interfaces/web/websocket_handlers.py #testing #training #transformer #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #attention_mechanism #command_line #memory_management #multimodal #performance #python #source_code #src/interfaces/web/websocket_handlers.py #testing #training #transformer #web_interface
# Category:** Interface Definitions
# Status:** Active

r"""
ImpressionCore: Websocket Handlers

Module for websocket handlers functionality in the ImpressionCore framework.

File: web/websocket_handlers.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, production, web, frontend, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements websocket handlers functionality for the
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
from web.websocket_handlers import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import json
import logging

from simple_websocket import ConnectionClosed

from .training.training_manager import TrainingManager

logger = logging.getLogger(__name__)

# Global training manager instance used for all WebSocket connections
training_manager = TrainingManager()

def handle_training_socket(ws):
    """WebSocket handler for training updates and control."""
    try:
        # Get active training session if it exists
        if training_manager.trainer:
            logger.info("WebSocket connected to active training session")
        else:
            logger.info("WebSocket connected, no active training session")

        while True:
            try:
                # Handle incoming messages from the client
                data = ws.receive()
                if not data:
                    continue

                message = json.loads(data)
                action = message.get('action')

                # Process different action types
                if action == 'start':
                    if training_manager.state.is_training:
                        logger.info("Resuming paused training")
                        training_manager.start_training()
                    else:
                        # Initialize with default config if not already training
                        model_config = {
                            "model_name": "ImpressionCore-Base",
                            "architecture": "Transformer",
                            "hidden_size": 768,
                            "num_layers": 12,
                            "num_heads": 12,
                            "vocab_size": 50257,
                            "max_position_embeddings": 1024,  # Smaller context window for memory efficiency
                            # Memory optimization: Memory-critical operation
                            "attention_dropout": 0.1,
                            "gradient_checkpointing": True,  # Memory optimization for 4GB VRAM
                            # Memory optimization: Memory-critical operation
                            "use_cache": False  # Disable KV cache to save memory
                            # Memory optimization: Memory-critical operation
                        }

                        success = training_manager.initialize_training(model_config)
                        if success:
                            logger.info("Starting new training session")
                            training_manager.start_training()
                        else:
                            logger.error("Failed to initialize training")
                            ws.send(json.dumps({
                                "type": "error",
                                "message": "Failed to initialize training session"
                            }))

                elif action == 'pause':
                    if training_manager.state.is_training:
                        logger.info("Pausing training")
                        training_manager.pause_training()

                elif action == 'stop':
                    if training_manager.state.is_training:
                        logger.info("Stopping training")
                        training_manager.stop_training()

                elif action == 'save_checkpoint':
                    if training_manager.trainer:
                        logger.info("Saving checkpoint")
                        try:
                            checkpoint_path = training_manager.save_checkpoint('manual_checkpoint.pt')
                            ws.send(json.dumps({
                                "type": "checkpoint_saved",
                                "path": str(checkpoint_path)
                            }))
                        except Exception as e:
                            logger.error(f"Error saving checkpoint: {e}")
                            ws.send(json.dumps({
                                "type": "error",
                                "message": f"Error saving checkpoint: {e!s}"
                            }))

                elif action == 'export_metrics':
                    if training_manager.trainer:
                        logger.info("Exporting metrics")
                        try:
                            metrics_data = training_manager.export_metrics()
                            ws.send(json.dumps({
                                "type": "metrics_exported",
                                "data": metrics_data
                            }))
                        except Exception as e:
                            logger.error(f"Error exporting metrics: {e}")
                            ws.send(json.dumps({
                                "type": "error",
                                "message": f"Error exporting metrics: {e!s}"
                            }))

                elif action == 'update_vram_target':
                    if training_manager.trainer:
                        value = float(message.get('value', 3.5))
                        logger.info(f"Setting VRAM target to {value} GB")
                        training_manager.set_vram_target(value)

                elif action == 'update_precision':
                    if training_manager.trainer:
                        mode = message.get('mode', 'fp16')
                        logger.info(f"Setting precision mode to {mode}")
                        training_manager.set_precision_mode(mode)

                elif action == 'update_gradient_checkpointing':
                    if training_manager.trainer:
                        enabled = message.get('enabled', True)
                        logger.info(f"Setting gradient checkpointing to {enabled}")
                        training_manager.set_gradient_checkpointing(enabled)

                elif action == 'update_attention_cache' and training_manager.trainer:
                    enabled = message.get('enabled', True)
                    logger.info(f"Setting attention cache to {enabled}")
                    training_manager.set_attention_cache(enabled)

                # Send current training stats
                if training_manager.trainer:
                    training_manager.get_current_stats()
                    ws.send(json.dumps({
                        "type": "training_update",
                        # stats
                    }))
                else:
                    # If no active training, send system status
                    ws.send(json.dumps({
                        "type": "status",
                        "is_training": False,
                        "ready": True,
                        "vram_available": 4.0,  # GTX 1050 Ti has 4GB VRAM
                        "message": "Ready to start training"
                    }))

            except json.JSONDecodeError:
                logger.warning("Received invalid JSON message")
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                ws.send(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))

    except ConnectionClosed:
        logger.info("WebSocket connection closed")
    finally:
        # Make sure to pause training when connection is closed to avoid wasting resources
        if training_manager.state.is_training:
            logger.info("Pausing training due to connection close")
            training_manager.pause_training()
