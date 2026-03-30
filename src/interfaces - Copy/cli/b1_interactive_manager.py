#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #command_line #cuda #deployment #documentation #gpu_optimization #inference #memory_management #multimodal #performance #python #source_code #src/interfaces/cli\b1_interactive_manager.py #testing #training
**Category:** Interface Definitions
**Status:** Active
"""









# Duplicate header block removed during migration cleanup (content retained in version history)

import os
import sys
import time

import click
import torch

# Import rich for beautiful CLI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm, Prompt  # noqa: F401
    from rich.syntax import Syntax  # noqa: F401
    from rich.table import Table
    from rich.tree import Tree  # noqa: F401
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import ImpressionCore components
try:
    from ...core.utils.rich_enhancements import FallbackConsole, RichStatusManager  # noqa: F401
    from ...core.utils.rich_status_animation import StatusAnimation
    from ...deployment.production_manager import ProductionDeploymentManager  # noqa: F401

    # Updated path after migration: benchmarks moved under evaluation/benchmarks
    from ...evaluation.benchmarks.b1_performance_suite import B1PerformanceBenchmark
    from ...inference.pipelines.multimodal_pipeline import MultimodalPipeline  # noqa: F401
    from ...training.models.architectures.b1.b1_model import ImpressionCoreB1Model
    B1_COMPONENTS_AVAILABLE = True
except ImportError:
    B1_COMPONENTS_AVAILABLE = False


class B1InteractiveManager:
    """
    Interactive management interface for ImpressionCore-B1.

    Provides comprehensive CLI tools for B1 model management,
    optimization, benchmarking, and production deployment.
    """

    def __init__(self):
        """Initialize B1 Interactive Manager."""

        if RICH_AVAILABLE:
            self.console = Console()
            self.display = RichStatusManager() if B1_COMPONENTS_AVAILABLE else None
            self.status_animation = StatusAnimation() if B1_COMPONENTS_AVAILABLE else None
        else:
            self.console = None
            self.display = None
            self.status_animation = None

        self.current_model = None
        self.current_config = None
        self.benchmark_suite = None
        self.deployment_manager = None

        # B1 configuration options
        self.b1_configs = {
            "lightweight": {
                "input_dim": 512,
                "hidden_dim": 768,
                "num_layers": 4,
                "num_heads": 8,
                "chunk_size": 128,
                "enable_gradient_checkpointing": True,
                "description": "Lightweight config for minimal VRAM usage"
            },
            "balanced": {
                "input_dim": 768,
                "hidden_dim": 1024,
                "num_layers": 6,
                "num_heads": 8,
                "chunk_size": 256,
                "enable_gradient_checkpointing": True,
                "description": "Balanced config for GTX 1050 Ti"
            },
            "performance": {
                "input_dim": 1024,
                "hidden_dim": 1536,
                "num_layers": 8,
                "num_heads": 12,
                "chunk_size": 512,
                "enable_gradient_checkpointing": True,
                "description": "High-performance config for larger GPUs"
            }
        }

    def show_welcome(self) -> None:
        """Display welcome message and system information."""

        if self.console:
            # Beautiful welcome panel
            welcome_text = """
🚀 ImpressionCore-B1 Interactive Manager

Welcome to the comprehensive management interface for ImpressionCore-B1!
This tool provides advanced model management, optimization, and deployment capabilities.

Features Available:
• B1 Model Configuration & Deployment
• Real-time Performance Monitoring
• Hardware Compatibility Testing
• Production Deployment Management
• Advanced Optimization Tools
            """

            self.console.print(Panel(
                welcome_text.strip(),
                title="🧠 ImpressionCore-B1 Management Console",
                title_align="center",
                border_style="blue"
            ))

            # System information
            self._show_system_info()
        else:
            print("🚀 ImpressionCore-B1 Interactive Manager")
            print("=" * 50)

    def _show_system_info(self) -> None:
        """Display current system information."""

        # Detect hardware
        cpu_count = os.cpu_count()
        gpu_available = torch.cuda.is_available()

        if gpu_available:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
        else:
            gpu_name = "Not Available"
            gpu_memory = 0

        # Create system info table
        if self.console:
            table = Table(title="🖥️ System Information")
            table.add_column("Component", style="cyan")
            table.add_column("Details", style="white")

            table.add_row("CPU Cores", str(cpu_count))
            table.add_row("GPU", gpu_name)
            table.add_row("GPU Memory", f"{gpu_memory}GB" if gpu_memory > 0 else "N/A")
            table.add_row("CUDA Available", "✅ Yes" if gpu_available else "❌ No")
            table.add_row("B1 Components", "✅ Available" if B1_COMPONENTS_AVAILABLE else "❌ Missing")

            self.console.print(table)
        else:
            print("\n🖥️ System Information:")
            print(f"   CPU Cores: {cpu_count}")
            print(f"   GPU: {gpu_name}")
            print(f"   GPU Memory: {gpu_memory}GB" if gpu_memory > 0 else "   GPU Memory: N/A")

    def show_main_menu(self) -> str:
        """Display main menu and get user choice."""

        menu_options = {
            "1": "🏗️ B1 Model Configuration & Deployment",
            "2": "📊 Performance Benchmarking & Testing",
            "3": "🔧 Hardware Compatibility Analysis",
            "4": "🚀 Production Deployment Management",
            "5": "⚙️ Advanced B1 Optimization Tools",
            "6": "📈 Real-time Monitoring & Status",
            "7": "📚 B1 Documentation & Help",
            "8": "🔄 System Diagnostics & Repair",
            "q": "❌ Exit"
        }

        if self.console:
            self.console.print("\n🎯 Main Menu", style="bold blue")

            for key, desc in menu_options.items():
                self.console.print(f"  {key}. {desc}")

            choice = Prompt.ask("\n🔥 Choose an option",
                              choices=list(menu_options.keys()),
                              default="1")
        else:
            print("\n🎯 Main Menu:")
            for key, desc in menu_options.items():
                print(f"  {key}. {desc}")

            choice = input("\n🔥 Choose an option (1-8, q): ").strip().lower()

        return choice

    def handle_model_configuration(self) -> None:
        """Handle B1 model configuration and deployment."""

        if self.console:
            self.console.print("\n🏗️ B1 Model Configuration & Deployment", style="bold green")
        else:
            print("\n🏗️ B1 Model Configuration & Deployment")

        # Show available configurations
        if self.console:
            config_table = Table(title="📋 Available B1 Configurations")
            config_table.add_column("Name", style="cyan")
            config_table.add_column("Description", style="white")
            config_table.add_column("VRAM Est.", style="yellow")

            vram_estimates = {"lightweight": "~300MB", "balanced": "~500MB", "performance": "~800MB"}

            for name, config in self.b1_configs.items():
                config_table.add_row(
                    name.title(),
                    config["description"],
                    vram_estimates.get(name, "Unknown")
                )

            self.console.print(config_table)

            # Get user choice
            config_choice = Prompt.ask(
                "\n🔧 Choose a configuration",
                choices=list(self.b1_configs.keys()),
                default="balanced"
            )
        else:
            print("\n📋 Available B1 Configurations:")
            for name, config in self.b1_configs.items():
                print(f"  {name.title()}: {config['description']}")

            config_choice = input("\n🔧 Choose a configuration (lightweight/balanced/performance): ").strip().lower()
            if config_choice not in self.b1_configs:
                config_choice = "balanced"

        # Deploy selected configuration
        self._deploy_b1_model(config_choice)

    def _deploy_b1_model(self, config_name: str) -> None:
        """Deploy B1 model with specified configuration."""

        config = self.b1_configs[config_name]

        if self.console:
            self.console.print(f"\n🚀 Deploying B1 Model: {config_name.title()}", style="bold yellow")
        else:
            print(f"\n🚀 Deploying B1 Model: {config_name.title()}")

        if not B1_COMPONENTS_AVAILABLE:
            if self.console:
                self.console.print("❌ B1 components not available!", style="bold red")
            else:
                print("❌ B1 components not available!")
            return

        try:
            # Start deployment animation
            if self.status_animation:
                self.status_animation.start(f"Deploying B1 model with {config_name} configuration...")
            elif self.console:
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    task = progress.add_task("Deploying B1 model...", total=None)

                    # Create and deploy model
                    start_time = time.time()

                    model = ImpressionCoreB1Model(**{k: v for k, v in config.items() if k != "description"})

                    if torch.cuda.is_available():
                        model = model.cuda()

                    # Test model functionality
                    test_input = torch.randn(1, 128, config["input_dim"])
                    if torch.cuda.is_available():
                        test_input = test_input.cuda()

                    with torch.no_grad():
                        model(test_input)

                    deployment_time = time.time() - start_time

                    progress.update(task, completed=True)
            else:
                print("Deploying B1 model...")
                start_time = time.time()

                model = ImpressionCoreB1Model(**{k: v for k, v in config.items() if k != "description"})

                if torch.cuda.is_available():
                    model = model.cuda()

                # Test model functionality
                test_input = torch.randn(1, 128, config["input_dim"])
                if torch.cuda.is_available():
                    test_input = test_input.cuda()

                with torch.no_grad():
                    model(test_input)

                deployment_time = time.time() - start_time

            # Stop animation
            if self.status_animation:
                self.status_animation.stop()

            # Store current model
            self.current_model = model
            self.current_config = config_name

            # Calculate model stats
            param_count = sum(p.numel() for p in model.parameters())
            param_size_mb = sum(p.numel() * p.element_size() for p in model.parameters()) / (1024 * 1024)

            gpu_memory_mb = torch.cuda.memory_allocated() / (1024 * 1024) if torch.cuda.is_available() else 0

            # Show deployment results
            if self.console:
                success_panel = f"""
✅ B1 Model Deployment Successful!

Configuration: {config_name.title()}
Parameters: {param_count:,} ({param_size_mb:.1f}MB)
Deployment Time: {deployment_time:.2f}s
GPU Memory: {gpu_memory_mb:.1f}MB
                """

                self.console.print(Panel(
                    success_panel.strip(),
                    title="🎉 Deployment Complete",
                    title_align="center",
                    border_style="green"
                ))
            else:
                print("✅ B1 Model Deployment Successful!")
                print(f"   Configuration: {config_name.title()}")
                print(f"   Parameters: {param_count:,}")
                print(f"   Deployment Time: {deployment_time:.2f}s")
                print(f"   GPU Memory: {gpu_memory_mb:.1f}MB")

        except Exception as e:
            if self.status_animation:
                self.status_animation.stop()

            if self.console:
                self.console.print(f"❌ Deployment Failed: {e!s}", style="bold red")
            else:
                print(f"❌ Deployment Failed: {e!s}")

    def handle_benchmarking(self) -> None:
        """Handle performance benchmarking and testing."""

        if self.console:
            self.console.print("\n📊 Performance Benchmarking & Testing", style="bold green")
        else:
            print("\n📊 Performance Benchmarking & Testing")

        if not B1_COMPONENTS_AVAILABLE:
            if self.console:
                self.console.print("❌ B1 components not available for benchmarking!", style="bold red")
            else:
                print("❌ B1 components not available for benchmarking!")
            return

        benchmark_options = {
            "1": "🚀 Quick Performance Test",
            "2": "🔬 Comprehensive Benchmark Suite",
            "3": "💾 Memory Usage Analysis",
            "4": "⚡ Inference Speed Test",
            "5": "🔧 Hardware Compatibility Check"
        }

        if self.console:
            for key, desc in benchmark_options.items():
                self.console.print(f"  {key}. {desc}")

            choice = Prompt.ask("\n🎯 Choose benchmark type",
                              choices=list(benchmark_options.keys()),
                              default="1")
        else:
            print("\nBenchmark Options:")
            for key, desc in benchmark_options.items():
                print(f"  {key}. {desc}")

            choice = input("\n🎯 Choose benchmark type (1-5): ").strip()

        # Initialize benchmark suite
        if not self.benchmark_suite:
            self.benchmark_suite = B1PerformanceBenchmark()

        # Run selected benchmark
        if choice == "1":
            self._run_quick_performance_test()
        elif choice == "2":
            self._run_comprehensive_benchmark()
        elif choice == "3":
            self._run_memory_analysis()
        elif choice == "4":
            self._run_inference_speed_test()
        elif choice == "5":
            self._run_hardware_compatibility_check()

    def _run_quick_performance_test(self) -> None:
        """Run quick performance test."""

        if self.console:
            self.console.print("\n🚀 Running Quick Performance Test...", style="bold yellow")
        else:
            print("\n🚀 Running Quick Performance Test...")

        try:
            results = self.benchmark_suite.benchmark_b1_model_instantiation()

            if results["success"]:
                metrics = results["metrics"]

                if self.console:
                    results_text = f"""
✅ Quick Performance Test Results

Instantiation Time: {metrics.get('total_instantiation_time_s', 'N/A')}s
Memory Increase: {metrics.get('memory_increase_mb', 'N/A')}MB
Successful Configs: {metrics.get('successful_configs', 0)}/{metrics.get('configurations_tested', 0)}
                    """

                    self.console.print(Panel(
                        results_text.strip(),
                        title="📊 Performance Results",
                        border_style="green"
                    ))
                else:
                    print("✅ Quick Performance Test Complete!")
                    print(f"   Instantiation Time: {metrics.get('total_instantiation_time_s', 'N/A')}s")
                    print(f"   Memory Increase: {metrics.get('memory_increase_mb', 'N/A')}MB")
            else:
                if self.console:
                    self.console.print(f"❌ Performance test failed: {results.get('error', 'Unknown error')}", style="bold red")
                else:
                    print(f"❌ Performance test failed: {results.get('error', 'Unknown error')}")

        except Exception as e:
            if self.console:
                self.console.print(f"❌ Benchmark failed: {e!s}", style="bold red")
            else:
                print(f"❌ Benchmark failed: {e!s}")

    def _run_comprehensive_benchmark(self) -> None:
        """Run comprehensive benchmark suite."""

        if self.console:
            self.console.print("\n🔬 Running Comprehensive Benchmark Suite...", style="bold yellow")

            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Running comprehensive benchmarks...", total=None)

                results = self.benchmark_suite.run_comprehensive_benchmark()

                progress.update(task, completed=True)
        else:
            print("\n🔬 Running Comprehensive Benchmark Suite...")
            results = self.benchmark_suite.run_comprehensive_benchmark()

        # Show summary
        if self.console:
            successful_tests = sum(1 for r in results["results"].values() if r.get("success", False))
            total_tests = len(results["results"])

            summary_text = f"""
✅ Comprehensive Benchmark Complete

Duration: {results['duration_seconds']}s
Tests Passed: {successful_tests}/{total_tests}
Hardware Compatible: {torch.cuda.is_available()}
            """

            self.console.print(Panel(
                summary_text.strip(),
                title="🏆 Benchmark Summary",
                border_style="green"
            ))
        else:
            print("✅ Comprehensive Benchmark Complete!")
            print(f"   Duration: {results['duration_seconds']}s")

    def _run_hardware_compatibility_check(self) -> None:
        """Run hardware compatibility check."""

        if self.console:
            self.console.print("\n🔧 Running Hardware Compatibility Check...", style="bold yellow")
        else:
            print("\n🔧 Running Hardware Compatibility Check...")

        try:
            results = self.benchmark_suite.benchmark_hardware_compatibility()

            if results["success"]:
                metrics = results["metrics"]
                overall_compat = metrics.get("overall_compatibility", False)

                if self.console:
                    compat_status = "✅ Compatible" if overall_compat else "❌ Issues Found"

                    compat_text = f"""
Hardware Compatibility Check

Status: {compat_status}
GTX 1050 Ti Detected: {metrics.get('is_gtx_1050_ti', False)}
Tests Completed: {len(metrics.get('compatibility_tests', []))}
                    """

                    border_color = "green" if overall_compat else "red"

                    self.console.print(Panel(
                        compat_text.strip(),
                        title="🖥️ Compatibility Results",
                        border_style=border_color
                    ))
                else:
                    compat_status = "Compatible" if overall_compat else "Issues Found"
                    print("✅ Hardware Compatibility Check Complete!")
                    print(f"   Status: {compat_status}")
            else:
                if self.console:
                    self.console.print(f"❌ Compatibility check failed: {results.get('error', 'Unknown error')}", style="bold red")
                else:
                    print(f"❌ Compatibility check failed: {results.get('error', 'Unknown error')}")

        except Exception as e:
            if self.console:
                self.console.print(f"❌ Compatibility check failed: {e!s}", style="bold red")
            else:
                print(f"❌ Compatibility check failed: {e!s}")

    def show_status(self) -> None:
        """Show current B1 system status."""

        if self.console:
            status_table = Table(title="🔍 B1 System Status")
            status_table.add_column("Component", style="cyan")
            status_table.add_column("Status", style="white")

            # Model status
            if self.current_model:
                status_table.add_row("B1 Model", f"✅ Loaded ({self.current_config})")
                param_count = sum(p.numel() for p in self.current_model.parameters())
                status_table.add_row("Parameters", f"{param_count:,}")
            else:
                status_table.add_row("B1 Model", "❌ Not Loaded")

            # Hardware status
            status_table.add_row("CUDA", "✅ Available" if torch.cuda.is_available() else "❌ Not Available")
            status_table.add_row("Components", "✅ Available" if B1_COMPONENTS_AVAILABLE else "❌ Missing")

            if torch.cuda.is_available():
                gpu_memory = torch.cuda.memory_allocated() / (1024 * 1024)
                status_table.add_row("GPU Memory", f"{gpu_memory:.1f}MB")

            self.console.print(status_table)
        else:
            print("\n🔍 B1 System Status:")
            if self.current_model:
                print(f"   B1 Model: ✅ Loaded ({self.current_config})")
            else:
                print("   B1 Model: ❌ Not Loaded")
            print(f"   CUDA: {'✅ Available' if torch.cuda.is_available() else '❌ Not Available'}")

    def run_interactive_session(self) -> None:
        """Run the main interactive session."""

        self.show_welcome()

        while True:
            try:
                choice = self.show_main_menu()

                if choice == "q":
                    if self.console:
                        self.console.print("\n👋 Goodbye! Thank you for using ImpressionCore-B1!", style="bold blue")
                    else:
                        print("\n👋 Goodbye! Thank you for using ImpressionCore-B1!")
                    break
                elif choice == "1":
                    self.handle_model_configuration()
                elif choice == "2":
                    self.handle_benchmarking()
                elif choice == "3":
                    self._run_hardware_compatibility_check()
                elif choice == "4":
                    if self.console:
                        self.console.print("\n🚀 Production deployment coming soon!", style="bold yellow")
                    else:
                        print("\n🚀 Production deployment coming soon!")
                elif choice == "5":
                    if self.console:
                        self.console.print("\n⚙️ Advanced optimization tools coming soon!", style="bold yellow")
                    else:
                        print("\n⚙️ Advanced optimization tools coming soon!")
                elif choice == "6":
                    self.show_status()
                elif choice == "7":
                    if self.console:
                        self.console.print("\n📚 Documentation and help coming soon!", style="bold yellow")
                    else:
                        print("\n📚 Documentation and help coming soon!")
                elif choice == "8":
                    if self.console:
                        self.console.print("\n🔄 System diagnostics coming soon!", style="bold yellow")
                    else:
                        print("\n🔄 System diagnostics coming soon!")

                # Pause before returning to menu
                if self.console:
                    self.console.print("\nPress Enter to continue...", style="dim")
                    input()
                else:
                    input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                if self.console:
                    self.console.print("\n\n🛑 Interrupted by user. Exiting...", style="bold red")
                else:
                    print("\n\n🛑 Interrupted by user. Exiting...")
                break
            except Exception as e:
                if self.console:
                    self.console.print(f"\n❌ Unexpected error: {e!s}", style="bold red")
                else:
                    print(f"\n❌ Unexpected error: {e!s}")


@click.command()
@click.option("--config", default="balanced", help="Default B1 configuration to use")
@click.option("--batch", is_flag=True, help="Run in batch mode (non-interactive)")
def main(config: str, batch: bool):
    """
    ImpressionCore-B1 Interactive Management CLI.

    This tool provides comprehensive management capabilities for ImpressionCore-B1
    including model configuration, benchmarking, and deployment.
    """

    print("🚀 ImpressionCore-B1 Interactive Manager")
    print("=" * 50)

    if not B1_COMPONENTS_AVAILABLE:
        print("❌ ImpressionCore-B1 components not available!")
        print("   Please ensure B1 model and dependencies are properly installed.")
        sys.exit(1)

    try:
        manager = B1InteractiveManager()

        if batch:
            # Run quick validation in batch mode
            print("Running quick B1 validation...")
            manager._deploy_b1_model(config)
            manager._run_quick_performance_test()
            print("✅ B1 validation complete!")
        else:
            # Run interactive session
            manager.run_interactive_session()

    except Exception as e:
        print(f"❌ Manager failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
