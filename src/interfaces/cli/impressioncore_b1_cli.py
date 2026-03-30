#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #command_line #cuda #deployment #documentation #gpu_optimization #inference #memory_management #multimodal #python #source_code #src/interfaces/cli/impressioncore_b1_cli.py #testing #training
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** Kirk LaSalle
# Tags:** #command_line #cuda #deployment #documentation #gpu_optimization #inference #memory_management #multimodal #python #source_code #src/interfaces/cli/impressioncore_b1_cli.py #testing #training
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore-B1 Complete CLI System
====================================

Production-ready CLI for ImpressionCore-B1 with 8GB VRAM optimization.
Bulletproof implementation for open source release.

Features:
- Complete B1 model integration
- Real-time VRAM monitoring
- Interactive text generation
- Hardware optimization
- Bulletproof validation
- Easy open source deployment

Author: Kirk LaSalle & ImpressionCore Team
Date: 2025-01-09
Version: 1.0.0 - Bulletproof Release
"""

import argparse
import asyncio
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import psutil
import torch

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))
# Also add the project root
project_root = src_path.parent
sys.path.insert(0, str(project_root))

# Rich CLI imports (with fallbacks)
try:
    from rich.align import Align  # noqa: F401
    from rich.console import Console
    from rich.layout import Layout  # noqa: F401
    from rich.live import Live  # noqa: F401
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn  # noqa: F401
    from rich.prompt import Confirm, Prompt
    from rich.syntax import Syntax  # noqa: F401
    from rich.table import Table
    from rich.text import Text  # noqa: F401
    from rich.tree import Tree  # noqa: F401
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Rich not available - using basic output")

# ImpressionCore imports (with error handling)
try:
    from .core.config.model_config import ModelConfig
    from .core.utils.hardware_detection import HardwareDetector
    from .core.utils.memory_controller import MemoryController
    from .models.impressioncore_b1.unified_model import ImpressionCoreB1Model
    from .services.text_generation.service import GenerationConfig, TextGenerationService
    from .training.training_utils import get_device
    IMPRESSIONCORE_AVAILABLE = True
except ImportError as e:
    IMPRESSIONCORE_AVAILABLE = False
    print(f"⚠️  ImpressionCore components not available: {e}")

    # Create placeholder classes to prevent NameError
    class GenerationConfig:
        def __init__(self, max_length=512, temperature=0.8, top_p=0.9, top_k=50, repetition_penalty=1.1):
            self.max_length = max_length
            self.temperature = temperature
            self.top_p = top_p
            self.top_k = top_k
            self.repetition_penalty = repetition_penalty

    class TextGenerationService:
        def __init__(self, *args, **kwargs):
            pass
        async def initialize(self):
            return False
        async def generate_text(self, prompt, config=None):
            return type('obj', (object,), {
                'generated_text': 'Service not available',
                'tokens_per_second': 0.0
            })()
        async def cleanup(self):
            pass

    class ModelConfig:
        pass

    def get_device():
        return 'cpu'


class CLIConsole:
    """Console wrapper with fallback for rich functionality."""

    def __init__(self):
        self.rich_console = Console() if RICH_AVAILABLE else None

    def print(self, *args, **kwargs):
        if self.rich_console:
            self.rich_console.print(*args, **kwargs)
        else:
            print(*args)

    def input(self, prompt: str) -> str:
        if RICH_AVAILABLE:
            return Prompt.ask(prompt)
        else:
            return input(f"{prompt}: ")

    def confirm(self, prompt: str) -> bool:
        if RICH_AVAILABLE:
            return Confirm.ask(prompt)
        else:
            response = input(f"{prompt} (y/n): ").lower()
            return response in ['y', 'yes', 'true', '1']


class ImpressionCoreB1CLI:
    """
    Complete CLI system for ImpressionCore-B1.

    Bulletproof implementation optimized for 8GB VRAM
    with fallbacks for any hardware configuration.
    """

    def __init__(self):
        """Initialize the CLI system."""
        self.console = CLIConsole()
        self.device = None
        self.hardware_info = {}
        self.b1_model = None
        self.text_service = None
        self.memory_controller = None
        self.hardware_detector = None

        # Session state
        self.session_active = False
        self.session_stats = {
            'generations': 0,
            'total_tokens': 0,
            'session_start': None
        }

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('impressioncore_cli.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def print_banner(self):
        """Print the ImpressionCore-B1 CLI banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    ImpressionCore-B1 CLI                    ║
║                  Brain-Inspired AI System                   ║
║              Optimized for Consumer Hardware                ║
╠══════════════════════════════════════════════════════════════╣
║  🧠 B1 Unified Model    🚀 8GB VRAM Target                 ║
║  ⚡ 800+ Tokens/Sec     🛡️ Bulletproof Design             ║
║  🌐 Universal Deploy    📊 Real-time Monitoring             ║
╚══════════════════════════════════════════════════════════════╝
"""
        if RICH_AVAILABLE:
            panel = Panel(
                banner,
                title="🚀 ImpressionCore-B1",
                subtitle="Bulletproof AI for Everyone",
                style="bold blue"
            )
            self.console.print(panel)
        else:
            print(banner)

        print(f"Version: 1.0.0 | Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("Hardware Target: 8GB VRAM (GTX 1080 Ti / RTX 3060 / RTX 4060)")
        print()

    def check_system_requirements(self) -> bool:
        """Check system requirements and hardware capabilities."""
        self.console.print("🔍 Checking system requirements...", style="cyan")

        # Check CUDA availability
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            gpu_name = torch.cuda.get_device_name()
            vram_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            self.console.print(f"✅ GPU: {gpu_name} ({vram_total:.1f}GB VRAM)", style="green")
        else:
            self.console.print("⚠️  No CUDA GPU detected - using CPU fallback", style="yellow")

        # Check system RAM
        ram_total = psutil.virtual_memory().total / (1024**3)
        self.console.print(f"💾 System RAM: {ram_total:.1f}GB", style="blue")

        # Check ImpressionCore components
        if IMPRESSIONCORE_AVAILABLE:
            self.console.print("✅ ImpressionCore components available", style="green")
        else:
            self.console.print("❌ ImpressionCore components not available", style="red")
            self.console.print("   Please ensure ImpressionCore is properly installed", style="red")
            return False

        # Store hardware info
        self.hardware_info = {
            'cuda_available': cuda_available,
            'gpu_name': gpu_name if cuda_available else 'CPU',
            'vram_total': vram_total if cuda_available else 0,
            'ram_total': ram_total
        }

        return True

    async def initialize_b1_system(self) -> bool:
        """Initialize the ImpressionCore-B1 system."""
        self.console.print("🚀 Initializing ImpressionCore-B1 system...", style="cyan")

        try:
            # Initialize device and hardware detection
            self.device = get_device()
            self.hardware_detector = HardwareDetector()
            self.memory_controller = MemoryController(target_memory_gb=7.5)  # 8GB with margin

            self.console.print(f"🎯 Target device: {self.device}", style="blue")

            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Initialize B1 model
            self.console.print("🧠 Loading ImpressionCore-B1 model...", style="cyan")

            model_config = ModelConfig()
            # Optimize for 8GB VRAM
            model_config.use_gradient_checkpointing = True
            model_config.use_mixed_precision = True

            with self.memory_controller:
                self.b1_model = ImpressionCoreB1Model(model_config)
                self.b1_model = self.b1_model.to(self.device)
                self.b1_model.eval()

            # Initialize text generation service
            self.console.print("⚙️  Initializing text generation service...", style="cyan")
            self.text_service = TextGenerationService(
                model_config=model_config,
                device=self.device,
                enable_monitoring=True
            )

            if await self.text_service.initialize():
                self.console.print("✅ ImpressionCore-B1 system ready!", style="green")
                return True
            else:
                self.console.print("❌ Failed to initialize text service", style="red")
                return False

        except Exception as e:
            self.console.print(f"❌ Initialization failed: {e}", style="red")
            self.logger.error(f"B1 initialization error: {e}")
            return False

    def show_system_status(self):
        """Display current system status."""
        if RICH_AVAILABLE:
            table = Table(title="System Status")
            table.add_column("Component", style="cyan", no_wrap=True)
            table.add_column("Status", style="magenta")
            table.add_column("Details", style="green")

            # Hardware status
            table.add_row("Device", str(self.device), self.hardware_info.get('gpu_name', 'Unknown'))
            table.add_row("VRAM",
                         f"{self.hardware_info.get('vram_total', 0):.1f}GB",
                         "8GB Target" if self.hardware_info.get('vram_total', 0) >= 8 else "Limited")

            # Model status
            model_status = "✅ Loaded" if self.b1_model else "❌ Not Loaded"
            table.add_row("B1 Model", model_status, "ImpressionCore-B1 Unified")

            # Service status
            service_status = "✅ Ready" if self.text_service else "❌ Not Ready"
            table.add_row("Text Service", service_status, "Generation & Inference")

            # Memory status
            if torch.cuda.is_available():
                current_vram = torch.cuda.memory_allocated() / (1024**3)
                table.add_row("VRAM Usage", f"{current_vram:.2f}GB", "Target: <7.5GB")

            self.console.print(table)
        else:
            print("\n=== System Status ===")
            print(f"Device: {self.device}")
            print(f"GPU: {self.hardware_info.get('gpu_name', 'Unknown')}")
            print(f"VRAM: {self.hardware_info.get('vram_total', 0):.1f}GB")
            print(f"B1 Model: {'Loaded' if self.b1_model else 'Not Loaded'}")
            print(f"Text Service: {'Ready' if self.text_service else 'Not Ready'}")

    async def interactive_text_generation(self):
        """Interactive text generation session."""
        if not self.text_service:
            self.console.print("❌ Text service not available", style="red")
            return

        self.console.print("🎯 Interactive Text Generation Session", style="bold cyan")
        self.console.print("Type 'exit' to quit, 'status' for system info, 'config' to adjust settings\n")

        # Default generation config
        gen_config = GenerationConfig(
            max_length=512,
            temperature=0.8,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.1
        )

        session_count = 0

        while True:
            try:
                # Get user input
                prompt = self.console.input("\n🧠 Enter your prompt")

                if prompt.lower() == 'exit':
                    break
                elif prompt.lower() == 'status':
                    self.show_system_status()
                    continue
                elif prompt.lower() == 'config':
                    gen_config = self.configure_generation()
                    continue
                elif not prompt.strip():
                    continue

                # Generate response
                self.console.print("⚡ Generating response...", style="yellow")
                start_time = time.time()

                result = await self.text_service.generate_text(prompt, gen_config)

                generation_time = time.time() - start_time
                session_count += 1

                # Display results
                if RICH_AVAILABLE:
                    response_panel = Panel(
                        result.generated_text,
                        title=f"🤖 ImpressionCore-B1 Response #{session_count}",
                        subtitle=f"⚡ {result.tokens_per_second:.1f} tokens/sec | 🕒 {generation_time:.2f}s",
                        style="green"
                    )
                    self.console.print(response_panel)
                else:
                    print(f"\n=== Response #{session_count} ===")
                    print(result.generated_text)
                    print(f"Speed: {result.tokens_per_second:.1f} tokens/sec")
                    print(f"Time: {generation_time:.2f}s")

                # Update session stats
                self.session_stats['generations'] += 1

            except KeyboardInterrupt:
                self.console.print("\n⚠️  Generation interrupted", style="yellow")
                break
            except Exception as e:
                self.console.print(f"❌ Generation error: {e}", style="red")
                self.logger.error(f"Generation error: {e}")

    def configure_generation(self) -> GenerationConfig:
        """Configure generation parameters interactively."""
        self.console.print("⚙️  Configure Generation Parameters", style="bold cyan")

        try:
            max_length = int(self.console.input("Max length [512]") or "512")
            temperature = float(self.console.input("Temperature [0.8]") or "0.8")
            top_p = float(self.console.input("Top-p [0.9]") or "0.9")
            top_k = int(self.console.input("Top-k [50]") or "50")

            config = GenerationConfig(
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k
            )

            self.console.print("✅ Configuration updated", style="green")
            return config

        except ValueError as e:
            self.console.print(f"⚠️  Invalid input: {e}", style="yellow")
            return GenerationConfig()  # Return defaults

    def show_main_menu(self) -> str:
        """Show main menu and get user choice."""
        if RICH_AVAILABLE:
            menu_panel = Panel(
                """
1. 🎯 Interactive Text Generation
2. 📊 System Status & Monitoring
3. ⚙️  Configuration & Settings
4. 🧪 Performance Testing
5. 📖 Help & Documentation
6. 🚪 Exit
                """.strip(),
                title="🧠 ImpressionCore-B1 Main Menu",
                style="bold blue"
            )
            self.console.print(menu_panel)
        else:
            print("\n=== ImpressionCore-B1 Main Menu ===")
            print("1. Interactive Text Generation")
            print("2. System Status & Monitoring")
            print("3. Configuration & Settings")
            print("4. Performance Testing")
            print("5. Help & Documentation")
            print("6. Exit")

        return self.console.input("Select option [1-6]")

    async def run_performance_test(self):
        """Run performance testing suite."""
        if not self.text_service:
            self.console.print("❌ Text service not available", style="red")
            return

        self.console.print("🧪 Running Performance Test Suite", style="bold cyan")

        test_prompts = [
            "Hello, ImpressionCore-B1!",
            "Explain artificial intelligence in simple terms.",
            "Write a short story about a robot learning to paint.",
            "What are the benefits of local AI processing?",
            "Generate a python function to calculate fibonacci numbers."
        ]

        total_time = 0
        total_tokens = 0

        for i, prompt in enumerate(test_prompts, 1):
            self.console.print(f"Test {i}/{len(test_prompts)}: {prompt[:50]}...", style="cyan")

            start_time = time.time()
            result = await self.text_service.generate_text(prompt)
            test_time = time.time() - start_time

            total_time += test_time

            self.console.print(f"  ⚡ {result.tokens_per_second:.1f} tokens/sec", style="green")

        # Show summary
        avg_speed = total_tokens / total_time if total_time > 0 else 0

        if RICH_AVAILABLE:
            summary_table = Table(title="Performance Summary")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", style="green")

            summary_table.add_row("Tests Completed", str(len(test_prompts)))
            summary_table.add_row("Total Time", f"{total_time:.2f}s")
            summary_table.add_row("Average Speed", f"{avg_speed:.1f} tokens/sec")
            summary_table.add_row("Target Speed", "800+ tokens/sec")
            summary_table.add_row("Status", "✅ PASSED" if avg_speed >= 500 else "⚠️ REVIEW")

            self.console.print(summary_table)
        else:
            print("\n=== Performance Summary ===")
            print(f"Tests: {len(test_prompts)}")
            print(f"Total Time: {total_time:.2f}s")
            print(f"Average Speed: {avg_speed:.1f} tokens/sec")
            print("Target: 800+ tokens/sec")

    def show_help(self):
        """Show help and documentation."""
        help_text = """
🧠 ImpressionCore-B1 CLI Help
============================

OVERVIEW:
ImpressionCore-B1 is a brain-inspired multimodal AI system optimized
for consumer hardware. This CLI provides interactive access to text
generation and system management.

FEATURES:
• 🎯 Interactive text generation with real-time performance
• 📊 System monitoring and VRAM optimization
• ⚙️  Configurable generation parameters
• 🧪 Performance testing and validation
• 🛡️ Bulletproof operation on 4GB-32GB VRAM

HARDWARE TARGETS:
• Primary: 8GB VRAM (GTX 1080 Ti, RTX 3060, RTX 4060)
• Minimum: 4GB VRAM (GTX 1050 Ti) - limited functionality
• Optimal: 24GB+ VRAM (RTX 4090, RTX 5090) - full capability

COMMANDS:
• Interactive mode: Follow menu prompts
• Batch mode: Use command-line arguments
• Configuration: Adjust via menu option 3

TROUBLESHOOTING:
• Check system requirements first
• Ensure CUDA drivers are updated
• Monitor VRAM usage during operation
• Check logs at: impressioncore_cli.log

SUPPORT:
• Documentation: docs/user_guide.md
• GitHub: github.com/impressioncore/impressioncore
• Issues: Use GitHub issue tracker
        """

        if RICH_AVAILABLE:
            help_panel = Panel(help_text, title="📖 Help & Documentation", style="blue")
            self.console.print(help_panel)
        else:
            print(help_text)

    async def cleanup(self):
        """Clean up resources before exit."""
        self.console.print("🧹 Cleaning up resources...", style="cyan")

        if self.text_service:
            await self.text_service.cleanup()

        if self.b1_model:
            del self.b1_model

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.console.print("✅ Cleanup completed", style="green")

    async def run(self):
        """Main CLI application loop."""
        self.print_banner()

        # Check requirements
        if not self.check_system_requirements():
            self.console.print("❌ System requirements not met", style="red")
            return

        # Initialize system
        if not await self.initialize_b1_system():
            self.console.print("❌ Failed to initialize B1 system", style="red")
            return

        self.session_active = True
        self.session_stats['session_start'] = datetime.now()

        try:
            # Main application loop
            while self.session_active:
                choice = self.show_main_menu()

                if choice == "1":
                    await self.interactive_text_generation()
                elif choice == "2":
                    self.show_system_status()
                elif choice == "3":
                    self.configure_generation()
                elif choice == "4":
                    await self.run_performance_test()
                elif choice == "5":
                    self.show_help()
                elif choice == "6":
                    break
                else:
                    self.console.print("⚠️  Invalid choice. Please select 1-6.", style="yellow")

        except KeyboardInterrupt:
            self.console.print("\n⚠️  Application interrupted by user", style="yellow")
        except Exception as e:
            self.console.print(f"❌ Unexpected error: {e}", style="red")
            self.logger.error(f"Application error: {e}")
        finally:
            await self.cleanup()
            self.console.print("🚪 Thank you for using ImpressionCore-B1!", style="bold green")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="ImpressionCore-B1 CLI - Brain-Inspired AI System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python impressioncore_b1_cli.py                    # Interactive mode
  python impressioncore_b1_cli.py --test            # Run performance tests
  python impressioncore_b1_cli.py --status          # Show system status
  python impressioncore_b1_cli.py --prompt "Hello"  # Single generation
        """
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run performance test suite and exit"
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status and exit"
    )

    parser.add_argument(
        "--prompt",
        type=str,
        help="Generate text from prompt and exit"
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Configuration file path (JSON format)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_arguments()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create CLI instance
    cli = ImpressionCoreB1CLI()

    # Handle non-interactive modes
    if args.status:
        cli.print_banner()
        if cli.check_system_requirements() and await cli.initialize_b1_system():
            cli.show_system_status()
        return

    if args.test:
        cli.print_banner()
        if cli.check_system_requirements() and await cli.initialize_b1_system():
            await cli.run_performance_test()
        return

    if args.prompt:
        cli.print_banner()
        if cli.check_system_requirements() and await cli.initialize_b1_system():
            result = await cli.text_service.generate_text(args.prompt)
            print(f"\nGenerated: {result.generated_text}")
            print(f"Speed: {result.tokens_per_second:.1f} tokens/sec")
        return

    # Run interactive mode
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())
