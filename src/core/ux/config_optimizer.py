"""
Configuration Optimizer for ImpressionCore

This module provides intelligent configuration optimization using multi-objective
optimization techniques to balance speed, quality, and memory usage based on
hardware capabilities and user preferences.

Author: GitHub Copilot & Kirk LaSalle
Created: May 30, 2025
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any, NamedTuple
from pathlib import Path
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import threading

# Rich enhancements for better UX
try:
    from ..utils.rich_enhancements import RichEnhancements
    from ..utils.rich_logging import get_rich_logger
    from ..utils.rich_status_animation import StatusAnimation
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Core ImpressionCore imports
from .hardware_detector import HardwareDetector, HardwareCapabilities
from .user_profiles import UserProfileManager, UserProfile


class OptimizationObjective(NamedTuple):
    """Represents an optimization objective with weight and direction."""
    name: str
    weight: float  # 0.0 to 1.0
    maximize: bool  # True to maximize, False to minimize


@dataclass
class ConfigurationCandidate:
    """Represents a configuration candidate for optimization."""
    config: Dict[str, Any]
    performance_score: float
    memory_usage: float
    quality_score: float
    user_satisfaction: float
    
    def __post_init__(self):
        """Calculate aggregate metrics."""
        self.aggregate_score = (
            0.3 * self.performance_score +
            0.25 * (1.0 - self.memory_usage) +  # Lower memory is better
            0.3 * self.quality_score +
            0.15 * self.user_satisfaction
        )


@dataclass
class OptimizationResult:
    """Result of configuration optimization."""
    optimal_config: Dict[str, Any]
    pareto_front: List[ConfigurationCandidate]
    optimization_time: float
    iterations: int
    convergence_achieved: bool
    improvement_percentage: float


class ConfigurationOptimizer:
    """
    Intelligent configuration optimizer using multi-objective optimization.
    
    Features:
    - Pareto-optimal configuration discovery
    - A/B testing framework
    - Dynamic adjustment algorithms
    - Hardware-aware optimization
    - User preference learning
    """
    
    def __init__(
        self,
        hardware_detector: HardwareDetector,
        user_profile_manager: UserProfileManager,
        config_dir: Optional[Path] = None,
        enable_ab_testing: bool = True,
        optimization_budget: int = 100
    ):
        """
        Initialize the Configuration Optimizer.
        
        Args:
            hardware_detector: Hardware detection system
            user_profile_manager: User profile management system
            config_dir: Directory for storing optimization data
            enable_ab_testing: Whether to enable A/B testing
            optimization_budget: Maximum optimization iterations
        """
        self.hardware_detector = hardware_detector
        self.user_profile_manager = user_profile_manager
        self.enable_ab_testing = enable_ab_testing
        self.optimization_budget = optimization_budget
        
        # Setup logging
        if RICH_AVAILABLE:
            self.logger = get_rich_logger(__name__)
            self.rich = RichEnhancements()
            self.status_animation = StatusAnimation()
        else:
            self.logger = logging.getLogger(__name__)
            self.rich = None
            self.status_animation = None
        
        # Setup directories
        self.config_dir = config_dir or Path.cwd() / "config_optimization"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize optimization database
        self.db_path = self.config_dir / "optimization_history.db"
        self._init_database()
        
        # Optimization state
        self.current_objectives = [
            OptimizationObjective("performance", 0.3, True),
            OptimizationObjective("memory_efficiency", 0.25, True),
            OptimizationObjective("quality", 0.3, True),
            OptimizationObjective("user_satisfaction", 0.15, True)
        ]
        
        # A/B testing state
        self.ab_tests = {}
        self.ab_lock = threading.Lock()
        
        # Configuration templates
        self.config_templates = self._load_config_templates()
        
        self.logger.info("Configuration Optimizer initialized")
    
    def _init_database(self):
        """Initialize the optimization history database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optimization_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    hardware_profile TEXT NOT NULL,
                    user_profile TEXT NOT NULL,
                    objectives TEXT NOT NULL,
                    optimal_config TEXT NOT NULL,
                    performance_score REAL NOT NULL,
                    memory_usage REAL NOT NULL,
                    quality_score REAL NOT NULL,
                    user_satisfaction REAL NOT NULL,
                    optimization_time REAL NOT NULL,
                    iterations INTEGER NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ab_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT NOT NULL,
                    config_a TEXT NOT NULL,
                    config_b TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    status TEXT NOT NULL,
                    results TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pareto_front (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    optimization_run_id INTEGER NOT NULL,
                    config TEXT NOT NULL,
                    performance_score REAL NOT NULL,
                    memory_usage REAL NOT NULL,
                    quality_score REAL NOT NULL,
                    user_satisfaction REAL NOT NULL,
                    FOREIGN KEY (optimization_run_id) REFERENCES optimization_runs (id)
                )
            """)
    
    def _load_config_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load configuration templates for different use cases."""
        return {
            "speed_optimized": {
                "model_precision": "fp16",
                "batch_size": 1,
                "max_length": 512,
                "num_beams": 1,
                "do_sample": False,
                "use_cache": True,
                "gradient_checkpointing": False,
                "optimization_level": "O1"
            },
            "quality_optimized": {
                "model_precision": "fp32",
                "batch_size": 1,
                "max_length": 2048,
                "num_beams": 4,
                "do_sample": True,
                "temperature": 0.7,
                "top_p": 0.9,
                "use_cache": True,
                "gradient_checkpointing": True,
                "optimization_level": "O0"
            },
            "memory_optimized": {
                "model_precision": "fp16",
                "batch_size": 1,
                "max_length": 256,
                "num_beams": 1,
                "do_sample": False,
                "use_cache": False,
                "gradient_checkpointing": True,
                "optimization_level": "O2",
                "cpu_offload": True
            },
            "balanced": {
                "model_precision": "fp16",
                "batch_size": 1,
                "max_length": 1024,
                "num_beams": 2,
                "do_sample": True,
                "temperature": 0.8,
                "top_p": 0.95,
                "use_cache": True,
                "gradient_checkpointing": True,
                "optimization_level": "O1"
            }
        }
    
    async def optimize_configuration(
        self,
        base_config: Optional[Dict[str, Any]] = None,
        objectives: Optional[List[OptimizationObjective]] = None,
        user_id: Optional[str] = None
    ) -> OptimizationResult:
        """
        Optimize configuration using multi-objective optimization.
        
        Args:
            base_config: Base configuration to optimize from
            objectives: Custom optimization objectives
            user_id: User ID for personalized optimization
            
        Returns:
            OptimizationResult with optimal configuration and Pareto front
        """
        start_time = time.time()
        
        if self.status_animation:
            self.status_animation.start("Optimizing configuration...")
        
        try:
            # Get hardware capabilities
            hardware_caps = await self.hardware_detector.detect_capabilities()
            
            # Get user profile if available
            user_profile = None
            if user_id:
                user_profile = await self.user_profile_manager.get_profile(user_id)
            
            # Use custom objectives or defaults
            if objectives:
                self.current_objectives = objectives
            
            # Generate initial population
            population = await self._generate_initial_population(
                base_config, hardware_caps, user_profile
            )
            
            # Run optimization
            pareto_front = await self._optimize_population(
                population, hardware_caps, user_profile
            )
            
            # Select optimal configuration
            optimal_config = self._select_optimal_config(pareto_front, user_profile)
            
            optimization_time = time.time() - start_time
            
            # Calculate improvement
            baseline_score = await self._evaluate_configuration(
                base_config or self.config_templates["balanced"],
                hardware_caps, user_profile
            )
            optimal_score = optimal_config.aggregate_score
            improvement = ((optimal_score - baseline_score.aggregate_score) / 
                          baseline_score.aggregate_score * 100)
            
            result = OptimizationResult(
                optimal_config=optimal_config.config,
                pareto_front=pareto_front,
                optimization_time=optimization_time,
                iterations=len(population),
                convergence_achieved=True,
                improvement_percentage=improvement
            )
            
            # Store results
            await self._store_optimization_result(
                result, hardware_caps, user_profile
            )
            
            self.logger.info(
                f"Configuration optimization completed in {optimization_time:.2f}s "
                f"with {improvement:.1f}% improvement"
            )
            
            return result
            
        finally:
            if self.status_animation:
                self.status_animation.stop()
    
    async def _generate_initial_population(
        self,
        base_config: Optional[Dict[str, Any]],
        hardware_caps: HardwareCapabilities,
        user_profile: Optional[UserProfile]
    ) -> List[ConfigurationCandidate]:
        """Generate initial population for optimization."""
        population = []
        
        # Start with templates
        for template_name, template_config in self.config_templates.items():
            candidate = await self._evaluate_configuration(
                template_config, hardware_caps, user_profile
            )
            population.append(candidate)
        
        # Add base config if provided
        if base_config:
            candidate = await self._evaluate_configuration(
                base_config, hardware_caps, user_profile
            )
            population.append(candidate)
        
        # Generate random variations
        for _ in range(max(0, self.optimization_budget - len(population))):
            variant_config = self._generate_config_variant(hardware_caps, user_profile)
            candidate = await self._evaluate_configuration(
                variant_config, hardware_caps, user_profile
            )
            population.append(candidate)
        
        return population
    
    def _generate_config_variant(
        self,
        hardware_caps: HardwareCapabilities,
        user_profile: Optional[UserProfile]
    ) -> Dict[str, Any]:
        """Generate a configuration variant based on hardware and user preferences."""
        # Start with balanced template
        config = self.config_templates["balanced"].copy()
        
        # Adjust based on hardware constraints
        if hardware_caps.gpu_memory_gb < 6:
            config.update({
                "model_precision": "fp16",
                "gradient_checkpointing": True,
                "cpu_offload": True,
                "max_length": min(config.get("max_length", 1024), 512)
            })
        
        # Adjust based on user preferences
        if user_profile:
            if user_profile.profile_type == "speed_focused":
                config.update({
                    "num_beams": 1,
                    "do_sample": False,
                    "max_length": min(config.get("max_length", 1024), 256)
                })
            elif user_profile.profile_type == "quality_focused":
                config.update({
                    "num_beams": 4,
                    "do_sample": True,
                    "temperature": 0.7,
                    "top_p": 0.9
                })
        
        # Add some randomization
        config["temperature"] = np.random.uniform(0.1, 1.5)
        config["top_p"] = np.random.uniform(0.8, 1.0)
        config["batch_size"] = np.random.choice([1, 2, 4])
        
        return config
    
    async def _evaluate_configuration(
        self,
        config: Dict[str, Any],
        hardware_caps: HardwareCapabilities,
        user_profile: Optional[UserProfile]
    ) -> ConfigurationCandidate:
        """Evaluate a configuration candidate."""
        # Performance score (based on theoretical throughput)
        performance_score = self._calculate_performance_score(config, hardware_caps)
        
        # Memory usage score (normalized)
        memory_usage = self._calculate_memory_usage(config, hardware_caps)
        
        # Quality score (based on generation parameters)
        quality_score = self._calculate_quality_score(config)
        
        # User satisfaction (based on preferences)
        user_satisfaction = self._calculate_user_satisfaction(config, user_profile)
        
        return ConfigurationCandidate(
            config=config,
            performance_score=performance_score,
            memory_usage=memory_usage,
            quality_score=quality_score,
            user_satisfaction=user_satisfaction
        )
    
    def _calculate_performance_score(
        self, config: Dict[str, Any], hardware_caps: HardwareCapabilities
    ) -> float:
        """Calculate theoretical performance score for a configuration."""
        score = 1.0
        
        # Precision impact
        if config.get("model_precision") == "fp16":
            score *= 1.5  # FP16 is faster
        elif config.get("model_precision") == "int8":
            score *= 2.0  # INT8 is much faster
        
        # Batch size impact
        batch_size = config.get("batch_size", 1)
        score *= min(batch_size * 0.8, 2.0)  # Diminishing returns
        
        # Generation parameters
        num_beams = config.get("num_beams", 1)
        score /= max(num_beams * 0.3, 1.0)  # Beam search is slower
        
        # Length impact
        max_length = config.get("max_length", 512)
        score /= (max_length / 512) ** 0.5  # Quadratic complexity
        
        # Hardware capability factor
        if hardware_caps.performance_tier == "high_end":
            score *= 1.2
        elif hardware_caps.performance_tier == "low_end":
            score *= 0.7
        
        return min(score, 1.0)
    
    def _calculate_memory_usage(
        self, config: Dict[str, Any], hardware_caps: HardwareCapabilities
    ) -> float:
        """Calculate normalized memory usage for a configuration."""
        base_memory = 2.0  # Base model memory in GB
        
        # Precision impact
        if config.get("model_precision") == "fp32":
            memory_multiplier = 2.0
        elif config.get("model_precision") == "fp16":
            memory_multiplier = 1.0
        elif config.get("model_precision") == "int8":
            memory_multiplier = 0.5
        else:
            memory_multiplier = 1.0
        
        # Batch size impact
        batch_size = config.get("batch_size", 1)
        batch_multiplier = batch_size
        
        # Length impact
        max_length = config.get("max_length", 512)
        length_multiplier = max_length / 512
        
        # Caching impact
        if config.get("use_cache", True):
            cache_multiplier = 1.5
        else:
            cache_multiplier = 1.0
        
        total_memory = (base_memory * memory_multiplier * batch_multiplier * 
                       length_multiplier * cache_multiplier)
        
        # Normalize by available GPU memory
        normalized = total_memory / hardware_caps.gpu_memory_gb
        
        return min(normalized, 1.0)
    
    def _calculate_quality_score(self, config: Dict[str, Any]) -> float:
        """Calculate quality score based on generation parameters."""
        score = 0.5  # Base score
        
        # Precision impact on quality
        if config.get("model_precision") == "fp32":
            score += 0.3
        elif config.get("model_precision") == "fp16":
            score += 0.2
        elif config.get("model_precision") == "int8":
            score += 0.1
        
        # Beam search impact
        num_beams = config.get("num_beams", 1)
        if num_beams > 1:
            score += min(num_beams * 0.1, 0.3)
        
        # Sampling parameters
        if config.get("do_sample", False):
            temperature = config.get("temperature", 1.0)
            top_p = config.get("top_p", 1.0)
            
            # Optimal temperature range
            if 0.7 <= temperature <= 1.0:
                score += 0.1
            
            # Top-p filtering
            if 0.9 <= top_p <= 0.95:
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_user_satisfaction(
        self, config: Dict[str, Any], user_profile: Optional[UserProfile]
    ) -> float:
        """Calculate user satisfaction score based on preferences."""
        if not user_profile:
            return 0.5  # Neutral satisfaction
        
        score = 0.5
        
        # Match configuration to user preferences
        if user_profile.profile_type == "speed_focused":
            # Prefer faster configurations
            if config.get("num_beams", 1) == 1:
                score += 0.2
            if not config.get("do_sample", True):
                score += 0.2
            if config.get("max_length", 512) <= 256:
                score += 0.1
        
        elif user_profile.profile_type == "quality_focused":
            # Prefer higher quality configurations
            if config.get("num_beams", 1) > 1:
                score += 0.2
            if config.get("do_sample", False):
                score += 0.2
            if config.get("model_precision") == "fp32":
                score += 0.1
        
        elif user_profile.profile_type == "balanced":
            # Prefer balanced configurations
            if 2 <= config.get("num_beams", 1) <= 4:
                score += 0.2
            if config.get("model_precision") == "fp16":
                score += 0.2
            if 512 <= config.get("max_length", 512) <= 1024:
                score += 0.1
        
        return min(score, 1.0)
    
    async def _optimize_population(
        self,
        population: List[ConfigurationCandidate],
        hardware_caps: HardwareCapabilities,
        user_profile: Optional[UserProfile]
    ) -> List[ConfigurationCandidate]:
        """Optimize population using genetic algorithm principles."""
        current_population = population.copy()
        
        for generation in range(min(10, self.optimization_budget // 10)):
            # Select best candidates
            current_population.sort(key=lambda x: x.aggregate_score, reverse=True)
            elite = current_population[:len(current_population)//2]
            
            # Generate offspring through crossover and mutation
            offspring = []
            for i in range(len(elite)//2):
                parent1 = elite[i*2]
                parent2 = elite[i*2 + 1] if i*2 + 1 < len(elite) else elite[0]
                
                child_config = self._crossover_configs(parent1.config, parent2.config)
                child_config = self._mutate_config(child_config, hardware_caps)
                
                child = await self._evaluate_configuration(
                    child_config, hardware_caps, user_profile
                )
                offspring.append(child)
            
            # Combine elite and offspring
            current_population = elite + offspring
        
        # Return Pareto front
        return self._extract_pareto_front(current_population)
    
    def _crossover_configs(
        self, config1: Dict[str, Any], config2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform crossover between two configurations."""
        child_config = {}
        
        for key in set(config1.keys()) | set(config2.keys()):
            # Randomly choose parent for each parameter
            if np.random.random() < 0.5 and key in config1:
                child_config[key] = config1[key]
            elif key in config2:
                child_config[key] = config2[key]
            elif key in config1:
                child_config[key] = config1[key]
        
        return child_config
    
    def _mutate_config(
        self, config: Dict[str, Any], hardware_caps: HardwareCapabilities
    ) -> Dict[str, Any]:
        """Apply random mutations to a configuration."""
        mutated_config = config.copy()
        mutation_rate = 0.1
        
        for key, value in mutated_config.items():
            if np.random.random() < mutation_rate:
                if key == "temperature" and isinstance(value, (int, float)):
                    mutated_config[key] = np.clip(value + np.random.normal(0, 0.1), 0.1, 2.0)
                elif key == "top_p" and isinstance(value, (int, float)):
                    mutated_config[key] = np.clip(value + np.random.normal(0, 0.05), 0.1, 1.0)
                elif key == "num_beams" and isinstance(value, int):
                    mutated_config[key] = max(1, value + np.random.choice([-1, 0, 1]))
                elif key == "batch_size" and isinstance(value, int):
                    mutated_config[key] = np.random.choice([1, 2, 4, 8])
        
        return mutated_config
    
    def _extract_pareto_front(
        self, population: List[ConfigurationCandidate]
    ) -> List[ConfigurationCandidate]:
        """Extract Pareto-optimal configurations from population."""
        pareto_front = []
        
        for candidate in population:
            is_dominated = False
            
            for other in population:
                if (other.performance_score >= candidate.performance_score and
                    other.memory_usage <= candidate.memory_usage and
                    other.quality_score >= candidate.quality_score and
                    other.user_satisfaction >= candidate.user_satisfaction and
                    (other.performance_score > candidate.performance_score or
                     other.memory_usage < candidate.memory_usage or
                     other.quality_score > candidate.quality_score or
                     other.user_satisfaction > candidate.user_satisfaction)):
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_front.append(candidate)
        
        return pareto_front
    
    def _select_optimal_config(
        self,
        pareto_front: List[ConfigurationCandidate],
        user_profile: Optional[UserProfile]
    ) -> ConfigurationCandidate:
        """Select the optimal configuration from Pareto front."""
        if not pareto_front:
            return ConfigurationCandidate(
                config=self.config_templates["balanced"],
                performance_score=0.5,
                memory_usage=0.5,
                quality_score=0.5,
                user_satisfaction=0.5
            )
        
        # Weight objectives based on user profile
        if user_profile and user_profile.profile_type == "speed_focused":
            weights = {"performance": 0.5, "memory": 0.2, "quality": 0.2, "satisfaction": 0.1}
        elif user_profile and user_profile.profile_type == "quality_focused":
            weights = {"performance": 0.2, "memory": 0.2, "quality": 0.5, "satisfaction": 0.1}
        else:
            weights = {"performance": 0.3, "memory": 0.25, "quality": 0.3, "satisfaction": 0.15}
        
        # Calculate weighted scores
        best_candidate = None
        best_score = -1
        
        for candidate in pareto_front:
            weighted_score = (
                weights["performance"] * candidate.performance_score +
                weights["memory"] * (1.0 - candidate.memory_usage) +
                weights["quality"] * candidate.quality_score +
                weights["satisfaction"] * candidate.user_satisfaction
            )
            
            if weighted_score > best_score:
                best_score = weighted_score
                best_candidate = candidate
        
        return best_candidate or pareto_front[0]
    
    async def _store_optimization_result(
        self,
        result: OptimizationResult,
        hardware_caps: HardwareCapabilities,
        user_profile: Optional[UserProfile]
    ):
        """Store optimization result in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Store main optimization run
                cursor = conn.execute("""
                    INSERT INTO optimization_runs 
                    (timestamp, hardware_profile, user_profile, objectives, 
                     optimal_config, performance_score, memory_usage, 
                     quality_score, user_satisfaction, optimization_time, iterations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    time.time(),
                    json.dumps(hardware_caps.__dict__, default=str),
                    json.dumps(user_profile.__dict__ if user_profile else {}),
                    json.dumps([obj._asdict() for obj in self.current_objectives]),
                    json.dumps(result.optimal_config),
                    result.pareto_front[0].performance_score if result.pareto_front else 0.0,
                    result.pareto_front[0].memory_usage if result.pareto_front else 0.0,
                    result.pareto_front[0].quality_score if result.pareto_front else 0.0,
                    result.pareto_front[0].user_satisfaction if result.pareto_front else 0.0,
                    result.optimization_time,
                    result.iterations
                ))
                
                run_id = cursor.lastrowid
                
                # Store Pareto front
                for candidate in result.pareto_front:
                    conn.execute("""
                        INSERT INTO pareto_front 
                        (optimization_run_id, config, performance_score, 
                         memory_usage, quality_score, user_satisfaction)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        run_id,
                        json.dumps(candidate.config),
                        candidate.performance_score,
                        candidate.memory_usage,
                        candidate.quality_score,
                        candidate.user_satisfaction
                    ))
                
        except Exception as e:
            self.logger.error(f"Failed to store optimization result: {e}")
    
    async def start_ab_test(
        self,
        test_name: str,
        config_a: Dict[str, Any],
        config_b: Dict[str, Any],
        duration_hours: float = 24.0
    ) -> str:
        """Start an A/B test between two configurations."""
        if not self.enable_ab_testing:
            raise ValueError("A/B testing is disabled")
        
        test_id = f"{test_name}_{int(time.time())}"
        
        with self.ab_lock:
            self.ab_tests[test_id] = {
                "name": test_name,
                "config_a": config_a,
                "config_b": config_b,
                "start_time": time.time(),
                "duration": duration_hours * 3600,
                "results_a": [],
                "results_b": [],
                "status": "running"
            }
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO ab_tests (test_name, config_a, config_b, timestamp, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                test_name,
                json.dumps(config_a),
                json.dumps(config_b),
                time.time(),
                "running"
            ))
        
        self.logger.info(f"Started A/B test '{test_name}' with ID {test_id}")
        return test_id
    
    async def get_ab_test_config(self, test_id: str, user_id: str) -> Dict[str, Any]:
        """Get configuration for A/B test participant."""
        if test_id not in self.ab_tests:
            raise ValueError(f"A/B test {test_id} not found")
        
        test = self.ab_tests[test_id]
        
        # Simple hash-based assignment
        assignment_hash = hash(f"{test_id}_{user_id}") % 2
        
        if assignment_hash == 0:
            return test["config_a"]
        else:
            return test["config_b"]
    
    async def record_ab_test_result(
        self,
        test_id: str,
        user_id: str,
        performance_metrics: Dict[str, float]
    ):
        """Record A/B test result for a user."""
        if test_id not in self.ab_tests:
            raise ValueError(f"A/B test {test_id} not found")
        
        test = self.ab_tests[test_id]
        assignment_hash = hash(f"{test_id}_{user_id}") % 2
        
        result_entry = {
            "user_id": user_id,
            "timestamp": time.time(),
            "metrics": performance_metrics
        }
        
        with self.ab_lock:
            if assignment_hash == 0:
                test["results_a"].append(result_entry)
            else:
                test["results_b"].append(result_entry)
    
    async def finalize_ab_test(self, test_id: str) -> Dict[str, Any]:
        """Finalize A/B test and return results."""
        if test_id not in self.ab_tests:
            raise ValueError(f"A/B test {test_id} not found")
        
        test = self.ab_tests[test_id]
        
        # Calculate statistics
        results_a = test["results_a"]
        results_b = test["results_b"]
        
        if not results_a or not results_b:
            raise ValueError("Insufficient data for A/B test analysis")
        
        # Calculate mean metrics
        metrics_a = {}
        metrics_b = {}
        
        for metric in results_a[0]["metrics"].keys():
            values_a = [r["metrics"][metric] for r in results_a]
            values_b = [r["metrics"][metric] for r in results_b]
            
            metrics_a[metric] = {
                "mean": np.mean(values_a),
                "std": np.std(values_a),
                "count": len(values_a)
            }
            
            metrics_b[metric] = {
                "mean": np.mean(values_b),
                "std": np.std(values_b),
                "count": len(values_b)
            }
        
        # Update test status
        with self.ab_lock:
            test["status"] = "completed"
        
        # Update database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE ab_tests 
                SET status = ?, results = ?
                WHERE test_name = ? AND timestamp = (
                    SELECT MAX(timestamp) FROM ab_tests WHERE test_name = ?
                )
            """, (
                "completed",
                json.dumps({
                    "metrics_a": metrics_a,
                    "metrics_b": metrics_b,
                    "winner": "A" if metrics_a.get("aggregate_score", {}).get("mean", 0) > 
                            metrics_b.get("aggregate_score", {}).get("mean", 0) else "B"
                }),
                test["name"],
                test["name"]
            ))
        
        return {
            "test_name": test["name"],
            "config_a": test["config_a"],
            "config_b": test["config_b"],
            "metrics_a": metrics_a,
            "metrics_b": metrics_b,
            "winner": "A" if metrics_a.get("aggregate_score", {}).get("mean", 0) > 
                     metrics_b.get("aggregate_score", {}).get("mean", 0) else "B"
        }
    
    async def get_optimization_history(
        self, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get optimization history from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM optimization_runs 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old optimization data."""
        cutoff_time = time.time() - (days_to_keep * 24 * 3600)
        
        with sqlite3.connect(self.db_path) as conn:
            # Clean optimization runs
            conn.execute("""
                DELETE FROM optimization_runs 
                WHERE timestamp < ?
            """, (cutoff_time,))
            
            # Clean A/B tests
            conn.execute("""
                DELETE FROM ab_tests 
                WHERE timestamp < ?
            """, (cutoff_time,))
        
        self.logger.info(f"Cleaned up optimization data older than {days_to_keep} days")


# Example usage and testing
if __name__ == "__main__":
    async def test_config_optimizer():
        """Test the configuration optimizer."""
        # Initialize components
        hardware_detector = HardwareDetector(enable_benchmarking=False)
        user_profile_manager = UserProfileManager()
        
        optimizer = ConfigurationOptimizer(
            hardware_detector=hardware_detector,
            user_profile_manager=user_profile_manager,
            optimization_budget=20
        )
        
        # Test optimization
        result = await optimizer.optimize_configuration()
        
        print(f"Optimization completed in {result.optimization_time:.2f}s")
        print(f"Improvement: {result.improvement_percentage:.1f}%")
        print(f"Optimal config: {result.optimal_config}")
        print(f"Pareto front size: {len(result.pareto_front)}")
    
    # Run test
    asyncio.run(test_config_optimizer())
