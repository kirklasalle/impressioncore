#!/usr/bin/env python3
"""
Test suite for ImpressionCore Deployment Integration

File: src/tests/deployment/test_deployment_integration.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-30
Modified: 2025-05-30
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [testing, deployment, integration, end-to-end]
Dependencies: [pytest, torch, unittest.mock]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Integration test suite for deployment system:
- End-to-end deployment workflows
- Cross-module integration
- Performance validation
- Resource management
"""

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
    DeploymentTarget
)


class ComplexTestModel(nn.Module):
    """More complex model for integration testing."""
    
    def __init__(self, vocab_size: int = 1000, hidden_size: int = 512, num_layers: int = 2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=hidden_size,
                nhead=8,
                dim_feedforward=hidden_size * 4,
                batch_first=True
            )
            for _ in range(num_layers)
        ])
        self.output_projection = nn.Linear(hidden_size, vocab_size)
    
    def forward(self, input_ids):
        x = self.embedding(input_ids)
        
        for layer in self.layers:
            x = layer(x)
        
        return self.output_projection(x)


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def complex_model():
    """Create complex test model."""
    model = ComplexTestModel()
    model.eval()
    return model


@pytest.fixture
def deployment_configs(temp_output_dir):
    """Create deployment configurations for different types."""
    base_config = {
        "output_dir": temp_output_dir,
        "model_name": "integration_test_model",
        "batch_size": 1,
        "sequence_length": 512,
        "verbose": False,
        "benchmark_performance": True
    }
    
    return {
        "onnx": DeploymentConfig(
            deployment_type=DeploymentType.ONNX,
            target_platform=DeploymentTarget.DESKTOP,
            **base_config
        ),
        "tensorrt": DeploymentConfig(
            deployment_type=DeploymentType.TENSORRT,
            target_platform=DeploymentTarget.SERVER,
            **base_config
        ),
        "mobile": DeploymentConfig(
            deployment_type=DeploymentType.MOBILE,
            target_platform=DeploymentTarget.MOBILE,
            **base_config
        ),
        "distributed": DeploymentConfig(
            deployment_type=DeploymentType.DISTRIBUTED,
            target_platform=DeploymentTarget.CLOUD,
            **base_config
        )
    }


class TestEndToEndDeployment:
    """Test complete deployment workflows."""
    
    @patch('...deployment.onnx_export.ONNXExporter')
    def test_complete_onnx_workflow(self, mock_onnx_exporter, deployment_configs, complex_model):
        """Test complete ONNX deployment workflow."""
        # Setup mock exporter
        mock_exporter_instance = Mock()
        mock_export_result = {
            "success": True,
            "model_path": "/path/to/model.onnx",
            "optimization_applied": True,
            "model_size_mb": 45.2,
            "export_time_seconds": 12.5
        }
        mock_exporter_instance.export_model.return_value = mock_export_result
        mock_onnx_exporter.return_value = mock_exporter_instance
        
        # Execute deployment
        config = deployment_configs["onnx"]
        manager = DeploymentManager(config)
        
        result = manager.deploy(complex_model, DeploymentType.ONNX)
        
        # Verify results
        assert result["success"] is True
        assert "model_path" in result
        assert "performance_metrics" in result
        
        # Verify artifacts were stored
        artifacts = manager.get_deployment_artifacts()
        assert "onnx" in artifacts
        
        # Verify performance metrics were collected
        metrics = manager.get_performance_metrics()
        assert "onnx" in metrics
        assert "latency_ms" in metrics["onnx"]
    
    @patch('...deployment.tensorrt_optimizer.TensorRTOptimizer')
    def test_complete_tensorrt_workflow(self, mock_tensorrt_optimizer, deployment_configs, complex_model):
        """Test complete TensorRT deployment workflow."""
        # Setup mock optimizer
        mock_optimizer_instance = Mock()
        mock_optimization_result = {
            "success": True,
            "engine_path": "/path/to/engine.trt",
            "optimization_applied": True,
            "speedup_factor": 2.3,
            "memory_reduction_percent": 15.0
        }
        mock_optimizer_instance.optimize_model.return_value = mock_optimization_result
        mock_tensorrt_optimizer.return_value = mock_optimizer_instance
        
        # Execute deployment
        config = deployment_configs["tensorrt"]
        manager = DeploymentManager(config)
        
        result = manager.deploy(complex_model, DeploymentType.TENSORRT)
        
        # Verify results
        assert result["success"] is True
        assert "engine_path" in result
        assert "speedup_factor" in result
        
        # Verify artifacts
        artifacts = manager.get_deployment_artifacts()
        assert "tensorrt" in artifacts
    
    @patch('...deployment.mobile_deployment.MobileDeployment')
    def test_complete_mobile_workflow(self, mock_mobile_deployment, deployment_configs, complex_model):
        """Test complete mobile deployment workflow."""
        # Setup mock mobile deployment
        mock_mobile_instance = Mock()
        mock_deployment_result = {
            "success": True,
            "mobile_model_path": "/path/to/mobile_model.ptl",
            "platforms": ["android", "ios"],
            "model_size_mb": 25.8,
            "quantization_applied": True
        }
        mock_mobile_instance.deploy_model.return_value = mock_deployment_result
        mock_mobile_deployment.return_value = mock_mobile_instance
        
        # Execute deployment
        config = deployment_configs["mobile"]
        manager = DeploymentManager(config)
        
        result = manager.deploy(complex_model, DeploymentType.MOBILE)
        
        # Verify results
        assert result["success"] is True
        assert "mobile_model_path" in result
        assert "platforms" in result
        
        # Verify artifacts
        artifacts = manager.get_deployment_artifacts()
        assert "mobile" in artifacts
    
    @patch('...deployment.distributed_inference.DistributedInference')
    def test_complete_distributed_workflow(self, mock_distributed_inference, deployment_configs, complex_model):
        """Test complete distributed deployment workflow."""
        # Setup mock distributed inference
        mock_distributed_instance = Mock()
        mock_setup_result = {
            "success": True,
            "distributed_config": "/path/to/config.yaml",
            "nodes": 4,
            "parallelism_strategy": "data_parallel",
            "estimated_throughput": 150.0
        }
        mock_distributed_instance.setup_distributed_model.return_value = mock_setup_result
        mock_distributed_inference.return_value = mock_distributed_instance
        
        # Execute deployment
        config = deployment_configs["distributed"]
        manager = DeploymentManager(config)
        
        result = manager.deploy(complex_model, DeploymentType.DISTRIBUTED)
        
        # Verify results
        assert result["success"] is True
        assert "distributed_config" in result
        assert "nodes" in result
        
        # Verify artifacts
        artifacts = manager.get_deployment_artifacts()
        assert "distributed" in artifacts


class TestCrossModuleIntegration:
    """Test integration between deployment modules."""
    
    @patch('...deployment.onnx_export.ONNXExporter')
    @patch('...deployment.tensorrt_optimizer.TensorRTOptimizer')
    def test_onnx_to_tensorrt_pipeline(self, mock_tensorrt, mock_onnx, deployment_configs, complex_model):
        """Test ONNX export followed by TensorRT optimization."""
        # Setup ONNX export mock
        mock_onnx_instance = Mock()
        onnx_result = {
            "success": True,
            "model_path": "/path/to/model.onnx"
        }
        mock_onnx_instance.export_model.return_value = onnx_result
        mock_onnx.return_value = mock_onnx_instance
        
        # Setup TensorRT optimization mock
        mock_tensorrt_instance = Mock()
        tensorrt_result = {
            "success": True,
            "engine_path": "/path/to/engine.trt"
        }
        mock_tensorrt_instance.optimize_model.return_value = tensorrt_result
        mock_tensorrt.return_value = mock_tensorrt_instance
        
        # First deploy to ONNX
        onnx_config = deployment_configs["onnx"]
        onnx_manager = DeploymentManager(onnx_config)
        onnx_deploy_result = onnx_manager.deploy(complex_model, DeploymentType.ONNX)
        
        # Then optimize with TensorRT
        tensorrt_config = deployment_configs["tensorrt"]
        tensorrt_manager = DeploymentManager(tensorrt_config)
        tensorrt_deploy_result = tensorrt_manager.deploy(complex_model, DeploymentType.TENSORRT)
        
        # Verify both deployments succeeded
        assert onnx_deploy_result["success"] is True
        assert tensorrt_deploy_result["success"] is True
    
    def test_multi_deployment_manager(self, deployment_configs, complex_model):
        """Test deploying same model to multiple targets."""
        deployment_results = {}
        
        # Deploy to multiple targets
        for deployment_type, config in deployment_configs.items():
            manager = DeploymentManager(config)
            
            # Mock the specific deployment methods
            with patch.object(manager, f'deploy_{deployment_type}') as mock_deploy:
                mock_deploy.return_value = {
                    "success": True,
                    "deployment_type": deployment_type
                }
                
                result = manager.deploy(complex_model, DeploymentType(deployment_type))
                deployment_results[deployment_type] = result
        
        # Verify all deployments
        assert len(deployment_results) == 4
        for deployment_type, result in deployment_results.items():
            assert result["success"] is True
            assert result["deployment_type"] == deployment_type


class TestPerformanceValidation:
    """Test performance validation and benchmarking."""
    
    def test_benchmark_comparison(self, deployment_configs, complex_model):
        """Test benchmarking and performance comparison."""
        config = deployment_configs["onnx"]
        config.benchmark_performance = True
        
        manager = DeploymentManager(config)
        
        # Mock deployment to focus on benchmarking
        with patch.object(manager, 'deploy_onnx') as mock_deploy:
            mock_deploy.return_value = {"success": True}
            
            result = manager.deploy(complex_model, DeploymentType.ONNX)
            
            # Verify performance metrics were collected
            assert "performance_metrics" in result
            metrics = result["performance_metrics"]
            
            assert "latency_ms" in metrics
            assert "throughput_tokens_per_sec" in metrics
            assert "memory_usage_mb" in metrics
            assert metrics["latency_ms"] > 0
    
    def test_memory_optimization_validation(self, deployment_configs, complex_model):
        """Test memory optimization validation."""
        config = deployment_configs["onnx"]
        config.memory_optimization = True
        config.max_memory_gb = 2.0  # Low memory target
        
        manager = DeploymentManager(config)
        
        # Test hardware compatibility
        compatibility = manager.analyze_hardware_compatibility()
        
        # Should detect memory requirements
        assert "memory_available_gb" in compatibility
        assert "meets_memory_requirements" in compatibility
    
    @patch('torch.cuda.is_available')
    @patch('torch.cuda.memory_allocated')
    def test_gpu_memory_monitoring(self, mock_memory_allocated, mock_cuda_available, deployment_configs, complex_model):
        """Test GPU memory monitoring during deployment."""
        mock_cuda_available.return_value = True
        mock_memory_allocated.return_value = 512 * 1024 * 1024  # 512MB
        
        config = deployment_configs["onnx"]
        manager = DeploymentManager(config)
        
        metrics = manager.benchmark_deployment(complex_model, DeploymentType.ONNX)
        
        # Should include memory usage
        assert "memory_usage_mb" in metrics
        assert metrics["memory_usage_mb"] == 512.0


class TestResourceManagement:
    """Test resource management and cleanup."""
    
    def test_deployment_cleanup(self, deployment_configs, complex_model):
        """Test deployment resource cleanup."""
        config = deployment_configs["onnx"]
        manager = DeploymentManager(config)
        
        # Deploy model
        with patch.object(manager, 'deploy_onnx') as mock_deploy:
            mock_deploy.return_value = {"success": True}
            result = manager.deploy(complex_model, DeploymentType.ONNX)
        
        # Test cleanup
        manager.cleanup()
        
        # Should not raise any exceptions
        assert result["success"] is True
    
    def test_multiple_deployment_cleanup(self, deployment_configs, complex_model):
        """Test cleanup with multiple deployments."""
        managers = []
        
        # Create multiple managers
        for config in deployment_configs.values():
            manager = DeploymentManager(config)
            managers.append(manager)
        
        # Clean up all managers
        for manager in managers:
            manager.cleanup()
        
        # Should complete without errors
        assert len(managers) == 4
    
    def test_report_generation(self, deployment_configs, complex_model):
        """Test deployment report generation."""
        config = deployment_configs["onnx"]
        manager = DeploymentManager(config)
        
        # Mock deployment result
        result = {
            "success": True,
            "model_path": "/path/to/model.onnx",
            "optimization_applied": True
        }
        
        # Generate report
        manager.save_deployment_report(DeploymentType.ONNX, result)
        
        # Verify report file exists
        report_path = Path(config.output_dir) / f"{config.model_name}_onnx_report.json"
        assert report_path.exists()


class TestErrorRecovery:
    """Test error handling and recovery."""
    
    def test_partial_deployment_failure(self, deployment_configs, complex_model):
        """Test handling of partial deployment failures."""
        config = deployment_configs["onnx"]
        manager = DeploymentManager(config)
        
        # Mock deployment to fail
        with patch.object(manager, 'deploy_onnx') as mock_deploy:
            mock_deploy.side_effect = RuntimeError("Deployment failed")
            
            with pytest.raises(RuntimeError, match="Deployment failed"):
                manager.deploy(complex_model, DeploymentType.ONNX)
    
    def test_invalid_model_recovery(self, deployment_configs):
        """Test recovery from invalid model scenarios."""
        config = deployment_configs["onnx"]
        manager = DeploymentManager(config)
        
        # Create invalid model
        class BrokenModel(nn.Module):
            def forward(self, x):
                raise RuntimeError("Broken model")
        
        broken_model = BrokenModel()
        
        with pytest.raises(ValueError, match="Model validation failed"):
            manager.deploy(broken_model)
    
    def test_hardware_constraint_validation(self, deployment_configs, complex_model):
        """Test validation of hardware constraints."""
        config = deployment_configs["onnx"]
        config.max_memory_gb = 0.1  # Unrealistic constraint
        
        manager = DeploymentManager(config)
        
        # Should still proceed but with warnings
        compatibility = manager.analyze_hardware_compatibility()
        assert "meets_memory_requirements" in compatibility


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
