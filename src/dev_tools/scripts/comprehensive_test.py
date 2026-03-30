#!/usr/bin/env python3
"""
ImpressionCore: Comprehensive Import and Functionality Test Suite

Tests all core modules, import paths, and basic functionality after
the src/ directory restructuring and import fixes.

File: src/dev_tools/scripts/comprehensive_test.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-06
Version: 1.0.0
"""

import sys
import os
import traceback
import importlib
from typing import List, Tuple, Dict
import time

# Add the project root to the Python path for proper imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class ImportTester:
    """Test suite for validating imports and basic functionality."""
    
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def test_import(self, module_name: str, description: str = "") -> bool:
        """
        Test importing a module.
        
        Args:
            module_name: Full module name to import
            description: Optional description of the test
            
        Returns:
            True if import succeeded, False otherwise
        """
        self.total_tests += 1
        test_desc = description or f"Import {module_name}"
        
        try:
            importlib.import_module(module_name)
            self.results.append(("✅ PASS", test_desc, ""))
            self.passed_tests += 1
            return True
        except Exception as e:
            self.results.append(("❌ FAIL", test_desc, str(e)))
            self.failed_tests += 1
            return False
    
    def test_basic_functionality(self, module_name: str, test_func, description: str = "") -> bool:
        """
        Test basic functionality of a module.
        
        Args:
            module_name: Module name for import
            test_func: Function to test basic functionality
            description: Test description
            
        Returns:
            True if test passed, False otherwise
        """
        self.total_tests += 1
        test_desc = description or f"Functionality test for {module_name}"
        
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Run the test function
            test_func(module)
            
            self.results.append(("✅ PASS", test_desc, ""))
            self.passed_tests += 1
            return True
        except Exception as e:
            self.results.append(("❌ FAIL", test_desc, str(e)))
            self.failed_tests += 1
            return False
    
    def print_results(self):
        """Print test results summary."""
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE IMPORT & FUNCTIONALITY TEST RESULTS")
        print("="*80)
        
        # Print individual results
        for status, description, error in self.results:
            print(f"{status} {description}")
            if error and "FAIL" in status:
                print(f"   Error: {error}")
        
        print("\n" + "-"*80)
        print(f"📊 SUMMARY: {self.passed_tests}/{self.total_tests} tests passed")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        
        if self.failed_tests == 0:
            print("🎉 ALL TESTS PASSED! ImpressionCore structure is working perfectly!")
        else:
            print(f"⚠️  {self.failed_tests} tests failed. Review above for details.")
        
        print("="*80)


def test_core_config(module):
    """Test core config functionality."""
    # Test that we can access the ConfigManager
    config_manager = getattr(module, 'ConfigManager', None)
    if config_manager is None:
        raise Exception("ConfigManager not found in core.config module")


def test_core_utils(module):
    """Test core utils functionality."""
    # Check for logging utilities
    logger_func = getattr(module, 'setup_logger', None)
    if logger_func is None:
        raise Exception("setup_logger not found in core.utils module")


def test_core_memory(module):
    """Test core memory functionality."""
    # Check for memory management
    memory_manager = getattr(module, 'MemoryManager', None)
    if memory_manager is None:
        raise Exception("MemoryManager not found in core.memory module")


def test_training_models(module):
    """Test training models functionality."""
    # Check for model classes
    model_class = getattr(module, 'ImpressionCoreModel', None)
    if model_class is None:
        raise Exception("ImpressionCoreModel not found in training.models module")


def test_services_api(module):
    """Test services API functionality."""
    # Check for API components
    api_handler = getattr(module, 'APIHandler', None)
    if api_handler is None:
        raise Exception("APIHandler not found in services.api module")


def main():
    """Run comprehensive tests."""
    print("🚀 Starting ImpressionCore Comprehensive Test Suite...")
    print(f"⏰ Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = ImportTester()
    
    # Core module import tests
    print("\n📦 Testing Core Module Imports...")
    tester.test_import("src", "Main src package")
    tester.test_import("src.core", "Core package")
    tester.test_import("src.core.config", "Core config package")
    tester.test_import("src.core.utils", "Core utils package")
    tester.test_import("src.core.memory", "Core memory package")
    tester.test_import("src.core.brain", "Core brain package")
    tester.test_import("src.core.ai", "Core AI package")
    
    # AI module import tests
    print("\n🤖 Testing AI Module Imports...")
    tester.test_import("src.core.ai.diffusion", "AI diffusion package")
    tester.test_import("src.core.ai.diffusion.unet", "UNet diffusion model")
    tester.test_import("src.core.ai.multimodal", "Multimodal AI package")
    tester.test_import("src.core.ai.multimodal.streaming_processor", "Streaming processor")
    tester.test_import("src.core.ai.generation", "AI generation package")
    tester.test_import("src.core.ai.inference", "AI inference package")
    tester.test_import("src.core.ai.preprocessing", "AI preprocessing package")
    
    # Training module tests
    print("\n🏋️ Testing Training Module Imports...")
    tester.test_import("src.training", "Training package")
    tester.test_import("src.training.models", "Training models package")
    
    # Services module tests
    print("\n🔧 Testing Services Module Imports...")
    tester.test_import("src.services", "Services package")
    tester.test_import("src.services.api", "API services package")
    
    # Interface module tests
    print("\n🖥️ Testing Interface Module Imports...")
    tester.test_import("src.interfaces", "Interfaces package")
    tester.test_import("src.interfaces.web", "Web interface package")
    
    # Data module tests
    print("\n📊 Testing Data Module Imports...")
    tester.test_import("src.data", "Data package")
    
    # Functionality tests
    print("\n⚙️ Testing Basic Functionality...")
    tester.test_basic_functionality(
        "src.core.config", 
        test_core_config, 
        "Core config functionality"
    )
    tester.test_basic_functionality(
        "src.core.utils", 
        test_core_utils, 
        "Core utils functionality"
    )
    tester.test_basic_functionality(
        "src.core.memory", 
        test_core_memory, 
        "Core memory functionality"
    )
    tester.test_basic_functionality(
        "src.training.models", 
        test_training_models, 
        "Training models functionality"
    )
    tester.test_basic_functionality(
        "src.services.api", 
        test_services_api, 
        "Services API functionality"
    )
    
    # Print results
    tester.print_results()
    
    # Return exit code
    return 0 if tester.failed_tests == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
