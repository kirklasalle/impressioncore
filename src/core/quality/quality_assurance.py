#!/usr/bin/env python3
"""
ImpressionCore: Priority 6C - Quality Assurance System

Comprehensive quality validation and regression testing for 256k context processing.
Ensures output quality preservation under memory pressure and degradation conditions.

File: src/core/quality/quality_assurance.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-30
Modified: 2025-05-30
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle <kirk@impressioncore.ai>

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [quality-assurance, validation, regression-testing, benchmarking, 2025]
Dependencies: [torch, numpy, typing, logging, metrics]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Production-ready quality assurance system featuring:
- Output quality validation against baselines
- Regression testing for long sequences
- Comparative benchmarking across configurations
- Quality degradation detection and measurement
- Automated quality preservation verification
- Performance-quality tradeoff analysis
"""

import torch
import torch.nn.functional as F
import numpy as np
import time
import math
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict
import json
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class QualityMetric(Enum):
    """Types of quality metrics to evaluate."""
    PERPLEXITY = "perplexity"
    BLEU_SCORE = "bleu_score"
    ROUGE_L = "rouge_l"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    ATTENTION_COHERENCE = "attention_coherence"
    SEQUENCE_COHERENCE = "sequence_coherence"
    FACTUAL_CONSISTENCY = "factual_consistency"
    FLUENCY_SCORE = "fluency_score"


class QualityThreshold(Enum):
    """Quality threshold levels."""
    EXCELLENT = "excellent"      # > 95% of baseline
    GOOD = "good"               # 90-95% of baseline
    ACCEPTABLE = "acceptable"   # 85-90% of baseline
    DEGRADED = "degraded"       # 80-85% of baseline
    POOR = "poor"              # < 80% of baseline


@dataclass
class QualityBenchmark:
    """Reference benchmark for quality comparison."""
    name: str
    context_length: int
    input_tokens: torch.Tensor
    reference_output: torch.Tensor
    baseline_metrics: Dict[QualityMetric, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_timestamp: float = field(default_factory=time.time)


@dataclass
class QualityTestResult:
    """Result of a quality test."""
    benchmark_name: str
    test_timestamp: float
    context_length: int
    configuration: Dict[str, Any]
    metrics: Dict[QualityMetric, float]
    baseline_comparison: Dict[QualityMetric, float]  # Ratio to baseline
    overall_quality_score: float
    quality_threshold: QualityThreshold
    passed: bool
    notes: str = ""
    processing_time_ms: float = 0.0


@dataclass
class RegressionTestSuite:
    """Collection of regression tests for different scenarios."""
    name: str
    benchmarks: List[QualityBenchmark]
    min_passing_rate: float = 0.9  # 90% of tests must pass
    quality_thresholds: Dict[QualityMetric, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.quality_thresholds:
            self.quality_thresholds = {
                QualityMetric.PERPLEXITY: 0.85,       # 85% of baseline (lower is better)
                QualityMetric.BLEU_SCORE: 0.90,       # 90% of baseline
                QualityMetric.ROUGE_L: 0.90,          # 90% of baseline
                QualityMetric.SEMANTIC_SIMILARITY: 0.85,  # 85% of baseline
                QualityMetric.ATTENTION_COHERENCE: 0.80,  # 80% of baseline
                QualityMetric.SEQUENCE_COHERENCE: 0.85,   # 85% of baseline
                QualityMetric.FACTUAL_CONSISTENCY: 0.90,  # 90% of baseline
                QualityMetric.FLUENCY_SCORE: 0.85         # 85% of baseline
            }


class QualityAssuranceSystem:
    """
    Comprehensive quality assurance system for 256k context processing.
    
    Features:
    - Quality metric computation and comparison
    - Regression testing against established baselines
    - Performance-quality tradeoff analysis
    - Automated quality degradation detection
    - Comparative benchmarking across configurations
    - Quality preservation verification under stress
    """
    
    def __init__(
        self,
        baseline_model: Optional[torch.nn.Module] = None,
        quality_cache_dir: str = "quality_cache",
        enable_caching: bool = True,
        verbose: bool = True
    ):
        self.baseline_model = baseline_model
        self.quality_cache_dir = Path(quality_cache_dir)
        self.enable_caching = enable_caching
        self.verbose = verbose
        
        # Quality data storage
        self.benchmarks: Dict[str, QualityBenchmark] = {}
        self.test_results: List[QualityTestResult] = []
        self.regression_suites: Dict[str, RegressionTestSuite] = {}
        
        # Quality metrics computations
        self.metric_computers: Dict[QualityMetric, Callable] = {
            QualityMetric.PERPLEXITY: self._compute_perplexity,
            QualityMetric.SEMANTIC_SIMILARITY: self._compute_semantic_similarity,
            QualityMetric.ATTENTION_COHERENCE: self._compute_attention_coherence,
            QualityMetric.SEQUENCE_COHERENCE: self._compute_sequence_coherence,
            QualityMetric.FLUENCY_SCORE: self._compute_fluency_score
        }
        
        # Cache setup
        if self.enable_caching:
            self.quality_cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Initialized QualityAssuranceSystem")
    
    def create_benchmark(
        self,
        name: str,
        input_tokens: torch.Tensor,
        reference_output: torch.Tensor,
        model: Optional[torch.nn.Module] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> QualityBenchmark:
        """
        Create a quality benchmark from input/output pair.
        
        Args:
            name: Benchmark identifier
            input_tokens: Input token sequence
            reference_output: Expected output sequence
            model: Model to use for baseline computation (optional)
            metadata: Additional benchmark metadata
            
        Returns:
            Created QualityBenchmark
        """
        context_length = input_tokens.shape[-1] if input_tokens.dim() > 1 else len(input_tokens)
        
        # Compute baseline metrics
        baseline_metrics = {}
        
        if model is not None:
            try:
                with torch.no_grad():
                    # Get model output for comparison
                    model_output = model(input_tokens.unsqueeze(0) if input_tokens.dim() == 1 else input_tokens)
                    
                    # Compute baseline metrics
                    for metric_type in QualityMetric:
                        if metric_type in self.metric_computers:
                            metric_value = self.metric_computers[metric_type](
                                model_output, reference_output, input_tokens
                            )
                            baseline_metrics[metric_type] = metric_value
                            
            except Exception as e:
                logger.warning(f"Failed to compute baseline metrics: {e}")
        
        benchmark = QualityBenchmark(
            name=name,
            context_length=context_length,
            input_tokens=input_tokens,
            reference_output=reference_output,
            baseline_metrics=baseline_metrics,
            metadata=metadata or {}
        )
        
        self.benchmarks[name] = benchmark
        
        # Cache benchmark if enabled
        if self.enable_caching:
            self._cache_benchmark(benchmark)
        
        logger.info(f"Created benchmark '{name}' with context length {context_length}")
        return benchmark
    
    def run_quality_test(
        self,
        benchmark_name: str,
        model: torch.nn.Module,
        configuration: Optional[Dict[str, Any]] = None,
        compute_all_metrics: bool = True
    ) -> QualityTestResult:
        """
        Run quality test against a specific benchmark.
        
        Args:
            benchmark_name: Name of benchmark to test against
            model: Model to evaluate
            configuration: Current model configuration
            compute_all_metrics: Whether to compute all available metrics
            
        Returns:
            QualityTestResult with comprehensive evaluation
        """
        if benchmark_name not in self.benchmarks:
            raise ValueError(f"Benchmark '{benchmark_name}' not found")
        
        benchmark = self.benchmarks[benchmark_name]
        start_time = time.time()
        
        try:
            with torch.no_grad():
                # Get model output
                input_tensor = benchmark.input_tokens
                if input_tensor.dim() == 1:
                    input_tensor = input_tensor.unsqueeze(0)
                
                model_output = model(input_tensor)
                
                # Compute quality metrics
                metrics = {}
                
                if compute_all_metrics:
                    for metric_type in QualityMetric:
                        if metric_type in self.metric_computers:
                            try:
                                metric_value = self.metric_computers[metric_type](
                                    model_output, benchmark.reference_output, benchmark.input_tokens
                                )
                                metrics[metric_type] = metric_value
                            except Exception as e:
                                logger.warning(f"Failed to compute {metric_type.value}: {e}")
                                metrics[metric_type] = 0.0
                else:
                    # Compute essential metrics only
                    essential_metrics = [
                        QualityMetric.PERPLEXITY,
                        QualityMetric.SEMANTIC_SIMILARITY,
                        QualityMetric.SEQUENCE_COHERENCE
                    ]
                    
                    for metric_type in essential_metrics:
                        if metric_type in self.metric_computers:
                            try:
                                metric_value = self.metric_computers[metric_type](
                                    model_output, benchmark.reference_output, benchmark.input_tokens
                                )
                                metrics[metric_type] = metric_value
                            except Exception as e:
                                logger.warning(f"Failed to compute {metric_type.value}: {e}")
                                metrics[metric_type] = 0.0
                
                # Compare to baseline
                baseline_comparison = {}
                for metric_type, value in metrics.items():
                    if metric_type in benchmark.baseline_metrics:
                        baseline_value = benchmark.baseline_metrics[metric_type]
                        if baseline_value != 0:
                            if metric_type == QualityMetric.PERPLEXITY:
                                # Lower is better for perplexity
                                ratio = baseline_value / max(value, 1e-8)
                            else:
                                # Higher is better for other metrics
                                ratio = value / baseline_value
                            baseline_comparison[metric_type] = ratio
                        else:
                            baseline_comparison[metric_type] = 1.0
                    else:
                        baseline_comparison[metric_type] = 1.0
                
                # Calculate overall quality score
                overall_score = self._calculate_overall_quality_score(
                    metrics, baseline_comparison
                )
                
                # Determine quality threshold
                quality_threshold = self._determine_quality_threshold(overall_score)
                
                # Determine if test passed
                passed = self._evaluate_test_pass(
                    baseline_comparison, quality_threshold
                )
                
                processing_time_ms = (time.time() - start_time) * 1000
                
                result = QualityTestResult(
                    benchmark_name=benchmark_name,
                    test_timestamp=time.time(),
                    context_length=benchmark.context_length,
                    configuration=configuration or {},
                    metrics=metrics,
                    baseline_comparison=baseline_comparison,
                    overall_quality_score=overall_score,
                    quality_threshold=quality_threshold,
                    passed=passed,
                    processing_time_ms=processing_time_ms
                )
                
                self.test_results.append(result)
                
                if self.verbose:
                    logger.info(
                        f"Quality test '{benchmark_name}': "
                        f"Score={overall_score:.3f}, "
                        f"Threshold={quality_threshold.value}, "
                        f"Passed={passed}"
                    )
                
                return result
                
        except Exception as e:
            logger.error(f"Quality test failed for '{benchmark_name}': {e}")
            # Return failed result
            return QualityTestResult(
                benchmark_name=benchmark_name,
                test_timestamp=time.time(),
                context_length=benchmark.context_length,
                configuration=configuration or {},
                metrics={},
                baseline_comparison={},
                overall_quality_score=0.0,
                quality_threshold=QualityThreshold.POOR,
                passed=False,
                notes=f"Test failed: {str(e)}",
                processing_time_ms=(time.time() - start_time) * 1000
            )
    
    def run_regression_suite(
        self,
        suite_name: str,
        model: torch.nn.Module,
        configuration: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run complete regression test suite.
        
        Args:
            suite_name: Name of regression suite to run
            model: Model to evaluate
            configuration: Current model configuration
            
        Returns:
            Comprehensive suite results
        """
        if suite_name not in self.regression_suites:
            raise ValueError(f"Regression suite '{suite_name}' not found")
        
        suite = self.regression_suites[suite_name]
        results = []
        start_time = time.time()
        
        logger.info(f"Running regression suite '{suite_name}' with {len(suite.benchmarks)} benchmarks")
        
        for benchmark in suite.benchmarks:
            try:
                result = self.run_quality_test(
                    benchmark.name,
                    model,
                    configuration,
                    compute_all_metrics=True
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Benchmark '{benchmark.name}' failed: {e}")
                continue
        
        # Analyze suite results
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        passing_rate = passed_tests / total_tests if total_tests > 0 else 0.0
        
        # Calculate average scores
        avg_quality_score = sum(r.overall_quality_score for r in results) / total_tests if total_tests > 0 else 0.0
        avg_processing_time = sum(r.processing_time_ms for r in results) / total_tests if total_tests > 0 else 0.0
        
        # Quality threshold distribution
        threshold_distribution = defaultdict(int)
        for result in results:
            threshold_distribution[result.quality_threshold.value] += 1
        
        # Metric averages
        metric_averages = defaultdict(float)
        metric_counts = defaultdict(int)
        
        for result in results:
            for metric_type, ratio in result.baseline_comparison.items():
                metric_averages[metric_type.value] += ratio
                metric_counts[metric_type.value] += 1
        
        for metric_name in metric_averages:
            if metric_counts[metric_name] > 0:
                metric_averages[metric_name] /= metric_counts[metric_name]
        
        suite_passed = passing_rate >= suite.min_passing_rate
        
        suite_results = {
            "suite_name": suite_name,
            "timestamp": time.time(),
            "duration_seconds": time.time() - start_time,
            "configuration": configuration or {},
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "passing_rate": passing_rate,
            "suite_passed": suite_passed,
            "min_required_rate": suite.min_passing_rate,
            "average_quality_score": avg_quality_score,
            "average_processing_time_ms": avg_processing_time,
            "quality_threshold_distribution": dict(threshold_distribution),
            "metric_baseline_ratios": dict(metric_averages),
            "individual_results": [
                {
                    "benchmark_name": r.benchmark_name,
                    "passed": r.passed,
                    "quality_score": r.overall_quality_score,
                    "quality_threshold": r.quality_threshold.value,
                    "processing_time_ms": r.processing_time_ms
                }
                for r in results
            ]
        }
        
        logger.info(
            f"Regression suite '{suite_name}' completed: "
            f"{passed_tests}/{total_tests} passed "
            f"({passing_rate:.1%}), "
            f"Average score: {avg_quality_score:.3f}"
        )
        
        return suite_results
    
    def create_regression_suite(
        self,
        name: str,
        benchmark_names: List[str],
        min_passing_rate: float = 0.9,
        quality_thresholds: Optional[Dict[QualityMetric, float]] = None
    ) -> RegressionTestSuite:
        """Create a regression test suite from existing benchmarks."""
        benchmarks = []
        
        for benchmark_name in benchmark_names:
            if benchmark_name in self.benchmarks:
                benchmarks.append(self.benchmarks[benchmark_name])
            else:
                logger.warning(f"Benchmark '{benchmark_name}' not found for suite '{name}'")
        
        suite = RegressionTestSuite(
            name=name,
            benchmarks=benchmarks,
            min_passing_rate=min_passing_rate,
            quality_thresholds=quality_thresholds or {}
        )
        
        self.regression_suites[name] = suite
        logger.info(f"Created regression suite '{name}' with {len(benchmarks)} benchmarks")
        
        return suite
    
    def _compute_perplexity(
        self,
        model_output: torch.Tensor,
        reference_output: torch.Tensor,
        input_tokens: torch.Tensor
    ) -> float:
        """Compute perplexity metric."""
        try:
            # Extract logits from model output
            if isinstance(model_output, tuple):
                logits = model_output[0]
            else:
                logits = model_output
            
            # Ensure reference output is properly shaped
            if reference_output.dim() == 1:
                target = reference_output
            else:
                target = reference_output.view(-1)
            
            # Compute cross entropy loss
            if logits.dim() == 3:  # [batch, seq, vocab]
                logits = logits.view(-1, logits.size(-1))
            
            # Align target length with logits
            min_len = min(logits.size(0), target.size(0))
            logits = logits[:min_len]
            target = target[:min_len]
            
            cross_entropy = F.cross_entropy(logits, target, reduction='mean')
            perplexity = torch.exp(cross_entropy).item()
            
            return perplexity
            
        except Exception as e:
            logger.warning(f"Failed to compute perplexity: {e}")
            return float('inf')
    
    def _compute_semantic_similarity(
        self,
        model_output: torch.Tensor,
        reference_output: torch.Tensor,
        input_tokens: torch.Tensor
    ) -> float:
        """Compute semantic similarity between outputs."""
        try:
            # Extract embeddings or logits
            if isinstance(model_output, tuple):
                embeddings = model_output[0]
            else:
                embeddings = model_output
            
            # Convert to embeddings if logits
            if embeddings.dim() == 3 and embeddings.size(-1) > 1000:  # Likely logits
                embeddings = F.softmax(embeddings, dim=-1)
            
            # Ensure reference is tensor
            if not isinstance(reference_output, torch.Tensor):
                reference_output = torch.tensor(reference_output, device=embeddings.device)
            
            # Pool embeddings to get sentence representation
            if embeddings.dim() == 3:
                model_embedding = embeddings.mean(dim=1)  # Average pooling
            else:
                model_embedding = embeddings
            
            # Create reference embedding (simplified)
            if reference_output.dim() == 1:
                ref_embedding = F.one_hot(reference_output, num_classes=embeddings.size(-1)).float()
                if ref_embedding.dim() == 2:
                    ref_embedding = ref_embedding.mean(dim=0, keepdim=True)
            else:
                ref_embedding = reference_output
            
            # Compute cosine similarity
            model_norm = F.normalize(model_embedding, p=2, dim=-1)
            ref_norm = F.normalize(ref_embedding, p=2, dim=-1)
            
            similarity = torch.mm(model_norm, ref_norm.t()).item()
            
            return max(0.0, similarity)  # Ensure non-negative
            
        except Exception as e:
            logger.warning(f"Failed to compute semantic similarity: {e}")
            return 0.0
    
    def _compute_attention_coherence(
        self,
        model_output: torch.Tensor,
        reference_output: torch.Tensor,
        input_tokens: torch.Tensor
    ) -> float:
        """Compute attention pattern coherence."""
        try:
            # This is a simplified coherence measure
            # In practice, you would extract attention weights from the model
            
            if isinstance(model_output, tuple) and len(model_output) > 1:
                # Try to get attention weights
                attention_weights = model_output[1] if hasattr(model_output[1], 'shape') else None
            else:
                attention_weights = None
            
            if attention_weights is not None:
                # Compute coherence as attention entropy (lower = more focused)
                if attention_weights.dim() == 4:  # [batch, heads, seq, seq]
                    attention_weights = attention_weights.mean(dim=1)  # Average over heads
                
                # Compute entropy of attention distribution
                attention_weights = attention_weights + 1e-8  # Avoid log(0)
                entropy = -(attention_weights * torch.log(attention_weights)).sum(dim=-1).mean()
                
                # Convert to coherence score (higher = more coherent)
                max_entropy = math.log(attention_weights.size(-1))
                coherence = 1.0 - (entropy / max_entropy)
                
                return max(0.0, coherence.item())
            else:
                # Fallback: use output consistency as proxy
                if model_output.dim() == 3:
                    output_var = model_output.var(dim=1).mean().item()
                    coherence = 1.0 / (1.0 + output_var)
                    return coherence
                else:
                    return 0.5  # Default moderate coherence
                    
        except Exception as e:
            logger.warning(f"Failed to compute attention coherence: {e}")
            return 0.0
    
    def _compute_sequence_coherence(
        self,
        model_output: torch.Tensor,
        reference_output: torch.Tensor,
        input_tokens: torch.Tensor
    ) -> float:
        """Compute sequence-level coherence."""
        try:
            # Extract logits
            if isinstance(model_output, tuple):
                logits = model_output[0]
            else:
                logits = model_output
            
            if logits.dim() == 3:
                # Compute token-to-token consistency
                probs = F.softmax(logits, dim=-1)
                
                # Measure consistency across sequence
                if probs.size(1) > 1:
                    consistency_scores = []
                    for i in range(probs.size(1) - 1):
                        curr_prob = probs[:, i, :]
                        next_prob = probs[:, i + 1, :]
                        consistency = F.cosine_similarity(curr_prob, next_prob).mean().item()
                        consistency_scores.append(consistency)
                    
                    sequence_coherence = sum(consistency_scores) / len(consistency_scores)
                    return max(0.0, sequence_coherence)
                else:
                    return 1.0  # Single token is perfectly coherent
            else:
                return 0.5  # Default moderate coherence
                
        except Exception as e:
            logger.warning(f"Failed to compute sequence coherence: {e}")
            return 0.0
    
    def _compute_fluency_score(
        self,
        model_output: torch.Tensor,
        reference_output: torch.Tensor,
        input_tokens: torch.Tensor
    ) -> float:
        """Compute fluency score based on output smoothness."""
        try:
            # Extract logits or probabilities
            if isinstance(model_output, tuple):
                logits = model_output[0]
            else:
                logits = model_output
            
            if logits.dim() == 3:
                probs = F.softmax(logits, dim=-1)
                
                # Compute entropy as fluency measure
                entropy = -(probs * torch.log(probs + 1e-8)).sum(dim=-1)
                
                # Optimal entropy for fluency (not too peaked, not too flat)
                vocab_size = probs.size(-1)
                max_entropy = math.log(vocab_size)
                optimal_entropy = max_entropy * 0.3  # 30% of maximum
                
                # Fluency score based on distance from optimal entropy
                entropy_diff = torch.abs(entropy - optimal_entropy)
                fluency = torch.exp(-entropy_diff / optimal_entropy).mean().item()
                
                return max(0.0, min(1.0, fluency))
            else:
                return 0.5  # Default moderate fluency
                
        except Exception as e:
            logger.warning(f"Failed to compute fluency score: {e}")
            return 0.0
    
    def _calculate_overall_quality_score(
        self,
        metrics: Dict[QualityMetric, float],
        baseline_comparison: Dict[QualityMetric, float]
    ) -> float:
        """Calculate overall quality score from individual metrics."""
        if not baseline_comparison:
            return 0.0
        
        # Weighted average of baseline comparisons
        weights = {
            QualityMetric.PERPLEXITY: 0.25,
            QualityMetric.SEMANTIC_SIMILARITY: 0.20,
            QualityMetric.SEQUENCE_COHERENCE: 0.15,
            QualityMetric.ATTENTION_COHERENCE: 0.15,
            QualityMetric.FLUENCY_SCORE: 0.15,
            QualityMetric.BLEU_SCORE: 0.10
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for metric_type, ratio in baseline_comparison.items():
            weight = weights.get(metric_type, 0.1)
            weighted_score += ratio * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_quality_threshold(self, overall_score: float) -> QualityThreshold:
        """Determine quality threshold based on overall score."""
        if overall_score >= 0.95:
            return QualityThreshold.EXCELLENT
        elif overall_score >= 0.90:
            return QualityThreshold.GOOD
        elif overall_score >= 0.85:
            return QualityThreshold.ACCEPTABLE
        elif overall_score >= 0.80:
            return QualityThreshold.DEGRADED
        else:
            return QualityThreshold.POOR
    
    def _evaluate_test_pass(
        self,
        baseline_comparison: Dict[QualityMetric, float],
        quality_threshold: QualityThreshold
    ) -> bool:
        """Evaluate whether test passes based on thresholds."""
        # Pass if quality is acceptable or better
        if quality_threshold in [QualityThreshold.EXCELLENT, QualityThreshold.GOOD, QualityThreshold.ACCEPTABLE]:
            return True
        
        # Additional checks for edge cases
        critical_metrics = [QualityMetric.PERPLEXITY, QualityMetric.SEMANTIC_SIMILARITY]
        
        for metric_type in critical_metrics:
            if metric_type in baseline_comparison:
                ratio = baseline_comparison[metric_type]
                
                # Minimum acceptable ratio for critical metrics
                min_ratio = 0.80 if metric_type == QualityMetric.PERPLEXITY else 0.75
                
                if ratio < min_ratio:
                    return False
        
        return quality_threshold != QualityThreshold.POOR
    
    def _cache_benchmark(self, benchmark: QualityBenchmark):
        """Cache benchmark to disk."""
        try:
            cache_file = self.quality_cache_dir / f"{benchmark.name}.json"
            
            # Convert to serializable format
            cache_data = {
                "name": benchmark.name,
                "context_length": benchmark.context_length,
                "input_tokens": benchmark.input_tokens.tolist(),
                "reference_output": benchmark.reference_output.tolist(),
                "baseline_metrics": {
                    metric.value: value for metric, value in benchmark.baseline_metrics.items()
                },
                "metadata": benchmark.metadata,
                "created_timestamp": benchmark.created_timestamp
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to cache benchmark: {e}")
    
    def load_cached_benchmark(self, name: str) -> Optional[QualityBenchmark]:
        """Load benchmark from cache."""
        try:
            cache_file = self.quality_cache_dir / f"{name}.json"
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Convert back to benchmark
            benchmark = QualityBenchmark(
                name=cache_data["name"],
                context_length=cache_data["context_length"],
                input_tokens=torch.tensor(cache_data["input_tokens"]),
                reference_output=torch.tensor(cache_data["reference_output"]),
                baseline_metrics={
                    QualityMetric(metric): value 
                    for metric, value in cache_data["baseline_metrics"].items()
                },
                metadata=cache_data["metadata"],
                created_timestamp=cache_data["created_timestamp"]
            )
            
            self.benchmarks[name] = benchmark
            return benchmark
            
        except Exception as e:
            logger.warning(f"Failed to load cached benchmark: {e}")
            return None
    
    def get_quality_analytics(self) -> Dict[str, Any]:
        """Get comprehensive quality analytics."""
        if not self.test_results:
            return {"message": "No test results available"}
        
        # Recent results (last 24 hours)
        recent_cutoff = time.time() - 86400
        recent_results = [r for r in self.test_results if r.test_timestamp > recent_cutoff]
        
        # Quality trends
        quality_scores = [r.overall_quality_score for r in self.test_results]
        recent_quality_scores = [r.overall_quality_score for r in recent_results]
        
        analytics = {
            "total_tests": len(self.test_results),
            "recent_tests": len(recent_results),
            "overall_stats": {
                "mean_quality_score": sum(quality_scores) / len(quality_scores),
                "min_quality_score": min(quality_scores),
                "max_quality_score": max(quality_scores),
                "passing_rate": sum(1 for r in self.test_results if r.passed) / len(self.test_results)
            },
            "recent_stats": {
                "mean_quality_score": sum(recent_quality_scores) / len(recent_quality_scores) if recent_quality_scores else 0,
                "passing_rate": sum(1 for r in recent_results if r.passed) / len(recent_results) if recent_results else 0
            },
            "quality_distribution": {
                threshold.value: sum(1 for r in self.test_results if r.quality_threshold == threshold)
                for threshold in QualityThreshold
            },
            "benchmarks_available": len(self.benchmarks),
            "regression_suites": len(self.regression_suites)
        }
        
        return analytics


# Global quality assurance instance
_global_qa_system: Optional[QualityAssuranceSystem] = None


def get_quality_assurance_system() -> QualityAssuranceSystem:
    """Get or create the global quality assurance system."""
    global _global_qa_system
    
    if _global_qa_system is None:
        _global_qa_system = QualityAssuranceSystem()
    
    return _global_qa_system


def create_quality_assurance_system(
    baseline_model: Optional[torch.nn.Module] = None,
    quality_cache_dir: str = "quality_cache",
    enable_caching: bool = True,
    verbose: bool = True
) -> QualityAssuranceSystem:
    """Create a new quality assurance system with custom configuration."""
    return QualityAssuranceSystem(
        baseline_model=baseline_model,
        quality_cache_dir=quality_cache_dir,
        enable_caching=enable_caching,
        verbose=verbose
    )


if __name__ == "__main__":
    # Test the quality assurance system
    qa_system = QualityAssuranceSystem()
    
    print("Testing quality assurance system...")
    
    # Create a test benchmark
    input_tokens = torch.randint(0, 1000, (128,))
    reference_output = torch.randint(0, 1000, (64,))
    
    benchmark = qa_system.create_benchmark(
        "test_benchmark",
        input_tokens,
        reference_output,
        metadata={"test": True}
    )
    
    print(f"Created benchmark: {benchmark.name}")
    
    # Get analytics
    analytics = qa_system.get_quality_analytics()
    print(f"Quality analytics: {analytics}")
    
    print("Quality assurance test completed")
