#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #memory_management #python #source_code #src/tests/test_b3_streaming_system.py #testing #tokenization #training #transformer
**Category:** Testing Framework
**Status:** Active

NOTE: Marked as slow; skipped by default unless IC_SKIP_SLOW=0.
"""
import os as _os

import pytest as _pytest

_pytestmark = _pytest.mark.slow
if _os.getenv("IC_SKIP_SLOW", "1") == "1":  # default skip to keep CI fast
    _pytest.skip("Skipping slow streaming system tests (unset IC_SKIP_SLOW or set to 0 to run)", allow_module_level=True)









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #cuda #memory_management #python #source_code #src\\tests\\test_b3_streaming_system.py #testing #tokenization #training #transformer
# Category:** Testing Framework
# Status:** Active

"""
ImpressionCore B3 Streaming System Test Suite
============================================
🧪 Comprehensive validation for 323K+ F: drive embeddings
🎯 GTX 1050 Ti optimization verification
⚡ Memory efficiency testing
"""

import json
import pickle
import time
from datetime import datetime
from pathlib import Path

import psutil
import torch
from rich.console import Console
from rich.progress import track
from rich.table import Table
from transformers import AutoTokenizer

from src.dev_tools.data_generation.b3_streaming_dataset import (
    StreamingConfig,
    StreamingDataset,
)

console = Console()

class StreamingSystemTester:
    """Comprehensive testing suite for streaming system"""

    def __init__(self):
        self.console = Console()
        self.results = {}

    def test_file_discovery(self, root_path: str = "F:/") -> dict:
        """Test file discovery capabilities"""
        console.print("[cyan]🔍 Testing file discovery...[/cyan]")

        root = Path(root_path)
        if not root.exists():
            return {"error": f"Root path {root_path} does not exist"}

        # Count .npy files
        npy_files = list(root.rglob("*.npy"))

        # Analyze file sizes
        total_size = 0
        size_distribution = {}

        for file_path in track(npy_files[:1000], description="Analyzing files"):
            try:
                size = file_path.stat().st_size
                total_size += size

                # Categorize by size
                if size < 1024:
                    category = "<1KB"
                elif size < 10240:
                    category = "1-10KB"
                elif size < 102400:
                    category = "10-100KB"
                elif size < 1024000:
                    category = "100KB-1MB"
                else:
                    category = ">1MB"

                size_distribution[category] = size_distribution.get(category, 0) + 1

            except Exception:
                continue

        result = {
            "total_files": len(npy_files),
            "total_size_gb": total_size / (1024**3),
            "size_distribution": size_distribution,
            "sample_files": [str(f) for f in npy_files[:5]]
        }

        console.print(f"[green]✅ Found {len(npy_files)} .npy files[/green]")
        return result

    def test_memory_efficiency(self) -> dict:
        """Test memory usage patterns"""
        console.print("[cyan]🧠 Testing memory efficiency...[/cyan]")

        # Get current memory usage
        memory_info = psutil.virtual_memory()
        vram_info = None

        if torch.cuda.is_available():
            vram_allocated = torch.cuda.memory_allocated() / 1024**3
            vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            vram_info = {
                "allocated_gb": vram_allocated,
                "total_gb": vram_total,
                "utilization": vram_allocated / vram_total
            }

        result = {
            "ram_total_gb": memory_info.total / 1024**3,
            "ram_available_gb": memory_info.available / 1024**3,
            "ram_utilization": memory_info.percent,
            "vram": vram_info
        }

        return result

    def test_streaming_dataset(self, test_path: str = "F:/") -> dict:
        """Test streaming dataset functionality"""
        console.print("[cyan]📊 Testing streaming dataset...[/cyan]")

        # Create test configuration
        config = StreamingConfig(
            root_path=test_path,
            max_seq_length=512,
            embedding_dim=768,
            num_workers=2,
            batch_size=4,
            memory_limit_gb=3.5
        )

        tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Test dataset
        dataset = StreamingDataset(config, tokenizer)

        # Collect samples
        samples = []
        start_time = time.time()

        for i, sample in enumerate(dataset):
            if i >= 100:  # Test with 100 samples
                break
            samples.append(sample)

        elapsed = time.time() - start_time

        result = {
            "samples_collected": len(samples),
            "processing_time": elapsed,
            "samples_per_second": len(samples) / elapsed,
            "sample_shapes": {
                "input_ids": samples[0]['input_ids'].shape if samples else None,
                "embeddings": samples[0]['embeddings'].shape if samples else None
            }
        }

        return result

    def test_gtx_1050_optimization(self) -> dict:
        """Test GTX 1050 Ti specific optimizations"""
        console.print("[cyan]🎯 Testing GTX 1050 Ti optimization...[/cyan]")

        if not torch.cuda.is_available():
            return {"error": "CUDA not available"}

        device = torch.device("cuda")

        # Test memory allocation
        try:
            # Test with different batch sizes
            batch_sizes = [1, 2, 4, 8, 16]
            results = {}

            for batch_size in batch_sizes:
                try:
                    # Create dummy tensors
                    input_ids = torch.randint(0, 1000, (batch_size, 512)).to(device)
                    embeddings = torch.randn(batch_size, 512, 768).to(device)

                    # Check memory usage
                    allocated = torch.cuda.memory_allocated() / 1024**3

                    results[batch_size] = {
                        "memory_gb": allocated,
                        "status": "success"
                    }

                    # Clean up
                    del input_ids, embeddings
                    torch.cuda.empty_cache()

                except RuntimeError as e:
                    results[batch_size] = {
                        "status": "failed",
                        "error": str(e)
                    }
                    break

            return {
                "device_name": torch.cuda.get_device_name(0),
                "memory_total_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3,
                "batch_size_tests": results,
                "optimal_batch_size": max([k for k, v in results.items() if v['status'] == 'success'])
            }

        except Exception as e:
            return {"error": str(e)}

    def test_checkpoint_system(self) -> dict:
        """Test checkpoint and resume functionality"""
        console.print("[cyan]💾 Testing checkpoint system...[/cyan]")

        checkpoint_path = Path("checkpoints/streaming_progress.pkl")

        # Test checkpoint creation
        test_data = {
            'processed_files': {'file1.npy', 'file2.npy'},
            'total_processed': 100,
            'timestamp': datetime.now().isoformat()
        }

        try:
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            with open(checkpoint_path, 'wb') as f:
                pickle.dump(test_data, f)

            # Test checkpoint loading
            with open(checkpoint_path, 'rb') as f:
                loaded_data = pickle.load(f)

            return {
                "checkpoint_created": True,
                "checkpoint_loaded": True,
                "data_integrity": loaded_data == test_data
            }

        except Exception as e:
            return {"error": str(e)}


def test_streaming_memory_efficiency_smoke():
    """Smoke test for streaming system when slow tests are enabled."""
    tester = StreamingSystemTester()
    result = tester.test_memory_efficiency()
    assert isinstance(result, dict)
    assert "ram_total_gb" in result
    assert "ram_available_gb" in result

    def run_full_test(self) -> dict:
        """Run comprehensive test suite"""
        console.print("[bold cyan]🧪 Running B3 Streaming System Tests[/bold cyan]")

        tests = {
            "file_discovery": self.test_file_discovery,
            "memory_efficiency": self.test_memory_efficiency,
            "streaming_dataset": self.test_streaming_dataset,
            "gtx_optimization": self.test_gtx_1050_optimization,
            "checkpoint_system": self.test_checkpoint_system
        }

        results = {}

        for test_name, test_func in tests.items():
            try:
                results[test_name] = test_func()
            except Exception as e:
                results[test_name] = {"error": str(e)}

        # Display results
        self._display_results(results)

        return results

    def _display_results(self, results: dict):
        """Display test results in a beautiful table"""
        table = Table(title="B3 Streaming System Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="white")

        for test_name, result in results.items():
            if "error" in result:
                status = "❌ Failed"
                details = result["error"]
            else:
                status = "✅ Passed"
                if test_name == "file_discovery":
                    details = f"{result.get('total_files', 0)} files, {result.get('total_size_gb', 0):.2f}GB"
                elif test_name == "memory_efficiency":
                    details = f"RAM: {result.get('ram_utilization', 0):.1f}%"
                elif test_name == "streaming_dataset":
                    details = f"{result.get('samples_per_second', 0):.1f} samples/sec"
                elif test_name == "gtx_optimization":
                    details = f"Optimal batch: {result.get('optimal_batch_size', 'N/A')}"
                elif test_name == "checkpoint_system":
                    details = "Checkpoint system working"
                else:
                    details = "Test completed"

            table.add_row(test_name.replace("_", " ").title(), status, details)

        console.print(table)

def main():
    """Main test execution"""
    tester = StreamingSystemTester()
    results = tester.run_full_test()

    # Save results
    with open("streaming_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    console.print("[bold green]🎉 All tests completed! Results saved to streaming_test_results.json[/bold green]")

if __name__ == "__main__":
    main()
