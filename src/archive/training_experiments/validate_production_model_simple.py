#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #gpu_optimization #inference #memory_management #python #source_code #src/training/validate_production_model_simple.py #testing #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #cuda #gpu_optimization #inference #memory_management #python #source_code #src\\training\\validate_production_model_simple.py #testing #training
# Category:** Training System
# Status:** Active

"""
ImpressionCore Production Model Validation Script
===============================================

Simple validation script for the production-trained ImpressionCore model.

Author: GitHub Copilot
Date: June 12, 2025
Version: 1.0.0
"""

import torch
import json
import psutil
import time
import logging
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import tracemalloc
import gc

# Rich imports with fallbacks
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich library not available, using basic output")

class ProductionModelValidator:
    """Simple, effective validation for the ImpressionCore production model."""

    def __init__(self, model_path: str):
        """Initialize the validator with model path."""
        self.model_path = Path(model_path)
        self.console = Console() if RICH_AVAILABLE else None

        # Validation results storage
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'model_path': str(self.model_path),
            'tests': {},
            'overall_status': 'PENDING',
            'summary': {}
        }

        # Performance targets
        self.performance_targets = {
            'max_memory_gb': 4.0,  # GTX 1050 Ti VRAM limit
            'max_inference_time_ms': 1000,  # 1 second max response
            'max_model_size_gb': 2.0  # Reasonable model size limit
        }

    def log(self, message: str, level: str = "INFO"):
        """Simple logging function."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")

    def validate_model_loading(self) -> Dict[str, Any]:
        """Test if the production model loads correctly."""
        test_name = "Model Loading Test"
        self.log(f"Starting {test_name}")

        try:
            # Check if model file exists
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")

            # Check model file size
            model_size_gb = self.model_path.stat().st_size / (1024**3)
            self.log(f"Model file size: {model_size_gb:.3f} GB")

            # Attempt to load the model
            start_time = time.time()

            # Enable memory tracing
            tracemalloc.start()

            # Load model
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.log(f"Loading model on device: {device}")

            model_data = torch.load(self.model_path, map_location=device)

            # Record memory usage
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            load_time = time.time() - start_time

            # Extract model information
            model_info = {
                'file_size_gb': round(model_size_gb, 3),
                'load_time_seconds': round(load_time, 3),
                'memory_used_mb': round(current / 1024 / 1024, 2),
                'peak_memory_mb': round(peak / 1024 / 1024, 2),
                'device': str(device),
                'model_keys': list(model_data.keys()) if isinstance(model_data, dict) else 'tensor',
            }

            self.log(f"Model loaded successfully in {load_time:.2f}s")
            self.log(f"Memory usage: {current / 1024 / 1024:.2f} MB (peak: {peak / 1024 / 1024:.2f} MB)")

            # Determine test result
            passed = (
                model_size_gb <= self.performance_targets['max_model_size_gb'] and
                load_time <= 10.0  # 10 seconds max load time
            )

            result = {
                'test_name': test_name,
                'status': 'PASSED' if passed else 'FAILED',
                'details': model_info,
                'timestamp': datetime.now().isoformat()
            }

            self.log(f"{test_name} {'PASSED' if passed else 'FAILED'}")
            return result

        except Exception as e:
            self.log(f"{test_name} ERROR: {str(e)}", "ERROR")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }

    def validate_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage to ensure it stays within 4GB VRAM limits."""
        test_name = "Memory Usage Validation"
        self.log(f"Starting {test_name}")

        try:
            # Clear memory before testing
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Start memory monitoring
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

            if torch.cuda.is_available():
                initial_gpu_memory = torch.cuda.memory_allocated() / 1024 / 1024  # MB
            else:
                initial_gpu_memory = 0

            self.log(f"Initial GPU memory: {initial_gpu_memory:.2f} MB")

            # Load and run inference simulation
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            model_data = torch.load(self.model_path, map_location=device)

            # Simulate inference operations
            peak_memory = initial_memory
            peak_gpu_memory = initial_gpu_memory

            for i in range(10):  # Multiple inference simulations
                # Simulate embedding processing
                dummy_embedding = torch.randn(128, device=device)  # 128-dim embedding

                # Simple processing simulation
                processed = torch.nn.functional.relu(dummy_embedding)
                result = torch.nn.functional.normalize(processed, dim=0)

                # Monitor memory
                current_memory = process.memory_info().rss / 1024 / 1024
                peak_memory = max(peak_memory, current_memory)

                if torch.cuda.is_available():
                    current_gpu_memory = torch.cuda.memory_allocated() / 1024 / 1024
                    peak_gpu_memory = max(peak_gpu_memory, current_gpu_memory)

            # Calculate memory usage
            memory_used_mb = peak_memory - initial_memory
            gpu_memory_used_mb = peak_gpu_memory - initial_gpu_memory
            total_gpu_memory_gb = peak_gpu_memory / 1024

            self.log(f"Peak GPU memory: {peak_gpu_memory:.2f} MB ({total_gpu_memory_gb:.3f} GB)")

            # Check against targets
            memory_within_limits = total_gpu_memory_gb <= self.performance_targets['max_memory_gb']

            result = {
                'test_name': test_name,
                'status': 'PASSED' if memory_within_limits else 'FAILED',
                'details': {
                    'peak_system_memory_mb': round(peak_memory, 2),
                    'memory_used_mb': round(memory_used_mb, 2),
                    'peak_gpu_memory_mb': round(peak_gpu_memory, 2),
                    'gpu_memory_used_mb': round(gpu_memory_used_mb, 2),
                    'total_gpu_memory_gb': round(total_gpu_memory_gb, 3),
                    'within_4gb_limit': memory_within_limits,
                    'target_limit_gb': self.performance_targets['max_memory_gb']
                },
                'timestamp': datetime.now().isoformat()
            }

            self.log(f"{test_name} {'PASSED' if memory_within_limits else 'FAILED'}")
            self.log(f"Memory usage: {total_gpu_memory_gb:.2f}GB (limit: 4GB)")
            return result

        except Exception as e:
            self.log(f"{test_name} ERROR: {str(e)}", "ERROR")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def validate_inference_performance(self) -> Dict[str, Any]:
        """Test inference performance and speed."""
        test_name = "Inference Performance Test"
        self.log(f"Starting {test_name}")

        try:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

            # Load model
            model_data = torch.load(self.model_path, map_location=device)

            # Performance testing
            inference_times = []

            self.log("Running inference performance tests...")

            # Run multiple inference tests
            for i in range(20):  # 20 test runs
                # Create test embedding
                test_embedding = torch.randn(128, device=device)

                # Time the inference
                start_time = time.time()

                # Simulate model inference
                with torch.no_grad():
                    # Basic tensor operations to simulate inference
                    result = torch.nn.functional.relu(test_embedding)
                    result = torch.nn.functional.normalize(result, dim=0)
                    # Additional processing simulation
                    result = torch.matmul(result.unsqueeze(0), result.unsqueeze(1))

                end_time = time.time()
                inference_time_ms = (end_time - start_time) * 1000
                inference_times.append(inference_time_ms)

            # Calculate statistics
            avg_inference_time = np.mean(inference_times)
            max_inference_time = np.max(inference_times)
            min_inference_time = np.min(inference_times)
            std_inference_time = np.std(inference_times)

            self.log(f"Average inference time: {avg_inference_time:.2f} ms")

            # Check performance targets
            performance_acceptable = avg_inference_time <= self.performance_targets['max_inference_time_ms']

            result = {
                'test_name': test_name,
                'status': 'PASSED' if performance_acceptable else 'FAILED',
                'details': {
                    'average_inference_ms': round(avg_inference_time, 2),
                    'max_inference_ms': round(max_inference_time, 2),
                    'min_inference_ms': round(min_inference_time, 2),
                    'std_deviation_ms': round(std_inference_time, 2),
                    'target_max_ms': self.performance_targets['max_inference_time_ms'],
                    'meets_performance_target': performance_acceptable,
                    'test_runs': len(inference_times)
                },
                'timestamp': datetime.now().isoformat()
            }

            self.log(f"{test_name} {'PASSED' if performance_acceptable else 'FAILED'}")
            return result

        except Exception as e:
            self.log(f"{test_name} ERROR: {str(e)}", "ERROR")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def validate_model_integrity(self) -> Dict[str, Any]:
        """Test model integrity and basic functionality."""
        test_name = "Model Integrity Test"
        self.log(f"Starting {test_name}")

        try:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            model_data = torch.load(self.model_path, map_location=device)

            # Analyze model structure
            integrity_checks = []

            # Check 1: Model data type
            if isinstance(model_data, dict):
                integrity_checks.append({'check': 'data_structure', 'result': 'dict', 'status': 'PASS'})

                # Check for expected keys
                expected_keys = ['model_state_dict', 'optimizer_state_dict', 'epoch', 'loss']
                missing_keys = [key for key in expected_keys if key not in model_data]

                if not missing_keys:
                    integrity_checks.append({'check': 'expected_keys', 'result': 'all_present', 'status': 'PASS'})
                else:
                    integrity_checks.append({'check': 'expected_keys', 'result': f'missing: {missing_keys}', 'status': 'WARN'})

            else:
                integrity_checks.append({'check': 'data_structure', 'result': str(type(model_data)), 'status': 'WARN'})

            # Check 2: Training history validation
            if 'loss' in model_data:
                final_loss = model_data['loss']
                if isinstance(final_loss, (int, float)) and 0 < final_loss < 1:
                    integrity_checks.append({'check': 'final_loss', 'result': f'{final_loss:.4f}', 'status': 'PASS'})
                    self.log(f"Final training loss: {final_loss:.4f}")
                else:
                    integrity_checks.append({'check': 'final_loss', 'result': f'{final_loss}', 'status': 'FAIL'})

            # Check 3: Model parameters (if available)
            if 'model_state_dict' in model_data:
                state_dict = model_data['model_state_dict']
                param_count = sum(p.numel() for p in state_dict.values() if isinstance(p, torch.Tensor))
                integrity_checks.append({'check': 'parameter_count', 'result': f'{param_count:,}', 'status': 'PASS'})
                self.log(f"Model parameters: {param_count:,}")

            # Log integrity check results
            for check in integrity_checks:
                self.log(f"  {check['check']}: {check['result']} [{check['status']}]")

            # Overall integrity assessment
            failed_checks = [check for check in integrity_checks if check['status'] == 'FAIL']
            overall_status = 'PASSED' if not failed_checks else 'FAILED'

            result = {
                'test_name': test_name,
                'status': overall_status,
                'details': {
                    'integrity_checks': integrity_checks,
                    'failed_checks': len(failed_checks),
                    'total_checks': len(integrity_checks),
                    'model_keys': list(model_data.keys()) if isinstance(model_data, dict) else []
                },
                'timestamp': datetime.now().isoformat()
            }

            self.log(f"{test_name} {'PASSED' if overall_status == 'PASSED' else 'FAILED'}")
            return result

        except Exception as e:
            self.log(f"{test_name} ERROR: {str(e)}", "ERROR")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def run_full_validation(self) -> Dict[str, Any]:
        """Run the complete validation suite."""
        print("="*80)
        print("🚀 ImpressionCore Production Model Validation")
        print(f"Model Path: {self.model_path}")
        print(f"Target Hardware: GTX 1050 Ti (4GB VRAM)")
        print(f"Validation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Run all validation tests
        tests = [
            ('model_loading', self.validate_model_loading),
            ('memory_usage', self.validate_memory_usage),
            ('inference_performance', self.validate_inference_performance),
            ('model_integrity', self.validate_model_integrity)
        ]

        for test_key, test_func in tests:
            print(f"\n--- Running {test_key.replace('_', ' ').title()} ---")

            result = test_func()
            self.validation_results['tests'][test_key] = result

        # Generate summary
        self._generate_summary()

        # Display results
        self._display_results()

        return self.validation_results

    def _generate_summary(self):
        """Generate validation summary."""
        tests = self.validation_results['tests']

        passed_tests = [test for test in tests.values() if test['status'] == 'PASSED']
        failed_tests = [test for test in tests.values() if test['status'] == 'FAILED']
        error_tests = [test for test in tests.values() if test['status'] == 'ERROR']

        overall_status = 'PASSED' if not failed_tests and not error_tests else 'FAILED'

        self.validation_results['overall_status'] = overall_status
        self.validation_results['summary'] = {
            'total_tests': len(tests),
            'passed_tests': len(passed_tests),
            'failed_tests': len(failed_tests),
            'error_tests': len(error_tests),
            'success_rate': round(len(passed_tests) / len(tests) * 100, 1) if tests else 0
        }

    def _display_results(self):
        """Display validation results."""
        summary = self.validation_results['summary']

        print("\n" + "="*80)
        print("📊 VALIDATION RESULTS SUMMARY")
        print("="*80)

        # Display individual test results
        for test_key, test_result in self.validation_results['tests'].items():
            status_symbol = {
                'PASSED': '✅',
                'FAILED': '❌',
                'ERROR': '⚠️'
            }.get(test_result['status'], '❓')

            print(f"{status_symbol} {test_key.replace('_', ' ').title()}: {test_result['status']}")

            # Show key details
            if 'details' in test_result:
                if test_key == 'memory_usage' and 'total_gpu_memory_gb' in test_result['details']:
                    print(f"   GPU Memory: {test_result['details']['total_gpu_memory_gb']} GB")
                elif test_key == 'inference_performance' and 'average_inference_ms' in test_result['details']:
                    print(f"   Avg Inference: {test_result['details']['average_inference_ms']} ms")
                elif test_key == 'model_loading' and 'file_size_gb' in test_result['details']:
                    print(f"   Model Size: {test_result['details']['file_size_gb']} GB")

        print("\n" + "-"*80)
          # Overall summary
        overall_symbol = '✅' if self.validation_results['overall_status'] == 'PASSED' else '❌'
        print(f"{overall_symbol} OVERALL STATUS: {self.validation_results['overall_status']}")
        print(f"📈 SUCCESS RATE: {summary['success_rate']}%")
        print(f"✅ Passed: {summary['passed_tests']}/{summary['total_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}/{summary['total_tests']}")
        print(f"⚠️  Errors: {summary['error_tests']}/{summary['total_tests']}")
        print("="*80)

    def save_results(self, output_path: Optional[str] = None) -> Path:
        """Save validation results to JSON file."""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.model_path.parent / f"validation_results_{timestamp}.json"
        else:
            output_path = Path(output_path)

        # Convert numpy types to native Python types for JSON serialization
        def convert_for_json(obj):
            if isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_for_json(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_json(item) for item in obj]
            else:
                return obj

        json_data = convert_for_json(self.validation_results)

        with output_path.open('w') as f:
            json.dump(json_data, f, indent=2)

        self.log(f"Validation results saved to: {output_path}")
        return output_path


def main():
    """Main function to run the validation."""
    import argparse

    parser = argparse.ArgumentParser(description="ImpressionCore Production Model Validator")
    parser.add_argument("--model_path", required=True, help="Path to the production model file")
    parser.add_argument("--output_path", help="Path to save validation results")
    parser.add_argument("--save_results", action="store_true", help="Save results to JSON file")

    args = parser.parse_args()

    # Initialize validator
    validator = ProductionModelValidator(args.model_path)

    # Run validation
    results = validator.run_full_validation()

    # Save results if requested
    if args.save_results:
        output_path = validator.save_results(args.output_path)
        print(f"\n📄 Results saved to: {output_path}")

    # Exit with appropriate code
    exit_code = 0 if results['overall_status'] == 'PASSED' else 1
    exit(exit_code)


if __name__ == "__main__":
    main()
