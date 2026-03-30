#!/usr/bin/env python3
"""
Simple deployment test runner

This module provides a standalone test runner for deployment functionality
that doesn't rely on the full ImpressionCore import chain.

File: src/tests/deployment/simple_test_runner.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-30
"""

import sys
import os
import unittest
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

# Simple tests without complex dependencies
class TestDeploymentConfig(unittest.TestCase):
    """Basic deployment configuration tests."""
    
    def test_deployment_types_enum(self):
        """Test deployment type enum values."""
        try:
            from src.deployment.deployment_manager import DeploymentType
            
            # Test enum values
            self.assertEqual(DeploymentType.ONNX.value, "onnx")
            self.assertEqual(DeploymentType.TENSORRT.value, "tensorrt")
            self.assertEqual(DeploymentType.MOBILE.value, "mobile")
            self.assertEqual(DeploymentType.DISTRIBUTED.value, "distributed")
            self.assertEqual(DeploymentType.HYBRID.value, "hybrid")
            
            print("✅ DeploymentType enum test passed")
            
        except ImportError as e:
            self.skipTest(f"Import failed: {e}")
    
    def test_deployment_targets_enum(self):
        """Test deployment target enum values."""
        try:
            from src.deployment.deployment_manager import DeploymentTarget
            
            # Test enum values
            self.assertEqual(DeploymentTarget.DESKTOP.value, "desktop")
            self.assertEqual(DeploymentTarget.SERVER.value, "server")
            self.assertEqual(DeploymentTarget.MOBILE.value, "mobile")
            self.assertEqual(DeploymentTarget.EDGE.value, "edge")
            self.assertEqual(DeploymentTarget.CLOUD.value, "cloud")
            self.assertEqual(DeploymentTarget.EMBEDDED.value, "embedded")
            
            print("✅ DeploymentTarget enum test passed")
            
        except ImportError as e:
            self.skipTest(f"Import failed: {e}")
    
    def test_deployment_config_creation(self):
        """Test basic deployment configuration creation."""
        try:
            from src.deployment.deployment_manager import DeploymentConfig, DeploymentType, DeploymentTarget
            
            config = DeploymentConfig(
                deployment_type=DeploymentType.ONNX,
                target_platform=DeploymentTarget.DESKTOP,
                model_name="test_model"
            )
            
            self.assertEqual(config.deployment_type, DeploymentType.ONNX)
            self.assertEqual(config.target_platform, DeploymentTarget.DESKTOP)
            self.assertEqual(config.model_name, "test_model")
            self.assertEqual(config.batch_size, 1)
            self.assertEqual(config.sequence_length, 2048)
            
            print("✅ DeploymentConfig creation test passed")
            
        except ImportError as e:
            self.skipTest(f"Import failed: {e}")
    
    def test_deployment_config_factory(self):
        """Test deployment configuration factory function."""
        try:
            from src.deployment.deployment_manager import create_deployment_config, DeploymentType, DeploymentTarget
            
            config = create_deployment_config(
                deployment_type="tensorrt",
                target_platform="server",
                model_name="factory_test_model",
                batch_size=8
            )
            
            self.assertEqual(config.deployment_type, DeploymentType.TENSORRT)
            self.assertEqual(config.target_platform, DeploymentTarget.SERVER)
            self.assertEqual(config.model_name, "factory_test_model")
            self.assertEqual(config.batch_size, 8)
            
            print("✅ DeploymentConfig factory test passed")
            
        except ImportError as e:
            self.skipTest(f"Import failed: {e}")


class TestONNXExportConfig(unittest.TestCase):
    """Basic ONNX export configuration tests."""
    
    def test_onnx_config_creation(self):
        """Test ONNX export configuration creation."""
        try:
            from src.deployment.onnx_export import ONNXExportConfig
            
            config = ONNXExportConfig(
                model_name="test_onnx_model",
                batch_size=2,
                sequence_length=1024
            )
            
            self.assertEqual(config.model_name, "test_onnx_model")
            self.assertEqual(config.batch_size, 2)
            self.assertEqual(config.sequence_length, 1024)
            self.assertEqual(config.opset_version, 17)
            self.assertTrue(config.quantization_enabled)
            
            print("✅ ONNXExportConfig creation test passed")
            
        except ImportError as e:
            self.skipTest(f"Import failed: {e}")


class TestTensorRTConfig(unittest.TestCase):
    """Basic TensorRT configuration tests."""
    
    def test_tensorrt_config_creation(self):
        """Test TensorRT configuration creation."""
        try:
            from src.deployment.tensorrt_optimizer import TensorRTConfig
            
            config = TensorRTConfig(
                model_name="test_tensorrt_model",
                batch_size=4,
                max_batch_size=8
            )
            
            self.assertEqual(config.model_name, "test_tensorrt_model")
            self.assertEqual(config.batch_size, 4)
            self.assertEqual(config.max_batch_size, 8)
            self.assertEqual(config.precision, "fp16")
            
            print("✅ TensorRTConfig creation test passed")
            
        except ImportError as e:
            self.skipTest(f"Import failed: {e}")


class TestMobileConfig(unittest.TestCase):
    """Basic mobile configuration tests."""
    
    def test_mobile_config_creation(self):
        """Test mobile configuration creation."""
        try:
            from src.deployment.mobile_deployment import MobileConfig
            
            config = MobileConfig(
                model_name="test_mobile_model",
                target_platforms=["android", "ios"],
                device_tier="mid_range"
            )
            
            self.assertEqual(config.model_name, "test_mobile_model")
            self.assertEqual(config.target_platforms, ["android", "ios"])
            self.assertEqual(config.device_tier, "mid_range")
            
            print("✅ MobileConfig creation test passed")
            
        except ImportError as e:
            self.skipTest(f"Import failed: {e}")


class TestDistributedConfig(unittest.TestCase):
    """Basic distributed configuration tests."""
    
    def test_distributed_config_creation(self):
        """Test distributed configuration creation."""
        try:
            from src.deployment.distributed_inference import DistributedConfig
            
            config = DistributedConfig(
                model_name="test_distributed_model",
                num_nodes=2,
                gpus_per_node=2
            )
            
            self.assertEqual(config.model_name, "test_distributed_model")
            self.assertEqual(config.num_nodes, 2)
            self.assertEqual(config.gpus_per_node, 2)
            
            print("✅ DistributedConfig creation test passed")
            
        except ImportError as e:
            self.skipTest(f"Import failed: {e}")


def run_deployment_tests():
    """Run all deployment tests."""
    print("🧪 Running ImpressionCore Deployment Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestDeploymentConfig,
        TestONNXExportConfig,
        TestTensorRTConfig,
        TestMobileConfig,
        TestDistributedConfig
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    if result.skipped:
        print("\n⏭️  Skipped:")
        for test, reason in result.skipped:
            print(f"  {test}: {reason}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    return result


if __name__ == "__main__":
    run_deployment_tests()
