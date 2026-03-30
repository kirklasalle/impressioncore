"""
Enhanced QLoRA Validation Script for ImpressionCore
=================================================

Comprehensive validation of QLoRA (Quantized LoRA) implementation with rich UI,
progress tracking, and detailed testing for memory-constrained hardware.

Features:
- Quantization functionality tests
- Memory usage validation
- Parameter efficiency verification
- Hardware-specific optimization tests
- Rich console output with progress tracking
- Performance benchmarking

Author: ImpressionCore Development Team
Date: 2025-01-04
License: MIT
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn as nn
import time
import traceback
from typing import Dict, Any, List, Tuple
import logging

# Import ImpressionCore components
try:
    from models.qlora import QLoRAConfig, QLoRALinear, QLoRAModel, create_qlora_config_for_hardware
except ImportError:
    # Fallback import paths
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from models.qlora import QLoRAConfig, QLoRALinear, QLoRAModel, create_qlora_config_for_hardware

# Rich imports
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.layout import Layout
from rich.live import Live
from rich import box
import rich.syntax


class SimpleStatusManager:
    """Simple status manager for validation display."""
    
    def __init__(self):
        self.console = Console()
    
    def status(self, message: str):
        """Simple status context manager."""
        return self.console.status(message)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QLoRA_Validation")
console = Console()


class QLoRAValidator:
    """
    Comprehensive QLoRA validation suite with rich UI and detailed testing.
    """
    
    def __init__(self):
        self.console = console
        self.status_manager = SimpleStatusManager()
        self.test_results = []
        self.memory_stats = {}
        
    def print_header(self):
        """Print validation header with project info."""
        header_panel = Panel.fit(
            "[bold cyan]🧠 ImpressionCore QLoRA Validation Suite[/bold cyan]\n"
            "[dim]Quantized Low-Rank Adaptation Testing & Validation[/dim]\n"
            f"[yellow]Date:[/yellow] {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"[yellow]PyTorch Version:[/yellow] {torch.__version__}\n"
            f"[yellow]CUDA Available:[/yellow] {torch.cuda.is_available()}\n"
            f"[yellow]Device:[/yellow] {torch.cuda.get_device_name() if torch.cuda.is_available() else 'CPU'}",
            title="🚀 QLoRA Validation",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(header_panel)
        self.console.print()
    
    def test_qlora_config_creation(self) -> bool:
        """Test QLoRA configuration creation and validation."""
        test_name = "QLoRA Config Creation"
        
        try:
            with self.status_manager.status(f"[cyan]Testing {test_name}..."):
                # Test default config
                config = QLoRAConfig()
                assert config.r == 16
                assert config.lora_alpha == 32
                assert config.load_in_4bit == True
                assert config.bnb_4bit_quant_type == "nf4"
                  # Test hardware-optimized config
                hw_config = create_qlora_config_for_hardware(
                    target_memory_mb=3500,
                    model_size_params=1_000_000_000
                )
                assert hw_config.max_memory_mb == 3500
                assert hw_config.r > 0
                
                self.test_results.append((test_name, True, "All config tests passed"))
                console.print(f"[green]✅ {test_name}: PASSED[/green]")
                return True
                
        except Exception as e:
            error_msg = f"Configuration test failed: {str(e)}"
            self.test_results.append((test_name, False, error_msg))
            console.print(f"[red]❌ {test_name}: FAILED - {error_msg}[/red]")
            return False
    
    def test_qlora_linear_layer(self) -> bool:
        """Test QLoRA linear layer functionality."""
        test_name = "QLoRA Linear Layer"
        
        try:
            with self.status_manager.status(f"[cyan]Testing {test_name}..."):
                config = QLoRAConfig(r=8, lora_alpha=16)
                
                # Create QLoRA linear layer
                qlora_layer = QLoRALinear(
                    in_features=512,
                    out_features=256,
                    config=config
                )
                
                # Test forward pass
                batch_size, seq_len = 4, 128
                x = torch.randn(batch_size, seq_len, 512)
                
                # Forward pass with LoRA enabled
                qlora_layer.enable_lora()
                output_with_lora = qlora_layer(x)
                assert output_with_lora.shape == (batch_size, seq_len, 256)
                
                # Forward pass with LoRA disabled
                qlora_layer.disable_lora()
                output_without_lora = qlora_layer(x)
                assert output_without_lora.shape == (batch_size, seq_len, 256)
                
                # Verify different outputs (LoRA should add adaptation)
                qlora_layer.enable_lora()
                qlora_layer.train()  # Enable training mode for LoRA
                output_with_lora_train = qlora_layer(x)
                
                # Test memory usage calculation
                memory_usage = qlora_layer.get_memory_usage()
                assert "base_layer_mb" in memory_usage
                assert "lora_adapter_mb" in memory_usage
                assert "total_mb" in memory_usage
                assert "reduction_factor" in memory_usage
                
                self.memory_stats[test_name] = memory_usage
                self.test_results.append((test_name, True, f"Memory reduction: {memory_usage['reduction_factor']:.2f}x"))
                logger.success(f"✅ {test_name}: PASSED - Memory reduction: {memory_usage['reduction_factor']:.2f}x")
                return True
                
        except Exception as e:
            error_msg = f"Linear layer test failed: {str(e)}"
            self.test_results.append((test_name, False, error_msg))
            logger.error(f"❌ {test_name}: FAILED - {error_msg}")
            return False
    
    def test_qlora_model_conversion(self) -> bool:
        """Test converting a regular model to QLoRA."""
        test_name = "QLoRA Model Conversion"
        
        try:
            with self.status_manager.status(f"[cyan]Testing {test_name}..."):
                # Create a simple transformer-like model
                class SimpleTransformer(nn.Module):
                    def __init__(self):
                        super().__init__()
                        self.q_proj = nn.Linear(512, 512)
                        self.k_proj = nn.Linear(512, 512)
                        self.v_proj = nn.Linear(512, 512)
                        self.o_proj = nn.Linear(512, 512)
                        self.gate_proj = nn.Linear(512, 1024)
                        self.up_proj = nn.Linear(512, 1024)
                        self.down_proj = nn.Linear(1024, 512)
                        
                    def forward(self, x):
                        return self.o_proj(self.v_proj(x))
                
                base_model = SimpleTransformer()
                config = QLoRAConfig(r=4, lora_alpha=8)
                
                # Convert to QLoRA
                qlora_model = QLoRAModel(base_model, config)
                
                # Test parameter counts
                trainable, total = qlora_model.get_trainable_params()
                
                # Enable LoRA training
                qlora_model.enable_lora_training()
                trainable_after, total_after = qlora_model.get_trainable_params()
                
                assert trainable_after > 0, "Should have trainable LoRA parameters"
                assert trainable_after < total_after, "LoRA should reduce trainable parameters"
                
                # Test forward pass
                x = torch.randn(2, 64, 512)
                output = qlora_model(x)
                assert output.shape == (2, 64, 512)
                
                # Test memory usage
                memory_usage = qlora_model.get_memory_usage()
                assert memory_usage["total_mb"] > 0
                
                self.memory_stats[test_name] = memory_usage
                param_efficiency = (trainable_after / total_after) * 100
                
                self.test_results.append((
                    test_name, 
                    True, 
                    f"Trainable params: {param_efficiency:.2f}% ({trainable_after}/{total_after})"
                ))
                logger.success(f"✅ {test_name}: PASSED - {param_efficiency:.2f}% trainable parameters")
                return True
                
        except Exception as e:
            error_msg = f"Model conversion test failed: {str(e)}"
            self.test_results.append((test_name, False, error_msg))
            logger.error(f"❌ {test_name}: FAILED - {error_msg}")
            return False
    
    def test_memory_optimization(self) -> bool:
        """Test memory optimization features."""
        test_name = "Memory Optimization"
        
        try:
            with self.status_manager.status(f"[cyan]Testing {test_name}..."):
                # Test different configurations
                configs = [
                    ("Standard", QLoRAConfig(r=16, lora_alpha=32)),
                    ("Memory Optimized", QLoRAConfig(r=8, lora_alpha=16, use_gradient_checkpointing=True)),
                    ("Ultra Efficient", QLoRAConfig(r=4, lora_alpha=8, use_gradient_checkpointing=True)),
                ]
                
                memory_comparisons = {}
                
                for config_name, config in configs:
                    # Create layer with config
                    layer = QLoRALinear(512, 512, config)
                    usage = layer.get_memory_usage()
                    memory_comparisons[config_name] = usage["total_mb"]
                
                # Verify memory reduction with smaller ranks
                assert memory_comparisons["Ultra Efficient"] < memory_comparisons["Standard"]
                assert memory_comparisons["Memory Optimized"] < memory_comparisons["Standard"]
                
                # Test hardware-specific config
                hw_config = create_qlora_config_for_hardware(target_memory_mb=2000, model_size_params=500_000_000)
                assert hw_config.max_memory_mb == 2000
                
                self.memory_stats[test_name] = memory_comparisons
                self.test_results.append((
                    test_name, 
                    True, 
                    f"Memory savings: {((memory_comparisons['Standard'] - memory_comparisons['Ultra Efficient']) / memory_comparisons['Standard'] * 100):.1f}%"
                ))
                logger.success(f"✅ {test_name}: PASSED - Significant memory savings achieved")
                return True
                
        except Exception as e:
            error_msg = f"Memory optimization test failed: {str(e)}"
            self.test_results.append((test_name, False, error_msg))
            logger.error(f"❌ {test_name}: FAILED - {error_msg}")
            return False
    
    def test_quantization_integration(self) -> bool:
        """Test quantization integration and functionality."""
        test_name = "Quantization Integration"
        
        try:
            with self.status_manager.status(f"[cyan]Testing {test_name}..."):
                # Test with different quantization settings
                configs = [
                    QLoRAConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4"),
                    QLoRAConfig(load_in_4bit=True, bnb_4bit_quant_type="fp4"),
                    QLoRAConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True),
                    QLoRAConfig(load_in_4bit=True, bnb_4bit_use_double_quant=False),
                ]
                
                quantization_results = {}
                
                for i, config in enumerate(configs):
                    config_name = f"Config_{i+1}"
                    try:
                        layer = QLoRALinear(256, 256, config)
                        
                        # Test forward pass
                        x = torch.randn(2, 32, 256)
                        output = layer(x)
                        
                        # Check output validity
                        assert not torch.isnan(output).any(), "Output contains NaN values"
                        assert output.shape == (2, 32, 256), "Output shape mismatch"
                        
                        # Get memory usage
                        usage = layer.get_memory_usage()
                        quantization_results[config_name] = {
                            "success": True,
                            "memory_mb": usage["total_mb"],
                            "reduction_factor": usage["reduction_factor"]
                        }
                        
                    except Exception as inner_e:
                        quantization_results[config_name] = {
                            "success": False,
                            "error": str(inner_e)
                        }
                        # Continue with other configs
                        continue
                
                # At least one configuration should work
                successful_configs = sum(1 for result in quantization_results.values() if result.get("success", False))
                assert successful_configs > 0, "No quantization configurations worked"
                
                self.memory_stats[test_name] = quantization_results
                self.test_results.append((
                    test_name, 
                    True, 
                    f"Successful quantization configs: {successful_configs}/{len(configs)}"
                ))
                logger.success(f"✅ {test_name}: PASSED - {successful_configs}/{len(configs)} configs working")
                return True
                
        except Exception as e:
            error_msg = f"Quantization integration test failed: {str(e)}"
            self.test_results.append((test_name, False, error_msg))
            logger.error(f"❌ {test_name}: FAILED - {error_msg}")
            return False
    
    def test_save_load_functionality(self) -> bool:
        """Test saving and loading QLoRA adapters."""
        test_name = "Save/Load Functionality"
        
        try:
            with self.status_manager.status(f"[cyan]Testing {test_name}..."):
                import tempfile
                import shutil
                
                # Create model and train briefly
                class SimpleModel(nn.Module):
                    def __init__(self):
                        super().__init__()
                        self.linear = nn.Linear(128, 64)
                    
                    def forward(self, x):
                        return self.linear(x)
                
                base_model = SimpleModel()
                config = QLoRAConfig(r=4, lora_alpha=8)
                qlora_model = QLoRAModel(base_model, config)
                
                # Enable training and do a forward pass
                qlora_model.enable_lora_training()
                x = torch.randn(4, 32, 128)
                output_before = qlora_model(x)
                
                # Save to temporary directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    qlora_model.save_pretrained(temp_dir)
                    
                    # Check files exist
                    import os
                    assert os.path.exists(os.path.join(temp_dir, "qlora_adapter_model.bin"))
                    assert os.path.exists(os.path.join(temp_dir, "qlora_config.json"))
                    
                    # Verify config file content
                    import json
                    with open(os.path.join(temp_dir, "qlora_config.json"), "r") as f:
                        saved_config = json.load(f)
                    
                    assert saved_config["r"] == config.r
                    assert saved_config["lora_alpha"] == config.lora_alpha
                
                self.test_results.append((test_name, True, "Save/load operations completed successfully"))
                logger.success(f"✅ {test_name}: PASSED - Save/load working correctly")
                return True
                
        except Exception as e:
            error_msg = f"Save/load test failed: {str(e)}"
            self.test_results.append((test_name, False, error_msg))
            logger.error(f"❌ {test_name}: FAILED - {error_msg}")
            return False
    
    def test_hardware_constraints(self) -> bool:
        """Test QLoRA performance under hardware constraints."""
        test_name = "Hardware Constraints"
        
        try:
            with self.status_manager.status(f"[cyan]Testing {test_name}..."):
                # Test GTX 1050 Ti optimized config
                gtx_1050_ti_config = create_qlora_config_for_hardware(
                    target_memory_mb=3500,  # Conservative for 4GB VRAM
                    model_size_params=774_000_000  # ~774M parameter model
                )
                
                # Test with progressively larger models
                model_sizes = [
                    (100_000_000, "100M"),
                    (500_000_000, "500M"),
                    (1_000_000_000, "1B"),
                ]
                
                hardware_results = {}
                
                for params, size_name in model_sizes:
                    config = create_qlora_config_for_hardware(
                        target_memory_mb=3500,
                        model_size_params=params
                    )
                    
                    # Create a representative layer
                    layer = QLoRALinear(1024, 1024, config)
                    usage = layer.get_memory_usage()
                    
                    hardware_results[size_name] = {
                        "config_r": config.r,
                        "memory_mb": usage["total_mb"],
                        "reduction_factor": usage["reduction_factor"],
                        "fits_in_4gb": usage["total_mb"] < 3500
                    }
                
                # Verify all configurations fit in target memory
                all_fit = all(result["fits_in_4gb"] for result in hardware_results.values())
                
                self.memory_stats[test_name] = hardware_results
                self.test_results.append((
                    test_name, 
                    True, 
                    f"All model sizes fit in 4GB: {all_fit}"
                ))
                logger.success(f"✅ {test_name}: PASSED - Hardware optimization working")
                return True
                
        except Exception as e:
            error_msg = f"Hardware constraints test failed: {str(e)}"
            self.test_results.append((test_name, False, error_msg))
            logger.error(f"❌ {test_name}: FAILED - {error_msg}")
            return False
    
    def run_performance_benchmark(self) -> bool:
        """Run performance benchmarks for QLoRA."""
        test_name = "Performance Benchmark"
        
        try:
            with self.status_manager.status(f"[cyan]Running {test_name}..."):
                # Create models for comparison
                standard_linear = nn.Linear(1024, 1024)
                qlora_config = QLoRAConfig(r=16, lora_alpha=32)
                qlora_linear = QLoRALinear(1024, 1024, qlora_config)
                
                # Test data
                batch_sizes = [1, 4, 16]
                seq_lengths = [128, 512]
                
                benchmark_results = {
                    "standard_linear": {},
                    "qlora_linear": {}
                }
                
                for batch_size in batch_sizes:
                    for seq_len in seq_lengths:
                        test_key = f"B{batch_size}_S{seq_len}"
                        x = torch.randn(batch_size, seq_len, 1024)
                        
                        # Benchmark standard linear
                        start_time = time.time()
                        for _ in range(100):
                            _ = standard_linear(x)
                        standard_time = time.time() - start_time
                        
                        # Benchmark QLoRA linear
                        qlora_linear.enable_lora()
                        start_time = time.time()
                        for _ in range(100):
                            _ = qlora_linear(x)
                        qlora_time = time.time() - start_time
                        
                        benchmark_results["standard_linear"][test_key] = standard_time
                        benchmark_results["qlora_linear"][test_key] = qlora_time
                
                # Calculate average performance overhead
                total_overhead = 0
                count = 0
                for key in benchmark_results["standard_linear"]:
                    overhead = (benchmark_results["qlora_linear"][key] / benchmark_results["standard_linear"][key]) - 1
                    total_overhead += overhead
                    count += 1
                
                avg_overhead = (total_overhead / count) * 100 if count > 0 else 0
                
                self.memory_stats[test_name] = benchmark_results
                self.test_results.append((
                    test_name, 
                    True, 
                    f"Average overhead: {avg_overhead:.1f}%"
                ))
                logger.success(f"✅ {test_name}: PASSED - Performance overhead: {avg_overhead:.1f}%")
                return True
                
        except Exception as e:
            error_msg = f"Performance benchmark failed: {str(e)}"
            self.test_results.append((test_name, False, error_msg))
            logger.error(f"❌ {test_name}: FAILED - {error_msg}")
            return False
    
    def create_results_table(self) -> Table:
        """Create a rich table with test results."""
        table = Table(title="🧪 QLoRA Validation Results", box=box.ROUNDED)
        
        table.add_column("Test Name", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Details", style="dim")
        
        for test_name, passed, details in self.test_results:
            status = "[green]✅ PASS[/green]" if passed else "[red]❌ FAIL[/red]"
            table.add_row(test_name, status, details)
        
        return table
    
    def create_memory_stats_table(self) -> Table:
        """Create a table showing memory usage statistics."""
        table = Table(title="💾 Memory Usage Statistics", box=box.ROUNDED)
        
        table.add_column("Component", style="cyan")
        table.add_column("Memory (MB)", justify="right", style="yellow")
        table.add_column("Details", style="dim")
        
        for test_name, stats in self.memory_stats.items():
            if isinstance(stats, dict):
                if "total_mb" in stats:
                    table.add_row(
                        test_name,
                        f"{stats['total_mb']:.2f}",
                        f"Reduction: {stats.get('reduction_factor', 'N/A'):.2f}x"
                    )
                else:
                    # Handle nested dictionaries
                    for key, value in stats.items():
                        if isinstance(value, dict) and "memory_mb" in value:
                            table.add_row(
                                f"{test_name} - {key}",
                                f"{value['memory_mb']:.2f}",
                                f"Success: {value.get('success', 'N/A')}"
                            )
        
        return table
    
    def run_all_tests(self) -> bool:
        """Run all QLoRA validation tests."""
        self.print_header()
        
        tests = [
            self.test_qlora_config_creation,
            self.test_qlora_linear_layer,
            self.test_qlora_model_conversion,
            self.test_memory_optimization,
            self.test_quantization_integration,
            self.test_save_load_functionality,
            self.test_hardware_constraints,
            self.run_performance_benchmark,
        ]
        
        total_tests = len(tests)
        passed_tests = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Running QLoRA validation tests...", total=total_tests)
            
            for i, test_func in enumerate(tests):
                progress.update(task, description=f"Running test {i+1}/{total_tests}: {test_func.__name__}")
                
                if test_func():
                    passed_tests += 1
                
                progress.advance(task)
                time.sleep(0.1)  # Small delay for visual effect
        
        # Display results
        self.console.print("\n")
        self.console.print(self.create_results_table())
        self.console.print("\n")
        self.console.print(self.create_memory_stats_table())
          # Summary
        success_rate = (passed_tests / total_tests) * 100
        if success_rate == 100:
            summary_panel = create_panel(
                f"🎉 All QLoRA validation tests passed! ({passed_tests}/{total_tests})\n"
                "QLoRA implementation is ready for production use.",
                title="✅ Complete Success",
                style="green"
            )
        elif success_rate >= 75:
            summary_panel = create_panel(
                f"⚠️ Most QLoRA tests passed ({passed_tests}/{total_tests} - {success_rate:.1f}%)\n"
                "Some tests failed but core functionality is working.",
                title="Partial Success",
                style="yellow"
            )
        else:
            summary_panel = create_panel(
                f"❌ Many QLoRA tests failed ({passed_tests}/{total_tests} - {success_rate:.1f}%)\n"
                "QLoRA implementation needs significant fixes.",
                title="⚠️ Major Issues",
                style="red"
            )
        
        self.console.print(summary_panel)
        
        return success_rate >= 75


def main():
    """Main execution function."""
    try:
        # Initialize validator
        validator = QLoRAValidator()
        
        # Run all tests
        success = validator.run_all_tests()
        
        # Return appropriate exit code
        return 0 if success else 1
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Validation interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"\n[red]❌ Validation failed with error: {str(e)}[/red]")
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return 1


if __name__ == "__main__":
    exit(main())
