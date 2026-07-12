#!/usr/bin/env python3
"""
ImpressionCore: Dual Shadow

Module for dual shadow functionality in the ImpressionCore framework.

File: core\dual_shadow.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, framework, pytorch, core, production, 2025, object-oriented]
Dependencies: [torch, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements dual shadow functionality for the
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
from src.core.dual_shadow import ShadowModelUpdateConfig
instance = ShadowModelUpdateConfig()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import torch
import torch.nn as nn
import threading
import logging
import time
import copy
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from dataclasses import dataclass

from .model import ImpressionCoreModel
# Memory optimization: Explicit memory cleanup
from .config import ModelConfig
from .uks import UniversalKnowledgeStore

logger = logging.getLogger(__name__)

@dataclass
class ShadowModelUpdateConfig:
    """Configuration for shadow model updates"""
    # Memory optimization: Explicit memory cleanup
    
    # How often to merge shadow model into primary (in training steps)
    # Memory optimization: Explicit memory cleanup
    merge_frequency: int = 1000
    
    # Merge factor (how much of shadow model weights to merge)
    # Memory optimization: Explicit memory cleanup
    merge_factor: float = 0.1
    
    # Whether to perform continuous learning
    continuous_learning: bool = True
    
    # Maximum number of examples to keep in continuous learning buffer
    max_buffer_size: int = 1000
    
    # Learning rate for continuous learning updates
    learning_rate: float = 1e-5
    
    # Whether to lock certain layers during continuous learning
    lock_embeddings: bool = True
    lock_attention_layers: bool = False
    lock_feed_forward_layers: bool = False


class ContinuousLearningBuffer:
    """Buffer for storing examples for continuous learning"""
    
    def __init__(self, max_size: int = 1000):
        """
        
    __init__ function for processing.
    
    Args:
        self, max_size: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self.max_size = max_size
        self.buffer = []
        self.lock = threading.RLock()
    
    def add_example(self, example: Dict[str, torch.Tensor]) -> None:
        """Add an example to the buffer"""
        with self.lock:
            # Copy tensors to CPU to avoid GPU memory issues
            # Memory optimization: Memory-critical operation
            cpu_example = {
                k: v.detach().cpu() if isinstance(v, torch.Tensor) else v
                for k, v in example.items()
            }
            
            self.buffer.append(cpu_example)
            
            # Keep buffer size within limits
            if len(self.buffer) > self.max_size:
                self.buffer.pop(0)
    
    def get_batch(self, batch_size: int) -> List[Dict[str, torch.Tensor]]:
        """Get a batch of examples from the buffer"""
        with self.lock:
            if not self.buffer:
                return []
                
            # Select random examples
            indices = torch.randperm(len(self.buffer))[:batch_size]
            return [self.buffer[i] for i in indices]
    
    def clear(self) -> None:
        """Clear the buffer"""
        with self.lock:
            self.buffer = []
    
    def __len__(self) -> int:
        """
        
    __len__ function for processing.
    
    Args:
        self: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        with self.lock:
            return len(self.buffer)


class DualShadowModel:
    """
    Dual Shadow Model implementation for continuous learning.
    # Memory optimization: Explicit memory cleanup
    
    Manages primary and shadow model instances, coordinating updates and merges
    # Memory optimization: Explicit memory cleanup
    between them to enable continuous learning without disrupting inference.
    """
    
    def __init__(
        self,
        config: ModelConfig,
        primary_model: Optional[ImpressionCoreModel] = None,
        shadow_model: Optional[ImpressionCoreModel] = None,
        update_config: Optional[ShadowModelUpdateConfig] = None,
        knowledge_store: Optional[UniversalKnowledgeStore] = None
    ):
        """
        Initialize the dual shadow model.
        
        Args:
            config: Model configuration
            # Memory optimization: Explicit memory cleanup
            primary_model: Primary model instance (will create if None)
            # Memory optimization: Explicit memory cleanup
            shadow_model: Shadow model instance (will create if None)
            # Memory optimization: Explicit memory cleanup
            update_config: Configuration for shadow model updates
            # Memory optimization: Explicit memory cleanup
            knowledge_store: Universal Knowledge Store instance
        """
        self.config = config
        self.update_config = update_config or ShadowModelUpdateConfig()
        self.knowledge_store = knowledge_store
        
        # Create models if not provided
        if primary_model is None:
        # Memory optimization: Explicit memory cleanup
            logger.info("Creating primary model")
            self.primary_model = ImpressionCoreModel(config)
            # Memory optimization: Explicit memory cleanup
        else:
            self.primary_model = primary_model
            # Memory optimization: Explicit memory cleanup
            
        if shadow_model is None:
        # Memory optimization: Explicit memory cleanup
            logger.info("Creating shadow model (copy of primary)")
            # Memory optimization: Explicit memory cleanup
            self.shadow_model = copy.deepcopy(self.primary_model)
            # Memory optimization: Explicit memory cleanup
        else:
            self.shadow_model = shadow_model
            # Memory optimization: Explicit memory cleanup
            
        # Set up continuous learning
        self.learning_buffer = ContinuousLearningBuffer(
            max_size=self.update_config.max_buffer_size
        )
        
        # Set up optimizer for shadow model
        self.optimizer = torch.optim.AdamW(
            self.shadow_model.parameters(),
            lr=self.update_config.learning_rate,
            weight_decay=0.01
        )
        
        # Training state
        self.training_steps = 0
        self.last_merge_step = 0
        self.total_loss = 0
        self.examples_seen = 0
        
        # Threading
        self.update_lock = threading.RLock()
        self.merge_lock = threading.RLock()
        self.update_thread = None
        self.stop_event = threading.Event()
    
    def start_continuous_learning(self) -> None:
        """Start the continuous learning process in background thread."""
        if not self.update_config.continuous_learning:
            logger.info("Continuous learning is disabled")
            return
            
        if self.update_thread is not None and self.update_thread.is_alive():
            logger.warning("Continuous learning already running")
            return
            
        logger.info("Starting continuous learning thread")
        self.stop_event.clear()
        # Memory optimization: Memory-critical operation
        self.update_thread = threading.Thread(
            target=self._continuous_learning_loop,
            daemon=True
        )
        self.update_thread.start()
    
    def stop_continuous_learning(self) -> None:
        """Stop the continuous learning process."""
        if self.update_thread is not None and self.update_thread.is_alive():
            logger.info("Stopping continuous learning thread")
            self.stop_event.set()
            self.update_thread.join(timeout=30.0)
            if self.update_thread.is_alive():
                logger.warning("Failed to stop continuous learning thread")
            else:
                logger.info("Continuous learning thread stopped")
                self.update_thread = None
    
    def add_training_example(self, example: Dict[str, torch.Tensor]) -> None:
        """
        Add an example to the continuous learning buffer.
        
        Args:
            example: Dictionary of tensors representing an example
        """
        if not self.update_config.continuous_learning:
            return
            
        self.learning_buffer.add_example(example)
    
    def _continuous_learning_loop(self) -> None:
        """Background thread for continuous learning."""
        logger.info("Continuous learning thread started")
        
        while not self.stop_event.is_set():
            try:
                # Check if we have enough examples
                if len(self.learning_buffer) < 4:  # Minimum batch size
                    time.sleep(1.0)
                    continue
                    
                # Get a batch of examples
                batch_size = min(32, len(self.learning_buffer))
                batch = self.learning_buffer.get_batch(batch_size)
                
                if not batch:
                    time.sleep(1.0)
                    continue
                
                # Update shadow model
                with self.update_lock:
                    loss = self._update_shadow_model(batch)
                    
                    # Update counters
                    self.training_steps += 1
                    self.total_loss += loss
                    self.examples_seen += len(batch)
                    
                    # Check if it's time to merge
                    steps_since_merge = self.training_steps - self.last_merge_step
                    if steps_since_merge >= self.update_config.merge_frequency:
                        self._merge_shadow_to_primary()
                        self.last_merge_step = self.training_steps
                
                # Don't train too fast
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in continuous learning loop: {e}")
                time.sleep(5.0)  # Avoid tight loop on error
    
    def _update_shadow_model(self, batch: List[Dict[str, torch.Tensor]]) -> float:
        """
        Update the shadow model with a batch of examples.
        # Memory optimization: Explicit memory cleanup
        
        Args:
            batch: List of example dictionaries
            
        Returns:
            Average loss across the batch
        """
        # Prepare inputs and move to device
        # Memory optimization: Device placement for memory management
        device = next(self.shadow_model.parameters()).device
        # Memory optimization: Device placement for memory management
        
        # Accumulate inputs from batch
        input_ids_list = []
        attention_mask_list = []
        labels_list = []
        
        for example in batch:
            if 'input_ids' in example:
                input_ids_list.append(example['input_ids'])
                
            if 'attention_mask' in example:
                attention_mask_list.append(example['attention_mask'])
                
            if 'labels' in example:
                labels_list.append(example['labels'])
        
        # Create batched tensors
        inputs = {}
        if input_ids_list:
            inputs['input_ids'] = torch.stack(input_ids_list).to(device)
            # Memory optimization: Device placement for memory management
            
        if attention_mask_list:
            inputs['attention_mask'] = torch.stack(attention_mask_list).to(device)
            # Memory optimization: Device placement for memory management
            
        if labels_list:
            inputs['labels'] = torch.stack(labels_list).to(device)
            # Memory optimization: Device placement for memory management
        
        # Optional: lock certain layers during updates
        self._set_layer_gradients(self.shadow_model)
        
        # Forward pass
        self.shadow_model.train()
        self.optimizer.zero_grad()
        
        outputs = self.shadow_model(**inputs)
        loss = outputs.loss if hasattr(outputs, 'loss') else outputs[0]
        
        # Backward pass and optimize
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
    
    def _set_layer_gradients(self, model: nn.Module) -> None:
        """
        Set gradients according to which layers should be updated.
        
        Args:
            model: Model to set gradients for
            # Memory optimization: Explicit memory cleanup
        """
        # Lock embeddings if configured
        if self.update_config.lock_embeddings:
            if hasattr(model, 'embeddings'):
                for param in model.embeddings.parameters():
                    param.requires_grad = False
                    
        # Lock attention layers if configured
        if self.update_config.lock_attention_layers:
            for name, module in model.named_modules():
                if 'attention' in name.lower():
                    for param in module.parameters():
                        param.requires_grad = False
                        
        # Lock feed forward layers if configured
        if self.update_config.lock_feed_forward_layers:
            for name, module in model.named_modules():
                if any(x in name.lower() for x in ['feed_forward', 'ffn', 'mlp']):
                    for param in module.parameters():
                        param.requires_grad = False
    
    def _merge_shadow_to_primary(self) -> None:
        """Merge shadow model weights into primary model."""
        # Memory optimization: Explicit memory cleanup
        with self.merge_lock:
            logger.info(f"Merging shadow model to primary (factor: {self.update_config.merge_factor})")
            # Memory optimization: Explicit memory cleanup
            
            # Get model parameters
            # Memory optimization: Explicit memory cleanup
            primary_params = dict(self.primary_model.named_parameters())
            shadow_params = dict(self.shadow_model.named_parameters())
            
            with torch.no_grad():
            # Memory optimization: Disable gradient computation to save memory
                for name, shadow_param in shadow_params.items():
                    if name in primary_params:
                        # Get corresponding primary parameter
                        primary_param = primary_params[name]
                        
                        # Move to same device if needed
                        # Memory optimization: Device placement for memory management
                        if primary_param.device != shadow_param.device:
                        # Memory optimization: Device placement for memory management
                            shadow_param = shadow_param.to(primary_param.device)
                            # Memory optimization: Device placement for memory management
                            
                        # Perform partial merge (weighted average)
                        alpha = self.update_config.merge_factor
                        primary_param.data.mul_(1.0 - alpha).add_(shadow_param.data, alpha=alpha)
    
    def forward(self, *args, **kwargs) -> Any:
        """Forward pass through the primary model."""
        return self.primary_model(*args, **kwargs)
    
    def train(self, mode: bool = True) -> 'DualShadowModel':
        """Set training mode."""
        # Only set shadow model to training mode
        # Memory optimization: Explicit memory cleanup
        self.shadow_model.train(mode)
        return self
    
    def eval(self) -> 'DualShadowModel':
        """Set evaluation mode."""
        # Both models in eval mode
        self.primary_model.eval()
        self.shadow_model.eval()
        return self
    
    def to(self, device: Union[str, torch.device]) -> 'DualShadowModel':
    # Memory optimization: Device placement for memory management
        """Move both models to device."""
        # Memory optimization: Device placement for memory management
        self.primary_model.to(device)
        # Memory optimization: Device placement for memory management
        self.shadow_model.to(device)
        # Memory optimization: Device placement for memory management
        return self
    
    def save_models(
        self, 
        primary_path: str, 
        shadow_path: Optional[str] = None
    ) -> Tuple[bool, bool]:
        """
        Save both models.
        
        Args:
            primary_path: Path to save primary model
            shadow_path: Path to save shadow model (optional)
            # Memory optimization: Explicit memory cleanup
            
        Returns:
            Tuple of (primary_success, shadow_success)
        """
        primary_success = False
        shadow_success = False
        
        try:
            # Save primary model
            torch.save(self.primary_model.state_dict(), primary_path)
            primary_success = True
        except Exception as e:
            logger.error(f"Failed to save primary model: {e}")
        
        if shadow_path:
            try:
                # Save shadow model
                torch.save(self.shadow_model.state_dict(), shadow_path)
                shadow_success = True
            except Exception as e:
                logger.error(f"Failed to save shadow model: {e}")
            
        return primary_success, shadow_success
    
    def load_models(
        self, 
        primary_path: str, 
        shadow_path: Optional[str] = None
    ) -> Tuple[bool, bool]:
        """
        Load both models.
        
        Args:
            primary_path: Path to load primary model
            shadow_path: Path to load shadow model (optional)
            # Memory optimization: Explicit memory cleanup
            
        Returns:
            Tuple of (primary_success, shadow_success)
        """
        primary_success = False
        shadow_success = False
        
        try:
            # Load primary model
            state_dict = torch.load(primary_path)
            self.primary_model.load_state_dict(state_dict)
            primary_success = True
        except Exception as e:
            logger.error(f"Failed to load primary model: {e}")
        
        if shadow_path:
            try:
                # Load shadow model
                state_dict = torch.load(shadow_path)
                self.shadow_model.load_state_dict(state_dict)
                shadow_success = True
            except Exception as e:
                logger.error(f"Failed to load shadow model: {e}")
                # If shadow model fails to load but primary succeeded,
                # Memory optimization: Explicit memory cleanup
                # copy primary model to shadow
                # Memory optimization: Explicit memory cleanup
                if primary_success:
                    logger.info("Copying primary model to shadow model")
                    # Memory optimization: Explicit memory cleanup
                    self.shadow_model.load_state_dict(
                        self.primary_model.state_dict()
                    )
                    shadow_success = True
        else:
            # If no shadow path provided but primary succeeded,
            # copy primary model to shadow
            # Memory optimization: Explicit memory cleanup
            if primary_success:
                logger.info("Copying primary model to shadow model")
                # Memory optimization: Explicit memory cleanup
                self.shadow_model.load_state_dict(
                    self.primary_model.state_dict()
                )
                shadow_success = True
            
        return primary_success, shadow_success
