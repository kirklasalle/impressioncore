# Lora Migration Guide

**Created:** May 04, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\lora-migration-guide.md #api #attention_mechanism #deployment #docs\reference\lora_migration_guide.md #documentation #memory_management #testing  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# LoRA Enhancement Migration Guide

## Overview

This document provides detailed technical guidance for migrating the current single-file LoRA implementation to the new modular package structure while maintaining backward compatibility. Following these steps will ensure a smooth transition and allow for incremental implementation of the enhanced features.

## Step 1: Create Package Structure

First, create the directory structure for the new LoRA package:

```bash
mkdir -p src/models/lora
touch src/models/lora/__init__.py
touch src/models/lora/base.py
touch src/models/lora/interfaces.py
touch src/models/lora/utils.py
```

## Step 2: Define Core Interfaces

Define the common interfaces that all LoRA variants will implement:

```python
# src/models/lora/interfaces.py

from typing import Dict, List, Optional, Protocol, Set, TypeVar, Union
import torch
import torch.nn as nn

T = TypeVar('T', bound=nn.Module)

class LoRALayerInterface(Protocol):
    """Interface for all LoRA layer implementations."""
    
    base_layer: nn.Module
    rank: int
    alpha: float
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass including adaptation."""
        ...
    
    def merge_weights(self) -> nn.Module:
        """Merge adapter weights with base weights."""
        ...
    
    def get_delta_weights(self) -> torch.Tensor:
        """Get weight delta introduced by adaptation."""
        ...

class LoRAConfigInterface(Protocol):
    """Interface for all LoRA configuration classes."""
    
    rank: int
    alpha: float
    dropout_p: float
    target_modules: Optional[List[str]]
    use_bias: bool
    module_filter: Optional[str]

class LoRAModelInterface(Protocol):
    """Interface for all LoRA model implementations."""
    
    base_model: nn.Module
    config: LoRAConfigInterface
    lora_layers: Dict[str, nn.Module]
    
    def _apply_lora_layers(self) -> None:
        """Apply LoRA layers to the base model."""
        ...
    
    def _freeze_non_lora_params(self) -> None:
        """Freeze all parameters except LoRA parameters."""
        ...
    
    def merge_and_unload(self) -> nn.Module:
        """Merge LoRA weights with base weights and return the base model."""
        ...
    
    def get_trainable_parameters(self) -> int:
        """Get the count of trainable parameters."""
        ...
    
    def estimate_memory_savings(self) -> Dict[str, float]:
        """Estimate memory savings from using LoRA."""
        ...
```

## Step 3: Migrate Core Functionality

Move the existing code from `lora.py` to the appropriate files in the new package:

```python
# src/models/lora/base.py

import torch
import torch.nn as nn
import torch.nn.functional as F
import logging
import math
from typing import List, Dict, Tuple, Optional, Union, Set
import re
import copy
import warnings

logger = logging.getLogger(__name__)

# Copy LoRALayer, LoRAConfig, and LoRAModel from the original file
# Ensure they implement the interfaces from interfaces.py

# ...

```

```python
# src/models/lora/utils.py

import torch
import torch.nn as nn
from typing import Dict, List, Optional

# Copy _find_layers and any other utility functions from the original file

# ...
```

## Step 4: Create Package Exports

Set up the package exports in the `__init__.py` file:

```python
# src/models/lora/__init__.py

from .base import LoRALayer, LoRAConfig, LoRAModel, apply_lora
from .utils import _find_layers

# Export core functionality with the same names as the original module
__all__ = [
    'LoRALayer', 
    'LoRAConfig', 
    'LoRAModel', 
    'apply_lora',
    '_find_layers'
]
```

## Step 5: Update Original File as Compatibility Layer

Modify the original `lora.py` file to import from the new package structure while maintaining the exact same API:

```python
# src/models/lora.py

"""
Memory-efficient Low-Rank Adaptation (LoRA) implementation for ImpressionCore.

This module provides a flexible, memory-efficient implementation of LoRA
with the following features:

1. Parameterized rank for controlling adaptation capacity and memory usage
2. Support for different adaptation targets (e.g., attention, MLP layers)
3. Memory usage optimization for low-VRAM devices
4. Weight merging utilities for deployment
5. Selective unfreezing of parameters

References:
    - LoRA: Low-Rank Adaptation of Large Language Models (Hu et al., 2021)
"""

# Import from the new package structure
from src.models.lora.base import LoRALayer, LoRAConfig, LoRAModel, apply_lora
from src.models.lora.utils import _find_layers

# Re-export everything with the same names
__all__ = [
    'LoRALayer', 
    'LoRAConfig', 
    'LoRAModel', 
    'apply_lora',
    '_find_layers'
]
```

## Step 6: Add Feature Detection to Base Classes

Update the base classes to detect and use enhanced features when available:

```python
# Example addition to src/models/lora/base.py

class LoRAConfig:
    # ...existing implementation...
    
    def create_model(self, base_model: nn.Module) -> 'LoRAModel':
        """
        Factory method to create the most appropriate LoRA model based on configuration.
        
        This method will check for feature flags and return the appropriate model implementation.
        """
        # Check for enhanced features
        if hasattr(self, 'enable_quantization') and self.enable_quantization:
            # Import here to avoid circular imports
            from .quantization import QLoRAModel
            return QLoRAModel(base_model, self)
        
        # Fall back to standard LoRA
        return LoRAModel(base_model, self)
```

## Step 7: Add Enhanced Configuration Class

Create an enhanced configuration class that includes feature flags:

```python
# src/models/lora/base.py (addition)

class EnhancedLoRAConfig(LoRAConfig):
    """Extended LoRA configuration with support for enhancements."""
    
    def __init__(
        self,
        # Base LoRA parameters
        rank: int = 8,
        alpha: float = 16.0,
        dropout_p: float = 0.0,
        target_modules: Optional[List[str]] = None,
        use_bias: bool = False,
        module_filter: Optional[str] = None,
        # Feature flags
        enable_quantization: bool = False,
        enable_hierarchical: bool = False,
        enable_dynamic_rank: bool = False,
        enable_composition: bool = False,
        enable_sparsity: bool = False,
        # Enhancement-specific parameters
        # (Will be added as each enhancement is implemented)
    ):
        # Initialize base parameters
        super().__init__(
            rank=rank,
            alpha=alpha,
            dropout_p=dropout_p,
            target_modules=target_modules,
            use_bias=use_bias,
            module_filter=module_filter
        )
        
        # Initialize feature flags
        self.enable_quantization = enable_quantization
        self.enable_hierarchical = enable_hierarchical
        self.enable_dynamic_rank = enable_dynamic_rank
        self.enable_composition = enable_composition
        self.enable_sparsity = enable_sparsity
        
        # Validate feature combinations
        self._validate_features()
    
    def _validate_features(self):
        """Validate feature combinations and raise warnings for incompatible features."""
        if self.enable_hierarchical and self.enable_dynamic_rank:
            warnings.warn(
                "Both hierarchical and dynamic rank features are enabled. "
                "These features may conflict. Consider using only one of them."
            )
```

## Step 8: Update Factory Function

Update the `apply_lora` factory function to support the enhanced features:

```python
# src/models/lora/base.py (modified)

def apply_lora(
    model: nn.Module,
    rank: int = 8,
    alpha: int = 16,
    dropout_p: float = 0.0,
    target_modules: Optional[List[str]] = None,
    # Enhancement flags and parameters
    enable_enhancements: bool = False,
    **enhancement_kwargs
) -> LoRAModel:
    """
    Apply LoRA to a model for efficient fine-tuning.
    
    Args:
        model: Model to apply LoRA to
        rank: Rank of low-rank decomposition
        alpha: Scaling factor for LoRA
        dropout_p: Dropout probability for LoRA
        target_modules: List of module types to apply LoRA to
        enable_enhancements: Whether to enable enhanced LoRA features
        **enhancement_kwargs: Additional keyword arguments for enhanced features
        
    Returns:
        Model wrapped with LoRA or an enhanced variant
    """
    if enable_enhancements:
        config = EnhancedLoRAConfig(
            rank=rank,
            alpha=alpha,
            dropout_p=dropout_p,
            target_modules=target_modules,
            **enhancement_kwargs
        )
        # Let the config create the appropriate model
        return config.create_model(model)
    else:
        # Use original behavior for backward compatibility
        config = LoRAConfig(
            rank=rank,
            alpha=alpha,
            dropout_p=dropout_p,
            target_modules=target_modules
        )
        return LoRAModel(model, config)
```

## Step 9: Create a Test Plan

Create a comprehensive test plan to ensure backward compatibility:

```python
# tests/models/test_lora_migration.py

import unittest
import torch
import torch.nn as nn

# Import from both the original and new locations
import src.models.lora as lora_original
from src.models.lora import LoRALayer, LoRAConfig, LoRAModel, apply_lora

class TestMigrationCompatibility(unittest.TestCase):
    """Test compatibility between original and new LoRA implementations."""
    
    def setUp(self):
        # Create a simple model for testing
        self.model = nn.Sequential(
            nn.Linear(10, 10, bias=True),
            nn.ReLU(),
            nn.Linear(10, 10, bias=True)
        )
        # Create random input
        self.input = torch.randn(2, 10)
    
    def test_original_imports_work(self):
        """Test that imports from the original module still work."""
        # Apply LoRA using the original import
        lora_model = lora_original.apply_lora(
            self.model,
            rank=4,
            alpha=8
        )
        # Check that it's the expected type
        self.assertIsInstance(lora_model, lora_original.LoRAModel)
    
    def test_new_imports_work(self):
        """Test that imports from the new module work."""
        # Apply LoRA using the new import
        lora_model = apply_lora(
            self.model,
            rank=4,
            alpha=8
        )
        # Check that it's the expected type
        self.assertIsInstance(lora_model, LoRAModel)
    
    def test_behavior_is_identical(self):
        """Test that the behavior is identical between old and new implementations."""
        # Apply LoRA using both imports
        lora_model_original = lora_original.apply_lora(
            self.model,
            rank=4,
            alpha=8
        )
        lora_model_new = apply_lora(
            self.model,
            rank=4,
            alpha=8
        )
        
        # Set both to eval mode for consistent behavior
        lora_model_original.eval()
        lora_model_new.eval()
        
        # Run both models with the same input
        with torch.no_grad():
            output_original = lora_model_original(self.input)
            output_new = lora_model_new(self.input)
        
        # Outputs should be identical
        self.assertTrue(torch.allclose(output_original, output_new))
```

## Step 10: Integration with Trainer

Update the `ModelTrainer` class to support enhanced LoRA features:

```python
# Example addition to src/models/trainer.py

def setup_enhanced_lora_fine_tuning(
    self,
    # Base parameters
    rank=4,
    alpha=8,
    target_modules=None,
    lora_dropout=0.0,
    # Enhancement flags
    enable_quantization=False,
    enable_hierarchical=False,
    enable_dynamic_rank=False,
    enable_composition=False,
    enable_sparsity=False,
    # Enhancement-specific parameters
    memory_constraint=4.0,  # GB, for dynamic rank
    **kwargs
):
    """
    Set up enhanced LoRA fine-tuning with selected features.
    
    Args:
        rank: Base LoRA rank (or starting point for dynamic/hierarchical)
        alpha: LoRA alpha parameter (scaling)
        target_modules: List of module names to apply LoRA to
        lora_dropout: Dropout probability for LoRA layers
        enable_quantization: Whether to enable 4-bit quantization
        enable_hierarchical: Whether to use hierarchical rank patterns
        enable_dynamic_rank: Whether to automatically determine optimal ranks
        enable_composition: Whether to enable adapter composition
        enable_sparsity: Whether to apply weight pruning
        memory_constraint: Memory constraint for dynamic rank selection (GB)
        **kwargs: Additional enhancement-specific parameters
        
    Returns:
        The model configured with enhanced LoRA adapters
    """
    try:
        # Import the enhanced LoRA package
        from src.models.lora import apply_lora
        
        # Log which enhancements are enabled
        enabled_features = []
        if enable_quantization: enabled_features.append("QLoRA")
        if enable_hierarchical: enabled_features.append("Hierarchical LoRA")
        if enable_dynamic_rank: enabled_features.append("Dynamic Rank Selection")
        if enable_composition: enabled_features.append("LoRA Composition")
        if enable_sparsity: enabled_features.append("Sparsity Integration")
        
        if enabled_features:
            logger.info(f"Setting up enhanced LoRA with: {', '.join(enabled_features)}")
        else:
            logger.info("Setting up standard LoRA (no enhancements enabled)")
        
        # Apply enhanced LoRA to the model
        lora_model = apply_lora(
            self.model,
            rank=rank,
            alpha=alpha,
            dropout_p=lora_dropout,
            target_modules=target_modules,
            enable_enhancements=bool(enabled_features),
            # Enhancement flags
            enable_quantization=enable_quantization,
            enable_hierarchical=enable_hierarchical,
            enable_dynamic_rank=enable_dynamic_rank,
            enable_composition=enable_composition,
            enable_sparsity=enable_sparsity,
            # Enhancement-specific parameters
            memory_constraint=memory_constraint,
            **kwargs
        )
        
        # Update model reference
        self.model = lora_model
        self.using_lora = True
        self.using_enhanced_lora = bool(enabled_features)
        
        # Count trainable parameters
        trainable_params = lora_model.get_trainable_parameters()
        total_params = sum(p.numel() for p in lora_model.parameters())
        logger.info(f"LoRA fine-tuning enabled with {len(enabled_features)} enhancements")
        logger.info(f"Trainable parameters: {trainable_params:,} ({trainable_params/total_params:.2%} of total)")
        
        # Estimate memory savings
        memory_stats = lora_model.estimate_memory_savings()
        logger.info(f"Estimated memory savings: {memory_stats['memory_savings_mb']:.2f} MB")
        
        return lora_model
    except ImportError as e:
        logger.error(f"Could not import enhanced LoRA package: {e}")
        # Fall back to regular LoRA setup
        logger.info("Falling back to standard LoRA setup")
        return self.setup_lora_fine_tuning(
            rank=rank,
            alpha=alpha,
            target_modules=target_modules,
            lora_dropout=lora_dropout
        )
```

## Migration Checklist

Use this checklist to ensure all aspects of the migration are completed:

1. [ ] Create package directory structure
2. [ ] Define interfaces in `interfaces.py`
3. [ ] Move core functionality to `base.py` and `utils.py`
4. [ ] Set up package exports in `__init__.py`
5. [ ] Update original `lora.py` as a compatibility layer
6. [ ] Add feature detection to base classes
7. [ ] Create enhanced configuration class
8. [ ] Update factory functions to support enhancements
9. [ ] Create and run test plan
10. [ ] Update `ModelTrainer` to support enhanced features
11. [ ] Implement individual enhancements in their respective files

## Best Practices During Migration

1. **Incremental Changes**: Commit after each step to enable easy rollback if needed
2. **Continuous Testing**: Run tests after each step to catch compatibility issues early
3. **Documentation Updates**: Update documentation to reflect new package structure
4. **Feature Flags**: Use feature flags to gradually enable new capabilities
5. **Deprecation Warnings**: Use warnings to indicate future API changes without breaking existing code

By following this migration guide, you'll establish a clean, modular architecture for the enhanced LoRA implementations while ensuring backward compatibility with existing code that uses the current implementation.
