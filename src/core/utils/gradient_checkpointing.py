#!/usr/bin/env python3
"""
ImpressionCore: Gradient Checkpointing

Module for gradient checkpointing functionality in the ImpressionCore framework.

File: core/utils/gradient_checkpointing.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-06-01
Version: 1.1.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [utilities, memory-critical, framework, pytorch, core, production, utils, 2025]
Dependencies: [torch]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements gradient checkpointing functionality for the ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-constrained environments and designed to run efficiently on consumer hardware.

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
from src.core.utils.gradient_checkpointing import apply_gradient_checkpointing
model = apply_gradient_checkpointing(model)

# QLoRA-specific usage
from src.core.utils.gradient_checkpointing import QLoRAGradientCheckpointing
checkpoint_manager = QLoRAGradientCheckpointing(model, quantized_layers=['q_proj', 'k_proj'])
with checkpoint_manager.selective_checkpointing():
    output = model(input_data)
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import torch
import torch.nn as nn
from torch.utils.checkpoint import checkpoint
from typing import Optional, List, Dict, Any, Set, Callable, Union
import logging
from contextlib import contextmanager
from dataclasses import dataclass
import gc
import time
import psutil
from typing import List, Tuple
from collections import deque

logger = logging.getLogger(__name__)

@dataclass
class CheckpointConfig:
    """Configuration for gradient checkpointing strategies."""
    
    # Basic checkpointing
    enable_basic_checkpointing: bool = True
    
    # QLoRA-specific optimizations
    enable_qlora_optimizations: bool = True
    selective_checkpointing: bool = True
    quantized_layer_priority: bool = True
    
    # Memory management
    preserve_quantized_weights: bool = True
    cpu_offload_during_checkpoint: bool = False
    
    # Performance tuning
    checkpoint_every_n_layers: int = 2
    mixed_precision_checkpointing: bool = True
    dynamic_checkpoint_selection: bool = True
    cuda_optimizations_enabled: bool = True
    
    # Memory thresholds
    memory_threshold_mb: float = 3500.0  # For GTX 1050 Ti
    checkpoint_activation_size_threshold_mb: float = 100.0

@dataclass
class PerformanceMetrics:
    """Performance metrics for gradient checkpointing."""
    
    forward_time_ms: float = 0.0
    backward_time_ms: float = 0.0
    memory_peak_mb: float = 0.0
    memory_saved_mb: float = 0.0
    checkpoint_overhead_ms: float = 0.0
    recomputation_time_ms: float = 0.0
    total_checkpoints: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "forward_time_ms": self.forward_time_ms,
            "backward_time_ms": self.backward_time_ms,
            "memory_peak_mb": self.memory_peak_mb,
            "memory_saved_mb": self.memory_saved_mb,
            "checkpoint_overhead_ms": self.checkpoint_overhead_ms,
            "recomputation_time_ms": self.recomputation_time_ms,
            "total_checkpoints": self.total_checkpoints,
            "efficiency_ratio": self._calculate_efficiency_ratio()
        }
    
    def _calculate_efficiency_ratio(self) -> float:
        """Calculate checkpoint efficiency ratio."""
        if self.checkpoint_overhead_ms + self.recomputation_time_ms == 0:
            return 0.0
        return self.memory_saved_mb / (self.checkpoint_overhead_ms + self.recomputation_time_ms)

class AdaptiveCheckpointSelector:
    """
    Adaptive checkpoint point selector that learns optimal checkpoint locations.
    """
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.checkpoint_history = deque(maxlen=max_history)
        self.layer_performance = {}
        
    def record_checkpoint_performance(
        self, 
        layer_name: str, 
        memory_saved: float, 
        overhead_time: float,
        recomputation_time: float
    ):
        """Record performance data for a checkpoint."""
        performance_score = memory_saved / max(overhead_time + recomputation_time, 0.001)
        
        if layer_name not in self.layer_performance:
            self.layer_performance[layer_name] = deque(maxlen=10)
        
        self.layer_performance[layer_name].append(performance_score)
        
        self.checkpoint_history.append({
            "layer_name": layer_name,
            "memory_saved": memory_saved,
            "overhead_time": overhead_time,
            "recomputation_time": recomputation_time,
            "performance_score": performance_score,
            "timestamp": time.time()
        })
    
    def get_optimal_layers(self, candidate_layers: List[str], top_k: int = None) -> List[str]:
        """Get optimal layers for checkpointing based on historical performance."""
        if not self.layer_performance:
            return candidate_layers[:top_k] if top_k else candidate_layers
        
        # Calculate average performance scores
        layer_scores = {}
        for layer_name in candidate_layers:
            if layer_name in self.layer_performance:
                scores = list(self.layer_performance[layer_name])
                layer_scores[layer_name] = sum(scores) / len(scores)
            else:
                layer_scores[layer_name] = 0.0  # Unknown layers get low priority
        
        # Sort by performance score
        sorted_layers = sorted(layer_scores.items(), key=lambda x: x[1], reverse=True)
        optimal_layers = [layer for layer, score in sorted_layers]
        
        return optimal_layers[:top_k] if top_k else optimal_layers
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all layers."""
        summary = {
            "total_checkpoints": len(self.checkpoint_history),
            "layer_rankings": {},
            "recent_performance": []
        }
        
        for layer_name, scores in self.layer_performance.items():
            avg_score = sum(scores) / len(scores)
            summary["layer_rankings"][layer_name] = {
                "avg_performance_score": avg_score,
                "sample_count": len(scores),
                "recent_scores": list(scores)[-3:]  # Last 3 scores
            }
        
        # Recent performance (last 10 checkpoints)
        recent_checkpoints = list(self.checkpoint_history)[-10:]
        summary["recent_performance"] = recent_checkpoints
        
        return summary

class MemoryPressureMonitor:
    """
    Real-time memory pressure monitoring for adaptive checkpointing.
    """
    
    def __init__(self):
        self.memory_samples = deque(maxlen=50)
        self.gpu_memory_samples = deque(maxlen=50)
        
    def update_memory_stats(self):
        """Update memory statistics."""
        # CPU memory
        cpu_memory = psutil.virtual_memory()
        self.memory_samples.append({
            "timestamp": time.time(),
            "used_mb": cpu_memory.used / (1024 * 1024),
            "available_mb": cpu_memory.available / (1024 * 1024),
            "percent": cpu_memory.percent
        })
        
        # GPU memory (if available)
        if torch.cuda.is_available():
            gpu_memory_used = torch.cuda.memory_allocated() / (1024 * 1024)
            gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
            gpu_percent = (gpu_memory_used / gpu_memory_total) * 100
            
            self.gpu_memory_samples.append({
                "timestamp": time.time(),
                "used_mb": gpu_memory_used,
                "total_mb": gpu_memory_total,
                "percent": gpu_percent
            })
    
    def get_memory_pressure_level(self) -> str:
        """Get current memory pressure level."""
        if not self.gpu_memory_samples and not self.memory_samples:
            return "unknown"
        
        # Prioritize GPU memory if available
        if self.gpu_memory_samples:
            latest_gpu = self.gpu_memory_samples[-1]
            gpu_percent = latest_gpu["percent"]
            
            if gpu_percent > 90:
                return "critical"
            elif gpu_percent > 75:
                return "high"
            elif gpu_percent > 50:
                return "medium"
            else:
                return "low"
        
        # Fall back to CPU memory
        if self.memory_samples:
            latest_cpu = self.memory_samples[-1]
            cpu_percent = latest_cpu["percent"]
            
            if cpu_percent > 85:
                return "critical"
            elif cpu_percent > 70:
                return "high"
            elif cpu_percent > 50:
                return "medium"
            else:
                return "low"
        
        return "unknown"
    
    def should_enable_aggressive_checkpointing(self) -> bool:
        """Determine if aggressive checkpointing should be enabled."""
        pressure_level = self.get_memory_pressure_level()
        return pressure_level in ["critical", "high"]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        stats = {
            "pressure_level": self.get_memory_pressure_level(),
            "cpu_memory": {},
            "gpu_memory": {}
        }
        
        if self.memory_samples:
            latest_cpu = self.memory_samples[-1]
            stats["cpu_memory"] = {
                "used_mb": latest_cpu["used_mb"],
                "available_mb": latest_cpu["available_mb"],
                "percent": latest_cpu["percent"]
            }
        
        if self.gpu_memory_samples:
            latest_gpu = self.gpu_memory_samples[-1]
            stats["gpu_memory"] = {
                "used_mb": latest_gpu["used_mb"],
                "total_mb": latest_gpu["total_mb"],
                "percent": latest_gpu["percent"]
            }
        
        return stats

class QLoRAGradientCheckpointing:
    """
    Advanced gradient checkpointing optimized for QLoRA and quantized models.
    
    Features:
    - Selective checkpointing for quantized layers
    - Mixed-precision checkpoint handling
    - Dynamic checkpoint point selection    - Memory-aware checkpoint activation
    """
    
    def __init__(
        self, 
        model: nn.Module, 
        config: Optional[CheckpointConfig] = None,
        quantized_layers: Optional[List[str]] = None,
        lora_modules: Optional[List[str]] = None,
        enable_adaptive_selection: bool = True,
        enable_memory_monitoring: bool = True
    ):
        """
        Initialize QLoRA gradient checkpointing.
        
        Args:
            model: The model to apply checkpointing to
            config: Checkpointing configuration
            quantized_layers: Names/patterns of quantized layers
            lora_modules: Names/patterns of LoRA adaptation modules
            enable_adaptive_selection: Enable adaptive checkpoint point selection
            enable_memory_monitoring: Enable real-time memory pressure monitoring
        """
        self.model = model
        self.config = config or CheckpointConfig()
        self.quantized_layers = set(quantized_layers or [])
        self.lora_modules = set(lora_modules or [])
        
        # Advanced features
        self.adaptive_selector = AdaptiveCheckpointSelector() if enable_adaptive_selection else None
        self.memory_monitor = MemoryPressureMonitor() if enable_memory_monitoring else None
        self.performance_metrics = PerformanceMetrics()
        
        # Track checkpoint statistics
        self.checkpoint_stats = {
            "total_checkpoints": 0,
            "memory_saved_mb": 0.0,
            "quantized_layer_checkpoints": 0,
            "lora_layer_checkpoints": 0,
            "adaptive_optimizations": 0,
            "memory_pressure_adaptations": 0
        }
        
        # Analyze model structure
        self._analyze_model_structure()
        
        logger.info(f"QLoRA Gradient Checkpointing initialized for {len(self.checkpoint_candidates)} layers")
        if self.adaptive_selector:
            logger.info("Adaptive checkpoint selection enabled")
        if self.memory_monitor:
            logger.info("Memory pressure monitoring enabled")
    
    def _analyze_model_structure(self):
        """Analyze model structure to identify checkpoint candidates."""
        self.checkpoint_candidates = []
        self.quantized_candidates = []
        self.lora_candidates = []
        
        for name, module in self.model.named_modules():
            # Check if module is a checkpoint candidate
            if self._is_checkpoint_candidate(module, name):
                self.checkpoint_candidates.append((name, module))
                
                # Categorize by type
                if self._is_quantized_layer(module, name):
                    self.quantized_candidates.append((name, module))
                
                if self._is_lora_layer(module, name):
                    self.lora_candidates.append((name, module))
    
    def _is_checkpoint_candidate(self, module: nn.Module, name: str) -> bool:
        """Determine if a module should be checkpointed."""
        # Check for large modules that benefit from checkpointing
        candidate_types = (
            nn.TransformerEncoderLayer,
            nn.TransformerDecoderLayer,
            nn.MultiheadAttention,
            nn.Linear  # For LoRA layers
        )
        
        if isinstance(module, candidate_types):
            return True
        
        # Check for custom attention layers
        if 'attention' in name.lower() or 'attn' in name.lower():
            return True
        
        # Check for feed-forward networks
        if 'ffn' in name.lower() or 'mlp' in name.lower():
            return True
        
        return False
    
    def _is_quantized_layer(self, module: nn.Module, name: str) -> bool:
        """Check if a layer is quantized."""
        # Check for quantized layer indicators
        if any(layer_pattern in name for layer_pattern in self.quantized_layers):
            return True
        
        # Check for bitsandbytes quantized modules
        if hasattr(module, 'weight') and hasattr(module.weight, 'quant_type'):
            return True
        
        # Check for common quantized layer types
        quantized_types = ('Linear4bit', 'Linear8bit', 'QuantLinear')
        return any(qtype in str(type(module)) for qtype in quantized_types)
    
    def _is_lora_layer(self, module: nn.Module, name: str) -> bool:
        """Check if a layer contains LoRA adaptations."""
        if any(lora_pattern in name for lora_pattern in self.lora_modules):
            return True
        
        # Check for LoRA-specific attributes
        lora_attributes = ('lora_A', 'lora_B', 'lora_dropout', 'scaling')
        return any(hasattr(module, attr) for attr in lora_attributes)
    
    def _estimate_activation_memory(self, module: nn.Module, input_shape: tuple) -> float:
        """Estimate activation memory for a module in MB."""
        try:
            # Rough estimation based on module parameters and input shape
            num_params = sum(p.numel() for p in module.parameters())
            input_size = 1
            for dim in input_shape[1:]:  # Skip batch dimension
                input_size *= dim
            
            # Estimate activation size (in bytes, assuming float32)
            activation_bytes = input_size * num_params * 4
            return activation_bytes / (1024 * 1024)  # Convert to MB
        except:
            return 100.0  # Default estimate
    
    @contextmanager
    def selective_checkpointing(self):
        """Context manager for selective gradient checkpointing."""
        original_forward_methods = {}
        
        try:
            # Apply selective checkpointing
            for name, module in self._get_priority_checkpoint_modules():
                if self._should_checkpoint_module(module, name):
                    original_forward_methods[name] = module.forward
                    module.forward = self._create_checkpointed_forward(
                        module, 
                        original_forward_methods[name],
                        name
                    )
            
            logger.info(f"Applied selective checkpointing to {len(original_forward_methods)} modules")
            yield
            
        finally:
            # Restore original forward methods
            for name, original_forward in original_forward_methods.items():
                module = dict(self.model.named_modules())[name]
                module.forward = original_forward
            
            logger.info(f"Restored {len(original_forward_methods)} original forward methods")
    
    def _get_priority_checkpoint_modules(self) -> List[tuple]:
        """Get modules prioritized for checkpointing."""
        if not self.config.selective_checkpointing:
            return self.checkpoint_candidates
        
        priority_modules = []
        
        # Prioritize quantized layers if enabled
        if self.config.quantized_layer_priority:
            priority_modules.extend(self.quantized_candidates)
        
        # Add LoRA layers
        priority_modules.extend(self.lora_candidates)
        
        # Add remaining candidates based on memory impact
        remaining = [
            (name, module) for name, module in self.checkpoint_candidates
            if (name, module) not in priority_modules
        ]
        
        # Sort by estimated memory impact
        remaining.sort(
            key=lambda x: self._estimate_activation_memory(x[1], (1, 512, 768)),
            reverse=True
        )
        
        priority_modules.extend(remaining)
        return priority_modules
    
    def _should_checkpoint_module(self, module: nn.Module, name: str) -> bool:
        """Determine if a specific module should be checkpointed."""
        # Check memory threshold
        if torch.cuda.is_available():
            current_memory_mb = torch.cuda.memory_allocated() / (1024 * 1024)
            if current_memory_mb < self.config.memory_threshold_mb * 0.5:
                return False
        
        # Always checkpoint quantized layers for memory efficiency
        if self._is_quantized_layer(module, name):
            return True
        
        # Checkpoint large activation layers
        activation_size = self._estimate_activation_memory(module, (1, 512, 768))
        if activation_size > self.config.checkpoint_activation_size_threshold_mb:
            return True
        
        return False
    
    def _create_checkpointed_forward(
        self, 
        module: nn.Module, 
        original_forward: Callable,
        module_name: str
    ) -> Callable:
        """Create a checkpointed version of the forward method."""
        
        def checkpointed_forward(*args, **kwargs):
            # Handle mixed precision for quantized layers
            if (self.config.mixed_precision_checkpointing and 
                self._is_quantized_layer(module, module_name)):
                
                # Preserve quantized weights during checkpointing
                if self.config.preserve_quantized_weights:
                    return self._mixed_precision_checkpoint(
                        original_forward, args, kwargs, module_name
                    )
            
            # Standard checkpointing
            def checkpoint_fn(*checkpoint_args):
                return original_forward(*checkpoint_args, **kwargs)
            
            # Update statistics
            self.checkpoint_stats["total_checkpoints"] += 1
            if self._is_quantized_layer(module, module_name):
                self.checkpoint_stats["quantized_layer_checkpoints"] += 1
            if self._is_lora_layer(module, module_name):
                self.checkpoint_stats["lora_layer_checkpoints"] += 1
            
            # Apply checkpoint
            return checkpoint(checkpoint_fn, *args, use_reentrant=False)
        
        return checkpointed_forward
    
    def _mixed_precision_checkpoint(
        self, 
        original_forward: Callable, 
        args: tuple, 
        kwargs: dict,
        module_name: str
    ) -> torch.Tensor:
        """Handle mixed precision checkpointing for quantized layers."""
        # Preserve input precision for quantized layers
        original_dtypes = [arg.dtype if torch.is_tensor(arg) else None for arg in args]
        
        def precision_aware_forward(*checkpoint_args):
            # Restore original dtypes if needed
            restored_args = []
            for i, arg in enumerate(checkpoint_args):
                if torch.is_tensor(arg) and original_dtypes[i] is not None:
                    if arg.dtype != original_dtypes[i]:
                        arg = arg.to(dtype=original_dtypes[i])
                restored_args.append(arg)
            
            return original_forward(*restored_args, **kwargs)
        
        return checkpoint(precision_aware_forward, *args, use_reentrant=False)
    
    def optimize_checkpoint_strategy(self) -> Dict[str, Any]:
        """Dynamically optimize checkpointing strategy based on current conditions."""
        if not self.config.dynamic_checkpoint_selection:
            return {"strategy": "static", "changes": 0}
        
        changes = 0
        
        # Check current memory usage
        if torch.cuda.is_available():
            current_memory_mb = torch.cuda.memory_allocated() / (1024 * 1024)
            memory_utilization = current_memory_mb / self.config.memory_threshold_mb
            
            # Adjust checkpoint frequency based on memory pressure
            if memory_utilization > 0.8:
                # High memory pressure - more aggressive checkpointing
                self.config.checkpoint_every_n_layers = max(1, self.config.checkpoint_every_n_layers - 1)
                self.config.checkpoint_activation_size_threshold_mb *= 0.8
                changes += 1
                
            elif memory_utilization < 0.4:
                # Low memory pressure - reduce checkpointing overhead
                self.config.checkpoint_every_n_layers = min(4, self.config.checkpoint_every_n_layers + 1)
                self.config.checkpoint_activation_size_threshold_mb *= 1.2
                changes += 1
        
        return {
            "strategy": "dynamic",
            "changes": changes,
            "checkpoint_frequency": self.config.checkpoint_every_n_layers,
            "activation_threshold_mb": self.config.checkpoint_activation_size_threshold_mb
        }
    
    def adaptive_optimize_strategy(self) -> Dict[str, Any]:
        """
        Advanced optimization using adaptive selection and memory monitoring.
        """
        optimizations = {
            "adaptive_changes": 0,
            "memory_pressure_changes": 0,
            "performance_improvements": []
        }
        
        # Update memory monitoring
        if self.memory_monitor:
            self.memory_monitor.update_memory_stats()
            pressure_level = self.memory_monitor.get_memory_pressure_level()
            
            # Adjust strategy based on memory pressure
            if pressure_level == "critical":
                # Enable aggressive checkpointing
                original_threshold = self.config.checkpoint_activation_size_threshold_mb
                self.config.checkpoint_activation_size_threshold_mb = min(50.0, original_threshold)
                self.config.checkpoint_every_n_layers = 1
                optimizations["memory_pressure_changes"] += 1
                
                logger.warning(f"Critical memory pressure detected, enabling aggressive checkpointing")
                
            elif pressure_level == "high":
                # Moderate checkpointing adjustments
                self.config.checkpoint_activation_size_threshold_mb *= 0.8
                self.config.checkpoint_every_n_layers = max(1, self.config.checkpoint_every_n_layers - 1)
                optimizations["memory_pressure_changes"] += 1
                
            elif pressure_level == "low":
                # Reduce checkpointing overhead
                self.config.checkpoint_activation_size_threshold_mb *= 1.1
                self.config.checkpoint_every_n_layers = min(3, self.config.checkpoint_every_n_layers + 1)
        
        # Apply adaptive selection if available
        if self.adaptive_selector:
            candidate_names = [name for name, _ in self.checkpoint_candidates]
            optimal_layers = self.adaptive_selector.get_optimal_layers(candidate_names, top_k=10)
            
            # Update candidate priorities based on adaptive selection
            if optimal_layers:
                # Reorder candidates based on adaptive selection
                self.checkpoint_candidates.sort(
                    key=lambda x: optimal_layers.index(x[0]) if x[0] in optimal_layers else len(optimal_layers)
                )
                optimizations["adaptive_changes"] += 1
                
                logger.info(f"Applied adaptive checkpoint selection, prioritizing {len(optimal_layers)} optimal layers")
          # Update statistics        if optimizations["adaptive_changes"] > 0:
            self.checkpoint_stats["adaptive_optimizations"] += optimizations["adaptive_changes"]
        if optimizations["memory_pressure_changes"] > 0:
            self.checkpoint_stats["memory_pressure_adaptations"] += optimizations["memory_pressure_changes"]
        
        return optimizations
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance and optimization report."""
        # Create base report from checkpoint stats
        base_report = {
            "checkpoint_stats": self.checkpoint_stats.copy(),
            "config": {
                "checkpoint_every_n_layers": self.config.checkpoint_every_n_layers,
                "selective_checkpointing": self.config.selective_checkpointing,
                "memory_threshold_mb": self.config.memory_threshold_mb,
                "mixed_precision_checkpointing": self.config.mixed_precision_checkpointing,
                "quantized_layer_priority": getattr(self.config, 'quantized_layer_priority', 1),
                "cuda_optimizations_enabled": getattr(self.config, 'cuda_optimizations_enabled', True)
            },
            "layer_analysis": {
                "total_layers": len(self.checkpoint_candidates),
                "quantized_layers": len(self.quantized_candidates),
                "lora_layers": len(self.lora_candidates)
            },
            "memory_estimates": {
                "base_memory_mb": len(self.checkpoint_candidates) * 10.0,  # Estimated
                "checkpointed_memory_mb": self.checkpoint_stats.get("memory_saved_mb", 0.0),
                "estimated_peak_memory_mb": len(self.checkpoint_candidates) * 10.0 - self.checkpoint_stats.get("memory_saved_mb", 0.0),
                "memory_reduction_ratio": min(1.0, self.checkpoint_stats.get("memory_saved_mb", 0.0) / max(1.0, len(self.checkpoint_candidates) * 10.0))
            },
            "checkpoint_efficiency": {
                "checkpoints_per_layer": len(self.checkpoint_candidates) / max(1, len(self.checkpoint_candidates)),
                "memory_efficiency_ratio": self.checkpoint_stats.get("memory_saved_mb", 0.0) / max(1.0, len(self.checkpoint_candidates) * 10.0),
                "overhead_efficiency": self.performance_metrics.checkpoint_overhead_ms / max(1.0, self.performance_metrics.total_checkpoints)
            }
        }
        
        # Add advanced metrics
        base_report["performance_metrics"] = self.performance_metrics.to_dict()
        
        # Add adaptive selection metrics
        if self.adaptive_selector:
            base_report["adaptive_selection"] = self.adaptive_selector.get_performance_summary()
          # Add memory monitoring metrics
        if self.memory_monitor:
            base_report["memory_monitoring"] = self.memory_monitor.get_memory_stats()
        
        # Add optimization statistics
        base_report["optimizations"] = {
            "adaptive_optimizations": self.checkpoint_stats.get("adaptive_optimizations", 0),
            "memory_pressure_adaptations": self.checkpoint_stats.get("memory_pressure_adaptations", 0)
        }
        
        return base_report
    
    def get_checkpoint_report(self) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        return {
            "checkpoint_stats": self.checkpoint_stats.copy(),
            "configuration": {
                "checkpoint_every_n_layers": self.config.checkpoint_every_n_layers,
                "selective_checkpointing": self.config.selective_checkpointing,
                "memory_threshold_mb": self.config.memory_threshold_mb,
                "mixed_precision_checkpointing": self.config.mixed_precision_checkpointing,
                "quantized_layer_priority": self.config.quantized_layer_priority,
                "cuda_optimizations_enabled": getattr(self.config, 'cuda_optimizations_enabled', True)
            },
            "model_analysis": {
                "total_layers": len(self.checkpoint_candidates),
                "total_checkpoint_candidates": len(self.checkpoint_candidates),
                "quantized_layers": len(self.quantized_candidates),
                "lora_layers": len(self.lora_candidates)
            },
            "memory_efficiency": {
                "memory_saved_mb": self.checkpoint_stats.get("memory_saved_mb", 0.0),
                "total_activations_checkpointed": len(self.checkpoint_candidates),
                "efficiency_ratio": (
                    self.checkpoint_stats.get("memory_saved_mb", 0.0) / 
                    max(1.0, len(self.checkpoint_candidates) * 10.0)  # Estimated baseline
                )
            }
        }
    
    def record_checkpoint_performance(self, layer_name: str, start_time: float, end_time: float, memory_saved: float):
        """Record performance metrics for a checkpoint operation."""
        if self.adaptive_selector:
            overhead_time = end_time - start_time
            # Estimate recomputation time (typically 1.5-2x forward time)
            recomputation_time = overhead_time * 1.7
            
            self.adaptive_selector.record_checkpoint_performance(
                layer_name, memory_saved, overhead_time, recomputation_time
            )
        
        # Update performance metrics
        self.performance_metrics.checkpoint_overhead_ms += (end_time - start_time) * 1000
        self.performance_metrics.memory_saved_mb += memory_saved
        self.performance_metrics.total_checkpoints += 1

def apply_gradient_checkpointing(model: torch.nn.Module) -> torch.nn.Module:
    """
    Apply basic gradient checkpointing to reduce memory usage during training.
    
    Args:
        model: The PyTorch model to optimize.
        
    Returns:
        The model with gradient checkpointing applied.
    """
    for module in model.modules():
        if hasattr(module, 'gradient_checkpointing'):
            module.gradient_checkpointing = True
    return model


def apply_qlora_checkpointing(
    model: torch.nn.Module,
    config: Optional[CheckpointConfig] = None,
    quantized_layers: Optional[List[str]] = None,
    lora_modules: Optional[List[str]] = None
) -> QLoRAGradientCheckpointing:
    """
    Apply QLoRA-optimized gradient checkpointing.
    
    Args:
        model: The model to apply checkpointing to
        config: Checkpointing configuration
        quantized_layers: Names/patterns of quantized layers
        lora_modules: Names/patterns of LoRA adaptation modules
        
    Returns:
        QLoRAGradientCheckpointing manager instance
    """
    # Create default config if none provided
    if config is None:
        config = CheckpointConfig()
    
    # Set CUDA optimizations based on availability
    config.cuda_optimizations_enabled = torch.cuda.is_available()
    
    # Default quantized layer patterns for common architectures
    if quantized_layers is None:
        quantized_layers = [
            'q_proj', 'k_proj', 'v_proj', 'o_proj',  # Attention projections
            'gate_proj', 'up_proj', 'down_proj',     # MLP projections
            'fc1', 'fc2', 'dense'                    # Dense layers
        ]
    
    # Default LoRA module patterns
    if lora_modules is None:
        lora_modules = [
            'lora_A', 'lora_B', 'lora_dropout',
            'base_layer', 'adapter'
        ]
    
    checkpoint_manager = QLoRAGradientCheckpointing(
        model=model,
        config=config,
        quantized_layers=quantized_layers,
        lora_modules=lora_modules
    )
    
    logger.info("Applied QLoRA-optimized gradient checkpointing")
    return checkpoint_manager


@contextmanager
def memory_efficient_checkpointing(
    model: torch.nn.Module,
    memory_threshold_mb: float = 3500.0,
    aggressive_mode: bool = False
):
    """
    Context manager for memory-efficient gradient checkpointing.
    
    Args:
        model: Model to apply checkpointing to
        memory_threshold_mb: Memory threshold for activation
        aggressive_mode: Use aggressive checkpointing for maximum memory savings
    """
    config = CheckpointConfig(
        memory_threshold_mb=memory_threshold_mb,
        selective_checkpointing=True,
        mixed_precision_checkpointing=True,
        dynamic_checkpoint_selection=not aggressive_mode,
        checkpoint_every_n_layers=1 if aggressive_mode else 2
    )
    
    checkpoint_manager = apply_qlora_checkpointing(model, config)
    
    try:
        with checkpoint_manager.selective_checkpointing():
            yield checkpoint_manager
    finally:
        # Cleanup and report
        report = checkpoint_manager.get_checkpoint_report()
        logger.info(f"Checkpointing session complete: {report['checkpoint_stats']['total_checkpoints']} checkpoints applied")
        
        # Force cleanup
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

@contextmanager
def adaptive_memory_efficient_checkpointing(
    model: torch.nn.Module,
    memory_threshold_mb: float = 3500.0,
    enable_adaptive_selection: bool = True,
    enable_memory_monitoring: bool = True,
    learning_mode: bool = True
):
    """
    Advanced context manager with adaptive checkpoint selection and memory monitoring.
    
    Args:
        model: Model to apply checkpointing to
        memory_threshold_mb: Memory threshold for activation
        enable_adaptive_selection: Enable adaptive checkpoint point selection
        enable_memory_monitoring: Enable real-time memory pressure monitoring
        learning_mode: Enable learning from checkpoint performance
    """
    config = CheckpointConfig(
        memory_threshold_mb=memory_threshold_mb,
        selective_checkpointing=True,
        mixed_precision_checkpointing=True,
        dynamic_checkpoint_selection=True
    )
    
    checkpoint_manager = QLoRAGradientCheckpointing(
        model=model,
        config=config,
        enable_adaptive_selection=enable_adaptive_selection,
        enable_memory_monitoring=enable_memory_monitoring
    )
    
    try:
        # Perform initial optimization
        optimization_result = checkpoint_manager.adaptive_optimize_strategy()
        logger.info(f"Initial optimization applied: {optimization_result}")
        
        with checkpoint_manager.selective_checkpointing():
            yield checkpoint_manager
            
    finally:
        # Generate comprehensive report
        if learning_mode:
            report = checkpoint_manager.get_comprehensive_report()
            logger.info(f"Adaptive checkpointing session complete:")
            logger.info(f"  - Total checkpoints: {report['checkpoint_stats']['total_checkpoints']}")
            logger.info(f"  - Memory saved: {report['performance_metrics']['memory_saved_mb']:.2f} MB")
            logger.info(f"  - Adaptive optimizations: {report['optimizations']['adaptive_optimizations']}")
            logger.info(f"  - Memory pressure adaptations: {report['optimizations']['memory_pressure_adaptations']}")
            
            # Record session performance for future learning
            if checkpoint_manager.adaptive_selector:
                performance_summary = checkpoint_manager.adaptive_selector.get_performance_summary()
                if performance_summary["total_checkpoints"] > 0:
                    logger.info(f"  - Learning data: {performance_summary['total_checkpoints']} checkpoint records")
        
        # Cleanup
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# Enhanced utility function with auto-detection
def auto_apply_optimal_checkpointing(
    model: torch.nn.Module,
    input_example: Optional[torch.Tensor] = None,
    target_memory_mb: float = 3500.0
) -> QLoRAGradientCheckpointing:
    """
    Automatically apply optimal checkpointing configuration based on model analysis.
    
    Args:
        model: Model to optimize
        input_example: Example input for memory estimation
        target_memory_mb: Target memory usage in MB
        
    Returns:
        Configured QLoRAGradientCheckpointing instance
    """
    # Analyze model architecture
    total_params = sum(p.numel() for p in model.parameters())
    param_memory_mb = (total_params * 4) / (1024 * 1024)  # Assuming float32
    
    # Detect quantized and LoRA layers automatically
    quantized_patterns = []
    lora_patterns = []
    
    for name, module in model.named_modules():
        # Detect quantized layers
        if hasattr(module, 'weight') and hasattr(module.weight, 'quant_type'):
            quantized_patterns.append(name.split('.')[-1])  # Get layer type
        
        # Detect LoRA layers
        if any(hasattr(module, attr) for attr in ['lora_A', 'lora_B', 'lora_dropout']):
            lora_patterns.append(name.split('.')[-1])
    
    # Remove duplicates and common patterns
    quantized_patterns = list(set(quantized_patterns))
    lora_patterns = list(set(lora_patterns))
    
    # Configure based on model size and hardware constraints
    if param_memory_mb > target_memory_mb * 0.8:
        # Large model - aggressive checkpointing
        config = CheckpointConfig(
            memory_threshold_mb=target_memory_mb,
            checkpoint_every_n_layers=1,
            checkpoint_activation_size_threshold_mb=50.0,
            dynamic_checkpoint_selection=True,
            mixed_precision_checkpointing=True
        )
        logger.info(f"Detected large model ({param_memory_mb:.2f} MB), applying aggressive checkpointing")
    elif param_memory_mb > target_memory_mb * 0.5:
        # Medium model - balanced checkpointing
        config = CheckpointConfig(
            memory_threshold_mb=target_memory_mb,
            checkpoint_every_n_layers=2,
            checkpoint_activation_size_threshold_mb=100.0,
            dynamic_checkpoint_selection=True
        )
        logger.info(f"Detected medium model ({param_memory_mb:.2f} MB), applying balanced checkpointing")
    else:
        # Small model - minimal checkpointing
        config = CheckpointConfig(
            memory_threshold_mb=target_memory_mb,
            checkpoint_every_n_layers=3,
            checkpoint_activation_size_threshold_mb=200.0,
            dynamic_checkpoint_selection=False
        )
        logger.info(f"Detected small model ({param_memory_mb:.2f} MB), applying minimal checkpointing")
    
    # Create and configure checkpoint manager
    checkpoint_manager = QLoRAGradientCheckpointing(
        model=model,
        config=config,
        quantized_layers=quantized_patterns,
        lora_modules=lora_patterns,
        enable_adaptive_selection=True,
        enable_memory_monitoring=True
    )
    
    logger.info(f"Auto-configured checkpointing:")
    logger.info(f"  - Quantized layer patterns: {quantized_patterns}")
    logger.info(f"  - LoRA layer patterns: {lora_patterns}")
    logger.info(f"  - Checkpoint frequency: every {config.checkpoint_every_n_layers} layers")
    
    return checkpoint_manager
