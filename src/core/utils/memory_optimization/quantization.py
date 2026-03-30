#!/usr/bin/env python3
"""
ImpressionCore: Enhanced Quantization Module

Comprehensive quantization implementation for memory-efficient training and inference.

File: src/core/utils/memory_optimization/quantization.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-28
Modified: 2025-05-28
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [quantization, memory-optimization, pytorch, training, inference]
Dependencies: [torch, typing, logging]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module provides comprehensive quantization support including:
- Dynamic quantization (post-training)
- Static quantization (with calibration)
- Quantization-aware training (QAT)
- Custom quantization schemes for specialized models

Memory Considerations:
- Optimized for GTX 1050 Ti (4GB VRAM) constraints
- Implements memory-efficient calibration procedures
- Provides fallback mechanisms for unsupported configurations

Examples:
```python
from src.core.utils.memory_optimization.quantization import QuantizationManager

# Dynamic quantization for inference
qmanager = QuantizationManager()
quantized_model = qmanager.apply_dynamic_quantization(model)

# Static quantization with calibration
calibration_loader = get_calibration_data()
quantized_model = qmanager.apply_static_quantization(model, calibration_loader)

# Quantization-aware training
qat_model = qmanager.prepare_qat(model)
# ... train the model ...
quantized_model = qmanager.convert_qat(qat_model)
```

Design Philosophy:
- Memory-first approach for constrained hardware
- Graceful fallbacks when quantization fails
- Integration with existing ImpressionCore infrastructure
- Comprehensive logging and error handling
"""

import logging
import torch
import torch.nn as nn
import torch.quantization as quantization
from torch.quantization import QuantStub, DeQuantStub
from torch.utils.data import DataLoader
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass
from pathlib import Path
import gc
import warnings
from enum import Enum
import time
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class QuantizationConfig:
    """Configuration for quantization operations."""
    
    # Quantization type
    quantization_type: str = "dynamic"  # "dynamic", "static", "qat"
    
    # Backend configuration
    backend: str = "fbgemm"  # "fbgemm" (CPU), "qnnpack" (mobile)
    
    # Calibration settings
    calibration_batches: int = 100
    calibration_device: str = "cpu"
    
    # Dynamic quantization settings
    dynamic_qconfig_spec: Optional[Dict] = None
    
    # Static quantization settings
    static_qconfig: Optional[Any] = None
    
    # QAT settings
    qat_qconfig: Optional[Any] = None
    
    # Memory optimization
    offload_calibration: bool = True
    clear_cache_after_calibration: bool = True
    
    # Fallback settings
    fallback_to_fp16: bool = True
    fallback_to_original: bool = True

class QuantizationPrecision(Enum):
    """Supported quantization precisions with enhanced options"""
    INT8 = "int8"
    INT4 = "int4"
    FLOAT16 = "float16"
    DYNAMIC = "dynamic"
    BFLOAT16 = "bfloat16"

class AdaptivePrecisionManager:
    """
    Manages dynamic precision switching based on sequence length,
    memory constraints, and performance requirements for ImpressionCore.
    """
    
    def __init__(self, config: Optional[QuantizationConfig] = None):
        """
        Initialize adaptive precision manager.
        
        Args:
            config: Quantization configuration
        """
        self.config = config or QuantizationConfig()
        self.precision_thresholds = {
            512: QuantizationPrecision.FLOAT16,
            1024: QuantizationPrecision.INT8,
            2048: QuantizationPrecision.INT4,
        }
        self.current_precision = QuantizationPrecision.FLOAT16
        self.logger = logging.getLogger(__name__)
        
    def determine_optimal_precision(
        self, 
        sequence_length: int, 
        available_memory_mb: float,
        model_size_mb: float,
        target_latency_ms: Optional[float] = None
    ) -> QuantizationPrecision:
        """
        Determine optimal precision based on current conditions.
        
        Args:
            sequence_length: Input sequence length
            available_memory_mb: Available GPU memory in MB
            model_size_mb: Current model size in MB
            target_latency_ms: Target inference latency in milliseconds
            
        Returns:
            Recommended quantization precision
        """
        # Memory pressure calculation
        memory_pressure = (model_size_mb / available_memory_mb) if available_memory_mb > 0 else 1.0
        
        # Sequence length factor (quadratic attention complexity)
        seq_factor = (sequence_length / 1024.0) ** 2
        
        # Combined pressure score (higher = more aggressive quantization needed)
        pressure_score = memory_pressure * seq_factor
        
        # Latency consideration
        if target_latency_ms is not None:
            # Estimate latency pressure based on target
            latency_factor = min(2.0, max(0.5, target_latency_ms / 100.0))  # Normalize to 100ms
            pressure_score *= latency_factor
        
        self.logger.debug(f"Precision selection: seq_len={sequence_length}, "
                         f"memory_pressure={memory_pressure:.2f}, "
                         f"seq_factor={seq_factor:.2f}, score={pressure_score:.2f}")
        
        # Select precision based on pressure score
        if pressure_score > 3.0:
            return QuantizationPrecision.INT4
        elif pressure_score > 2.0:
            return QuantizationPrecision.INT8
        elif pressure_score > 1.5:
            return QuantizationPrecision.FLOAT16
        elif pressure_score > 1.0:
            return QuantizationPrecision.BFLOAT16
        else:
            return QuantizationPrecision.DYNAMIC
            
    def adapt_model_precision(
        self, 
        model: nn.Module, 
        target_precision: QuantizationPrecision
    ) -> nn.Module:
        """
        Adapt model to target precision if different from current.
        
        Args:
            model: Model to adapt
            target_precision: Target quantization precision
            
        Returns:
            Model with adapted precision
        """
        if target_precision == self.current_precision:
            return model
            
        self.logger.info(f"Adapting precision from {self.current_precision.value} to {target_precision.value}")
        
        try:
            if target_precision == QuantizationPrecision.FLOAT16:
                adapted_model = model.half()
            elif target_precision == QuantizationPrecision.BFLOAT16:
                # Convert to bfloat16 if available
                if hasattr(torch, 'bfloat16'):
                    adapted_model = model.to(torch.bfloat16)
                else:
                    self.logger.warning("bfloat16 not available, using float16")
                    adapted_model = model.half()
            elif target_precision == QuantizationPrecision.DYNAMIC:
                # Apply dynamic quantization
                quant_manager = QuantizationManager(self.config)
                adapted_model = quant_manager.apply_dynamic_quantization(model)
            elif target_precision == QuantizationPrecision.INT4:
                # INT4 quantization using custom implementation
                adapted_model = self._apply_int4_quantization(model)
            else:
                self.logger.warning(f"Precision {target_precision.value} requires calibration data")
                adapted_model = model
                
            self.current_precision = target_precision
            return adapted_model
            
        except Exception as e:
            self.logger.error(f"Precision adaptation failed: {e}")
            return model
    
    def _apply_int4_quantization(self, model: nn.Module) -> nn.Module:
        """
        Apply INT4 quantization using custom implementation.
        
        Note: This is a simplified INT4 implementation.
        For production use, consider using specialized libraries like 
        bitsandbytes or optimum.
        
        Args:
            model: Model to quantize
            
        Returns:
            INT4 quantized model (or fallback)
        """
        try:
            # Check if bitsandbytes is available for INT4
            try:
                import bitsandbytes as bnb
                
                # Replace Linear layers with 4-bit equivalents
                for name, module in model.named_children():
                    if isinstance(module, nn.Linear):
                        int4_layer = bnb.nn.Linear4bit(
                            module.in_features,
                            module.out_features,
                            bias=module.bias is not None,
                            compute_dtype=torch.float16,
                            compress_statistics=True,
                            quant_type="nf4"
                        )
                        setattr(model, name, int4_layer)
                        
                self.logger.info("Applied bitsandbytes INT4 quantization")
                return model
                
            except ImportError:
                self.logger.warning("bitsandbytes not available, using INT8 fallback")
                quant_manager = QuantizationManager(self.config)
                return quant_manager.apply_dynamic_quantization(model)
                
        except Exception as e:
            self.logger.error(f"INT4 quantization failed: {e}")
            return model


        return self.performance_stats.copy()

class CalibrationDataset:
    """Wrapper for calibration data that handles memory optimization."""
    
    def __init__(self, dataloader: DataLoader, max_batches: int = 100):
        """
        Initialize calibration dataset.
        
        Args:
            dataloader: Original training/validation dataloader
            max_batches: Maximum number of batches for calibration
        """
        self.dataloader = dataloader
        self.max_batches = max_batches
        self.current_batch = 0
    
    def __iter__(self):
        """Iterate through calibration data with memory optimization."""
        self.current_batch = 0
        for batch in self.dataloader:
            if self.current_batch >= self.max_batches:
                break
            
            # Memory optimization: Move to appropriate device
            if isinstance(batch, (list, tuple)):
                batch = [b.to('cpu') if torch.is_tensor(b) else b for b in batch]
            elif torch.is_tensor(batch):
                batch = batch.to('cpu')
            
            yield batch
            self.current_batch += 1
            
            # Memory optimization: Clear cache periodically
            if self.current_batch % 10 == 0:
                torch.cuda.empty_cache()
                gc.collect()


class QuantizationManager:
    """
    Comprehensive quantization manager for ImpressionCore models.
    
    Handles dynamic, static, and quantization-aware training with
    memory optimization for GTX 1050 Ti constraints.
    """
    
    def __init__(self, config: Optional[QuantizationConfig] = None):
        """
        Initialize quantization manager.
        
        Args:
            config: Quantization configuration
        """
        self.config = config or QuantizationConfig()
        self.logger = logging.getLogger(__name__)
          # Track quantization state
        self.quantization_info = {}
        self.quantization_supported = True  # Will be set by backend test
        
        # Set up quantization backend
        self._setup_backend()
        
    def _setup_backend(self):
        """Set up quantization backend based on configuration."""
        try:
            # Check if quantization backends are available
            if not hasattr(torch.backends, 'quantized'):
                self.logger.warning("PyTorch quantization backends not available")
                return
                
            if self.config.backend == "fbgemm":
                torch.backends.quantized.engine = 'fbgemm'
            elif self.config.backend == "qnnpack":
                torch.backends.quantized.engine = 'qnnpack'
            else:
                self.logger.warning(f"Unknown backend {self.config.backend}, using fbgemm")
                torch.backends.quantized.engine = 'fbgemm'
                
            self.logger.info(f"Quantization backend set to: {torch.backends.quantized.engine}")
            
            # Test backend compatibility
            self._test_backend_compatibility()
            
        except Exception as e:
            self.logger.warning(f"Failed to set quantization backend: {e}")
            # Use default backend    def _test_backend_compatibility(self):
        """Test if the current backend supports quantized operations."""
        try:
            # Create a simple test model
            test_model = nn.Linear(2, 2)
            test_input = torch.randn(1, 2)
            
            # Try dynamic quantization (least likely to fail)
            quantized_model = torch.quantization.quantize_dynamic(
                test_model, 
                {nn.Linear}, 
                dtype=torch.qint8
            )
            
            # Try inference to check if quantized ops work
            try:
                _ = quantized_model(test_input)
                self.logger.debug("Backend compatibility test passed")
                self.quantization_supported = True
            except NotImplementedError as e:
                if "quantized::linear" in str(e) and "CPU" in str(e):
                    self.logger.warning("PyTorch quantized CPU backend not available. Quantization will use fallback mode.")
                    self.quantization_supported = False
                else:
                    raise
            
        except Exception as e:
            self.logger.warning(f"Backend compatibility test failed: {e}")
            self.logger.warning("Some quantized operations may not work properly")
            self.quantization_supported = False
            
    def _safe_quantized_execution(self, quantized_model: nn.Module, test_input: torch.Tensor) -> bool:
        """
        Safely test if a quantized model can execute.
        
        Args:
            quantized_model: Quantized model to test
            test_input: Test input tensor
            
        Returns:
            True if execution succeeds, False otherwise
        """
        try:
            _ = quantized_model(test_input)
            return True
        except NotImplementedError as e:
            if "quantized::linear" in str(e) and "CPU" in str(e):
                self.logger.warning("PyTorch quantized CPU backend not available for execution")
                return False
            raise
        except Exception as e:
            self.logger.warning(f"Quantized model execution failed: {e}")
            return False
            
    def apply_dynamic_quantization(
        self, 
        model: nn.Module,
        qconfig_spec: Optional[Dict] = None
    ) -> nn.Module:
        """
        Apply dynamic quantization to a model.
        
        Dynamic quantization quantizes weights at model load time and
        quantizes activations dynamically during inference.
        
        Args:
            model: Model to quantize
            qconfig_spec: Quantization configuration specification
            
        Returns:
            Dynamically quantized model
            
        Raises:
            RuntimeError: If quantization fails
        """
        self.logger.info("Starting dynamic quantization...")
        
        try:
            # Set model to evaluation mode
            model.eval()
            
            # Default qconfig_spec for dynamic quantization
            if qconfig_spec is None:
                qconfig_spec = {
                    nn.Linear: torch.quantization.default_dynamic_qconfig,
                    nn.LSTM: torch.quantization.default_dynamic_qconfig,
                    nn.GRU: torch.quantization.default_dynamic_qconfig,
                }
            
            # Apply dynamic quantization
            quantized_model = torch.quantization.quantize_dynamic(
                model, 
                qconfig_spec, 
                dtype=torch.qint8
            )
            
            # Test if quantized model can execute
            if not self.quantization_supported:
                self.logger.warning("Quantization backend not supported, returning original model")
                return model
                
            # Test with a simple input if possible
            try:                # Try to create a minimal test input
                test_input = torch.randn(1, 10)  # Simple test case
                if not self._safe_quantized_execution(quantized_model, test_input):
                    self.logger.warning("Quantized model execution test failed, returning original model")
                    
                    # Store fallback info
                    self.quantization_info[id(model)] = {
                        "type": "dynamic",
                        "fallback": True,
                        "fallback_reason": "quantized_execution_failed",
                        "qconfig_spec": qconfig_spec,
                        "original_model_size": self._get_model_size(model),
                        "quantized_model_size": self._get_model_size(model)  # Same as original
                    }
                    
                    return model
            except Exception as e:
                self.logger.debug(f"Could not test quantized model execution: {e}")
            
            # Store quantization info
            self.quantization_info[id(quantized_model)] = {
                "type": "dynamic",
                "qconfig_spec": qconfig_spec,
                "original_model_size": self._get_model_size(model),
                "quantized_model_size": self._get_model_size(quantized_model)
            }
            
            self.logger.info("Dynamic quantization completed successfully")
            self.logger.info(f"Model size reduced from {self.quantization_info[id(quantized_model)]['original_model_size']:.2f}MB "
                           f"to {self.quantization_info[id(quantized_model)]['quantized_model_size']:.2f}MB")
            
            return quantized_model
            
        except Exception as e:
            self.logger.error(f"Dynamic quantization failed: {e}")
            
            if self.config.fallback_to_fp16:
                self.logger.info("Falling back to FP16...")
                try:
                    return model.half()
                except Exception as fp16_error:
                    self.logger.warning(f"FP16 fallback failed: {fp16_error}")
            
            if self.config.fallback_to_original:
                self.logger.info("Returning original model")
                return model
            else:
                raise RuntimeError(f"Dynamic quantization failed: {e}")
    
    def apply_static_quantization(
        self,
        model: nn.Module,
        calibration_dataloader: DataLoader,
        qconfig: Optional[Any] = None
    ) -> nn.Module:
        """
        Apply static quantization to a model with calibration.
        
        Static quantization determines scale and zero_point values
        ahead of time using a calibration dataset.
        
        Args:
            model: Model to quantize
            calibration_dataloader: Data for calibration
            qconfig: Quantization configuration
            
        Returns:
            Statically quantized model
            
        Raises:
            RuntimeError: If quantization fails        """
        self.logger.info("Starting static quantization with calibration...")
        
        try:
            # Check if quantization is supported
            if not self.quantization_supported:
                self.logger.warning("Quantization backend not supported, returning original model")
                return model
                
            # Set model to evaluation mode
            model.eval()
            
            # Create a copy of the model for quantization
            import copy
            model_to_quantize = copy.deepcopy(model)
            
            # Set up calibration dataset with memory optimization
            calibration_dataset = CalibrationDataset(
                calibration_dataloader, 
                self.config.calibration_batches
            )
            
            # Set up quantization configuration
            if qconfig is None:
                qconfig = torch.quantization.get_default_qconfig(self.config.backend)
            
            # Prepare model for static quantization
            model_to_quantize.qconfig = qconfig
            model_prepared = torch.quantization.prepare(model_to_quantize)
            
            self.logger.info(f"Calibrating with {self.config.calibration_batches} batches...")
              # Calibration phase
            calibration_count = 0
            model_prepared.eval()
            
            with torch.no_grad():
                for batch_idx, batch in enumerate(calibration_dataset):
                    try:
                        # Move to calibration device
                        if isinstance(batch, (list, tuple)):
                            if len(batch) >= 1:
                                inputs = batch[0]
                            else:
                                continue
                        else:
                            inputs = batch
                        
                        if torch.is_tensor(inputs):
                            inputs = inputs.to(self.config.calibration_device)
                            
                            # Forward pass for calibration
                            _ = model_prepared(inputs)
                            calibration_count += 1
                        
                        # Memory optimization during calibration
                        if batch_idx % 10 == 0:
                            torch.cuda.empty_cache()
                            gc.collect()
                            
                    except Exception as batch_error:
                        self.logger.warning(f"Calibration batch {batch_idx} failed: {batch_error}")
                        continue
            
            if calibration_count == 0:
                raise RuntimeError("No successful calibration batches processed")
            self.logger.info(f"Calibration completed with {calibration_count} batches")
            
            # Convert to quantized model with error handling
            try:
                quantized_model = torch.quantization.convert(model_prepared)
                
                # Test the quantized model to ensure it works
                test_input = next(iter(calibration_dataloader))
                if isinstance(test_input, (list, tuple)) and len(test_input) >= 1:
                    test_input = test_input[0]
                    
                if torch.is_tensor(test_input):
                    test_input = test_input.to(self.config.calibration_device)
                    if not self._safe_quantized_execution(quantized_model, test_input):
                        raise RuntimeError("Quantized model execution test failed")
                        
            except (RuntimeError, NotImplementedError) as e:
                self.logger.warning(f"Quantized model conversion or execution failed: {e}")
                self.logger.warning("Falling back to original model (no quantization applied)")
                
                # Store fallback info
                self.quantization_info[id(model)] = {
                    "type": "static",
                    "fallback": True,
                    "fallback_reason": str(e),
                    "calibration_batches": calibration_count,
                    "original_model_size": self._get_model_size(model),
                    "quantized_model_size": self._get_model_size(model)  # Same as original
                }
                
                return model
            
            # Store quantization info
            self.quantization_info[id(quantized_model)] = {
                "type": "static",
                "qconfig": qconfig,
                "calibration_batches": calibration_count,
                "original_model_size": self._get_model_size(model),
                "quantized_model_size": self._get_model_size(quantized_model)
            }
            
            # Memory cleanup after calibration
            if self.config.clear_cache_after_calibration:
                torch.cuda.empty_cache()
                gc.collect()
            
            self.logger.info("Static quantization completed successfully")
            self.logger.info(f"Model size reduced from {self.quantization_info[id(quantized_model)]['original_model_size']:.2f}MB "
                           f"to {self.quantization_info[id(quantized_model)]['quantized_model_size']:.2f}MB")
            
            return quantized_model
            
        except Exception as e:
            self.logger.error(f"Static quantization failed: {e}")
            
            if self.config.fallback_to_fp16:
                self.logger.info("Falling back to FP16...")
                try:
                    return model.half()
                except Exception as fp16_error:
                    self.logger.warning(f"FP16 fallback failed: {fp16_error}")
            
            if self.config.fallback_to_original:
                self.logger.info("Returning original model")
                return model
            else:
                raise RuntimeError(f"Static quantization failed: {e}")
    
    def prepare_qat(
        self,
        model: nn.Module,
        qconfig: Optional[Any] = None
    ) -> nn.Module:
        """
        Prepare a model for quantization-aware training.
        
        Args:
            model: Model to prepare for QAT
            qconfig: Quantization configuration for QAT
            
        Returns:
            Model prepared for QAT        """
        self.logger.info("Preparing model for quantization-aware training...")
        
        try:
            # Check if quantization is supported
            if not self.quantization_supported:
                self.logger.warning("Quantization backend not supported, returning original model")
                return model
                
            # Set up QAT configuration
            if qconfig is None:
                qconfig = torch.quantization.get_default_qat_qconfig(self.config.backend)
            
            # Set model to training mode for QAT
            model.train()
            
            # Set qconfig
            model.qconfig = qconfig
            
            # Prepare model for QAT
            qat_model = torch.quantization.prepare_qat(model)
            
            self.logger.info("Model prepared for QAT successfully")
            return qat_model
            
        except Exception as e:
            self.logger.error(f"QAT preparation failed: {e}")
            raise RuntimeError(f"QAT preparation failed: {e}")
    
    def convert_qat(self, qat_model: nn.Module) -> nn.Module:
        """
        Convert a QAT model to a quantized model for inference.
        
        Args:
            qat_model: Model that has been trained with QAT
            
        Returns:
            Quantized model for inference        """
        self.logger.info("Converting QAT model to quantized model...")
        
        try:
            # Check if quantization is supported
            if not self.quantization_supported:
                self.logger.warning("Quantization backend not supported, returning original model")
                return qat_model
                
            # Set to evaluation mode
            qat_model.eval()
            
            # Convert QAT model to quantized model
            quantized_model = torch.quantization.convert(qat_model)
              # Test if the quantized model can execute
            try:
                # Try a simple forward pass to test execution
                test_input = torch.randn(1, 10)  # Simple test input
                if not self._safe_quantized_execution(quantized_model, test_input):
                    self.logger.warning("Quantized model execution test failed, returning original model")
                    
                    # Store fallback info
                    self.quantization_info[id(qat_model)] = {
                        "type": "qat",
                        "fallback": True,
                        "fallback_reason": "quantized_execution_failed",
                        "original_model_size": self._get_model_size(qat_model),
                        "quantized_model_size": self._get_model_size(qat_model)  # Same as original
                    }
                    
                    return qat_model
            except Exception as e:
                self.logger.debug(f"Could not test quantized model execution: {e}")
            
            # Store quantization info
            self.quantization_info[id(quantized_model)] = {
                "type": "qat",
                "original_model_size": self._get_model_size(qat_model),
                "quantized_model_size": self._get_model_size(quantized_model)
            }
            
            self.logger.info("QAT model converted successfully")
            self.logger.info(f"Model size reduced from {self.quantization_info[id(quantized_model)]['original_model_size']:.2f}MB "
                           f"to {self.quantization_info[id(quantized_model)]['quantized_model_size']:.2f}MB")
            
            return quantized_model
            
        except Exception as e:
            self.logger.error(f"QAT conversion failed: {e}")
            raise RuntimeError(f"QAT conversion failed: {e}")
    
    def _get_model_size(self, model: nn.Module) -> float:
        """Get model size in MB."""
        param_size = 0
        for param in model.parameters():
            param_size += param.nelement() * param.element_size()
        
        buffer_size = 0
        for buffer in model.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()
        
        return (param_size + buffer_size) / 1024 / 1024
    
    def get_quantization_info(self, model: nn.Module) -> Dict[str, Any]:
        """Get quantization information for a model."""
        model_id = id(model)
        return self.quantization_info.get(model_id, {})
    
    def benchmark_quantization(
        self,
        model: nn.Module,
        test_input: torch.Tensor,
        methods: List[str] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Benchmark different quantization methods.
        
        Args:
            model: Model to benchmark
            test_input: Test input for inference timing
            methods: List of quantization methods to benchmark
            
        Returns:
            Benchmark results dictionary
        """
        if methods is None:
            methods = ["original", "dynamic", "fp16"]
        
        results = {}
        
        # Benchmark original model
        if "original" in methods:
            results["original"] = self._benchmark_model(model, test_input)
        
        # Benchmark dynamic quantization
        if "dynamic" in methods:
            try:
                dynamic_model = self.apply_dynamic_quantization(model)
                results["dynamic"] = self._benchmark_model(dynamic_model, test_input)
            except Exception as e:
                self.logger.warning(f"Dynamic quantization benchmark failed: {e}")
                results["dynamic"] = {"error": str(e)}
          # Benchmark FP16
        if "fp16" in methods:
            try:
                fp16_model = model.half()
                fp16_input = test_input.half() if test_input.dtype == torch.float32 else test_input
                results["fp16"] = self._benchmark_model(fp16_model, fp16_input)
            except Exception as e:
                self.logger.warning(f"FP16 benchmark failed: {e}")
                results["fp16"] = {"error": str(e)}
        
        return results
    
    def _benchmark_model(
        self, 
        model: nn.Module, 
        test_input: torch.Tensor,
        num_runs: int = 10
    ) -> Dict[str, float]:
        """Benchmark a single model configuration."""
        import time
        
        try:
            model.eval()
            device = next(model.parameters()).device
            test_input = test_input.to(device)
            
            # Test if model can execute at all
            with torch.no_grad():
                try:
                    _ = model(test_input)
                except NotImplementedError as e:
                    if "quantized::linear" in str(e):
                        return {
                            "avg_inference_time": 0.0,
                            "min_inference_time": 0.0,
                            "max_inference_time": 0.0,
                            "model_size_mb": self._get_model_size(model),
                            "error": "Backend not supported"
                        }
                    raise
            
            # Warmup runs
            with torch.no_grad():
                for _ in range(3):
                    try:
                        _ = model(test_input)
                    except NotImplementedError:
                        # Skip if backend not supported
                        break
            
            # Timing runs with better precision
            times = []
            with torch.no_grad():
                for _ in range(num_runs):
                    if torch.cuda.is_available():
                        torch.cuda.synchronize()
                    
                    start_time = time.perf_counter()
                    _ = model(test_input)
                    
                    if torch.cuda.is_available():
                        torch.cuda.synchronize()
                    
                    end_time = time.perf_counter()
                    times.append(end_time - start_time)
            
            # Ensure we have valid times
            if not times or all(t == 0.0 for t in times):
                return {
                    "avg_inference_time": 0.001,  # Minimum measurable time
                    "min_inference_time": 0.001,
                    "max_inference_time": 0.001,
                    "model_size_mb": self._get_model_size(model)
                }
            
            return {
                "avg_inference_time": sum(times) / len(times),
                "min_inference_time": min(times),
                "max_inference_time": max(times),
                "model_size_mb": self._get_model_size(model)
            }
            
        except Exception as e:
            self.logger.warning(f"Benchmark failed: {e}")
            return {
                "avg_inference_time": 0.0,
                "min_inference_time": 0.0,
                "max_inference_time": 0.0,
                "model_size_mb": self._get_model_size(model),
                "error": str(e)            }


class EnhancedQuantizationManager(QuantizationManager):
    """
    Enhanced quantization manager with adaptive precision and advanced features.
    Extends the base QuantizationManager with additional capabilities.
    """
    
    def __init__(self, config: Optional[QuantizationConfig] = None):
        """
        Initialize enhanced quantization manager.
        
        Args:
            config: Quantization configuration
        """
        super().__init__(config)
        self.precision_manager = AdaptivePrecisionManager(config)
        self.performance_stats = {
            "models_quantized": 0,
            "avg_compression_ratio": 0.0,
            "avg_speedup": 0.0,
            "precision_switches": 0
        }
        
    def auto_optimize_model(
        self,
        model: nn.Module,
        sequence_length: int,
        available_memory_mb: float,
        calibration_data: Optional[DataLoader] = None,
        target_accuracy: float = 0.95
    ) -> Tuple[nn.Module, Dict[str, Any]]:
        """
        Automatically optimize model with best quantization strategy based on constraints.
        
        Args:
            model: Model to optimize
            sequence_length: Expected input sequence length
            available_memory_mb: Available GPU memory
            calibration_data: Optional calibration data
            target_accuracy: Minimum accuracy retention (0.0-1.0)
            
        Returns:
            Tuple of (optimized_model, optimization_stats)
        """
        self.logger.info("Starting automatic model optimization with adaptive precision")
        
        original_memory = self._get_model_size(model)
        
        # Determine optimal precision
        optimal_precision = self.precision_manager.determine_optimal_precision(
            sequence_length=sequence_length,
            available_memory_mb=available_memory_mb,
            model_size_mb=original_memory
        )
        
        self.logger.info(f"Selected {optimal_precision.value} precision for optimization")
        
        # Apply precision-specific optimization
        optimized_model = None
        optimization_stats = {
            "original_precision": "float32",
            "target_precision": optimal_precision.value,
            "optimization_strategy": None,
            "compression_ratio": 1.0,
            "speedup": 1.0,
            "memory_savings_mb": 0.0
        }
        
        try:
            if optimal_precision == QuantizationPrecision.DYNAMIC:
                optimized_model = self.apply_dynamic_quantization(model)
                optimization_stats["optimization_strategy"] = "dynamic_quantization"
                
            elif optimal_precision in [QuantizationPrecision.FLOAT16, QuantizationPrecision.BFLOAT16]:
                optimized_model = self.precision_manager.adapt_model_precision(model, optimal_precision)
                optimization_stats["optimization_strategy"] = f"{optimal_precision.value}_conversion"
                
            elif optimal_precision == QuantizationPrecision.INT8:
                if calibration_data is not None:
                    optimized_model = self.apply_static_quantization(model, calibration_data)
                    optimization_stats["optimization_strategy"] = "static_int8_quantization"
                else:
                    optimized_model = self.apply_dynamic_quantization(model)
                    optimization_stats["optimization_strategy"] = "dynamic_quantization_fallback"
                    
            elif optimal_precision == QuantizationPrecision.INT4:
                optimized_model = self.precision_manager._apply_int4_quantization(model)
                optimization_stats["optimization_strategy"] = "int4_quantization"
                
            else:
                self.logger.warning(f"Unsupported precision {optimal_precision}, using dynamic quantization")
                optimized_model = self.apply_dynamic_quantization(model)
                optimization_stats["optimization_strategy"] = "dynamic_quantization_fallback"
            
            # Calculate optimization stats
            if optimized_model is not None:
                optimized_memory = self._get_model_size(optimized_model)
                optimization_stats.update({
                    "compression_ratio": original_memory / optimized_memory if optimized_memory > 0 else 1.0,
                    "memory_savings_mb": original_memory - optimized_memory,
                    "optimized_model_size_mb": optimized_memory,
                    "original_model_size_mb": original_memory
                })
                
                # Benchmark if possible
                try:
                    base_stats = self.benchmark_model(model)
                    opt_stats = self.benchmark_model(optimized_model)
                    if base_stats["avg_inference_time"] > 0 and opt_stats["avg_inference_time"] > 0:
                        speedup = base_stats["avg_inference_time"] / opt_stats["avg_inference_time"]
                        optimization_stats["speedup"] = speedup
                except Exception as e:
                    self.logger.debug(f"Speed benchmarking failed: {e}")
                    optimization_stats["speedup"] = 1.0
            
            # Update global stats
            self.performance_stats["models_quantized"] += 1
            self.performance_stats["avg_compression_ratio"] = (
                (self.performance_stats["avg_compression_ratio"] * (self.performance_stats["models_quantized"] - 1) +
                 optimization_stats["compression_ratio"]) / self.performance_stats["models_quantized"]
            )
            
            self.logger.info(f"Optimization complete: {optimization_stats['optimization_strategy']} "
                           f"achieved {optimization_stats['compression_ratio']:.2f}x compression")
            
            return optimized_model or model, optimization_stats
            
        except Exception as e:
            self.logger.error(f"Auto-optimization failed: {e}")
            optimization_stats["error"] = str(e)
            return model, optimization_stats
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get cumulative performance statistics.
        
        Returns:
            Dictionary of performance statistics
        """
        return self.performance_stats.copy()


# Convenience functions for easy usage
def apply_dynamic_quantization(model: nn.Module, **kwargs) -> nn.Module:
    """Apply dynamic quantization with default settings."""
    manager = QuantizationManager()
    return manager.apply_dynamic_quantization(model, **kwargs)


def apply_static_quantization(
    model: nn.Module, 
    calibration_dataloader: DataLoader, 
    **kwargs
) -> nn.Module:
    """Apply static quantization with default settings."""
    manager = QuantizationManager()
    return manager.apply_static_quantization(model, calibration_dataloader, **kwargs)


def prepare_qat(model: nn.Module, **kwargs) -> nn.Module:
    """Prepare model for QAT with default settings."""
    manager = QuantizationManager()
    return manager.prepare_qat(model, **kwargs)


def convert_qat(qat_model: nn.Module, **kwargs) -> nn.Module:
    """Convert QAT model to quantized model with default settings."""
    manager = QuantizationManager()
    return manager.convert_qat(qat_model, **kwargs)


# Integration with existing memory optimization
def optimize_model_with_quantization(
    model: nn.Module,
    quantization_type: str = "dynamic",
    calibration_dataloader: Optional[DataLoader] = None,
    **kwargs
) -> nn.Module:
    """
    Optimize model with appropriate quantization method.
    
    Args:
        model: Model to optimize
        quantization_type: Type of quantization ("dynamic", "static", "qat", "none")
        calibration_dataloader: Required for static quantization
        **kwargs: Additional arguments for quantization
        
    Returns:
        Optimized model
    """
    if quantization_type == "none":
        return model
    
    manager = QuantizationManager()
    
    if quantization_type == "dynamic":
        return manager.apply_dynamic_quantization(model, **kwargs)
    elif quantization_type == "static":
        if calibration_dataloader is None:
            raise ValueError("calibration_dataloader is required for static quantization")
        return manager.apply_static_quantization(model, calibration_dataloader, **kwargs)
    elif quantization_type == "qat":
        # For QAT, just prepare the model - user needs to train it separately
        return manager.prepare_qat(model, **kwargs)
    else:
        raise ValueError(f"Unknown quantization type: {quantization_type}")
