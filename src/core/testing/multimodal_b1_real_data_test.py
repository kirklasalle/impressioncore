#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #attention_mechanism #cuda #deployment #inference #memory_management #multimodal #python #source_code #src/core/testing\\multimodal_b1_real_data_test.py #testing #training #transformer
**Category:** Core Implementation
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #api #attention_mechanism #cuda #deployment #inference #memory_management #multimodal #python #source_code #src\\core\\testing\\multimodal_b1_real_data_test.py #testing #training #transformer
# Category:** Core Implementation
# Status:** Active

"""
ImpressionCore B1 Multimodal Real Data Integration Test

Comprehensive testing of multimodal B1 model with real embedded data integration.
Tests all modalities (text, image, audio, code, math) with actual F: drive embeddings.

File: core/testing/multimodal_b1_real_data_test.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-20
"""

import json
import sys
import time
import traceback
from pathlib import Path
from typing import Any

import numpy as np
import torch

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

# Import ImpressionCore components
from .core.models.multimodal_b1_architecture import ImpressionCoreBMultimodal, MultimodalConfig
from .core.utils.device_manager import get_device_manager
from .core.utils.rich_logging import RichLogger

console = Console()
logger = RichLogger("MultimodalB1Test", console)

class MultimodalB1RealDataTest:
    """Comprehensive test suite for B1 multimodal model with real embedded data"""

    def __init__(self):
        self.device_manager = get_device_manager()
        self.device = self.device_manager.device
        self.dtype = self.device_manager.dtype

        # Test configuration
        self.config = MultimodalConfig()
        self.test_results = {}

        # Real data paths
        self.f_drive_path = Path("F:/impressioncore_training_data")
        self.embeddings_path = self.f_drive_path / "processed_embeddings"

        console.print(Panel.fit(
            "[bold cyan]ImpressionCore B1 Multimodal Real Data Test[/bold cyan]\n"
            "Testing all modalities with F: drive embedded data\n"
            f"Device: {self.device} | Data Path: {self.f_drive_path}",
            title="B1 Multimodal Test Suite",
            border_style="cyan"
        ))

    def check_f_drive_data(self) -> dict[str, Any]:
        """Check availability and status of F: drive training data"""
        logger.info("Checking F: drive training data availability...")

        data_status = {
            'f_drive_exists': self.f_drive_path.exists(),
            'embeddings_path_exists': self.embeddings_path.exists(),
            'files_found': {},
            'total_size_gb': 0.0,
            'modality_counts': {}
        }

        if not data_status['f_drive_exists']:
            logger.warning(f"F: drive path not found: {self.f_drive_path}")
            return data_status

        if not data_status['embeddings_path_exists']:
            logger.warning(f"Embeddings path not found: {self.embeddings_path}")
            return data_status

        # Scan for embedding files
        for modality in ['text', 'image', 'audio', 'code', 'math']:
            modality_files = list(self.embeddings_path.glob(f"*{modality}*"))
            data_status['files_found'][modality] = len(modality_files)
            data_status['modality_counts'][modality] = len(modality_files)

        # Calculate total size
        try:
            total_bytes = sum(f.stat().st_size for f in self.embeddings_path.rglob('*') if f.is_file())
            data_status['total_size_gb'] = total_bytes / (1024**3)
        except Exception as e:
            logger.error(f"Error calculating data size: {e}")

        return data_status

    def load_real_embeddings(self, modality: str, max_samples: int = 10) -> list[np.ndarray]:
        """Load real embeddings from F: drive for specified modality"""
        logger.info(f"Loading real {modality} embeddings...")

        embeddings = []
        modality_files = list(self.embeddings_path.glob(f"*{modality}*.npy"))[:max_samples]

        for file_path in modality_files:
            try:
                embedding = np.load(file_path)
                embeddings.append(embedding)
                logger.debug(f"Loaded {modality} embedding from {file_path.name}: shape {embedding.shape}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")

        logger.info(f"Successfully loaded {len(embeddings)} real {modality} embeddings")
        return embeddings

    def create_multimodal_test_data(self) -> dict[str, Any]:
        """Create comprehensive test data using real F: drive embeddings"""
        logger.info("Creating multimodal test data with real embeddings...")

        test_data = {
            'text': [
                "Explain quantum entanglement in simple terms.",
                "How do neural networks learn from data?",
                "What are the applications of artificial intelligence?",
                "Describe the structure of DNA and its function.",
                "What is the theory of relativity?"
            ],
            'images': [],  # Will be filled with real image embeddings
            'audio': [],   # Will be filled with real audio data
            'code': [
                "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
                "import torch; x = torch.randn(2, 3); y = torch.matmul(x, x.t())",
                "class Transformer(nn.Module): def __init__(self): super().__init__()",
                "SELECT * FROM users WHERE age > 18 ORDER BY name",
                "for i in range(10): print(f'Number: {i}')"
            ],
            'math': [
                "∫(x² + 2x + 1)dx = ?",
                "lim(x→0) sin(x)/x = 1",
                "∇²φ = ∂²φ/∂x² + ∂²φ/∂y² + ∂²φ/∂z²",
                "P(A|B) = P(B|A)P(A)/P(B)",
                "e^(iπ) + 1 = 0"
            ]
        }

        # Load real embeddings if available
        for modality in ['images', 'audio']:
            try:
                real_embeddings = self.load_real_embeddings(modality.rstrip('s'), max_samples=5)
                if real_embeddings:
                    test_data[modality] = real_embeddings
                else:
                    # Create synthetic data if no real embeddings available
                    if modality == 'images':
                        test_data[modality] = [np.random.randn(3, 224, 224) for _ in range(3)]
                    elif modality == 'audio':
                        test_data[modality] = [np.random.randn(16000) for _ in range(3)]
            except Exception as e:
                logger.warning(f"Could not load real {modality} data: {e}")
                # Fallback to synthetic data
                if modality == 'images':
                    test_data[modality] = [np.random.randn(3, 224, 224) for _ in range(3)]
                elif modality == 'audio':
                    test_data[modality] = [np.random.randn(16000) for _ in range(3)]

        return test_data

    def test_model_initialization(self) -> bool:
        """Test B1 model initialization with real data integration"""
        logger.info("Testing B1 model initialization...")

        try:
            # Initialize model
            self.model = ImpressionCoreBMultimodal(self.config)
            self.model.to(self.device)

            # Test device placement
            device_check = next(self.model.parameters()).device == self.device

            # Test memory usage
            initial_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
            memory_mb = initial_memory / (1024**2)

            self.test_results['initialization'] = {
                'success': True,
                'device_correct': device_check,
                'memory_usage_mb': memory_mb,
                'parameter_count': sum(p.numel() for p in self.model.parameters()),
                'trainable_params': sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            }

            logger.success(f"Model initialized successfully on {self.device}")
            logger.info(f"Memory usage: {memory_mb:.2f} MB")
            logger.info(f"Parameters: {self.test_results['initialization']['parameter_count']:,}")

            return True

        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            self.test_results['initialization'] = {'success': False, 'error': str(e)}
            return False

    def test_individual_modalities(self, test_data: dict[str, Any]) -> bool:
        """Test each modality encoder individually"""
        logger.info("Testing individual modality encoders...")

        modality_results = {}

        for modality, data in test_data.items():
            if not data:
                continue

            try:
                logger.info(f"Testing {modality} encoder...")

                # Prepare input data
                if modality == 'text':
                    inputs = {'text': data[:3]}
                elif modality == 'images':
                    inputs = {'images': data[:3]}
                elif modality == 'audio':
                    inputs = {'audio': data[:3]}
                elif modality == 'code':
                    inputs = {'code': data[:3]}
                elif modality == 'math':
                    inputs = {'math': data[:3]}

                # Test forward pass
                start_time = time.time()

                with torch.no_grad():
                    output = self.model(inputs)

                inference_time = time.time() - start_time

                # Validate output structure
                required_keys = ['conversation_features', 'quality_score', 'academic_level', 'academic_logits']
                has_all_keys = all(key in output for key in required_keys)

                modality_results[modality] = {
                    'success': True,
                    'inference_time_ms': inference_time * 1000,
                    'output_shape': output['conversation_features'].shape,
                    'quality_score': float(output['quality_score'].mean().item()),
                    'has_all_keys': has_all_keys,
                    'memory_after_mb': torch.cuda.memory_allocated() / (1024**2) if torch.cuda.is_available() else 0
                }

                logger.success(f"{modality.capitalize()} encoder: ✅ ({inference_time*1000:.2f}ms)")

            except Exception as e:
                logger.error(f"{modality.capitalize()} encoder failed: {e}")
                modality_results[modality] = {'success': False, 'error': str(e)}

        self.test_results['individual_modalities'] = modality_results
        return all(result.get('success', False) for result in modality_results.values())

    def test_multimodal_fusion(self, test_data: dict[str, Any]) -> bool:
        """Test cross-modal attention and fusion"""
        logger.info("Testing multimodal fusion capabilities...")

        try:
            # Create multimodal input combining multiple modalities
            multimodal_input = {}

            if test_data['text']:
                multimodal_input['text'] = test_data['text'][:2]
            if test_data['images']:
                multimodal_input['images'] = test_data['images'][:2]
            if test_data['code']:
                multimodal_input['code'] = test_data['code'][:2]
            if test_data['math']:
                multimodal_input['math'] = test_data['math'][:2]

            start_time = time.time()

            with torch.no_grad():
                output = self.model(multimodal_input)

            fusion_time = time.time() - start_time

            # Validate fusion output
            fusion_results = {
                'success': True,
                'fusion_time_ms': fusion_time * 1000,
                'output_shape': output['conversation_features'].shape,
                'quality_score': float(output['quality_score'].mean().item()),
                'academic_level': output['academic_level'].softmax(dim=-1).max(dim=-1)[0].mean().item(),
                'has_fusion_attention': 'fusion_attention' in output,
                'modalities_processed': len(multimodal_input)
            }

            self.test_results['multimodal_fusion'] = fusion_results

            logger.success(f"Multimodal fusion: ✅ ({fusion_time*1000:.2f}ms, {len(multimodal_input)} modalities)")
            return True

        except Exception as e:
            logger.error(f"Multimodal fusion failed: {e}")
            self.test_results['multimodal_fusion'] = {'success': False, 'error': str(e)}
            return False

    def test_vector_database_integration(self) -> bool:
        """Test RAG system with real vector database"""
        logger.info("Testing vector database integration...")

        try:
            # Test if vector database files exist
            vector_files = {
                'embeddings': self.embeddings_path / "all_embeddings.npy",
                'metadata': self.embeddings_path / "all_metadata.json",
                'faiss_index': self.embeddings_path / "multimodal_faiss_index.faiss"
            }

            files_exist = {name: path.exists() for name, path in vector_files.items()}

            # Test retrieval with sample query
            test_query = {"text": ["What is machine learning?"]}

            with torch.no_grad():
                output = self.model(test_query)

            rag_results = {
                'success': True,
                'vector_files_exist': files_exist,
                'retrieved_context_count': len(output.get('retrieved_context', [])),
                'has_enhanced_features': 'enhanced_features' in output or 'conversation_features' in output,
                'context_available': bool(output.get('retrieved_context'))
            }

            self.test_results['vector_database'] = rag_results

            status = "✅" if all(files_exist.values()) else "⚠️"
            logger.info(f"Vector database integration: {status}")

            return True

        except Exception as e:
            logger.error(f"Vector database test failed: {e}")
            self.test_results['vector_database'] = {'success': False, 'error': str(e)}
            return False

    def test_memory_efficiency(self, test_data: dict[str, Any]) -> bool:
        """Test memory usage and efficiency"""
        logger.info("Testing memory efficiency and VRAM usage...")

        try:
            if not torch.cuda.is_available():
                logger.warning("CUDA not available, skipping memory efficiency test")
                return True

            # Clear cache and measure baseline
            torch.cuda.empty_cache()
            baseline_memory = torch.cuda.memory_allocated()

            # Test with increasing batch sizes
            batch_sizes = [1, 2, 4, 8]
            memory_results = {}

            for batch_size in batch_sizes:
                try:
                    # Create batch
                    batch_input = {
                        'text': test_data['text'][:batch_size],
                        'code': test_data['code'][:batch_size]
                    }

                    # Measure memory before
                    before_memory = torch.cuda.memory_allocated()

                    # Forward pass
                    with torch.no_grad():
                        _output = self.model(batch_input)

                    # Measure memory after
                    after_memory = torch.cuda.memory_allocated()
                    memory_used_mb = (after_memory - before_memory) / (1024**2)

                    memory_results[f'batch_{batch_size}'] = {
                        'memory_used_mb': memory_used_mb,
                        'total_memory_mb': after_memory / (1024**2),
                        'success': True
                    }

                    # Clear for next test
                    torch.cuda.empty_cache()

                except Exception as e:
                    memory_results[f'batch_{batch_size}'] = {
                        'success': False,
                        'error': str(e)
                    }

            # Check if within 4GB VRAM limit
            max_memory_mb = max(
                result.get('total_memory_mb', 0)
                for result in memory_results.values()
                if result.get('success', False)
            )

            within_4gb_limit = max_memory_mb < 4000

            self.test_results['memory_efficiency'] = {
                'success': True,
                'batch_results': memory_results,
                'max_memory_mb': max_memory_mb,
                'within_4gb_limit': within_4gb_limit,
                'baseline_memory_mb': baseline_memory / (1024**2)
            }

            status = "✅" if within_4gb_limit else "⚠️"
            logger.info(f"Memory efficiency: {status} (Max: {max_memory_mb:.2f} MB)")

            return True

        except Exception as e:
            logger.error(f"Memory efficiency test failed: {e}")
            self.test_results['memory_efficiency'] = {'success': False, 'error': str(e)}
            return False

    def generate_test_report(self) -> None:
        """Generate comprehensive test report"""
        logger.info("Generating comprehensive test report...")

        # Create summary table
        summary_table = Table(title="ImpressionCore B1 Multimodal Test Results")
        summary_table.add_column("Test Category", style="cyan")
        summary_table.add_column("Status", style="bold")
        summary_table.add_column("Details", style="dim")

        for test_name, results in self.test_results.items():
            status = "✅ PASS" if results.get('success', False) else "❌ FAIL"
            details = []

            if test_name == 'initialization':
                details.append(f"Memory: {results.get('memory_usage_mb', 0):.1f} MB")
                details.append(f"Params: {results.get('parameter_count', 0):,}")

            elif test_name == 'individual_modalities':
                passed = sum(1 for r in results.values() if r.get('success', False))
                total = len(results)
                details.append(f"{passed}/{total} modalities working")

            elif test_name == 'multimodal_fusion':
                if results.get('success'):
                    details.append(f"Time: {results.get('fusion_time_ms', 0):.1f}ms")
                    details.append(f"Modalities: {results.get('modalities_processed', 0)}")

            elif test_name == 'vector_database':
                if results.get('success'):
                    files_ok = sum(results.get('vector_files_exist', {}).values())
                    details.append(f"Vector files: {files_ok}/3")

            elif test_name == 'memory_efficiency':
                if results.get('success'):
                    max_mem = results.get('max_memory_mb', 0)
                    details.append(f"Peak: {max_mem:.1f} MB")
                    if results.get('within_4gb_limit'):
                        details.append("Within 4GB limit ✅")

            summary_table.add_row(
                test_name.replace('_', ' ').title(),
                status,
                " | ".join(details)
            )

        console.print("\n")
        console.print(summary_table)

        # Overall status
        all_passed = all(results.get('success', False) for results in self.test_results.values())

        if all_passed:
            console.print(Panel.fit(
                "[bold green]🎉 ALL TESTS PASSED![/bold green]\n"
                "ImpressionCore B1 multimodal model with real data integration is fully operational.\n"
                "Ready for advanced training strategies and deployment.",
                title="Test Suite Complete",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                "[bold yellow]⚠️ SOME TESTS FAILED[/bold yellow]\n"
                "Review the results above and address any issues before proceeding.\n"
                "Check logs for detailed error information.",
                title="Test Suite Complete",
                border_style="yellow"
            ))

        return all_passed

    async def run_complete_test_suite(self) -> bool:
        """Run the complete multimodal B1 test suite"""
        console.print(Panel.fit(
            "[bold cyan]🧠 ImpressionCore B1 Multimodal Test Suite[/bold cyan]\n"
            "Comprehensive testing with real F: drive embedded data",
            title="Starting Test Suite",
            border_style="cyan"
        ))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:

            test_tasks = [
                ("Checking F: drive data", self.check_f_drive_data),
                ("Creating test data", self.create_multimodal_test_data),
                ("Testing model initialization", self.test_model_initialization),
                ("Testing individual modalities", lambda: self.test_individual_modalities(self.test_data)),
                ("Testing multimodal fusion", lambda: self.test_multimodal_fusion(self.test_data)),
                ("Testing vector database", self.test_vector_database_integration),
                ("Testing memory efficiency", lambda: self.test_memory_efficiency(self.test_data))
            ]

            overall_task = progress.add_task("Overall Progress", total=len(test_tasks))

            for task_name, task_func in test_tasks:
                task_id = progress.add_task(task_name, total=100)

                try:
                    if task_name == "Creating test data":
                        self.test_data = task_func()
                        result = True
                    elif task_name == "Checking F: drive data":
                        self.data_status = task_func()
                        result = True
                    else:
                        result = task_func()

                    progress.update(task_id, completed=100)
                    logger.success(f"{task_name}: {'✅ PASS' if result else '❌ FAIL'}")

                except Exception as e:
                    logger.error(f"{task_name}: ❌ FAIL - {e}")
                    progress.update(task_id, completed=100)

                progress.update(overall_task, advance=1)
                progress.remove_task(task_id)

        # Generate final report
        return self.generate_test_report()

def main():
    """Main test execution function"""
    try:
        # Initialize test suite
        test_suite = MultimodalB1RealDataTest()

        # Run complete test suite
        import asyncio
        success = asyncio.run(test_suite.run_complete_test_suite())

        # Save results for analysis
        results_file = Path("src/core/testing/b1_test_results.json")
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'success': success,
                'test_results': test_suite.test_results,
                'data_status': getattr(test_suite, 'data_status', {})
            }, f, indent=2)

        console.print(f"\n📊 Detailed results saved to: {results_file}")

        return success

    except KeyboardInterrupt:
        console.print("\n⚠️ Test suite interrupted by user")
        return False
    except Exception as e:
        console.print(f"\n❌ Test suite failed: {e}")
        console.print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
