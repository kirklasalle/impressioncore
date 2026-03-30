"""
ImpressionCore Text Generation Service Demo
==========================================

Demonstration and testing script for the text generation service.
Shows CUDA optimization, memory management, and real-time monitoring.

Usage:
    python -m src.services.text_generation.demo

Author: ImpressionCore Team
Date: 2025-01-09
"""

import asyncio
import time
import logging
from typing import List

from src.services.text_generation import (
    create_text_generation_service,
    GenerationConfig,
    text_generation_service
)
from src.core.utils.rich_enhancements import RichUI


class TextGenerationDemo:
    """Demo class for text generation service."""
    
    def __init__(self):
        self.rich_ui = RichUI()
        self.logger = logging.getLogger(__name__)
    
    async def run_basic_demo(self):
        """Run basic text generation demo."""
        self.rich_ui.print_header("ImpressionCore Text Generation Demo")
        
        async with text_generation_service() as service:
            # Initialize service
            self.rich_ui.print_status("Initializing text generation service...", "info")
            if not await service.initialize():
                self.rich_ui.print_status("❌ Failed to initialize service", "error")
                return
            
            # Demo prompts
            prompts = [
                "The future of AI is",
                "In a world where privacy matters,",
                "ImpressionCore enables developers to",
                "Local AI processing provides",
                "The GTX 1050 Ti proves that"
            ]
            
            # Test different configurations
            configs = [
                GenerationConfig(max_length=100, temperature=0.7, top_p=0.9),
                GenerationConfig(max_length=150, temperature=1.0, top_k=50),
                GenerationConfig(max_length=200, temperature=0.5, repetition_penalty=1.2)
            ]
            
            results = []
            
            for i, prompt in enumerate(prompts):
                config = configs[i % len(configs)]
                
                self.rich_ui.print_status(f"Generating text for prompt {i+1}/{len(prompts)}", "info")
                self.rich_ui.print_info(f"Prompt: '{prompt}'")
                
                try:
                    start_time = time.time()
                    result = await service.generate_text(prompt, config)
                    
                    # Display results
                    self.rich_ui.print_success(f"✅ Generated in {result.generation_time:.2f}s")
                    self.rich_ui.print_info(f"Generated: {result.generated_text}")
                    self.rich_ui.print_info(f"Speed: {result.tokens_per_second:.2f} tokens/sec")
                    self.rich_ui.print_info(f"Memory: {result.memory_used:.2f} GB VRAM")
                    
                    results.append(result)
                    
                    # Brief pause between generations
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.rich_ui.print_error(f"❌ Generation failed: {e}")
            
            # Display summary statistics
            await self._display_summary(service, results)
    
    async def run_performance_benchmark(self):
        """Run performance benchmark tests."""
        self.rich_ui.print_header("Performance Benchmark")
        
        async with text_generation_service() as service:
            if not await service.initialize():
                return
            
            # Benchmark parameters
            benchmark_prompts = ["Performance test prompt"] * 10
            config = GenerationConfig(max_length=100, temperature=0.8)
            
            self.rich_ui.print_status("Running performance benchmark...", "info")
            
            start_time = time.time()
            results = []
            
            for i, prompt in enumerate(benchmark_prompts):
                self.rich_ui.print_status(f"Benchmark {i+1}/{len(benchmark_prompts)}", "info")
                
                try:
                    result = await service.generate_text(prompt, config)
                    results.append(result)
                    
                except Exception as e:
                    self.rich_ui.print_error(f"Benchmark {i+1} failed: {e}")
            
            total_time = time.time() - start_time
            
            # Calculate benchmark statistics
            if results:
                avg_time = sum(r.generation_time for r in results) / len(results)
                avg_speed = sum(r.tokens_per_second for r in results) / len(results)
                max_memory = max(r.memory_used for r in results)
                
                self.rich_ui.print_success("📊 Benchmark Results:")
                self.rich_ui.print_info(f"Total runs: {len(results)}")
                self.rich_ui.print_info(f"Total time: {total_time:.2f}s")
                self.rich_ui.print_info(f"Average generation time: {avg_time:.2f}s")
                self.rich_ui.print_info(f"Average speed: {avg_speed:.2f} tokens/sec")
                self.rich_ui.print_info(f"Peak memory usage: {max_memory:.2f} GB")
                self.rich_ui.print_info(f"Throughput: {len(results)/total_time:.2f} generations/sec")
    
    async def run_memory_stress_test(self):
        """Run memory stress test to validate VRAM management."""
        self.rich_ui.print_header("Memory Stress Test")
        
        async with text_generation_service() as service:
            if not await service.initialize():
                return
            
            # Get initial memory stats
            initial_stats = service.get_stats()
            initial_memory = initial_stats['memory_info'].get('cuda_memory_allocated_gb', 0)
            
            self.rich_ui.print_info(f"Initial VRAM usage: {initial_memory:.2f} GB")
            
            # Stress test with multiple concurrent generations
            stress_prompts = [
                "This is a memory stress test prompt for concurrent generation testing."
            ] * 20
            
            config = GenerationConfig(max_length=200, temperature=0.8)
            
            self.rich_ui.print_status("Running memory stress test...", "info")
            
            # Sequential generations to test memory stability
            peak_memory = 0
            for i, prompt in enumerate(stress_prompts):
                try:
                    result = await service.generate_text(prompt, config)
                    peak_memory = max(peak_memory, result.memory_used)
                    
                    if i % 5 == 0:
                        self.rich_ui.print_status(f"Stress test {i+1}/{len(stress_prompts)}", "info")
                        self.rich_ui.print_info(f"Current memory: {result.memory_used:.2f} GB")
                    
                except Exception as e:
                    self.rich_ui.print_error(f"Stress test {i+1} failed: {e}")
                    break
            
            # Final memory stats
            final_stats = service.get_stats()
            final_memory = final_stats['memory_info'].get('cuda_memory_allocated_gb', 0)
            
            self.rich_ui.print_success("🧠 Memory Stress Test Results:")
            self.rich_ui.print_info(f"Initial memory: {initial_memory:.2f} GB")
            self.rich_ui.print_info(f"Peak memory: {peak_memory:.2f} GB")
            self.rich_ui.print_info(f"Final memory: {final_memory:.2f} GB")
            self.rich_ui.print_info(f"Memory increase: {final_memory - initial_memory:.2f} GB")
            
            # Validate GTX 1050 Ti compatibility (4GB limit)
            if peak_memory < 3.5:
                self.rich_ui.print_success("✅ GTX 1050 Ti compatible (< 3.5GB)")
            else:
                self.rich_ui.print_warning(f"⚠️ High memory usage: {peak_memory:.2f} GB")
    
    async def _display_summary(self, service, results: List):
        """Display summary statistics."""
        if not results:
            return
        
        self.rich_ui.print_header("Generation Summary")
        
        # Service statistics
        stats = service.get_stats()
        
        self.rich_ui.print_info("📊 Service Statistics:")
        self.rich_ui.print_info(f"Total generations: {stats['service_stats']['total_generations']}")
        self.rich_ui.print_info(f"Total tokens: {stats['service_stats']['total_tokens']}")
        self.rich_ui.print_info(f"Average speed: {stats['service_stats']['average_speed']:.2f} tokens/sec")
        
        # Device information
        self.rich_ui.print_info("\n🖥️ Device Information:")
        device_info = stats['device_info']
        self.rich_ui.print_info(f"Device: {device_info['device']}")
        self.rich_ui.print_info(f"CUDA available: {device_info['cuda_available']}")
        if device_info['gpu_name']:
            self.rich_ui.print_info(f"GPU: {device_info['gpu_name']}")
        
        # Memory information
        memory_info = stats['memory_info']
        if 'cuda_memory_allocated_gb' in memory_info:
            self.rich_ui.print_info(f"VRAM allocated: {memory_info['cuda_memory_allocated_gb']:.2f} GB")
            self.rich_ui.print_info(f"VRAM free: {memory_info['cuda_memory_free_gb']:.2f} GB")


async def main():
    """Main demo function."""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    demo = TextGenerationDemo()
    
    try:
        # Run all demos
        await demo.run_basic_demo()
        await asyncio.sleep(2)
        
        await demo.run_performance_benchmark()
        await asyncio.sleep(2)
        
        await demo.run_memory_stress_test()
        
    except KeyboardInterrupt:
        demo.rich_ui.print_status("Demo interrupted by user", "warning")
    except Exception as e:
        demo.rich_ui.print_error(f"Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
