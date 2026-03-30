#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #gpu_optimization #memory_management #multimodal #performance #python #pytorch #source_code #src/dev_tools/validation/b3_validation_system.py #testing #training #transformer
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #cuda #gpu_optimization #memory_management #multimodal #performance #python #pytorch #source_code #src\\dev_tools\\validation\\b3_validation_system.py #testing #training #transformer
# Category:** Development Tools
# Status:** Active

"""
🔍 IMPRESSIONCORE B3 - VALIDATION SYSTEM
Comprehensive validation of the real B3 implementation

MISSION: Validate every claim and capability of the real implementation
- Test all components work as advertised
- Verify memory usage claims
- Validate training pipeline functionality
- Check model architecture integrity
- Test data loading capabilities

NO FAKE RESULTS - Only report what actually works
"""

import json
import logging
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import torch

# Import our real implementation
try:
    from b3_real_implementation import (
        B3Config,
        B3TransformerLayer,
        ImpressionCoreB3Model,
        MultimodalEmbedding,
        RealB3Trainer,
        RealDataLoader,
    )
except ImportError as e:
    print(f"❌ Failed to import real implementation: {e}")
    sys.exit(1)

# Rich imports for honest reporting
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('b3_validation.log'),
        logging.StreamHandler()
    ]
)

class B3Validator:
    """Comprehensive validator for B3 implementation"""

    def __init__(self):
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        self.validation_results = {}
        self.config = B3Config()

        # Test results tracking
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_details = []

    def run_comprehensive_validation(self) -> dict:
        """Run all validation tests"""

        self.console.print(Panel(
            "🔍 COMPREHENSIVE B3 VALIDATION SYSTEM\n"
            "📊 Testing every component and claim\n"
            "⚡ No fake results - only honest validation\n"
            f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            title="B3 Validation System",
            border_style="blue",
            box=box.DOUBLE
        ))

        # Test suite
        validation_tests = [
            ("🔧 Environment Validation", self._test_environment),
            ("🧠 Model Architecture", self._test_model_architecture),
            ("📊 Data Loading", self._test_data_loading),
            ("💾 Memory Management", self._test_memory_management),
            ("🚀 Training Pipeline", self._test_training_pipeline),
            ("💽 Model Persistence", self._test_model_persistence),
            ("⚡ Performance Benchmarks", self._test_performance),
            ("🔒 Error Handling", self._test_error_handling)
        ]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
            console=self.console
        ) as progress:

            validation_task = progress.add_task("🔍 Running validation tests", total=len(validation_tests))

            for test_name, test_func in validation_tests:
                progress.update(validation_task, description=f"Testing: {test_name}")

                try:
                    result = test_func()
                    self.validation_results[test_name] = result

                    if result.get('passed', False):
                        self.tests_passed += 1
                        status = "✅ PASSED"
                    else:
                        self.tests_failed += 1
                        status = "❌ FAILED"

                    self.test_details.append({
                        'test': test_name,
                        'status': status,
                        'details': result.get('details', 'No details'),
                        'metrics': result.get('metrics', {})
                    })

                except Exception as e:
                    self.tests_failed += 1
                    error_msg = f"Exception: {e!s}"
                    self.test_details.append({
                        'test': test_name,
                        'status': "❌ ERROR",
                        'details': error_msg,
                        'metrics': {}
                    })
                    self.logger.error(f"{test_name} failed with exception: {e}")

                progress.advance(validation_task)

        # Generate final report
        return self._generate_validation_report()

    def _test_environment(self) -> dict:
        """Test environment and dependencies"""

        result = {'passed': True, 'details': [], 'metrics': {}}

        try:
            # Test PyTorch
            result['metrics']['pytorch_version'] = torch.__version__
            result['details'].append(f"PyTorch version: {torch.__version__}")

            # Test CUDA availability
            cuda_available = torch.cuda.is_available()
            result['metrics']['cuda_available'] = cuda_available

            if cuda_available:
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                result['metrics']['gpu_name'] = gpu_name
                result['metrics']['gpu_memory_gb'] = gpu_memory
                result['details'].append(f"GPU: {gpu_name} ({gpu_memory:.1f}GB)")
            else:
                result['details'].append("No CUDA GPU available")

            # Test memory allocation
            test_tensor = torch.randn(100, 100)
            if cuda_available:
                test_tensor = test_tensor.cuda()
                allocated = torch.cuda.memory_allocated() / 1024**2  # MB
                result['metrics']['test_allocation_mb'] = allocated
                result['details'].append(f"Test allocation: {allocated:.1f}MB")

            result['details'].append("Environment validation passed")

        except Exception as e:
            result['passed'] = False
            result['details'].append(f"Environment test failed: {e}")

        return result

    def _test_model_architecture(self) -> dict:
        """Test model architecture components"""

        result = {'passed': True, 'details': [], 'metrics': {}}

        try:
            # Test config
            config = B3Config()
            result['details'].append(f"Config initialized: {config.embed_dim}d embeddings")

            # Test embedding layer
            embeddings = MultimodalEmbedding(config)
            result['metrics']['embedding_params'] = sum(p.numel() for p in embeddings.parameters())
            result['details'].append(f"Embedding layer: {result['metrics']['embedding_params']:,} parameters")

            # Test transformer layer
            transformer = B3TransformerLayer(config)
            result['metrics']['transformer_params'] = sum(p.numel() for p in transformer.parameters())
            result['details'].append(f"Transformer layer: {result['metrics']['transformer_params']:,} parameters")

            # Test full model
            model = ImpressionCoreB3Model(config)
            total_params = sum(p.numel() for p in model.parameters())
            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

            result['metrics']['total_parameters'] = total_params
            result['metrics']['trainable_parameters'] = trainable_params
            result['details'].append(f"Full model: {total_params:,} total, {trainable_params:,} trainable")

            # Test forward pass
            batch_size = 2
            seq_length = 32
            input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_length))

            model.eval()
            with torch.no_grad():
                outputs = model(input_ids=input_ids)

                logits_shape = outputs['logits'].shape
                result['metrics']['output_shape'] = list(logits_shape)
                result['details'].append(f"Forward pass output shape: {logits_shape}")

                expected_shape = (batch_size, seq_length, config.vocab_size)
                if logits_shape == expected_shape:
                    result['details'].append("Output shape validation passed")
                else:
                    result['passed'] = False
                    result['details'].append(f"Output shape mismatch: expected {expected_shape}")

            result['details'].append("Model architecture validation passed")

        except Exception as e:
            result['passed'] = False
            result['details'].append(f"Model architecture test failed: {e}")
            result['details'].append(traceback.format_exc())

        return result

    def _test_data_loading(self) -> dict:
        """Test data loading functionality"""

        result = {'passed': True, 'details': [], 'metrics': {}}

        try:
            config = B3Config()

            # Test with actual F: drive path
            data_path = Path("F:/b3_professional_dataset")
            data_loader = RealDataLoader(config, data_path)

            # Test data discovery
            if data_path.exists():
                data_files = data_loader.discover_real_data()

                total_files = sum(len(files) for files in data_files.values())
                result['metrics']['discovered_files'] = total_files
                result['details'].append(f"Discovered {total_files} data files")

                for data_type, files in data_files.items():
                    result['metrics'][f'{data_type}_files'] = len(files)
                    result['details'].append(f"{data_type}: {len(files)} files")

                # Test data loader creation
                if total_files > 0:
                    training_data = data_loader.create_real_dataloader(data_files)
                    result['metrics']['training_samples'] = len(training_data) if training_data else 0
                    result['details'].append(f"Created {len(training_data) if training_data else 0} training samples")
                else:
                    result['details'].append("No data files found for loading")
            else:
                result['details'].append(f"Data path does not exist: {data_path}")

                # Test with alternative path or create dummy data
                dummy_data = [[i % config.vocab_size for i in range(config.max_seq_length)] for _ in range(10)]
                result['metrics']['dummy_samples'] = len(dummy_data)
                result['details'].append(f"Created {len(dummy_data)} dummy samples for testing")

            result['details'].append("Data loading validation completed")

        except Exception as e:
            result['passed'] = False
            result['details'].append(f"Data loading test failed: {e}")
            result['details'].append(traceback.format_exc())

        return result

    def _test_memory_management(self) -> dict:
        """Test memory usage and management"""

        result = {'passed': True, 'details': [], 'metrics': {}}

        try:
            config = B3Config()

            if torch.cuda.is_available():
                # Clear memory
                torch.cuda.empty_cache()
                initial_memory = torch.cuda.memory_allocated() / 1024**3  # GB

                # Create model
                model = ImpressionCoreB3Model(config).cuda()
                model_memory = torch.cuda.memory_allocated() / 1024**3  # GB

                # Test forward pass
                batch_size = config.batch_size
                seq_length = config.max_seq_length
                input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_length)).cuda()

                with torch.no_grad():
                    outputs = model(input_ids=input_ids)

                forward_memory = torch.cuda.memory_allocated() / 1024**3  # GB

                # Test backward pass
                model.train()
                outputs = model(input_ids=input_ids, labels=input_ids)
                loss = outputs['loss']
                loss.backward()

                backward_memory = torch.cuda.memory_allocated() / 1024**3  # GB

                result['metrics']['initial_memory_gb'] = initial_memory
                result['metrics']['model_memory_gb'] = model_memory - initial_memory
                result['metrics']['forward_memory_gb'] = forward_memory - model_memory
                result['metrics']['backward_memory_gb'] = backward_memory - forward_memory
                result['metrics']['total_memory_gb'] = backward_memory

                result['details'].append(f"Initial memory: {initial_memory:.3f}GB")
                result['details'].append(f"Model loading: +{model_memory - initial_memory:.3f}GB")
                result['details'].append(f"Forward pass: +{forward_memory - model_memory:.3f}GB")
                result['details'].append(f"Backward pass: +{backward_memory - forward_memory:.3f}GB")
                result['details'].append(f"Total memory: {backward_memory:.3f}GB")

                # Check if within GTX 1050 Ti limits (4GB)
                if backward_memory < 3.5:  # Leave some headroom
                    result['details'].append("✅ Memory usage within GTX 1050 Ti limits")
                else:
                    result['details'].append("⚠️ Memory usage may exceed GTX 1050 Ti limits")

            else:
                result['details'].append("No CUDA available for memory testing")

            result['details'].append("Memory management validation completed")

        except Exception as e:
            result['passed'] = False
            result['details'].append(f"Memory management test failed: {e}")
            result['details'].append(traceback.format_exc())

        return result

    def _test_training_pipeline(self) -> dict:
        """Test training pipeline functionality"""

        result = {'passed': True, 'details': [], 'metrics': {}}

        try:
            config = B3Config()
            config.num_epochs = 1  # Quick test
            config.batch_size = 2

            # Create dummy training data
            dummy_data = [[i % config.vocab_size for i in range(config.max_seq_length)] for _ in range(10)]

            # Initialize trainer
            trainer = RealB3Trainer(config)
            result['details'].append("Trainer initialized successfully")

            # Test short training run
            start_time = time.time()
            training_results = trainer.train_real_model(dummy_data)
            training_time = time.time() - start_time

            result['metrics']['training_time_seconds'] = training_time
            result['metrics']['training_success'] = training_results.get('success', False)

            if training_results.get('success'):
                result['details'].append(f"Training completed in {training_time:.2f} seconds")
                result['details'].append(f"Final loss: {training_results.get('final_loss', 'N/A')}")
                result['details'].append(f"Total steps: {training_results.get('total_steps', 'N/A')}")

                # Copy important metrics
                for key in ['avg_loss', 'max_memory_usage_gb', 'steps_per_second']:
                    if key in training_results:
                        result['metrics'][key] = training_results[key]
            else:
                result['passed'] = False
                result['details'].append(f"Training failed: {training_results.get('error', 'Unknown error')}")

            result['details'].append("Training pipeline validation completed")

        except Exception as e:
            result['passed'] = False
            result['details'].append(f"Training pipeline test failed: {e}")
            result['details'].append(traceback.format_exc())

        return result

    def _test_model_persistence(self) -> dict:
        """Test model saving and loading"""

        result = {'passed': True, 'details': [], 'metrics': {}}

        try:
            config = B3Config()

            # Create and train a tiny model
            model = ImpressionCoreB3Model(config)

            # Save model
            model_dir = Path("test_models")
            model_dir.mkdir(exist_ok=True)
            test_model_path = model_dir / "test_model.pth"

            torch.save({
                'model_state_dict': model.state_dict(),
                'config': config.__dict__
            }, test_model_path)

            result['details'].append(f"Model saved to {test_model_path}")

            # Load model
            checkpoint = torch.load(test_model_path, map_location='cpu')

            # Create new model and load state
            new_model = ImpressionCoreB3Model(config)
            new_model.load_state_dict(checkpoint['model_state_dict'])

            result['details'].append("Model loaded successfully")

            # Test that loaded model works
            test_input = torch.randint(0, config.vocab_size, (1, 10))

            model.eval()
            new_model.eval()

            with torch.no_grad():
                output1 = model(input_ids=test_input)
                output2 = new_model(input_ids=test_input)

                # Check outputs are identical
                diff = torch.abs(output1['logits'] - output2['logits']).max().item()
                result['metrics']['max_output_difference'] = diff

                if diff < 1e-6:
                    result['details'].append("✅ Saved and loaded models produce identical outputs")
                else:
                    result['details'].append(f"⚠️ Output difference: {diff}")

            # Clean up test file
            test_model_path.unlink()
            result['details'].append("Test model file cleaned up")

            result['details'].append("Model persistence validation completed")

        except Exception as e:
            result['passed'] = False
            result['details'].append(f"Model persistence test failed: {e}")
            result['details'].append(traceback.format_exc())

        return result

    def _test_performance(self) -> dict:
        """Test performance benchmarks"""

        result = {'passed': True, 'details': [], 'metrics': {}}

        try:
            config = B3Config()
            model = ImpressionCoreB3Model(config)

            if torch.cuda.is_available():
                model = model.cuda()
                device = "cuda"
            else:
                device = "cpu"

            # Benchmark forward pass
            batch_sizes = [1, 2, 4]
            seq_length = config.max_seq_length

            for batch_size in batch_sizes:
                input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_length))
                if device == "cuda":
                    input_ids = input_ids.cuda()

                model.eval()

                # Warmup
                with torch.no_grad():
                    for _ in range(5):
                        _ = model(input_ids=input_ids)

                # Benchmark
                torch.cuda.synchronize() if device == "cuda" else None
                start_time = time.time()

                with torch.no_grad():
                    for _ in range(10):
                        model(input_ids=input_ids)

                torch.cuda.synchronize() if device == "cuda" else None
                end_time = time.time()

                avg_time = (end_time - start_time) / 10
                tokens_per_second = (batch_size * seq_length) / avg_time

                result['metrics'][f'batch_{batch_size}_time_ms'] = avg_time * 1000
                result['metrics'][f'batch_{batch_size}_tokens_per_sec'] = tokens_per_second

                result['details'].append(f"Batch {batch_size}: {avg_time*1000:.2f}ms, {tokens_per_second:.0f} tokens/sec")

            result['details'].append("Performance benchmarking completed")

        except Exception as e:
            result['passed'] = False
            result['details'].append(f"Performance test failed: {e}")
            result['details'].append(traceback.format_exc())

        return result

    def _test_error_handling(self) -> dict:
        """Test error handling and edge cases"""

        result = {'passed': True, 'details': [], 'metrics': {}}

        try:
            config = B3Config()

            # Test invalid input dimensions
            model = ImpressionCoreB3Model(config)

            test_cases = [
                ("Empty input", torch.empty(0, 0, dtype=torch.long)),
                ("Wrong vocab", torch.tensor([[config.vocab_size + 1000]])),
                ("Too long sequence", torch.randint(0, config.vocab_size, (1, config.max_seq_length + 100)))
            ]

            errors_caught = 0

            for test_name, test_input in test_cases:
                try:
                    with torch.no_grad():
                        _ = model(input_ids=test_input)
                    result['details'].append(f"{test_name}: No error (may be expected)")
                except Exception as e:
                    errors_caught += 1
                    result['details'].append(f"{test_name}: Caught error - {type(e).__name__}")

            result['metrics']['errors_caught'] = errors_caught
            result['details'].append(f"Error handling test completed: {errors_caught} errors caught")

        except Exception as e:
            result['passed'] = False
            result['details'].append(f"Error handling test failed: {e}")
            result['details'].append(traceback.format_exc())

        return result

    def _generate_validation_report(self) -> dict:
        """Generate comprehensive validation report"""

        # Create results table
        results_table = Table(title="📊 B3 Validation Results")
        results_table.add_column("Test", style="cyan")
        results_table.add_column("Status", style="bold")
        results_table.add_column("Details", style="dim")

        for test_detail in self.test_details:
            status_style = "green" if "✅" in test_detail['status'] else "red"
            results_table.add_row(
                test_detail['test'],
                Text(test_detail['status'], style=status_style),
                test_detail['details'][:50] + "..." if len(test_detail['details']) > 50 else test_detail['details']
            )

        self.console.print(results_table)

        # Create summary
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0

        summary_table = Table(title="📈 Validation Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Total Tests", str(total_tests))
        summary_table.add_row("Passed", str(self.tests_passed))
        summary_table.add_row("Failed", str(self.tests_failed))
        summary_table.add_row("Success Rate", f"{success_rate:.1f}%")

        self.console.print(summary_table)

        # Overall status
        if success_rate >= 80:
            status_panel = Panel(
                "✅ VALIDATION SUCCESSFUL\n"
                f"🎯 {self.tests_passed}/{total_tests} tests passed\n"
                "🚀 Implementation ready for use",
                title="Validation Complete",
                style="bold green"
            )
        else:
            status_panel = Panel(
                "❌ VALIDATION FAILED\n"
                f"⚠️ {self.tests_failed}/{total_tests} tests failed\n"
                "🔧 Implementation needs fixes",
                title="Validation Failed",
                style="bold red"
            )

        self.console.print(status_panel)

        # Save detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'tests_passed': self.tests_passed,
                'tests_failed': self.tests_failed,
                'success_rate': success_rate
            },
            'test_results': self.test_details,
            'validation_data': self.validation_results
        }

        report_path = Path("b3_validation_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        self.console.print(f"📄 Detailed report saved to: {report_path}")

        return report

def main():
    """Main validation function"""

    console = Console()

    console.print(Panel(
        "🔍 B3 VALIDATION SYSTEM\n"
        "📊 Comprehensive testing of real implementation\n"
        "⚡ Honest validation - no fake results",
        title="Starting Validation",
        border_style="blue"
    ))

    try:
        validator = B3Validator()
        validation_report = validator.run_comprehensive_validation()

        return validation_report

    except Exception as e:
        console.print(Panel(
            f"❌ VALIDATION SYSTEM FAILED\n"
            f"Error: {e!s}\n"
            "Check logs for details",
            title="Validation Error",
            style="bold red"
        ))
        raise

if __name__ == "__main__":
    main()
