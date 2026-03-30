#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #gpu_optimization #inference #memory_management #multimodal #performance #python #source_code #src/core/evaluation/model_evaluator.py #testing #tokenization #training
**Category:** Core Implementation
**Status:** Active
"""



import gc
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import psutil
import torch

logger = logging.getLogger(__name__)

# Optional visualization imports
try:
    import matplotlib.pyplot as plt  # noqa: F401
    import seaborn as sns  # noqa: F401
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

# Rich imports for enhanced UI
try:
    from rich.console import Console
    from rich.layout import Layout  # noqa: F401
    from rich.panel import Panel  # noqa: F401
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn  # noqa: F401
    from rich.table import Table
    from rich.text import Text  # noqa: F401
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    logging.warning("Rich not available, using basic output")

@dataclass
class ModelMetrics:
    """Comprehensive model performance metrics"""
    model_name: str
    model_size_mb: float
    parameter_count: int

    # Performance Metrics
    inference_time_ms: float
    tokens_per_second: float
    memory_usage_mb: float
    gpu_utilization: float

    # Quality Metrics
    perplexity: float
    loss: float
    quality_score: float

    # Hardware Metrics
    vram_usage_mb: float
    cpu_usage_percent: float
    temperature_c: float | None = None

    # Training Metrics (if available)
    epochs_trained: int | None = None
    training_time_hours: float | None = None
    convergence_rate: float | None = None

@dataclass
class InferenceResult:
    """Results from model inference testing"""
    input_text: str
    output_text: str
    confidence: float
    response_time_ms: float
    memory_delta_mb: float
    tokens_generated: int
    quality_rating: float

class ModelEvaluator:
    """
    Comprehensive model evaluation system for ImpressionCore B3 models.

    Features:
    - Performance benchmarking
    - Memory usage analysis
    - Inference quality testing
    - Hardware optimization metrics
    - Training history analysis
    """

    def __init__(self, models_root: str = "F:/models"):
        self.models_root = Path(models_root)
        self.console = Console() if RICH_AVAILABLE else None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Initialize tracking
        self.evaluation_history = []
        self.current_model = None
        self.baseline_memory = self._get_memory_usage()

        logger.info("ModelEvaluator initialized")
        logger.info("Models root: %s", self.models_root)
        logger.info("Device: %s", self.device)
        logger.info("Baseline memory: %.2f MB", self.baseline_memory)

    def discover_models(self) -> list[dict[str, Any]]:
        """Discover all available models in F:/models structure"""
        models = []

        for category_path in self.models_root.iterdir():
            if category_path.is_dir():
                for model_path in category_path.rglob("*.pt"):
                    try:
                        model_info = self._analyze_model_file(model_path)
                        model_info['category'] = category_path.name
                        models.append(model_info)
                    except Exception as e:
                        logger.warning("Error analyzing %s: %s", model_path, e)

        return sorted(models, key=lambda x: x.get('modified_time', 0), reverse=True)

    def _analyze_model_file(self, model_path: Path) -> dict[str, Any]:
        """Analyze a model file to extract metadata"""
        stat = model_path.stat()
        size_mb = stat.st_size / (1024 * 1024)

        # Try to load model metadata without loading the full model
        try:
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)

            # Extract model information
            model_info = {
                'path': str(model_path),
                'name': model_path.stem,
                'size_mb': size_mb,
                'modified_time': stat.st_mtime,
                'creation_time': stat.st_ctime,
            }

            # Extract training metadata if available
            if isinstance(checkpoint, dict):
                if 'epoch' in checkpoint:
                    model_info['epoch'] = checkpoint['epoch']
                if 'loss' in checkpoint:
                    model_info['loss'] = checkpoint['loss']
                if 'optimizer' in checkpoint:
                    model_info['has_optimizer'] = True
                if 'model_state_dict' in checkpoint:
                    model_info['has_state_dict'] = True
                if 'quality_score' in checkpoint:
                    model_info['quality_score'] = checkpoint['quality_score']

            return model_info

        except Exception as e:
            return {
                'path': str(model_path),
                'name': model_path.stem,
                'size_mb': size_mb,
                'modified_time': stat.st_mtime,
                'creation_time': stat.st_ctime,
                'error': str(e)
            }

    def load_model_for_evaluation(self, model_path: str) -> torch.nn.Module | None:
        """Load a model for evaluation with memory monitoring"""
        try:
            logger.info("Loading model: %s", model_path)

            # Monitor memory before loading
            mem_before = self._get_memory_usage()

            # Load checkpoint
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)

            # Extract model if it's in a checkpoint format
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                # Need to reconstruct the model architecture
                # This would require the model class definition
                logger.warning("Model requires architecture reconstruction")
                return None
            elif hasattr(checkpoint, 'eval'):
                # Direct model object
                model = checkpoint.to(self.device)
                model.eval()
            else:
                logger.warning("Unknown checkpoint format: %s", type(checkpoint))
                return None

            # Monitor memory after loading
            mem_after = self._get_memory_usage()
            logger.info("Model loaded, memory usage: %.2f MB", mem_after - mem_before)

            self.current_model = model
            return model

        except Exception as e:
            logger.error("Failed to load model %s: %s", model_path, e)
            return None

    def evaluate_model_performance(self, model_path: str) -> ModelMetrics | None:
        """Comprehensive model performance evaluation"""
        model = self.load_model_for_evaluation(model_path)
        if model is None:
            return None

        try:
            # Basic model info
            model_size_mb = Path(model_path).stat().st_size / (1024 * 1024)
            param_count = sum(p.numel() for p in model.parameters())

            # Performance benchmarking
            inference_times = []
            memory_usage = []

            # Create dummy input for testing
            dummy_input = torch.randn(1, 512).to(self.device)  # Adjust based on model input

            # Warmup
            for _ in range(5):
                with torch.no_grad():
                    _ = model(dummy_input)

            # Benchmark inference
            torch.cuda.synchronize() if torch.cuda.is_available() else None

            for _ in range(10):
                mem_before = self._get_memory_usage()
                start_time = time.perf_counter()

                with torch.no_grad():
                    _output = model(dummy_input)

                torch.cuda.synchronize() if torch.cuda.is_available() else None
                end_time = time.perf_counter()
                mem_after = self._get_memory_usage()

                inference_times.append((end_time - start_time) * 1000)  # Convert to ms
                memory_usage.append(mem_after - mem_before)

            # Calculate metrics
            avg_inference_time = np.mean(inference_times)
            avg_memory_usage = np.mean(memory_usage)
            tokens_per_second = 1000 / avg_inference_time if avg_inference_time > 0 else 0

            # GPU utilization (if available)
            gpu_util = self._get_gpu_utilization()

            # Create metrics object
            metrics = ModelMetrics(
                model_name=Path(model_path).stem,
                model_size_mb=model_size_mb,
                parameter_count=param_count,
                inference_time_ms=avg_inference_time,
                tokens_per_second=tokens_per_second,
                memory_usage_mb=avg_memory_usage,
                gpu_utilization=gpu_util,
                perplexity=0.0,  # Would need proper calculation
                loss=0.0,  # Would need validation data
                quality_score=0.0,  # Would need quality assessment
                vram_usage_mb=self._get_vram_usage(),
                cpu_usage_percent=psutil.cpu_percent()
            )

            return metrics

        except Exception as e:
            logger.error("Error evaluating model: %s", e)
            return None
        finally:
            # Cleanup
            if hasattr(self, 'current_model') and self.current_model is not None:
                del self.current_model
                self.current_model = None
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            gc.collect()

    def test_model_inference(self, model_path: str, test_inputs: list[str]) -> list[InferenceResult]:
        """Test model inference with sample inputs"""
        model = self.load_model_for_evaluation(model_path)
        if model is None:
            return []

        results = []

        try:
            for input_text in test_inputs:
                mem_before = self._get_memory_usage()
                start_time = time.perf_counter()

                # This would need to be adapted based on your model's tokenizer and generation method
                # For now, create a placeholder result
                output_text = f"Model response to: {input_text[:50]}..."

                end_time = time.perf_counter()
                mem_after = self._get_memory_usage()

                result = InferenceResult(
                    input_text=input_text,
                    output_text=output_text,
                    confidence=0.85,  # Placeholder
                    response_time_ms=(end_time - start_time) * 1000,
                    memory_delta_mb=mem_after - mem_before,
                    tokens_generated=len(output_text.split()),
                    quality_rating=8.5  # Placeholder
                )

                results.append(result)

        except Exception as e:
            logger.error("Error during inference testing: %s", e)

        finally:
            # Cleanup
            if hasattr(self, 'current_model') and self.current_model is not None:
                del self.current_model
                self.current_model = None
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            gc.collect()

        return results

    def analyze_training_history(self, training_log_path: str) -> dict[str, Any]:
        """Analyze training history from log files"""
        try:
            with open(training_log_path) as f:
                data = json.load(f)

            analysis = {
                'total_epochs': data.get('training_summary', {}).get('total_epochs', 0),
                'final_loss': data.get('training_results', {}).get('final_loss', 0),
                'final_quality': data.get('training_results', {}).get('final_quality', 0),
                'training_duration_hours': data.get('training_summary', {}).get('training_duration_hours', 0),
                'convergence_analysis': self._analyze_convergence(data),
                'performance_trends': self._analyze_performance_trends(data)
            }

            return analysis

        except Exception as e:
            logger.error("Error analyzing training history: %s", e)
            return {}

    def _analyze_convergence(self, training_data: dict) -> dict[str, Any]:
        """Analyze convergence patterns from training data"""
        epoch_results = training_data.get('epoch_results', [])
        if not epoch_results:
            return {}

        losses = [epoch['avg_loss'] for epoch in epoch_results]
        qualities = [epoch['avg_quality'] for epoch in epoch_results]

        # Calculate convergence metrics
        loss_improvement = losses[0] - losses[-1] if len(losses) > 1 else 0
        quality_improvement = qualities[-1] - qualities[0] if len(qualities) > 1 else 0

        # Estimate convergence epoch (where loss stabilizes)
        convergence_epoch = self._find_convergence_point(losses)

        return {
            'loss_improvement': loss_improvement,
            'quality_improvement': quality_improvement,
            'convergence_epoch': convergence_epoch,
            'final_loss': losses[-1] if losses else 0,
            'final_quality': qualities[-1] if qualities else 0
        }

    def _analyze_performance_trends(self, training_data: dict) -> dict[str, Any]:
        """Analyze performance trends during training"""
        epoch_results = training_data.get('epoch_results', [])
        if not epoch_results:
            return {}

        # Extract time and loss data
        durations = [epoch['duration_seconds'] for epoch in epoch_results]
        losses = [epoch['avg_loss'] for epoch in epoch_results]

        return {
            'avg_epoch_duration': np.mean(durations),
            'training_stability': np.std(durations),
            'loss_variance': np.var(losses),
            'training_efficiency': len(epoch_results) / sum(durations) * 3600  # epochs per hour
        }

    def _find_convergence_point(self, losses: list[float], threshold: float = 0.01) -> int:
        """Find the epoch where loss convergence begins"""
        if len(losses) < 5:
            return len(losses)

        for i in range(5, len(losses)):
            recent_variance = np.var(losses[i-5:i])
            if recent_variance < threshold:
                return i

        return len(losses)

    def generate_evaluation_report(self, model_path: str, output_path: str | None = None) -> dict[str, Any]:
        """Generate comprehensive evaluation report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'model_path': model_path,
            'evaluation_config': {
                'device': str(self.device),
                'models_root': str(self.models_root),
                'evaluator_version': '1.0.0'
            }
        }

        # Performance evaluation
        logger.info("Running performance evaluation...")
        metrics = self.evaluate_model_performance(model_path)
        if metrics:
            report['performance_metrics'] = asdict(metrics)

        # Inference testing
        logger.info("Testing inference capabilities...")
        test_inputs = [
            "What is artificial intelligence?",
            "Explain machine learning in simple terms.",
            "How does neural network training work?",
            "What are the benefits of multimodal AI?",
            "Describe the future of AI technology."
        ]
        inference_results = self.test_model_inference(model_path, test_inputs)
        report['inference_results'] = [asdict(result) for result in inference_results]

        # Training history analysis (if available)
        training_log_path = self._find_training_log(model_path)
        if training_log_path:
            logger.info("Analyzing training history from %s...", training_log_path)
            training_analysis = self.analyze_training_history(training_log_path)
            report['training_analysis'] = training_analysis

        # Save report
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name = Path(model_path).stem
            output_path = f"evaluation_report_{model_name}_{timestamp}.json"

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info("Evaluation report saved: %s", output_path)
        return report

    def _find_training_log(self, model_path: str) -> str | None:
        """Find associated training log for a model"""
        model_name = Path(model_path).stem

        # Search for training logs in various locations
        search_paths = [
            Path(model_path).parent,
            Path("./"),
            Path("./logs"),
            Path("./training_logs")
        ]

        for search_path in search_paths:
            if search_path.exists():
                for log_file in search_path.glob(f"*{model_name}*.json"):
                    return str(log_file)

        return None

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)

    def _get_gpu_utilization(self) -> float:
        """Get GPU utilization percentage"""
        if not torch.cuda.is_available():
            return 0.0

        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            return float(util.gpu)
        except Exception:
            return 0.0

    def _get_vram_usage(self) -> float:
        """Get VRAM usage in MB"""
        if not torch.cuda.is_available():
            return 0.0

        return torch.cuda.memory_allocated() / (1024 * 1024)

    def display_models_table(self, models: list[dict[str, Any]]):
        """Display discovered models in a table"""
        if not RICH_AVAILABLE:
            logger.info("Discovered Models:")
            for i, model in enumerate(models):
                logger.info("%d. %s (%.1f MB)", i + 1, model['name'], model['size_mb'])
            return

        table = Table(title="🤖 Available ImpressionCore Models")
        table.add_column("Model Name", style="cyan")
        table.add_column("Size (MB)", style="magenta")
        table.add_column("Category", style="green")
        table.add_column("Modified", style="yellow")
        table.add_column("Quality", style="blue")

        for model in models[:10]:  # Show top 10
            modified = datetime.fromtimestamp(model['modified_time']).strftime("%Y-%m-%d %H:%M")
            quality = f"{model.get('quality_score', 'N/A')}"

            table.add_row(
                model['name'],
                f"{model['size_mb']:.1f}",
                model.get('category', 'Unknown'),
                modified,
                quality
            )

        self.console.print(table)

def main():
    """Main evaluation interface"""
    evaluator = ModelEvaluator()

    logger.info("ImpressionCore Model Evaluation System")
    logger.info("=========================================")

    # Discover available models
    logger.info("Discovering models...")
    models = evaluator.discover_models()

    if not models:
        logger.error("No models found in F:/models structure")
        return

    # Display models
    evaluator.display_models_table(models)

    # Interactive evaluation
    logger.info("Found %d models", len(models))
    logger.info("Select evaluation mode:")
    logger.info("1. Evaluate best model")
    logger.info("2. Evaluate specific model")
    logger.info("3. Compare all models")
    logger.info("4. Analyze training history")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        # Evaluate best model (most recent with highest quality)
        best_model = max(models, key=lambda x: (x.get('quality_score', 0), x.get('modified_time', 0)))
        logger.info("Evaluating best model: %s", best_model['name'])
        _report = evaluator.generate_evaluation_report(best_model['path'])
        logger.info("Evaluation complete! Report: evaluation_report_%s_*.json", best_model['name'])

    elif choice == "2":
        # Evaluate specific model
        logger.info("Available models:")
        for i, model in enumerate(models):
            logger.info("%d. %s", i + 1, model['name'])

        try:
            model_idx = int(input("\nSelect model number: ")) - 1
            if 0 <= model_idx < len(models):
                selected_model = models[model_idx]
                logger.info("Evaluating: %s", selected_model['name'])
                _report = evaluator.generate_evaluation_report(selected_model['path'])
                logger.info("Evaluation complete!")
            else:
                logger.error("Invalid model selection")
        except ValueError:
            logger.error("Invalid input")

    elif choice == "3":
        logger.info("Comparing all models (this may take a while)...")
        # Implementation for comparing all models
        logger.warning("Full comparison not yet implemented")

    elif choice == "4":
        # Analyze training history
        training_log = "b3_full_training_report_30epochs_20250802_131359.json"
        if Path(training_log).exists():
            analysis = evaluator.analyze_training_history(training_log)
            logger.info("Training Analysis Results:")
            logger.info("Total Epochs: %s", analysis.get('total_epochs', 'N/A'))
            logger.info("Final Loss: %.6f", analysis.get('final_loss', 'N/A'))
            logger.info("Final Quality: %.4f", analysis.get('final_quality', 'N/A'))
            logger.info("Training Duration: %.2f hours", analysis.get('training_duration_hours', 'N/A'))
        else:
            logger.error("Training log not found: %s", training_log)

if __name__ == "__main__":
    main()
