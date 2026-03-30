#!/usr/bin/env python3
"""
Test suite for ImpressionCore Deployment Manager

File: src/tests/deployment/test_deployment_manager.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-30
Modified: 2025-05-30
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [testing, deployment, integration]
Dependencies: [pytest, torch, unittest.mock]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM) and deployment targets

Description:
Comprehensive test suite for deployment manager orchestrator:
- Configuration validation
- Model deployment workflows
- Hardware compatibility checks
- Performance benchmarking
- Error handling and recovery
"""

import os
import json
import tempfile
import pytest
import torch
import torch.nn as nn
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from ...deployment.deployment_manager import (
    DeploymentManager,
    DeploymentConfig,
    DeploymentType,
    DeploymentTarget,
    create_deployment_config
)


class SimpleTestModel(nn.Module):
    """Simple model for testing deployment."""
    
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
    """Create basic deployment configuration."""
    return DeploymentConfig(
        deployment_type=DeploymentType.ONNX,
        target_platform=DeploymentTarget.DESKTOP,
        output_dir=temp_output_dir,
        model_name="test_model",
        batch_size=1,
        sequence_length=512,
        verbose=False,
        benchmark_performance=False
    )


class TestDeploymentConfig:
    """Test deployment configuration."""
    
    def test_config_creation(self):
        """Test configuration creation with defaults."""
        config = DeploymentConfig()
        
        assert config.deployment_type == DeploymentType.ONNX
        assert config.target_platform == DeploymentTarget.DESKTOP
        assert config.model_name == "impressioncore_model"
        assert config.batch_size == 1
        assert config.sequence_length == 2048
    
    def test_config_factory_function(self):
        """Test configuration factory function."""
        config = create_deployment_config(
            deployment_type="tensorrt",
            target_platform="server",
            model_name="custom_model",
            batch_size=4
        )
        
        assert config.deployment_type == DeploymentType.TENSORRT
        assert config.target_platform == DeploymentTarget.SERVER
        assert config.model_name == "custom_model"
        assert config.batch_size == 4


class TestDeploymentManager:
    """Test deployment manager functionality."""
    
    def test_initialization(self, basic_config):
        """Test deployment manager initialization."""
        manager = DeploymentManager(basic_config)
        
        assert manager.config == basic_config
        assert manager.onnx_exporter is None
        assert manager.tensorrt_optimizer is None
        assert manager.mobile_deployment is None
        assert manager.distributed_inference is None
        assert len(manager.deployment_artifacts) == 0
        assert len(manager.performance_metrics) == 0
    
    def test_model_validation_success(self, basic_config, test_model):
        """Test successful model validation."""
        manager = DeploymentManager(basic_config)
        
        # Create proper input shape for the test model
        basic_config.sequence_length = 512  # Match model input size
        
        is_valid = manager.validate_model(test_model)
        assert is_valid is True
    
    def test_model_validation_failure(self, basic_config):
        """Test model validation failure."""
        manager = DeploymentManager(basic_config)
        
        # Create a broken model
        class BrokenModel(nn.Module):
            def forward(self, x):
                raise RuntimeError("Broken model")
        
        broken_model = BrokenModel()
        is_valid = manager.validate_model(broken_model)
        assert is_valid is False
    
    @patch('torch.cuda.is_available')
    @patch('torch.cuda.device_count')
    @patch('torch.cuda.get_device_name')
    @patch('torch.cuda.get_device_properties')
    def test_hardware_compatibility_analysis_gpu(
        self, mock_props, mock_name, mock_count, mock_available, basic_config
    ):
        """Test hardware compatibility analysis with GPU."""
        # Setup GPU mocks
        mock_available.return_value = True
        mock_count.return_value = 1
        mock_name.return_value = "NVIDIA GTX 1050 Ti"
        
        # Mock GPU properties
        mock_device_props = Mock()
        mock_device_props.total_memory = 4 * 1024 * 1024 * 1024  # 4GB
        mock_props.return_value = mock_device_props
        
        manager = DeploymentManager(basic_config)
        compatibility = manager.analyze_hardware_compatibility()
        
        assert compatibility["cuda_available"] is True
        assert compatibility["device_count"] == 1
        assert compatibility["device_name"] == "NVIDIA GTX 1050 Ti"
        assert compatibility["memory_available_gb"] == 4.0
        assert compatibility["meets_memory_requirements"] is True
    
    @patch('torch.cuda.is_available')
    def test_hardware_compatibility_analysis_cpu(self, mock_available, basic_config):
        """Test hardware compatibility analysis with CPU only."""
        mock_available.return_value = False
        
        manager = DeploymentManager(basic_config)
        compatibility = manager.analyze_hardware_compatibility()
        
        assert compatibility["cuda_available"] is False
        assert compatibility["device_count"] == 0
        assert compatibility["device_name"] == "CPU"
        assert compatibility["memory_available_gb"] == 0.0
    
    def test_strategy_selection_mobile(self, basic_config):
        """Test deployment strategy selection for mobile."""
        basic_config.target_platform = DeploymentTarget.MOBILE
        manager = DeploymentManager(basic_config)
        
        strategy = manager.select_optimal_strategy(Mock())
        assert strategy == DeploymentType.MOBILE
    
    def test_strategy_selection_cloud(self, basic_config):
        """Test deployment strategy selection for cloud."""
        basic_config.target_platform = DeploymentTarget.CLOUD
        manager = DeploymentManager(basic_config)
        
        strategy = manager.select_optimal_strategy(Mock())
        assert strategy == DeploymentType.DISTRIBUTED
    
    @patch('torch.cuda.is_available')
    def test_strategy_selection_desktop_gpu(self, mock_available, basic_config):
        """Test deployment strategy selection for desktop with GPU."""
        mock_available.return_value = True
        basic_config.target_platform = DeploymentTarget.DESKTOP
        
        manager = DeploymentManager(basic_config)
        
        with patch.object(manager, 'analyze_hardware_compatibility') as mock_analysis:
            mock_analysis.return_value = {
                "cuda_available": True,
                "tensorrt_available": True,
                "onnx_available": True
            }
            
            strategy = manager.select_optimal_strategy(Mock())
            assert strategy == DeploymentType.TENSORRT
    
    @patch('...deployment.onnx_export.ONNXExporter')
    def test_deploy_onnx(self, mock_onnx_exporter, basic_config, test_model):
        """Test ONNX deployment."""
        # Setup mock exporter
        mock_exporter_instance = Mock()
        mock_export_result = {
            "model_path": "/path/to/model.onnx",
            "success": True,
            "optimization_applied": True
        }
        mock_exporter_instance.export_model.return_value = mock_export_result
        mock_onnx_exporter.return_value = mock_exporter_instance
        
        manager = DeploymentManager(basic_config)
        result = manager.deploy_onnx(test_model)
        
        assert result == mock_export_result
        assert "onnx" in manager.deployment_artifacts
        assert manager.deployment_artifacts["onnx"] == mock_export_result
    
    @patch('...deployment.tensorrt_optimizer.TensorRTOptimizer')
    def test_deploy_tensorrt(self, mock_tensorrt_optimizer, basic_config, test_model):
        """Test TensorRT deployment."""
        # Setup mock optimizer
        mock_optimizer_instance = Mock()
        mock_optimization_result = {
            "engine_path": "/path/to/engine.trt",
            "success": True,
            "optimization_applied": True
        }
        mock_optimizer_instance.optimize_model.return_value = mock_optimization_result
        mock_tensorrt_optimizer.return_value = mock_optimizer_instance
        
        manager = DeploymentManager(basic_config)
        result = manager.deploy_tensorrt(test_model)
        
        assert result == mock_optimization_result
        assert "tensorrt" in manager.deployment_artifacts
        assert manager.deployment_artifacts["tensorrt"] == mock_optimization_result
    
    @patch('...deployment.mobile_deployment.MobileDeployment')
    def test_deploy_mobile(self, mock_mobile_deployment, basic_config, test_model):
        """Test mobile deployment."""
        # Setup mock mobile deployment
        mock_mobile_instance = Mock()
        mock_deployment_result = {
            "mobile_model_path": "/path/to/mobile_model.ptl",
            "success": True,
            "platforms": ["android", "ios"]
        }
        mock_mobile_instance.deploy_model.return_value = mock_deployment_result
        mock_mobile_deployment.return_value = mock_mobile_instance
        
        manager = DeploymentManager(basic_config)
        result = manager.deploy_mobile(test_model)
        
        assert result == mock_deployment_result
        assert "mobile" in manager.deployment_artifacts
        assert manager.deployment_artifacts["mobile"] == mock_deployment_result
    
    @patch('...deployment.distributed_inference.DistributedInference')
    def test_deploy_distributed(self, mock_distributed_inference, basic_config, test_model):
        """Test distributed deployment."""
        # Setup mock distributed inference
        mock_distributed_instance = Mock()
        mock_setup_result = {
            "distributed_config": "/path/to/config.yaml",
            "success": True,
            "nodes": 2
        }
        mock_distributed_instance.setup_distributed_model.return_value = mock_setup_result
        mock_distributed_inference.return_value = mock_distributed_instance
        
        manager = DeploymentManager(basic_config)
        result = manager.deploy_distributed(test_model)
        
        assert result == mock_setup_result
        assert "distributed" in manager.deployment_artifacts
        assert manager.deployment_artifacts["distributed"] == mock_setup_result
    
    def test_benchmark_deployment(self, basic_config, test_model):
        """Test deployment benchmarking."""
        basic_config.sequence_length = 512  # Match test model
        manager = DeploymentManager(basic_config)
        
        metrics = manager.benchmark_deployment(test_model, DeploymentType.ONNX)
        
        assert "latency_ms" in metrics
        assert "throughput_tokens_per_sec" in metrics
        assert "memory_usage_mb" in metrics
        assert "accuracy_score" in metrics
        assert metrics["latency_ms"] > 0
        assert metrics["throughput_tokens_per_sec"] > 0
    
    @patch.object(DeploymentManager, 'deploy_onnx')
    @patch.object(DeploymentManager, 'validate_model')
    def test_deploy_integration(self, mock_validate, mock_deploy_onnx, basic_config, test_model):
        """Test integrated deployment workflow."""
        mock_validate.return_value = True
        mock_deploy_result = {"success": True, "model_path": "/path/to/model.onnx"}
        mock_deploy_onnx.return_value = mock_deploy_result
        
        manager = DeploymentManager(basic_config)
        result = manager.deploy(test_model, DeploymentType.ONNX)
        
        mock_validate.assert_called_once_with(test_model)
        mock_deploy_onnx.assert_called_once_with(test_model)
        assert result == mock_deploy_result
    
    def test_deployment_report_saving(self, basic_config, test_model):
        """Test deployment report saving."""
        manager = DeploymentManager(basic_config)
        
        # Mock result data
        result = {
            "success": True,
            "model_path": "/path/to/model.onnx"
        }
        
        manager.save_deployment_report(DeploymentType.ONNX, result)
        
        # Check report file exists
        report_path = Path(basic_config.output_dir) / f"{basic_config.model_name}_onnx_report.json"
        assert report_path.exists()
        
        # Verify report content
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        assert report_data["deployment_type"] == "onnx"
        assert report_data["config"]["model_name"] == basic_config.model_name
        assert report_data["result"] == result
    
    def test_get_deployment_artifacts(self, basic_config):
        """Test getting deployment artifacts."""
        manager = DeploymentManager(basic_config)
        
        # Add some test artifacts
        manager.deployment_artifacts["onnx"] = {"path": "/model.onnx"}
        manager.deployment_artifacts["tensorrt"] = {"path": "/model.trt"}
        
        artifacts = manager.get_deployment_artifacts()
        assert len(artifacts) == 2
        assert "onnx" in artifacts
        assert "tensorrt" in artifacts
    
    def test_get_performance_metrics(self, basic_config):
        """Test getting performance metrics."""
        manager = DeploymentManager(basic_config)
        
        # Add some test metrics
        manager.performance_metrics["onnx"] = {"latency_ms": 50.0}
        manager.performance_metrics["tensorrt"] = {"latency_ms": 25.0}
        
        metrics = manager.get_performance_metrics()
        assert len(metrics) == 2
        assert "onnx" in metrics
        assert "tensorrt" in metrics
    
    def test_cleanup(self, basic_config):
        """Test deployment manager cleanup."""
        manager = DeploymentManager(basic_config)
        
        # Should not raise any exceptions
        manager.cleanup()


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_invalid_deployment_type(self, basic_config, test_model):
        """Test handling of invalid deployment type."""
        manager = DeploymentManager(basic_config)
        
        with pytest.raises(ValueError, match="Unsupported deployment type"):
            manager.deploy(test_model, "invalid_type")
    
    def test_model_validation_failure_blocks_deployment(self, basic_config):
        """Test that model validation failure prevents deployment."""
        manager = DeploymentManager(basic_config)
        
        # Create a model that will fail validation
        class BrokenModel(nn.Module):
            def forward(self, x):
                raise RuntimeError("Broken")
        
        broken_model = BrokenModel()
        
        with pytest.raises(ValueError, match="Model validation failed"):
            manager.deploy(broken_model)
    
    @patch('...deployment.onnx_export.ONNXExporter')
    def test_deployment_failure_propagation(self, mock_onnx_exporter, basic_config, test_model):
        """Test that deployment failures are properly propagated."""
        # Setup mock to raise exception
        mock_exporter_instance = Mock()
        mock_exporter_instance.export_model.side_effect = RuntimeError("Export failed")
        mock_onnx_exporter.return_value = mock_exporter_instance
        
        manager = DeploymentManager(basic_config)
        
        with pytest.raises(RuntimeError, match="Export failed"):
            manager.deploy_onnx(test_model)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
