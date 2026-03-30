#!/usr/bin/env python3
"""
ImpressionCore: Quantization Integration Tests

Test suite for enhanced quantization functionality.

File: src/tests/integration/test_quantization_integration.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-28
Modified: 2025-05-28
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle

License: MIT
Copyright (c) 2025 ImpressionCore Team
"""

import pytest
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import logging
from unittest.mock import patch, MagicMock

# Test imports
from src.core.utils.memory_optimization.quantization import (
    QuantizationManager,
    QuantizationConfig,
    CalibrationDataset,
    apply_dynamic_quantization,
    apply_static_quantization,
    prepare_qat,
    convert_qat,
    optimize_model_with_quantization
)

logger = logging.getLogger(__name__)

def create_test_model():
    """Create a simple test model for quantization testing."""
    return nn.Sequential(
        nn.Linear(10, 20),
        nn.ReLU(),
        nn.Linear(20, 10),
        nn.ReLU(),
        nn.Linear(10, 2)
    )

def create_test_dataloader(batch_size: int = 4, num_batches: int = 10):
    """Create a test dataloader for calibration."""
    # Generate random data
    data = torch.randn(batch_size * num_batches, 10)
    targets = torch.randint(0, 2, (batch_size * num_batches,))
    
    dataset = TensorDataset(data, targets)
    return DataLoader(dataset, batch_size=batch_size, shuffle=False)

class TestQuantizationManager:
    """Test suite for QuantizationManager."""
    
    def test_quantization_manager_initialization(self):
        """Test QuantizationManager initialization."""
        # Default initialization
        manager = QuantizationManager()
        assert manager.config is not None
        assert manager.config.quantization_type == "dynamic"
        
        # Custom configuration
        config = QuantizationConfig(quantization_type="static", calibration_batches=50)
        manager = QuantizationManager(config)
        assert manager.config.quantization_type == "static"
        assert manager.config.calibration_batches == 50
    
    def test_dynamic_quantization(self):
        """Test dynamic quantization functionality."""
        model = create_test_model()
        manager = QuantizationManager()
        
        # Get original model size
        original_size = manager._get_model_size(model)
        
        # Apply dynamic quantization
        quantized_model = manager.apply_dynamic_quantization(model)
        
        # Verify model is quantized
        assert quantized_model is not None
        assert hasattr(quantized_model, '_modules')
        
        # Check quantization info
        info = manager.get_quantization_info(quantized_model)
        assert info["type"] == "dynamic"
        assert "original_model_size" in info
        assert "quantized_model_size" in info
        
        # Test inference still works
        test_input = torch.randn(1, 10)
        with torch.no_grad():
            output = quantized_model(test_input)
            assert output.shape == (1, 2)
    
    def test_dynamic_quantization_fallback(self):
        """Test dynamic quantization fallback mechanisms."""
        model = create_test_model()
        config = QuantizationConfig(fallback_to_fp16=True, fallback_to_original=True)
        manager = QuantizationManager(config)
        
        # Mock quantization to fail
        with patch('torch.quantization.quantize_dynamic', side_effect=RuntimeError("Quantization failed")):
            # Should fallback to FP16
            result_model = manager.apply_dynamic_quantization(model)
            assert result_model is not None
    
    def test_static_quantization(self):
        """Test static quantization with calibration."""
        model = create_test_model()
        manager = QuantizationManager()
        calibration_loader = create_test_dataloader(batch_size=2, num_batches=5)
        
        # Apply static quantization
        quantized_model = manager.apply_static_quantization(model, calibration_loader)
        
        # Verify model is quantized
        assert quantized_model is not None
        
        # Check quantization info
        info = manager.get_quantization_info(quantized_model)
        assert info["type"] == "static"
        assert "calibration_batches" in info
        assert info["calibration_batches"] > 0
        
        # Test inference still works
        test_input = torch.randn(1, 10)
        with torch.no_grad():
            output = quantized_model(test_input)
            assert output.shape == (1, 2)
    
    def test_static_quantization_with_minimal_data(self):
        """Test static quantization handles minimal calibration data."""
        model = create_test_model()
        manager = QuantizationManager()
        
        # Create very small calibration dataset
        calibration_loader = create_test_dataloader(batch_size=1, num_batches=1)
        
        # Should still work with minimal data
        quantized_model = manager.apply_static_quantization(model, calibration_loader)
        assert quantized_model is not None
    
    def test_qat_preparation(self):
        """Test QAT model preparation."""
        model = create_test_model()
        manager = QuantizationManager()
        
        # Prepare model for QAT
        qat_model = manager.prepare_qat(model)
        
        # Verify QAT model preparation
        assert qat_model is not None
        assert hasattr(qat_model, 'qconfig')
        
        # QAT model should be in training mode
        assert qat_model.training
    
    def test_qat_conversion(self):
        """Test QAT model conversion to quantized model."""
        model = create_test_model()
        manager = QuantizationManager()
        
        # Prepare for QAT
        qat_model = manager.prepare_qat(model)
        
        # Simulate some training (just a forward pass)
        test_input = torch.randn(4, 10)
        with torch.no_grad():
            _ = qat_model(test_input)
        
        # Convert QAT model to quantized
        quantized_model = manager.convert_qat(qat_model)
        
        # Verify conversion
        assert quantized_model is not None
        
        # Check quantization info
        info = manager.get_quantization_info(quantized_model)
        assert info["type"] == "qat"
        
        # Test inference
        with torch.no_grad():
            output = quantized_model(test_input)
            assert output.shape == (4, 2)
    
    def test_model_size_calculation(self):
        """Test model size calculation utility."""
        model = create_test_model()
        manager = QuantizationManager()
        
        size_mb = manager._get_model_size(model)
        assert isinstance(size_mb, float)
        assert size_mb > 0
    
    def test_quantization_benchmarking(self):
        """Test quantization benchmarking functionality."""
        model = create_test_model()
        manager = QuantizationManager()
        test_input = torch.randn(1, 10)
        
        # Run benchmark
        results = manager.benchmark_quantization(model, test_input, methods=["original", "dynamic"])
        
        # Verify results structure
        assert "original" in results
        assert "dynamic" in results
        
        # Check original results
        original_results = results["original"]
        assert "avg_inference_time" in original_results
        assert "model_size_mb" in original_results
        assert original_results["avg_inference_time"] > 0
        assert original_results["model_size_mb"] > 0

class TestCalibrationDataset:
    """Test suite for CalibrationDataset."""
    
    def test_calibration_dataset_initialization(self):
        """Test CalibrationDataset initialization."""
        dataloader = create_test_dataloader()
        calibration_dataset = CalibrationDataset(dataloader, max_batches=5)
        
        assert calibration_dataset.dataloader is dataloader
        assert calibration_dataset.max_batches == 5
        assert calibration_dataset.current_batch == 0
    
    def test_calibration_dataset_iteration(self):
        """Test CalibrationDataset iteration with max_batches limit."""
        dataloader = create_test_dataloader(num_batches=10)
        calibration_dataset = CalibrationDataset(dataloader, max_batches=3)
        
        batch_count = 0
        for batch in calibration_dataset:
            batch_count += 1
            assert len(batch) == 2  # data and targets
        
        # Should stop at max_batches
        assert batch_count == 3

class TestConvenienceFunctions:
    """Test suite for convenience functions."""
    
    def test_apply_dynamic_quantization(self):
        """Test apply_dynamic_quantization convenience function."""
        model = create_test_model()
        quantized_model = apply_dynamic_quantization(model)
        
        assert quantized_model is not None
        
        # Test inference
        test_input = torch.randn(1, 10)
        with torch.no_grad():
            output = quantized_model(test_input)
            assert output.shape == (1, 2)
    
    def test_apply_static_quantization(self):
        """Test apply_static_quantization convenience function."""
        model = create_test_model()
        calibration_loader = create_test_dataloader(batch_size=2, num_batches=3)
        
        quantized_model = apply_static_quantization(model, calibration_loader)
        
        assert quantized_model is not None
        
        # Test inference
        test_input = torch.randn(1, 10)
        with torch.no_grad():
            output = quantized_model(test_input)
            assert output.shape == (1, 2)
    
    def test_prepare_qat_function(self):
        """Test prepare_qat convenience function."""
        model = create_test_model()
        qat_model = prepare_qat(model)
        
        assert qat_model is not None
        assert qat_model.training
    
    def test_convert_qat_function(self):
        """Test convert_qat convenience function."""
        model = create_test_model()
        qat_model = prepare_qat(model)
        
        # Simulate training
        test_input = torch.randn(2, 10)
        with torch.no_grad():
            _ = qat_model(test_input)
        
        quantized_model = convert_qat(qat_model)
        
        assert quantized_model is not None
        
        # Test inference
        with torch.no_grad():
            output = quantized_model(test_input)
            assert output.shape == (2, 2)
    
    def test_optimize_model_with_quantization(self):
        """Test optimize_model_with_quantization function."""
        model = create_test_model()
        
        # Test dynamic quantization
        dynamic_model = optimize_model_with_quantization(model, "dynamic")
        assert dynamic_model is not None
        
        # Test static quantization
        calibration_loader = create_test_dataloader()
        static_model = optimize_model_with_quantization(
            model, "static", calibration_dataloader=calibration_loader
        )
        assert static_model is not None
        
        # Test QAT preparation
        qat_model = optimize_model_with_quantization(model, "qat")
        assert qat_model is not None
        assert qat_model.training
        
        # Test no quantization
        no_quant_model = optimize_model_with_quantization(model, "none")
        assert no_quant_model is model  # Should return same model
        
        # Test invalid quantization type
        with pytest.raises(ValueError):
            optimize_model_with_quantization(model, "invalid_type")
        
        # Test static quantization without calibration data
        with pytest.raises(ValueError):
            optimize_model_with_quantization(model, "static")

class TestQuantizationIntegration:
    """Integration tests for quantization with other components."""
    
    def test_quantization_with_memory_optimization(self):
        """Test quantization integration with memory optimization."""
        model = create_test_model()
        
        # Test import of quantization functions from memory optimization module
        from src.core.utils.memory_optimization import (
            apply_dynamic_quantization,
            apply_static_quantization,
            optimize_model_with_quantization
        )
        
        # Test dynamic quantization
        dynamic_model = apply_dynamic_quantization(model)
        assert dynamic_model is not None
        
        # Test static quantization
        calibration_loader = create_test_dataloader()
        static_model = apply_static_quantization(model, calibration_loader)
        assert static_model is not None
    
    def test_quantization_error_handling(self):
        """Test quantization error handling and fallbacks."""
        model = create_test_model()
        
        # Test with invalid backend
        config = QuantizationConfig(backend="invalid_backend")
        manager = QuantizationManager(config)
        
        # Should still work with fallback
        quantized_model = manager.apply_dynamic_quantization(model)
        assert quantized_model is not None
    
    def test_quantization_memory_cleanup(self):
        """Test that quantization properly handles memory cleanup."""
        model = create_test_model()
        calibration_loader = create_test_dataloader()
        
        config = QuantizationConfig(clear_cache_after_calibration=True)
        manager = QuantizationManager(config)
        
        # This should complete without memory errors
        quantized_model = manager.apply_static_quantization(model, calibration_loader)
        assert quantized_model is not None

if __name__ == "__main__":
    # Run specific tests for debugging
    test_manager = TestQuantizationManager()
    test_manager.test_dynamic_quantization()
    test_manager.test_static_quantization()
    
    test_convenience = TestConvenienceFunctions()
    test_convenience.test_apply_dynamic_quantization()
    
    print("All quantization integration tests passed!")
