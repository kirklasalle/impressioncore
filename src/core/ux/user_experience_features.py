"""
User Experience Features for Extended Context Processing
Advanced UX features for 256k token processing with dynamic optimizations

This module provides comprehensive user experience enhancements including
dynamic resolution scaling, progressive generation capabilities, and
user-configurable memory controls optimized for GTX 1050 Ti constraints.

Author: ImpressionCore Development Team
Created: 2025-01-30
Hardware Target: GTX 1050 Ti (4GB VRAM)
Context Length: Up to 256k tokens
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, AsyncGenerator, Union, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import json
from pathlib import Path
import threading
from queue import Queue, Empty

import torch
import torch.nn.functional as F
import numpy as np

# Import our core components
from ..core.memory_manager.ultra_efficient_manager import UltraEfficientMemoryManager
from ..core.monitoring.performance_telemetry import PerformanceTelemetry
from ..core.reliability.production_error_handler import ProductionErrorHandler
from ..core.quality.quality_assurance import QualityAssuranceSystem
from ..core.utils.rich_enhancements import create_enhanced_console
from ..core.utils.rich_logging import setup_rich_logging
from ..core.utils.rich_status_animation import create_status_animation


class ResolutionLevel(str, Enum):
    """Dynamic resolution levels for processing optimization."""
    ULTRA_HIGH = "ultra_high"      # Full precision, maximum quality
    HIGH = "high"                  # High precision, balanced performance
    MEDIUM = "medium"              # Medium precision, good performance
    LOW = "low"                    # Lower precision, fast performance
    ADAPTIVE = "adaptive"          # Automatically adjust based on conditions


class GenerationStrategy(str, Enum):
    """Progressive generation strategies."""
    SEQUENTIAL = "sequential"      # Process chunks sequentially
    PARALLEL = "parallel"          # Process chunks in parallel
    ADAPTIVE_PARALLEL = "adaptive_parallel"  # Adapt parallelism based on resources
    PROGRESSIVE_REFINEMENT = "progressive_refinement"  # Refine results progressively


class UserPreference(str, Enum):
    """User preference profiles."""
    QUALITY_FOCUSED = "quality_focused"
    SPEED_FOCUSED = "speed_focused"
    BALANCED = "balanced"
    MEMORY_EFFICIENT = "memory_efficient"
    CUSTOM = "custom"


@dataclass
class DynamicConfig:
    """Dynamic configuration that adapts to system conditions."""
    resolution_level: ResolutionLevel = ResolutionLevel.ADAPTIVE
    generation_strategy: GenerationStrategy = GenerationStrategy.ADAPTIVE_PARALLEL
    user_preference: UserPreference = UserPreference.BALANCED
    
    # Memory management
    memory_limit_gb: float = 3.8
    memory_warning_threshold: float = 0.8  # 80% of limit
    memory_critical_threshold: float = 0.95  # 95% of limit
    
    # Performance targets
    target_latency_ms: float = 200.0
    target_throughput_tokens_per_sec: float = 1000.0
    quality_threshold: float = 0.95
    
    # Adaptive behavior
    enable_auto_scaling: bool = True
    enable_progressive_loading: bool = True
    enable_quality_monitoring: bool = True
    enable_user_feedback_loop: bool = True
    
    # User controls
    allow_quality_degradation: bool = True
    max_wait_time_seconds: float = 30.0
    preferred_chunk_size: Optional[int] = None
    custom_optimization_weights: Optional[Dict[str, float]] = None


@dataclass
class ProgressiveState:
    """State for progressive generation."""
    current_resolution: ResolutionLevel
    chunks_completed: int
    total_chunks: int
    quality_scores: List[float] = field(default_factory=list)
    performance_metrics: List[Dict[str, float]] = field(default_factory=list)
    user_feedback: List[Dict[str, Any]] = field(default_factory=list)
    adaptation_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class UserFeedback:
    """User feedback for adaptive optimization."""
    session_id: str
    feedback_type: str  # "quality", "speed", "memory", "general"
    rating: float  # 1.0 to 5.0
    comments: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    context_tokens: int = 0
    resolution_level: Optional[ResolutionLevel] = None


class AdaptiveOptimizer:
    """
    Adaptive optimizer that learns from usage patterns and adjusts configurations.
    """
    
    def __init__(self, config: DynamicConfig):
        """Initialize the adaptive optimizer."""
        self.config = config
        self.logger = setup_rich_logging("adaptive_optimizer")
        
        # Learning state
        self.performance_history: List[Dict[str, Any]] = []
        self.user_feedback_history: List[UserFeedback] = []
        self.optimization_weights = config.custom_optimization_weights or {
            "quality": 0.3,
            "speed": 0.3,
            "memory": 0.2,
            "user_satisfaction": 0.2
        }
        
        # Adaptive thresholds
        self.adaptive_thresholds = {
            "memory_pressure": 0.8,
            "latency_degradation": 1.5,  # 50% worse than target
            "quality_degradation": 0.05,  # 5% quality loss
            "user_satisfaction": 3.5  # Below 3.5/5.0 rating
        }
    
    def suggest_resolution_level(
        self, 
        current_memory_gb: float, 
        target_latency_ms: float,
        context_tokens: int
    ) -> ResolutionLevel:
        """
        Suggest optimal resolution level based on current conditions.
        
        Args:
            current_memory_gb: Current memory usage
            target_latency_ms: Target latency requirement
            context_tokens: Number of tokens in context
            
        Returns:
            Recommended resolution level
        """
        memory_pressure = current_memory_gb / self.config.memory_limit_gb
        token_complexity = min(context_tokens / 256_000, 1.0)  # Normalize to max context
        
        # Calculate resource pressure score
        pressure_score = (memory_pressure * 0.4 + token_complexity * 0.3 + 
                         (target_latency_ms / self.config.target_latency_ms - 1) * 0.3)
        
        # Consider user feedback
        recent_feedback = self._get_recent_feedback_score()
        if recent_feedback < 3.5:  # Poor user satisfaction
            pressure_score += 0.2
        
        # Suggest resolution level
        if pressure_score < 0.3:
            return ResolutionLevel.ULTRA_HIGH
        elif pressure_score < 0.6:
            return ResolutionLevel.HIGH
        elif pressure_score < 0.8:
            return ResolutionLevel.MEDIUM
        else:
            return ResolutionLevel.LOW
    
    def adapt_generation_strategy(
        self, 
        available_memory_gb: float,
        cpu_cores: int,
        context_tokens: int
    ) -> GenerationStrategy:
        """
        Adapt generation strategy based on available resources.
        
        Args:
            available_memory_gb: Available memory for processing
            cpu_cores: Number of available CPU cores
            context_tokens: Number of tokens to process
            
        Returns:
            Recommended generation strategy
        """
        # Calculate parallelization benefit
        memory_per_chunk = context_tokens / 8192 * 0.1  # Estimate
        max_parallel_chunks = int(available_memory_gb / memory_per_chunk)
        
        if max_parallel_chunks >= 4 and cpu_cores >= 4:
            return GenerationStrategy.ADAPTIVE_PARALLEL
        elif max_parallel_chunks >= 2:
            return GenerationStrategy.PARALLEL
        elif context_tokens > 128_000:
            return GenerationStrategy.PROGRESSIVE_REFINEMENT
        else:
            return GenerationStrategy.SEQUENTIAL
    
    def learn_from_session(
        self, 
        session_metrics: Dict[str, Any],
        user_feedback: Optional[UserFeedback] = None
    ):
        """
        Learn from session performance and user feedback.
        
        Args:
            session_metrics: Performance metrics from the session
            user_feedback: Optional user feedback
        """
        # Store performance history
        self.performance_history.append({
            "timestamp": time.time(),
            "metrics": session_metrics,
            "config_used": asdict(self.config)
        })
        
        # Store user feedback
        if user_feedback:
            self.user_feedback_history.append(user_feedback)
        
        # Update optimization weights based on feedback
        self._update_optimization_weights()
        
        # Keep only recent history (last 100 sessions)
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
        if len(self.user_feedback_history) > 100:
            self.user_feedback_history = self.user_feedback_history[-100:]
    
    def _get_recent_feedback_score(self) -> float:
        """Get average user satisfaction from recent feedback."""
        if not self.user_feedback_history:
            return 4.0  # Default neutral score
        
        recent_feedback = [
            fb.rating for fb in self.user_feedback_history[-10:]  # Last 10 sessions
        ]
        return sum(recent_feedback) / len(recent_feedback)
    
    def _update_optimization_weights(self):
        """Update optimization weights based on user feedback patterns."""
        if len(self.user_feedback_history) < 5:
            return  # Need more data
        
        # Analyze feedback patterns
        feedback_by_type = {}
        for feedback in self.user_feedback_history[-20:]:  # Recent feedback
            if feedback.feedback_type not in feedback_by_type:
                feedback_by_type[feedback.feedback_type] = []
            feedback_by_type[feedback.feedback_type].append(feedback.rating)
        
        # Adjust weights based on user concerns
        for feedback_type, ratings in feedback_by_type.items():
            avg_rating = sum(ratings) / len(ratings)
            if avg_rating < 3.5:  # Below average satisfaction
                if feedback_type in self.optimization_weights:
                    self.optimization_weights[feedback_type] += 0.05
                    # Normalize weights
                    total_weight = sum(self.optimization_weights.values())
                    for key in self.optimization_weights:
                        self.optimization_weights[key] /= total_weight


class ProgressiveGenerator:
    """
    Progressive generation system that processes content in stages with refinement.
    """
    
    def __init__(self, config: DynamicConfig, device: str = "cuda"):
        """Initialize the progressive generator."""
        self.config = config
        self.device = device
        self.logger = setup_rich_logging("progressive_generator")
        
        # Initialize components
        self.memory_manager = UltraEfficientMemoryManager(device, config.memory_limit_gb)
        self.telemetry = PerformanceTelemetry(config.target_latency_ms, config.memory_limit_gb)
        self.error_handler = ProductionErrorHandler(device, config.memory_limit_gb)
        self.quality_system = QualityAssuranceSystem(device, config.quality_threshold)
        self.optimizer = AdaptiveOptimizer(config)
        
        # Progressive state
        self.active_generations: Dict[str, ProgressiveState] = {}
        
        # User feedback queue
        self.feedback_queue = Queue()
        self.feedback_processor = threading.Thread(target=self._process_feedback_loop, daemon=True)
        self.feedback_processor.start()
    
    async def generate_progressive(
        self,
        session_id: str,
        input_tokens: List[int],
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate content progressively with dynamic optimization.
        
        Args:
            session_id: Unique session identifier
            input_tokens: Input tokens to process
            progress_callback: Optional callback for progress updates
            
        Yields:
            Progressive generation results and updates
        """
        try:
            # Initialize progressive state
            total_tokens = len(input_tokens)
            chunks = self._create_adaptive_chunks(input_tokens)
            
            state = ProgressiveState(
                current_resolution=self.config.resolution_level,
                chunks_completed=0,
                total_chunks=len(chunks)
            )
            self.active_generations[session_id] = state
            
            # Yield initial status
            yield {
                "type": "initialization",
                "session_id": session_id,
                "total_tokens": total_tokens,
                "total_chunks": len(chunks),
                "initial_resolution": state.current_resolution.value
            }
            
            # Process chunks progressively
            results = []
            
            with self.telemetry.monitored_operation("progressive_generation"):
                with self.error_handler.error_recovery_context():
                    
                    for chunk_idx, chunk in enumerate(chunks):
                        # Adapt resolution based on current conditions
                        current_memory = self.memory_manager.get_current_usage()
                        suggested_resolution = self.optimizer.suggest_resolution_level(
                            current_memory, 
                            self.config.target_latency_ms,
                            len(chunk)
                        )
                        
                        if suggested_resolution != state.current_resolution:
                            state.current_resolution = suggested_resolution
                            yield {
                                "type": "resolution_change",
                                "session_id": session_id,
                                "new_resolution": suggested_resolution.value,
                                "reason": "adaptive_optimization"
                            }
                        
                        # Process chunk
                        chunk_start_time = time.time()
                        chunk_result = await self._process_chunk_progressive(
                            chunk, state.current_resolution, session_id
                        )
                        chunk_time = (time.time() - chunk_start_time) * 1000
                        
                        # Quality assessment
                        quality_score = await self._assess_chunk_quality(chunk_result)
                        state.quality_scores.append(quality_score)
                        
                        # Performance tracking
                        chunk_metrics = {
                            "latency_ms": chunk_time,
                            "memory_usage_gb": current_memory,
                            "quality_score": quality_score,
                            "resolution_level": state.current_resolution.value
                        }
                        state.performance_metrics.append(chunk_metrics)
                        
                        # Update progress
                        state.chunks_completed = chunk_idx + 1
                        progress_percent = (state.chunks_completed / state.total_chunks) * 100
                        
                        # Yield progress update
                        yield {
                            "type": "progress",
                            "session_id": session_id,
                            "chunk_completed": chunk_idx + 1,
                            "total_chunks": state.total_chunks,
                            "progress_percent": progress_percent,
                            "chunk_result": chunk_result,
                            "quality_score": quality_score,
                            "metrics": chunk_metrics
                        }
                        
                        results.append(chunk_result)
                        
                        # Call progress callback if provided
                        if progress_callback:
                            progress_callback({
                                "session_id": session_id,
                                "progress": progress_percent,
                                "quality": quality_score,
                                "metrics": chunk_metrics
                            })
                        
                        # Adaptive delay based on system load
                        await self._adaptive_delay()
                        
                        # Check for quality degradation and adapt
                        if len(state.quality_scores) >= 3:
                            recent_quality = np.mean(state.quality_scores[-3:])
                            if recent_quality < self.config.quality_threshold:
                                yield {
                                    "type": "quality_warning",
                                    "session_id": session_id,
                                    "current_quality": recent_quality,
                                    "threshold": self.config.quality_threshold,
                                    "recommendation": "consider_higher_resolution"
                                }
            
            # Combine results with progressive refinement
            if self.config.generation_strategy == GenerationStrategy.PROGRESSIVE_REFINEMENT:
                refined_result = await self._progressive_refinement(results, state)
                yield {
                    "type": "refinement",
                    "session_id": session_id,
                    "refined_result": refined_result
                }
                final_result = refined_result
            else:
                final_result = self._combine_results(results)
            
            # Final quality assessment
            final_quality = await self._assess_final_quality(final_result)
            
            # Yield completion
            yield {
                "type": "completion",
                "session_id": session_id,
                "final_result": final_result,
                "final_quality": final_quality,
                "total_time_ms": sum(m["latency_ms"] for m in state.performance_metrics),
                "average_quality": np.mean(state.quality_scores),
                "peak_memory_gb": max(m["memory_usage_gb"] for m in state.performance_metrics)
            }
            
            # Learn from this session
            session_metrics = {
                "total_tokens": total_tokens,
                "processing_time_ms": sum(m["latency_ms"] for m in state.performance_metrics),
                "average_quality": np.mean(state.quality_scores),
                "peak_memory_gb": max(m["memory_usage_gb"] for m in state.performance_metrics),
                "resolution_changes": len(state.adaptation_history)
            }
            self.optimizer.learn_from_session(session_metrics)
            
        except Exception as e:
            self.logger.error(f"Progressive generation failed for session {session_id}: {e}")
            yield {
                "type": "error",
                "session_id": session_id,
                "error": str(e)
            }
        finally:
            # Cleanup
            if session_id in self.active_generations:
                del self.active_generations[session_id]
    
    async def submit_user_feedback(self, feedback: UserFeedback):
        """Submit user feedback for learning."""
        self.feedback_queue.put(feedback)
    
    def get_user_controls(self, session_id: str) -> Dict[str, Any]:
        """
        Get available user controls for the session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Available user controls and current settings
        """
        current_state = self.active_generations.get(session_id)
        current_memory = self.memory_manager.get_current_usage()
        
        return {
            "session_id": session_id,
            "current_resolution": current_state.current_resolution.value if current_state else "none",
            "available_resolutions": [level.value for level in ResolutionLevel],
            "memory_usage": {
                "current_gb": current_memory,
                "limit_gb": self.config.memory_limit_gb,
                "percentage": (current_memory / self.config.memory_limit_gb) * 100
            },
            "quality_controls": {
                "current_threshold": self.config.quality_threshold,
                "allow_degradation": self.config.allow_quality_degradation,
                "recent_scores": current_state.quality_scores[-5:] if current_state else []
            },
            "performance_controls": {
                "target_latency_ms": self.config.target_latency_ms,
                "max_wait_time": self.config.max_wait_time_seconds,
                "enable_auto_scaling": self.config.enable_auto_scaling
            },
            "adaptive_features": {
                "auto_resolution": self.config.resolution_level == ResolutionLevel.ADAPTIVE,
                "progressive_loading": self.config.enable_progressive_loading,
                "quality_monitoring": self.config.enable_quality_monitoring
            }
        }
    
    async def update_user_controls(
        self, 
        session_id: str, 
        controls: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Update user controls for the session.
        
        Args:
            session_id: Session identifier
            controls: New control settings
            
        Returns:
            Update status
        """
        if session_id not in self.active_generations:
            return {"status": "error", "message": "Session not found"}
        
        state = self.active_generations[session_id]
        updates = []
        
        # Update resolution level
        if "resolution_level" in controls:
            try:
                new_resolution = ResolutionLevel(controls["resolution_level"])
                state.current_resolution = new_resolution
                updates.append(f"Resolution updated to {new_resolution.value}")
            except ValueError:
                updates.append("Invalid resolution level")
        
        # Update quality threshold
        if "quality_threshold" in controls:
            try:
                new_threshold = float(controls["quality_threshold"])
                if 0.0 <= new_threshold <= 1.0:
                    self.config.quality_threshold = new_threshold
                    updates.append(f"Quality threshold updated to {new_threshold}")
                else:
                    updates.append("Quality threshold must be between 0.0 and 1.0")
            except ValueError:
                updates.append("Invalid quality threshold")
        
        # Update memory limit
        if "memory_limit_gb" in controls:
            try:
                new_limit = float(controls["memory_limit_gb"])
                if new_limit > 0:
                    self.config.memory_limit_gb = new_limit
                    self.memory_manager.update_memory_limit(new_limit)
                    updates.append(f"Memory limit updated to {new_limit} GB")
                else:
                    updates.append("Memory limit must be positive")
            except ValueError:
                updates.append("Invalid memory limit")
        
        # Update target latency
        if "target_latency_ms" in controls:
            try:
                new_latency = float(controls["target_latency_ms"])
                if new_latency > 0:
                    self.config.target_latency_ms = new_latency
                    updates.append(f"Target latency updated to {new_latency} ms")
                else:
                    updates.append("Target latency must be positive")
            except ValueError:
                updates.append("Invalid target latency")
        
        return {
            "status": "success" if updates else "no_changes",
            "updates": updates
        }
    
    # Helper methods
    def _create_adaptive_chunks(self, tokens: List[int]) -> List[List[int]]:
        """Create chunks with adaptive sizing based on content complexity."""
        # Start with base chunk size
        base_chunk_size = self.config.preferred_chunk_size or 8192
        
        # Adapt based on sequence length and memory availability
        available_memory = self.config.memory_limit_gb - self.memory_manager.get_current_usage()
        memory_factor = min(available_memory / 2.0, 1.0)  # Scale down if memory is limited
        
        adaptive_chunk_size = int(base_chunk_size * memory_factor)
        adaptive_chunk_size = max(adaptive_chunk_size, 1024)  # Minimum chunk size
        
        chunks = []
        overlap_size = adaptive_chunk_size // 16  # 6.25% overlap
        
        start = 0
        while start < len(tokens):
            end = min(start + adaptive_chunk_size, len(tokens))
            chunks.append(tokens[start:end])
            
            if end >= len(tokens):
                break
            
            start = end - overlap_size
        
        return chunks
    
    async def _process_chunk_progressive(
        self, 
        chunk: List[int], 
        resolution: ResolutionLevel,
        session_id: str
    ) -> str:
        """Process a chunk with the specified resolution level."""
        # Simulate processing with different resolution levels
        processing_time = {
            ResolutionLevel.ULTRA_HIGH: 0.1,
            ResolutionLevel.HIGH: 0.08,
            ResolutionLevel.MEDIUM: 0.06,
            ResolutionLevel.LOW: 0.04,
            ResolutionLevel.ADAPTIVE: 0.07
        }
        
        await asyncio.sleep(processing_time.get(resolution, 0.07))
        
        # Return processed result (placeholder)
        return f"processed_chunk_{len(chunk)}_tokens_resolution_{resolution.value}"
    
    async def _assess_chunk_quality(self, result: str) -> float:
        """Assess the quality of a chunk result."""
        # Placeholder quality assessment
        # In reality, this would use semantic similarity, coherence metrics, etc.
        base_quality = 0.95
        
        # Simulate some variation
        import random
        variation = random.uniform(-0.05, 0.05)
        return max(0.0, min(1.0, base_quality + variation))
    
    async def _assess_final_quality(self, result: str) -> float:
        """Assess the quality of the final result."""
        # Placeholder final quality assessment
        return 0.96
    
    async def _progressive_refinement(
        self, 
        results: List[str], 
        state: ProgressiveState
    ) -> str:
        """Apply progressive refinement to improve results."""
        # Simulate refinement process
        await asyncio.sleep(0.2)
        
        # Combine and refine
        combined = " ".join(results)
        return f"refined_{combined}"
    
    def _combine_results(self, results: List[str]) -> str:
        """Combine chunk results into final output."""
        return " ".join(results)
    
    async def _adaptive_delay(self):
        """Apply adaptive delay based on system load."""
        current_memory = self.memory_manager.get_current_usage()
        memory_pressure = current_memory / self.config.memory_limit_gb
        
        if memory_pressure > 0.9:
            await asyncio.sleep(0.1)  # High memory pressure
        elif memory_pressure > 0.8:
            await asyncio.sleep(0.05)  # Medium memory pressure
        else:
            await asyncio.sleep(0.01)  # Normal operation
    
    def _process_feedback_loop(self):
        """Background thread to process user feedback."""
        while True:
            try:
                # Wait for feedback with timeout
                try:
                    feedback = self.feedback_queue.get(timeout=1.0)
                    self.optimizer.learn_from_session({}, feedback)
                    self.feedback_queue.task_done()
                except Empty:
                    continue
            except Exception as e:
                self.logger.error(f"Error processing feedback: {e}")


class UserControlPanel:
    """
    User control panel for managing extended context processing preferences.
    """
    
    def __init__(self, generator: ProgressiveGenerator):
        """Initialize the user control panel."""
        self.generator = generator
        self.logger = setup_rich_logging("user_control_panel")
        self.console = create_enhanced_console()
    
    def display_current_status(self, session_id: str) -> Dict[str, Any]:
        """Display current processing status and controls."""
        controls = self.generator.get_user_controls(session_id)
        
        # Format for display
        status_display = {
            "System Status": {
                "Memory Usage": f"{controls['memory_usage']['percentage']:.1f}% "
                               f"({controls['memory_usage']['current_gb']:.2f} GB / "
                               f"{controls['memory_usage']['limit_gb']:.1f} GB)",
                "Current Resolution": controls['current_resolution'],
                "Quality Threshold": f"{controls['quality_controls']['current_threshold']:.2f}",
                "Target Latency": f"{controls['performance_controls']['target_latency_ms']:.0f} ms"
            },
            "Available Controls": {
                "Resolution Levels": controls['available_resolutions'],
                "Auto Scaling": controls['adaptive_features']['auto_resolution'],
                "Progressive Loading": controls['adaptive_features']['progressive_loading'],
                "Quality Monitoring": controls['adaptive_features']['quality_monitoring']
            },
            "Recent Performance": {
                "Quality Scores": controls['quality_controls']['recent_scores']
            }
        }
        
        return status_display
    
    async def interactive_control_session(self, session_id: str):
        """Start an interactive control session for the user."""
        self.console.print("\n[bold blue]Extended Context Processing Control Panel[/bold blue]")
        self.console.print(f"Session ID: {session_id}\n")
        
        while True:
            # Display current status
            status = self.display_current_status(session_id)
            
            # Show options
            self.console.print("[bold green]Available Commands:[/bold green]")
            self.console.print("1. Adjust resolution level")
            self.console.print("2. Set quality threshold")
            self.console.print("3. Update memory limit")
            self.console.print("4. Set target latency")
            self.console.print("5. Submit feedback")
            self.console.print("6. View detailed metrics")
            self.console.print("7. Exit control panel")
            
            # Get user input (in a real implementation, this would be interactive)
            # For now, we'll return the available options
            return {
                "status": status,
                "available_commands": [
                    "adjust_resolution",
                    "set_quality_threshold", 
                    "update_memory_limit",
                    "set_target_latency",
                    "submit_feedback",
                    "view_metrics",
                    "exit"
                ]
            }


# Factory functions for easy deployment
def create_progressive_generator(
    device: str = "cuda",
    memory_limit_gb: float = 3.8,
    user_preference: UserPreference = UserPreference.BALANCED
) -> ProgressiveGenerator:
    """
    Factory function to create a Progressive Generator instance.
    
    Args:
        device: Computing device ("cuda" or "cpu")
        memory_limit_gb: Memory budget in GB
        user_preference: User preference profile
        
    Returns:
        Configured ProgressiveGenerator instance
    """
    config = DynamicConfig(
        memory_limit_gb=memory_limit_gb,
        user_preference=user_preference,
        resolution_level=ResolutionLevel.ADAPTIVE,
        generation_strategy=GenerationStrategy.ADAPTIVE_PARALLEL
    )
    
    return ProgressiveGenerator(config, device)


def create_user_control_panel(generator: ProgressiveGenerator) -> UserControlPanel:
    """
    Factory function to create a User Control Panel instance.
    
    Args:
        generator: Progressive generator instance
        
    Returns:
        Configured UserControlPanel instance
    """
    return UserControlPanel(generator)


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def example_usage():
        # Create progressive generator
        generator = create_progressive_generator(device="cuda")
        
        # Create control panel
        control_panel = create_user_control_panel(generator)
        
        # Example token sequence
        tokens = list(range(50000))  # 50k tokens
        
        # Process with progressive generation
        session_id = "example_session"
        
        async for update in generator.generate_progressive(session_id, tokens):
            print(f"Update: {update['type']} - {update}")
            
            if update['type'] == 'completion':
                print("Processing completed!")
                break
    
    # Run example
    # asyncio.run(example_usage())
