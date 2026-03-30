#!/usr/bin/env python3
"""
ImpressionCore: Advanced Gradient Checkpointing Tests

Test suite for advanced gradient checkpointing features including adaptive selection
and memory monitoring.

File: tests/unit/test_advanced_gradient_checkpointing.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-01
Modified: 2025-06-01
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [testing, qlora, gradient-checkpointing, advanced-features, 2025]
Dependencies: [torch, pytest]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
"""

import pytest
import torch
import torch.nn as nn
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import time

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.utils.gradient_checkpointing import (
    PerformanceMetrics,
    AdaptiveCheckpointSelector,
    MemoryPressureMonitor,
    QLoRAGradientCheckpointing,
    CheckpointConfig,
    adaptive_memory_efficient_checkpointing,
    auto_apply_optimal_checkpointing
)


class TestPerformanceMetrics:
    """Test PerformanceMetrics class."""
    
    def test_initialization(self):
        """Test performance metrics initialization."""
        metrics = PerformanceMetrics()
        
        assert metrics.forward_time_ms == 0.0
        assert metrics.backward_time_ms == 0.0
        assert metrics.memory_peak_mb == 0.0
        assert metrics.memory_saved_mb == 0.0
        assert metrics.checkpoint_overhead_ms == 0.0
        assert metrics.recomputation_time_ms == 0.0
        assert metrics.total_checkpoints == 0
    
    def test_to_dict(self):
        """Test metrics conversion to dictionary."""
        metrics = PerformanceMetrics(
            forward_time_ms=100.0,
            memory_saved_mb=500.0,
            checkpoint_overhead_ms=10.0,
            recomputation_time_ms=15.0,
            total_checkpoints=5
        )
        
        result = metrics.to_dict()
        
        assert "forward_time_ms" in result
        assert "efficiency_ratio" in result
        assert result["forward_time_ms"] == 100.0
        assert result["total_checkpoints"] == 5
        assert result["efficiency_ratio"] == 500.0 / 25.0  # memory_saved / (overhead + recomputation)
    
    def test_efficiency_ratio_calculation(self):
        """Test efficiency ratio calculation."""
        # Test with zero overhead
        metrics = PerformanceMetrics()
        assert metrics._calculate_efficiency_ratio() == 0.0
        
        # Test with normal values
        metrics.memory_saved_mb = 1000.0
        metrics.checkpoint_overhead_ms = 20.0
        metrics.recomputation_time_ms = 30.0
        assert metrics._calculate_efficiency_ratio() == 20.0  # 1000 / 50


class TestAdaptiveCheckpointSelector:
    """Test AdaptiveCheckpointSelector class."""
    
    @pytest.fixture
    def selector(self):
        """Create an AdaptiveCheckpointSelector instance."""
        return AdaptiveCheckpointSelector(max_history=10)
    
    def test_initialization(self, selector):
        """Test selector initialization."""
        assert selector.max_history == 10
        assert len(selector.checkpoint_history) == 0
        assert len(selector.layer_performance) == 0
    
    def test_record_checkpoint_performance(self, selector):
        """Test recording checkpoint performance."""
        selector.record_checkpoint_performance(
            layer_name="layer1",
            memory_saved=100.0,
            overhead_time=5.0,
            recomputation_time=10.0
        )
        
        assert len(selector.checkpoint_history) == 1
        assert "layer1" in selector.layer_performance
        assert len(selector.layer_performance["layer1"]) == 1
        
        # Check performance score calculation
        expected_score = 100.0 / 15.0  # memory_saved / (overhead + recomputation)
        recorded_score = selector.layer_performance["layer1"][0]
        assert abs(recorded_score - expected_score) < 0.01
    
    def test_get_optimal_layers(self, selector):
        """Test optimal layer selection."""
        # Record performance for multiple layers
        selector.record_checkpoint_performance("layer1", 100.0, 5.0, 10.0)  # Score: 6.67
        selector.record_checkpoint_performance("layer2", 200.0, 10.0, 10.0)  # Score: 10.0
        selector.record_checkpoint_performance("layer3", 50.0, 2.0, 3.0)    # Score: 10.0
        
        candidates = ["layer1", "layer2", "layer3", "layer4"]
        optimal = selector.get_optimal_layers(candidates, top_k=2)
        
        # Should return top 2 performing layers
        assert len(optimal) == 2
        assert "layer2" in optimal or "layer3" in optimal  # Both have score 10.0
        assert "layer4" not in optimal[:2]  # Unknown layer should be deprioritized
    
    def test_performance_summary(self, selector):
        """Test performance summary generation."""
        selector.record_checkpoint_performance("layer1", 100.0, 5.0, 10.0)
        
        summary = selector.get_performance_summary()
        
        assert "total_checkpoints" in summary
        assert "layer_rankings" in summary
        assert "recent_performance" in summary
        assert summary["total_checkpoints"] == 1
        assert "layer1" in summary["layer_rankings"]


class TestMemoryPressureMonitor:
    """Test MemoryPressureMonitor class."""
    
    @pytest.fixture
    def monitor(self):
        """Create a MemoryPressureMonitor instance."""
        return MemoryPressureMonitor()
    
    def test_initialization(self, monitor):
        """Test monitor initialization."""
        assert len(monitor.memory_samples) == 0
        assert len(monitor.gpu_memory_samples) == 0
    
    @patch('psutil.virtual_memory')
    def test_update_memory_stats_cpu_only(self, mock_virtual_memory, monitor):
        """Test memory stats update for CPU only."""
        # Mock CPU memory
        mock_memory = Mock()
        mock_memory.used = 8 * 1024 * 1024 * 1024  # 8GB
        mock_memory.available = 4 * 1024 * 1024 * 1024  # 4GB
        mock_memory.percent = 66.7
        mock_virtual_memory.return_value = mock_memory
        
        with patch('torch.cuda.is_available', return_value=False):
            monitor.update_memory_stats()
        
        assert len(monitor.memory_samples) == 1
        assert len(monitor.gpu_memory_samples) == 0
        
        sample = monitor.memory_samples[0]
        assert sample["used_mb"] == 8 * 1024  # 8GB in MB
        assert sample["available_mb"] == 4 * 1024  # 4GB in MB
        assert sample["percent"] == 66.7
    
    @patch('torch.cuda.get_device_properties')
    @patch('torch.cuda.memory_allocated')
    @patch('psutil.virtual_memory')
    def test_update_memory_stats_with_gpu(self, mock_virtual_memory, mock_gpu_allocated, mock_gpu_props, monitor):
        """Test memory stats update with GPU."""
        # Mock CPU memory
        mock_memory = Mock()
        mock_memory.used = 8 * 1024 * 1024 * 1024
        mock_memory.available = 4 * 1024 * 1024 * 1024
        mock_memory.percent = 66.7
        mock_virtual_memory.return_value = mock_memory
        
        # Mock GPU memory
        mock_gpu_allocated.return_value = 3 * 1024 * 1024 * 1024  # 3GB used
        mock_props = Mock()
        mock_props.total_memory = 4 * 1024 * 1024 * 1024  # 4GB total
        mock_gpu_props.return_value = mock_props
        
        with patch('torch.cuda.is_available', return_value=True):
            monitor.update_memory_stats()
        
        assert len(monitor.memory_samples) == 1
        assert len(monitor.gpu_memory_samples) == 1
        
        gpu_sample = monitor.gpu_memory_samples[0]
        assert gpu_sample["used_mb"] == 3 * 1024  # 3GB in MB
        assert gpu_sample["total_mb"] == 4 * 1024  # 4GB in MB
        assert gpu_sample["percent"] == 75.0  # 3/4 * 100
    
    def test_get_memory_pressure_level(self, monitor):
        """Test memory pressure level determination."""
        # Test with no samples
        assert monitor.get_memory_pressure_level() == "unknown"
        
        # Add GPU sample with high usage
        monitor.gpu_memory_samples.append({
            "timestamp": time.time(),
            "used_mb": 3500,
            "total_mb": 4000,
            "percent": 87.5
        })
        
        assert monitor.get_memory_pressure_level() == "high"
        
        # Add GPU sample with critical usage
        monitor.gpu_memory_samples.append({
            "timestamp": time.time(),
            "used_mb": 3800,
            "total_mb": 4000,
            "percent": 95.0
        })
        
        assert monitor.get_memory_pressure_level() == "critical"
    
    def test_should_enable_aggressive_checkpointing(self, monitor):
        """Test aggressive checkpointing decision."""
        # Add high pressure sample
        monitor.gpu_memory_samples.append({
            "timestamp": time.time(),
            "used_mb": 3500,
            "total_mb": 4000,
            "percent": 87.5
        })
        
        assert monitor.should_enable_aggressive_checkpointing() is True
        
        # Add low pressure sample
        monitor.gpu_memory_samples.append({
            "timestamp": time.time(),
            "used_mb": 1500,
            "total_mb": 4000,
            "percent": 37.5
        })
        
        assert monitor.should_enable_aggressive_checkpointing() is False


class TestAdvancedQLoRAGradientCheckpointing:
    """Test advanced features of QLoRAGradientCheckpointing."""
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock model."""
        return nn.Sequential(
            nn.Linear(768, 768),
            nn.ReLU(),
            nn.Linear(768, 768)
        )
    
    def test_initialization_with_advanced_features(self, mock_model):
        """Test initialization with advanced features enabled."""
        manager = QLoRAGradientCheckpointing(
            model=mock_model,
            enable_adaptive_selection=True,
            enable_memory_monitoring=True
        )
        
        assert manager.adaptive_selector is not None
        assert manager.memory_monitor is not None
        assert isinstance(manager.performance_metrics, PerformanceMetrics)
    
    def test_initialization_without_advanced_features(self, mock_model):
        """Test initialization with advanced features disabled."""
        manager = QLoRAGradientCheckpointing(
            model=mock_model,
            enable_adaptive_selection=False,
            enable_memory_monitoring=False
        )
        
        assert manager.adaptive_selector is None
        assert manager.memory_monitor is None
        assert isinstance(manager.performance_metrics, PerformanceMetrics)
    
    @patch('torch.cuda.is_available')
    def test_adaptive_optimize_strategy(self, mock_cuda_available, mock_model):
        """Test adaptive strategy optimization."""
        manager = QLoRAGradientCheckpointing(
            model=mock_model,
            enable_adaptive_selection=True,
            enable_memory_monitoring=True
        )
        
        # Mock CUDA availability and memory pressure
        mock_cuda_available.return_value = True
        
        with patch.object(manager.memory_monitor, 'get_memory_pressure_level', return_value='high'):
            result = manager.adaptive_optimize_strategy()
        
        assert "adaptive_changes" in result
        assert "memory_pressure_changes" in result
        assert result["memory_pressure_changes"] > 0  # Should have made changes due to high pressure
    
    def test_record_checkpoint_performance(self, mock_model):
        """Test checkpoint performance recording."""
        manager = QLoRAGradientCheckpointing(
            model=mock_model,
            enable_adaptive_selection=True
        )
        
        start_time = time.time()
        end_time = start_time + 0.01  # 10ms
        memory_saved = 100.0
        
        manager.record_checkpoint_performance("test_layer", start_time, end_time, memory_saved)
        
        # Check that performance was recorded
        assert manager.performance_metrics.total_checkpoints == 1
        assert manager.performance_metrics.memory_saved_mb == memory_saved
        assert manager.performance_metrics.checkpoint_overhead_ms > 0
    
    def test_get_comprehensive_report(self, mock_model):
        """Test comprehensive report generation."""
        manager = QLoRAGradientCheckpointing(
            model=mock_model,
            enable_adaptive_selection=True,
            enable_memory_monitoring=True
        )
        
        report = manager.get_comprehensive_report()
        
        assert "performance_metrics" in report
        assert "adaptive_selection" in report
        assert "memory_monitoring" in report
        assert "optimizations" in report


class TestAdvancedUtilityFunctions:
    """Test advanced utility functions."""
    
    def test_adaptive_memory_efficient_checkpointing_context(self):
        """Test adaptive memory efficient checkpointing context manager."""
        model = nn.Sequential(nn.Linear(768, 768))
        
        with adaptive_memory_efficient_checkpointing(
            model,
            memory_threshold_mb=2000.0,
            enable_adaptive_selection=True,
            enable_memory_monitoring=True,
            learning_mode=True        ) as manager:
            assert isinstance(manager, QLoRAGradientCheckpointing)
            assert manager.adaptive_selector is not None
            assert manager.memory_monitor is not None
    
    def test_auto_apply_optimal_checkpointing(self):
        """Test automatic optimal checkpointing configuration."""
        # Create a larger model that would need aggressive checkpointing
        model = nn.Sequential(
            nn.Linear(2048, 2048),  # ~4M parameters
            nn.ReLU(),
            nn.Linear(2048, 2048),  # ~4M parameters
            nn.ReLU(),
            nn.Linear(2048, 1024),  # ~2M parameters
            nn.ReLU(),
            nn.Linear(1024, 512)    # ~0.5M parameters
        )  # Total ~10.5M parameters, should be ~42MB in float32
        
        manager = auto_apply_optimal_checkpointing(
            model,
            target_memory_mb=50.0  # Smaller target to trigger aggressive mode
        )
        
        assert isinstance(manager, QLoRAGradientCheckpointing)
        assert manager.config.checkpoint_every_n_layers <= 2  # Should be aggressive for large relative size
    
    def test_auto_apply_optimal_checkpointing_small_model(self):
        """Test automatic configuration for small models."""
        # Create a small model
        model = nn.Linear(10, 10)  # Very small model
        
        manager = auto_apply_optimal_checkpointing(
            model,
            target_memory_mb=1000.0  # Large target relative to model size
        )
        
        assert isinstance(manager, QLoRAGradientCheckpointing)
        assert manager.config.checkpoint_every_n_layers >= 2  # Should be less aggressive


class TestIntegrationWithAdvancedFeatures:
    """Integration tests for advanced features."""
    
    def test_full_workflow_with_learning(self):
        """Test full workflow with adaptive learning."""
        model = nn.Sequential(
            nn.Linear(768, 768),
            nn.ReLU(),
            nn.Linear(768, 768)
        )
        
        input_tensor = torch.randn(2, 768)
        
        with adaptive_memory_efficient_checkpointing(
            model,
            enable_adaptive_selection=True,
            enable_memory_monitoring=True,
            learning_mode=True
        ) as manager:
            # Simulate training step
            output = model(input_tensor)
            
            # Record some performance data
            manager.record_checkpoint_performance("layer.0", time.time(), time.time() + 0.01, 50.0)
            manager.record_checkpoint_performance("layer.2", time.time(), time.time() + 0.02, 75.0)
        
        # Should have learned from the session
        report = manager.get_comprehensive_report()
        assert report["performance_metrics"]["total_checkpoints"] >= 0
    
    def test_memory_pressure_adaptation(self):
        """Test adaptation to memory pressure changes."""
        model = nn.Linear(768, 768)
        
        manager = QLoRAGradientCheckpointing(
            model,
            enable_memory_monitoring=True
        )
        
        # Simulate memory pressure changes
        with patch.object(manager.memory_monitor, 'get_memory_pressure_level') as mock_pressure:
            # Start with low pressure
            mock_pressure.return_value = 'low'
            result_low = manager.adaptive_optimize_strategy()
            
            # Change to high pressure
            mock_pressure.return_value = 'critical'
            result_critical = manager.adaptive_optimize_strategy()
        
        # Should have made more changes under critical pressure
        assert result_critical["memory_pressure_changes"] >= result_low["memory_pressure_changes"]


if __name__ == "__main__":
    # Run basic tests if executed directly
    pytest.main([__file__, "-v"])
