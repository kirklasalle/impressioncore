#!/usr/bin/env python3
"""
Test suite for ImpressionCore ONNX Export Module

File: src/tests/deployment/test_onnx_export.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-30
Modified: 2025-05-30
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [testing, onnx, export, deployment]
Dependencies: [pytest, torch, unittest.mock]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Test suite for ONNX export functionality:
- Model export validation
- Quantization integration
- Mobile optimization
- Error handling
"""

import tempfile
import pytest
import torch
import torch.nn as nn
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from ...deployment.onnx_export import ONNXExporter, ONNXExportConfig


class SimpleTestModel(nn.Module):
    """Simple model for testing ONNX export."""
    
    def __init__(self, input_size: int = 512, hidden_size: int = 256, output_size: int = 128):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.linear2 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        x = self.linear1(x)
        x = self.relu(x)
        x = self.linear2(x)
        return x


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def test_model():
    """Create test model."""
    model = SimpleTestModel()
    model.eval()
    return model


@pytest.fixture
def basic_config(temp_output_dir):
    """Create basic ONNX export configuration."""
    return ONNXExportConfig(
        output_dir=temp_output_dir,
        model_name="test_model",
        batch_size=1,
        sequence_length=512,
        verbose=False
    )


class TestONNXExportConfig:
    """Test ONNX export configuration."""
    
    def test_config_defaults(self):
        """Test configuration default values."""
        config = ONNXExportConfig()
        
        assert config.model_name == "impressioncore_model"
        assert config.batch_size == 1
        assert config.sequence_length == 2048
        assert config.opset_version == 17
        assert config.optimize_for_mobile is False
        assert config.quantization_enabled is True
    
    def test_config_custom_values(self):
        """Test configuration with custom values."""
        config = ONNXExportConfig(
            model_name="custom_model",
            batch_size=4,
            sequence_length=1024,
            opset_version=15,
            optimize_for_mobile=True
        )
        
        assert config.model_name == "custom_model"
        assert config.batch_size == 4
        assert config.sequence_length == 1024
        assert config.opset_version == 15
        assert config.optimize_for_mobile is True


class TestONNXExporter:
    """Test ONNX exporter functionality."""
    
    def test_initialization(self, basic_config):
        """Test ONNX exporter initialization."""
        exporter = ONNXExporter(basic_config)
        
        assert exporter.config == basic_config
        assert exporter.quantization_manager is not None
    
    @patch('torch.onnx.export')
    def test_export_model_basic(self, mock_export, basic_config, test_model):
        """Test basic model export."""
        exporter = ONNXExporter(basic_config)
        
        result = exporter.export_model(test_model)
        
        # Verify export was called
        mock_export.assert_called_once()
        
        # Check result structure
        assert "success" in result
        assert "model_path" in result
        assert "optimization_applied" in result
        assert result["success"] is True
    
    @patch('torch.onnx.export')
    def test_export_model_with_quantization(self, mock_export, basic_config, test_model):
        """Test model export with quantization enabled."""
        basic_config.quantization_enabled = True
        basic_config.quantization_type = "int8"
        
        exporter = ONNXExporter(basic_config)
        
        with patch.object(exporter.quantization_manager, 'quantize_model') as mock_quantize:
            mock_quantize.return_value = test_model
            
            result = exporter.export_model(test_model)
            
            mock_quantize.assert_called_once()
            assert result["success"] is True
    
    @patch('torch.onnx.export')
    def test_export_model_mobile_optimization(self, mock_export, basic_config, test_model):
        """Test model export with mobile optimization."""
        basic_config.optimize_for_mobile = True
        
        exporter = ONNXExporter(basic_config)
        
        result = exporter.export_model(test_model)
        
        assert result["success"] is True
        assert "mobile_optimized" in result
    
    def test_create_dummy_input(self, basic_config):
        """Test dummy input creation."""
        exporter = ONNXExporter(basic_config)
        
        dummy_input = exporter._create_dummy_input()
        
        expected_shape = (basic_config.batch_size, basic_config.sequence_length)
        assert dummy_input.shape == expected_shape
        assert dummy_input.dtype == torch.float32
    
    def test_create_dummy_input_fp16(self, basic_config):
        """Test dummy input creation with FP16."""
        basic_config.precision = "fp16"
        exporter = ONNXExporter(basic_config)
        
        dummy_input = exporter._create_dummy_input()
        assert dummy_input.dtype == torch.float16
    
    @patch('onnx.load')
    @patch('onnxruntime.InferenceSession')
    def test_validate_onnx_model(self, mock_session, mock_load, basic_config):
        """Test ONNX model validation."""
        # Setup mocks
        mock_model = Mock()
        mock_load.return_value = mock_model
        
        mock_session_instance = Mock()
        mock_session_instance.run.return_value = [torch.randn(1, 128).numpy()]
        mock_session.return_value = mock_session_instance
        
        exporter = ONNXExporter(basic_config)
        
        # Create a temporary ONNX file
        onnx_path = Path(basic_config.output_dir) / "test_model.onnx"
        onnx_path.touch()
        
        is_valid = exporter._validate_onnx_model(str(onnx_path))
        
        assert is_valid is True
        mock_load.assert_called_once_with(str(onnx_path))
        mock_session.assert_called_once()
    
    def test_validate_onnx_model_missing_file(self, basic_config):
        """Test ONNX model validation with missing file."""
        exporter = ONNXExporter(basic_config)
        
        is_valid = exporter._validate_onnx_model("nonexistent_model.onnx")
        assert is_valid is False
    
    @patch('torch.onnx.export')
    def test_export_model_error_handling(self, mock_export, basic_config, test_model):
        """Test error handling during export."""
        # Setup mock to raise exception
        mock_export.side_effect = RuntimeError("Export failed")
        
        exporter = ONNXExporter(basic_config)
        
        result = exporter.export_model(test_model)
        
        assert result["success"] is False
        assert "error" in result
        assert "Export failed" in result["error"]
    
    def test_get_export_path(self, basic_config):
        """Test export path generation."""
        exporter = ONNXExporter(basic_config)
        
        export_path = exporter._get_export_path()
        expected_path = Path(basic_config.output_dir) / f"{basic_config.model_name}.onnx"
        
        assert export_path == str(expected_path)
    
    def test_get_export_path_mobile(self, basic_config):
        """Test export path generation for mobile."""
        basic_config.optimize_for_mobile = True
        exporter = ONNXExporter(basic_config)
        
        export_path = exporter._get_export_path()
        expected_path = Path(basic_config.output_dir) / f"{basic_config.model_name}_mobile.onnx"
        
        assert export_path == str(expected_path)
    
    @patch('torch.onnx.export')
    def test_export_dynamic_axes(self, mock_export, basic_config, test_model):
        """Test export with dynamic axes."""
        basic_config.dynamic_axes = {
            'input': {0: 'batch_size', 1: 'sequence_length'},
            'output': {0: 'batch_size'}
        }
        
        exporter = ONNXExporter(basic_config)
        exporter.export_model(test_model)
        
        # Verify dynamic_axes was passed to export
        args, kwargs = mock_export.call_args
        assert 'dynamic_axes' in kwargs
        assert kwargs['dynamic_axes'] == basic_config.dynamic_axes
    
    @patch('torch.onnx.export')
    def test_export_input_names(self, mock_export, basic_config, test_model):
        """Test export with custom input/output names."""
        basic_config.input_names = ['input_ids']
        basic_config.output_names = ['logits']
        
        exporter = ONNXExporter(basic_config)
        exporter.export_model(test_model)
        
        # Verify names were passed to export
        args, kwargs = mock_export.call_args
        assert 'input_names' in kwargs
        assert 'output_names' in kwargs
        assert kwargs['input_names'] == ['input_ids']
        assert kwargs['output_names'] == ['logits']


class TestQuantizationIntegration:
    """Test quantization integration with ONNX export."""
    
    @patch('torch.onnx.export')
    def test_int8_quantization(self, mock_export, basic_config, test_model):
        """Test INT8 quantization integration."""
        basic_config.quantization_enabled = True
        basic_config.quantization_type = "int8"
        
        exporter = ONNXExporter(basic_config)
        
        with patch.object(exporter.quantization_manager, 'quantize_model') as mock_quantize:
            # Setup quantization to return the model
            mock_quantize.return_value = test_model
            
            result = exporter.export_model(test_model)
            
            # Verify quantization was called with correct parameters
            mock_quantize.assert_called_once_with(
                test_model, 
                quantization_type="int8",
                device=torch.device("cpu")
            )
            assert result["success"] is True
    
    @patch('torch.onnx.export')
    def test_int4_quantization(self, mock_export, basic_config, test_model):
        """Test INT4 quantization integration."""
        basic_config.quantization_enabled = True
        basic_config.quantization_type = "int4"
        
        exporter = ONNXExporter(basic_config)
        
        with patch.object(exporter.quantization_manager, 'quantize_model') as mock_quantize:
            mock_quantize.return_value = test_model
            
            result = exporter.export_model(test_model)
            
            mock_quantize.assert_called_once_with(
                test_model,
                quantization_type="int4", 
                device=torch.device("cpu")
            )
            assert result["success"] is True
    
    @patch('torch.onnx.export')
    def test_quantization_disabled(self, mock_export, basic_config, test_model):
        """Test export with quantization disabled."""
        basic_config.quantization_enabled = False
        
        exporter = ONNXExporter(basic_config)
        
        with patch.object(exporter.quantization_manager, 'quantize_model') as mock_quantize:
            result = exporter.export_model(test_model)
            
            # Verify quantization was not called
            mock_quantize.assert_not_called()
            assert result["success"] is True


class TestOptionalDependencies:
    """Test handling of optional dependencies."""
    
    @patch('torch.onnx.export')
    def test_missing_onnx_dependency(self, mock_export, basic_config, test_model):
        """Test graceful handling when ONNX is not available."""
        exporter = ONNXExporter(basic_config)
        
        with patch('importlib.util.find_spec', return_value=None):
            result = exporter.export_model(test_model)
            
            # Should still attempt export but may fail gracefully
            assert "success" in result
    
    @patch('torch.onnx.export')
    def test_missing_onnxruntime_dependency(self, mock_export, basic_config, test_model):
        """Test handling when ONNXRuntime is not available."""
        exporter = ONNXExporter(basic_config)
        
        # Mock import error for onnxruntime
        with patch('builtins.__import__', side_effect=ImportError("No module named 'onnxruntime'")):
            # Export should succeed even if validation fails
            result = exporter.export_model(test_model)
            assert "success" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
