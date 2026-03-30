#!/usr/bin/env python3
"""
ImpressionCore: Advanced Optimizers Integration Tests

Comprehensive test suite for memory-efficient optimizers and advanced optimization features.

File: tests/integration/test_advanced_optimizers.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-28
Modified: 2025-05-28
Version: 1.0.0

Authors:
- GitHub Copilot
- ImpressionCore Team

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [testing, integration, optimizers, memory-optimization, pytorch]
Dependencies: [torch, pytest, bitsandbytes?, psutil]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Integration tests for the advanced memory-efficient optimizer implementations,
including 8-bit optimizers, automatic optimizer selection, memory monitoring,
and custom optimization strategies.
"""

import pytest
import torch
import torch.nn as nn
import logging
import gc
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.utils.memory_optimization.advanced_optimizer import (
    get_memory_efficient_optimizer,
    MemoryEfficientOptimizerManager,
    MemoryOptimizationConfig,
    CustomMemoryEfficientOptimizers
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleTestModel(nn.Module):
    """Simple model for testing optimizers."""
    
    def __init__(self, input_size=10, hidden_size=20, output_size=1):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )
    
    def forward(self, x):
        return self.layers(x)


@pytest.fixture
def test_model():
    """Create a test model for optimizer testing."""
    model = SimpleTestModel(input_size=10, hidden_size=20, output_size=1)
    return model


@pytest.fixture
def test_data():
    """Create test data for training."""
    batch_size = 4
    input_size = 10
    X = torch.randn(batch_size, input_size)
    y = torch.randn(batch_size, 1)
    return X, y


class TestMemoryEfficientOptimizers:
    """Test suite for memory-efficient optimizer factory."""
    
    def test_standard_optimizers(self, test_model):
        """Test creation of standard optimizers."""
        optimizers_to_test = ["adamw", "adam", "sgd", "rmsprop", "adagrad"]
        
        for opt_name in optimizers_to_test:
            optimizer = get_memory_efficient_optimizer(test_model, opt_name, lr=1e-3)
            assert optimizer is not None
            assert hasattr(optimizer, 'step')
            assert hasattr(optimizer, 'zero_grad')
            logger.info(f"✓ Successfully created {opt_name} optimizer")

    def test_8bit_optimizers_with_bitsandbytes(self, test_model):
        """Test 8-bit optimizers when bitsandbytes is available."""
        bit_optimizers = ["adam8bit", "adamw8bit", "sgd8bit"]
        
        for opt_name in bit_optimizers:
            try:
                optimizer = get_memory_efficient_optimizer(test_model, opt_name, lr=1e-3)
                assert optimizer is not None
                
                # Check if it's actually a bitsandbytes optimizer or fallback
                optimizer_class = optimizer.__class__.__name__
                logger.info(f"✓ Created {opt_name} -> {optimizer_class}")
            except ImportError as e:
                # Expected if bitsandbytes not available
                logger.info(f"⚠ {opt_name} not available (bitsandbytes not installed): {e}")
                pytest.skip(f"bitsandbytes not available for {opt_name}")

    def test_8bit_optimizers_behavior(self, test_model):
        """Test that 8-bit optimizers work correctly (either 8-bit or fallback to standard)."""
        
        # Test that 8-bit optimizers either work as 8-bit or fallback properly
        bit_optimizers = ["adam8bit", "adamw8bit", "sgd8bit"]
        expected_fallbacks = ["Adam", "AdamW", "SGD"]
        expected_8bit = ["Adam8bit", "AdamW8bit", "SGD8bit"]
        
        for opt_name, expected_fallback, expected_8bit_name in zip(bit_optimizers, expected_fallbacks, expected_8bit):
            optimizer = get_memory_efficient_optimizer(test_model, opt_name, lr=1e-3)
            assert optimizer is not None
            
            optimizer_class = optimizer.__class__.__name__
            logger.info(f"✓ {opt_name} created as {optimizer_class}")
            
            # Should be either the 8-bit version OR the standard fallback
            assert optimizer_class in [expected_8bit_name, expected_fallback], \
                f"Expected {opt_name} to be either {expected_8bit_name} or {expected_fallback}, got {optimizer_class}"
            
            if optimizer_class == expected_8bit_name:
                logger.info(f"✓ {opt_name} successfully using 8-bit version")
            else:
                logger.info(f"✓ {opt_name} correctly fell back to {expected_fallback}")

    def test_paged_optimizer_selection_and_functionality(self, test_model, test_data):
        """Test selection and functionality of PagedAdamW32bit."""
        # This test requires a GPU and bitsandbytes
        if not torch.cuda.is_available():
            pytest.skip("Paged optimizer test requires CUDA.")
        
        try:
            import bitsandbytes as bnb
            # Attempt to use a feature that would fail if not compiled correctly
            _ = bnb.optim.PagedAdamW32bit(test_model.parameters(), lr=1e-3) 
        except Exception as e:
            pytest.skip(f"bitsandbytes PagedAdamW32bit not fully functional: {e}")

        X, y = test_data
        loss_fn = nn.MSELoss()

        # Move model to GPU
        model = test_model.to('cuda')
        X = X.to('cuda')
        y = y.to('cuda')

        optimizer_name = "paged_adamw_32bit"
        
        try:
            optimizer = get_memory_efficient_optimizer(model, optimizer_name, lr=1e-2)
            assert optimizer is not None
            optimizer_class_name = optimizer.__class__.__name__
            logger.info(f"✓ Created {optimizer_name} -> {optimizer_class_name}")

            # It should be PagedAdamW32bit, or fallback if something is wrong with bnb setup
            # For this specific test, we want to ensure PagedAdamW32bit is tried.
            # The get_memory_efficient_optimizer has fallbacks, so we check the class name.
            assert "PagedAdamW32bit" in optimizer_class_name or "AdamW8bit" in optimizer_class_name or "AdamW" in optimizer_class_name

            if "PagedAdamW32bit" not in optimizer_class_name:
                logger.warning(f"PagedAdamW32bit was not selected, got {optimizer_class_name} instead. Test will proceed with this optimizer.")

            # Perform a few training steps
            initial_loss = None
            for step in range(5):
                optimizer.zero_grad()
                output = model(X)
                loss = loss_fn(output, y)
                
                if initial_loss is None:
                    initial_loss = loss.item()
                
                loss.backward()
                optimizer.step()
            
            final_loss = loss.item()
            
            assert final_loss != initial_loss, f"Loss didn't change for {optimizer_name} (selected: {optimizer_class_name})"
            logger.info(f"✓ {optimizer_name} (selected: {optimizer_class_name}) training: {initial_loss:.4f} -> {final_loss:.4f}")

        except Exception as e:
            # If bitsandbytes is imported but paged optimizer fails at runtime for other reasons
            logger.error(f"Error during {optimizer_name} test: {e}")
            pytest.fail(f"Error during {optimizer_name} test: {e}")
        finally:
            # Clean up CUDA memory
            del model, X, y
            if 'optimizer' in locals():
                del optimizer
            gc.collect()
            torch.cuda.empty_cache()

    def test_invalid_optimizer_name(self, test_model):
        """Test error handling for invalid optimizer names."""
        with pytest.raises(ValueError, match="Unsupported optimizer"):
            get_memory_efficient_optimizer(test_model, "invalid_optimizer", lr=1e-3)
    
    def test_optimizer_functionality(self, test_model, test_data):
        """Test that optimizers actually work for training steps."""
        X, y = test_data
        loss_fn = nn.MSELoss()
        
        # Test with different optimizers
        optimizers_to_test = ["adamw", "adam", "sgd"]
        
        for opt_name in optimizers_to_test:
            model = SimpleTestModel()  # Fresh model for each test
            optimizer = get_memory_efficient_optimizer(model, opt_name, lr=1e-2)
            
            # Perform a few training steps
            initial_loss = None
            for step in range(5):
                optimizer.zero_grad()
                output = model(X)
                loss = loss_fn(output, y)
                
                if initial_loss is None:
                    initial_loss = loss.item()
                
                loss.backward()
                optimizer.step()
            
            final_loss = loss.item()
            
            # Loss should decrease (or at least change)
            assert final_loss != initial_loss, f"Loss didn't change for {opt_name}"
            logger.info(f"✓ {opt_name} training: {initial_loss:.4f} -> {final_loss:.4f}")


class TestMemoryEfficientOptimizerManager:
    """Test suite for the optimizer manager."""
    
    def test_manager_initialization(self, test_model):
        """Test manager initialization."""
        manager = MemoryEfficientOptimizerManager(test_model)
        
        assert manager.model is test_model
        assert manager.device is not None
        assert isinstance(manager.memory_stats, dict)
        assert len(manager.optimizer_preferences) > 0
        logger.info("✓ Manager initialized successfully")
    
    def test_memory_estimation(self, test_model):
        """Test optimizer memory estimation."""
        manager = MemoryEfficientOptimizerManager(test_model)
        num_params = sum(p.numel() for p in test_model.parameters())
        
        # Test different optimizer types
        for opt_type in ["adam8bit", "adamw", "sgd"]:
            memory_est = manager.estimate_optimizer_memory(opt_type, num_params)
            assert memory_est > 0
            assert isinstance(memory_est, float)
            logger.info(f"✓ {opt_type} estimated memory: {memory_est:.6f} GB")
    
    def test_available_memory_detection(self, test_model):
        """Test available memory detection."""
        manager = MemoryEfficientOptimizerManager(test_model)
        available_memory = manager.get_available_memory()
        
        assert available_memory > 0
        assert isinstance(available_memory, float)
        logger.info(f"✓ Detected available memory: {available_memory:.2f} GB")
    
    def test_optimal_optimizer_selection(self, test_model):
        """Test automatic optimizer selection."""
        manager = MemoryEfficientOptimizerManager(test_model)
        optimizer = manager.select_optimal_optimizer(lr=1e-3)
        
        assert optimizer is not None
        assert hasattr(optimizer, 'step')
        assert manager.memory_stats["optimizer_type"] is not None
        logger.info(f"✓ Selected optimizer: {manager.memory_stats['optimizer_type']}")
    
    def test_memory_monitoring(self, test_model):
        """Test memory usage monitoring."""
        manager = MemoryEfficientOptimizerManager(test_model)
        stats = manager.monitor_memory_usage()
        
        assert isinstance(stats, dict)
        assert "allocated_memory" in stats or "peak_memory" in stats
        logger.info(f"✓ Memory monitoring: {stats}")
    
    def test_memory_report_generation(self, test_model):
        """Test comprehensive memory report generation."""
        manager = MemoryEfficientOptimizerManager(test_model)
        
        # First select an optimizer
        optimizer = manager.select_optimal_optimizer(lr=1e-3)
        
        # Generate report
        report = manager.get_memory_report()
        
        assert isinstance(report, dict)
        assert "optimizer_type" in report
        assert "memory_efficiency" in report
        assert "recommendations" in report
        logger.info(f"✓ Memory report generated: {report['optimizer_type']}")


class TestCustomMemoryEfficientOptimizers:
    """Test suite for custom optimizer implementations."""
    
    def test_gradient_accumulation_optimizer(self, test_model, test_data):
        """Test gradient accumulation optimizer wrapper."""
        X, y = test_data
        loss_fn = nn.MSELoss()
        
        # Create base optimizer
        base_optimizer = get_memory_efficient_optimizer(test_model, "adamw", lr=1e-2)
        
        # Wrap with gradient accumulation
        accumulation_steps = 2
        acc_optimizer = CustomMemoryEfficientOptimizers.create_gradient_accumulation_optimizer(
            base_optimizer, accumulation_steps
        )
        
        assert acc_optimizer is not None
        assert hasattr(acc_optimizer, 'step')
        assert hasattr(acc_optimizer, 'zero_grad')
        assert acc_optimizer.accumulation_steps == accumulation_steps
        
        # Test training with accumulation
        initial_loss = None
        for step in range(4):  # Multiple of accumulation_steps
            output = test_model(X)
            loss = loss_fn(output, y)
            
            if initial_loss is None:
                initial_loss = loss.item()
            
            loss.backward()
            acc_optimizer.step()
            acc_optimizer.zero_grad()
        
        final_loss = loss.item()
        assert final_loss != initial_loss
        logger.info(f"✓ Gradient accumulation training: {initial_loss:.4f} -> {final_loss:.4f}")
    
    def test_memory_adaptive_optimizer(self, test_model, test_data):
        """Test memory-adaptive optimizer."""
        X, y = test_data
        loss_fn = nn.MSELoss()
        
        # Create memory-adaptive optimizer
        adaptive_optimizer = CustomMemoryEfficientOptimizers.create_memory_adaptive_optimizer(
            test_model, lr=1e-2
        )
        
        assert adaptive_optimizer is not None
        assert hasattr(adaptive_optimizer, 'step')
        assert hasattr(adaptive_optimizer, 'zero_grad')
        assert len(adaptive_optimizer.optimizers) > 0
        
        # Test training with adaptation
        initial_loss = None
        for step in range(15):  # Enough steps to trigger memory checks
            adaptive_optimizer.zero_grad()
            output = test_model(X)
            loss = loss_fn(output, y)
            
            if initial_loss is None:
                initial_loss = loss.item()
            
            loss.backward()
            adaptive_optimizer.step()
        
        final_loss = loss.item()
        assert final_loss != initial_loss
        logger.info(f"✓ Memory-adaptive training: {initial_loss:.4f} -> {final_loss:.4f}")
        logger.info(f"✓ Final optimizer: {adaptive_optimizer.current_optimizer_name}")


class TestMemoryOptimizationConfig:
    """Test suite for memory optimization configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = MemoryOptimizationConfig()
        
        assert config.enable_8bit_optimizers is True
        assert config.preferred_optimizer == "adam8bit"
        assert config.fallback_optimizer == "adamw"
        assert config.target_vram_gb == 4.0  # GTX 1050 Ti
        assert config.max_model_size_gb == 2.0
        logger.info("✓ Default configuration validated")
    
    def test_custom_config(self):
        """Test custom configuration creation."""
        config = MemoryOptimizationConfig(
            enable_8bit_optimizers=False,
            preferred_optimizer="adamw",
            target_vram_gb=8.0,
            enable_gradient_checkpointing=False
        )
        
        assert config.enable_8bit_optimizers is False
        assert config.preferred_optimizer == "adamw"
        assert config.target_vram_gb == 8.0
        assert config.enable_gradient_checkpointing is False
        logger.info("✓ Custom configuration validated")


class TestIntegrationScenarios:
    """Integration tests for real-world scenarios."""
    
    def test_end_to_end_optimizer_workflow(self, test_model, test_data):
        """Test complete workflow from selection to training."""
        X, y = test_data
        loss_fn = nn.MSELoss()
        
        # Step 1: Create manager and select optimizer
        manager = MemoryEfficientOptimizerManager(test_model)
        optimizer = manager.select_optimal_optimizer(lr=1e-2)
        
        # Step 2: Monitor memory before training
        initial_memory = manager.monitor_memory_usage()
        
        # Step 3: Perform training
        losses = []
        for epoch in range(10):
            optimizer.zero_grad()
            output = test_model(X)
            loss = loss_fn(output, y)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
        
        # Step 4: Monitor memory after training
        final_memory = manager.monitor_memory_usage()
        
        # Step 5: Generate report
        report = manager.get_memory_report()
        
        # Validations
        assert len(losses) == 10
        assert losses[0] != losses[-1]  # Loss should change
        assert report["optimizer_type"] is not None        
        logger.info(f"✓ End-to-end workflow completed")
        logger.info(f"✓ Training: {losses[0]:.4f} -> {losses[-1]:.4f}")
        logger.info(f"✓ Final optimizer: {report['optimizer_type']}")
    
    def test_memory_constrained_scenario(self, test_model):
        """Test behavior under simulated memory constraints."""
        manager = MemoryEfficientOptimizerManager(test_model)
        
        # Mock low memory availability
        with patch.object(manager, 'get_available_memory', return_value=0.5):  # 0.5 GB
            optimizer = manager.select_optimal_optimizer(lr=1e-3)
            
            # Should select most memory-efficient optimizer
            assert optimizer is not None
            optimizer_type = manager.memory_stats.get("optimizer_type", "")
            
            # Should prefer memory-efficient options (paged > 8bit > sgd)
            assert any(keyword in optimizer_type.lower() for keyword in ["paged", "sgd", "8bit"]), \
                f"Expected memory-efficient optimizer (paged/8bit/sgd), got: {optimizer_type}"
            logger.info(f"✓ Low memory scenario handled: {optimizer_type}")
    
    def test_optimizer_comparison(self, test_data):
        """Compare performance of different optimizers."""
        X, y = test_data
        loss_fn = nn.MSELoss()
        
        optimizers_to_compare = ["adamw", "adam", "sgd"]
        results = {}
        
        for opt_name in optimizers_to_compare:
            # Fresh model for fair comparison
            model = SimpleTestModel()
            optimizer = get_memory_efficient_optimizer(model, opt_name, lr=1e-2)
            
            losses = []
            for epoch in range(10):
                optimizer.zero_grad()
                output = model(X)
                loss = loss_fn(output, y)
                loss.backward()
                optimizer.step()
                losses.append(loss.item())
            
            results[opt_name] = {
                "initial_loss": losses[0],
                "final_loss": losses[-1],
                "improvement": losses[0] - losses[-1]
            }
        
        # Log results for analysis
        for opt_name, result in results.items():
            logger.info(f"✓ {opt_name}: {result['initial_loss']:.4f} -> {result['final_loss']:.4f} "
                       f"(improvement: {result['improvement']:.4f})")
        
        # All optimizers should show some improvement
        for opt_name, result in results.items():
            assert result["improvement"] != 0, f"No improvement for {opt_name}"


# Cleanup and utilities
def cleanup_memory():
    """Clean up GPU/CPU memory after tests."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Automatically clean up memory after each test."""
    yield
    cleanup_memory()


if __name__ == "__main__":
    # Run specific test groups
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
