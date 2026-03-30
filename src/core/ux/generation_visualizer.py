"""
Progressive Generation Visualizer - Phase 7B Priority 7 Implementation
Advanced Progressive Generation UI - Visualization Components

This module provides advanced visualization tools for progressive generation
processes, including multi-stage processing visualization, quality progression
charts, memory usage heat maps, and processing timeline displays.

Author: ImpressionCore Development Team
Created: 2025-05-30
Hardware Target: GTX 1050 Ti (4GB VRAM)
Phase: Priority 7 Phase 7B - Advanced Progressive Generation UI
Dependencies: Phase 7A (Enhanced Dynamic Configuration System)
"""

import asyncio
import time
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple, NamedTuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import logging
from collections import deque, defaultdict

# Rich library for enhanced visualization
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.tree import Tree
# from rich.gauge import Gauge  # Not available in Rich 14.0.0
from rich.box import ROUNDED, HEAVY, SIMPLE
from rich.color import Color

# Core ImpressionCore imports
try:
    from ..memory_manager.memory_optimizer import MemoryOptimizer, MemoryMetrics
    from ..monitoring.performance_monitor import PerformanceMonitor
    from .hardware_detector import HardwareDetector, HardwareInfo
    from .user_profiles import UserProfileManager, UserProfile
    from .config_optimizer import ConfigurationOptimizer, OptimizationResult
    from .user_experience_features import ProgressiveGenerator, ResolutionLevel
except ImportError:
    # Fallback for testing or standalone usage
    MemoryOptimizer = None
    PerformanceMonitor = None
    HardwareDetector = None
    UserProfileManager = None
    ConfigurationOptimizer = None
    ProgressiveGenerator = None


class VisualizationType(Enum):
    """Types of visualizations available."""
    PIPELINE = "pipeline"
    QUALITY_CHART = "quality_chart"
    MEMORY_HEATMAP = "memory_heatmap"
    TIMELINE = "timeline"
    PERFORMANCE_GRAPH = "performance_graph"
    RESOURCE_USAGE = "resource_usage"


class ProcessingStage(Enum):
    """Processing pipeline stages."""
    INPUT = "input"
    TOKENIZATION = "tokenization"
    EMBEDDING = "embedding"
    ATTENTION = "attention"
    GENERATION = "generation"
    POST_PROCESSING = "post_processing"
    OUTPUT = "output"


@dataclass
class PipelineState:
    """Current state of processing pipeline."""
    current_stage: ProcessingStage = ProcessingStage.INPUT
    stage_progress: Dict[ProcessingStage, float] = field(default_factory=dict)
    stage_metrics: Dict[ProcessingStage, Dict[str, Any]] = field(default_factory=dict)
    total_progress: float = 0.0
    estimated_completion: Optional[datetime] = None
    active_stages: List[ProcessingStage] = field(default_factory=list)
    bottlenecks: List[Tuple[ProcessingStage, str]] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize stage progress if empty."""
        if not self.stage_progress:
            for stage in ProcessingStage:
                self.stage_progress[stage] = 0.0
                self.stage_metrics[stage] = {}


@dataclass
class QualityMetric:
    """Quality measurement data point."""
    timestamp: datetime
    quality_score: float
    resolution_level: str
    processing_time: float
    memory_usage: float
    stage: ProcessingStage
    user_satisfaction: Optional[float] = None
    
    def __post_init__(self):
        """Validate quality metrics."""
        self.quality_score = max(0.0, min(1.0, self.quality_score))


@dataclass
class MemoryData:
    """Memory usage data for visualization."""
    timestamp: datetime
    gpu_memory: Dict[str, float]  # {allocation_type: mb_used}
    cpu_memory: Dict[str, float]
    memory_pools: Dict[str, Dict[str, float]]
    fragmentation_score: float
    allocation_efficiency: float
    
    def total_gpu_memory(self) -> float:
        """Calculate total GPU memory usage."""
        return sum(self.gpu_memory.values())
    
    def total_cpu_memory(self) -> float:
        """Calculate total CPU memory usage."""
        return sum(self.cpu_memory.values())


class ChartRenderer:
    """Renderer for various chart types using Rich components."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize chart renderer."""
        self.console = console or Console()
        self.color_palette = [
            "red", "green", "blue", "yellow", "magenta", "cyan",
            "bright_red", "bright_green", "bright_blue", "bright_yellow"
        ]
    
    def render_bar_chart(self, 
                        data: Dict[str, float], 
                        title: str = "Chart",
                        max_width: int = 50) -> Panel:
        """
        Render horizontal bar chart.
        
        Args:
            data: Dictionary of label -> value pairs
            title: Chart title
            max_width: Maximum width of bars
            
        Returns:
            Rich Panel containing the chart
        """
        if not data:
            return Panel("No data available", title=title)
        
        max_value = max(data.values()) if data.values() else 1
        
        chart_text = Text()
        for i, (label, value) in enumerate(data.items()):
            bar_length = int((value / max_value) * max_width)
            color = self.color_palette[i % len(self.color_palette)]
            
            # Create bar
            bar = "█" * bar_length + "░" * (max_width - bar_length)
            
            # Add to chart
            chart_text.append(f"{label:15} ", style="white")
            chart_text.append(f"[{bar}] ", style=color)
            chart_text.append(f"{value:.2f}\n", style="bright_white")
        
        return Panel(chart_text, title=title, box=ROUNDED)
    
    def render_line_graph(self, 
                         data_series: Dict[str, List[Tuple[float, float]]], 
                         title: str = "Graph",
                         width: int = 60,
                         height: int = 20) -> Panel:
        """
        Render ASCII line graph.
        
        Args:
            data_series: Dictionary of series_name -> [(x, y), ...] pairs
            title: Graph title
            width: Graph width in characters
            height: Graph height in characters
            
        Returns:
            Rich Panel containing the graph
        """
        if not data_series:
            return Panel("No data available", title=title)
        
        # Find data ranges
        all_x = []
        all_y = []
        for series in data_series.values():
            all_x.extend([point[0] for point in series])
            all_y.extend([point[1] for point in series])
        
        if not all_x or not all_y:
            return Panel("No data points", title=title)
        
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        
        # Avoid division by zero
        x_range = max_x - min_x if max_x != min_x else 1
        y_range = max_y - min_y if max_y != min_y else 1
        
        # Create graph grid
        graph = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Plot each series
        for i, (series_name, points) in enumerate(data_series.items()):
            char = ['*', '+', 'o', 'x', '#'][i % 5]
            
            for x, y in points:
                # Map to grid coordinates
                grid_x = int(((x - min_x) / x_range) * (width - 1))
                grid_y = int(((max_y - y) / y_range) * (height - 1))
                
                if 0 <= grid_x < width and 0 <= grid_y < height:
                    graph[grid_y][grid_x] = char
        
        # Convert to text
        graph_text = Text()
        for row in graph:
            graph_text.append(''.join(row) + '\n', style="cyan")
        
        # Add legend
        legend_text = Text("\nLegend: ")
        for i, series_name in enumerate(data_series.keys()):
            char = ['*', '+', 'o', 'x', '#'][i % 5]
            color = self.color_palette[i % len(self.color_palette)]
            legend_text.append(f"{char}={series_name} ", style=color)
        
        graph_text.append(legend_text)
        
        return Panel(graph_text, title=title, box=ROUNDED)
    
    def render_heatmap(self, 
                      data: List[List[float]], 
                      labels_x: List[str],
                      labels_y: List[str],
                      title: str = "Heatmap") -> Panel:
        """
        Render ASCII heatmap.
        
        Args:
            data: 2D array of values
            labels_x: X-axis labels
            labels_y: Y-axis labels
            title: Heatmap title
            
        Returns:
            Rich Panel containing the heatmap
        """
        if not data or not data[0]:
            return Panel("No data available", title=title)
        
        # Find min/max for normalization
        flat_data = [val for row in data for val in row]
        min_val, max_val = min(flat_data), max(flat_data)
        val_range = max_val - min_val if max_val != min_val else 1
        
        # Characters for different intensities
        intensity_chars = [' ', '░', '▒', '▓', '█']
        
        heatmap_text = Text()
        
        # Add column headers
        heatmap_text.append("     ")
        for label in labels_x:
            heatmap_text.append(f"{label:4}", style="white")
        heatmap_text.append("\n")
        
        # Add rows with data
        for i, row in enumerate(data):
            # Row label
            if i < len(labels_y):
                heatmap_text.append(f"{labels_y[i]:4} ", style="white")
            else:
                heatmap_text.append("     ")
            
            # Data cells
            for value in row:
                # Normalize value to intensity
                normalized = (value - min_val) / val_range
                intensity_idx = int(normalized * (len(intensity_chars) - 1))
                intensity_idx = max(0, min(len(intensity_chars) - 1, intensity_idx))
                
                # Color based on intensity
                if normalized > 0.8:
                    style = "bright_red"
                elif normalized > 0.6:
                    style = "red"
                elif normalized > 0.4:
                    style = "yellow"
                elif normalized > 0.2:
                    style = "green"
                else:
                    style = "blue"
                
                heatmap_text.append(intensity_chars[intensity_idx] * 4, style=style)
            
            heatmap_text.append("\n")
        
        return Panel(heatmap_text, title=title, box=ROUNDED)


class MemoryTracker:
    """Tracks memory usage for visualization."""
    
    def __init__(self, max_history: int = 1000):
        """Initialize memory tracker."""
        self.max_history = max_history
        self.memory_history: deque = deque(maxlen=max_history)
        self.allocation_types = [
            "model_weights", "activations", "gradients", "optimizer_states",
            "input_buffers", "output_buffers", "cache", "other"
        ]
    
    def record_memory_usage(self, memory_data: MemoryData) -> None:
        """Record memory usage data point."""
        self.memory_history.append(memory_data)
    
    def get_memory_timeline(self, seconds: int = 60) -> List[MemoryData]:
        """Get memory usage timeline for specified seconds."""
        cutoff_time = datetime.now() - timedelta(seconds=seconds)
        return [data for data in self.memory_history if data.timestamp >= cutoff_time]
    
    def get_memory_heatmap_data(self) -> Tuple[List[List[float]], List[str], List[str]]:
        """
        Get memory data formatted for heatmap visualization.
        
        Returns:
            Tuple of (data_matrix, x_labels, y_labels)
        """
        if not self.memory_history:
            return [[0]], ["No Data"], ["No Data"]
        
        # Get recent memory data
        recent_data = list(self.memory_history)[-20:]  # Last 20 data points
        
        # Create matrix: rows = time points, cols = allocation types
        data_matrix = []
        time_labels = []
        
        for memory_data in recent_data:
            row = []
            for alloc_type in self.allocation_types:
                gpu_usage = memory_data.gpu_memory.get(alloc_type, 0)
                cpu_usage = memory_data.cpu_memory.get(alloc_type, 0)
                total_usage = gpu_usage + cpu_usage
                row.append(total_usage)
            
            data_matrix.append(row)
            time_labels.append(memory_data.timestamp.strftime("%H:%M:%S"))
        
        return data_matrix, self.allocation_types, time_labels


class TimelineManager:
    """Manages processing timeline data and visualization."""
    
    def __init__(self, max_events: int = 10000):
        """Initialize timeline manager."""
        self.max_events = max_events
        self.events: deque = deque(maxlen=max_events)
        self.stage_durations: Dict[ProcessingStage, List[float]] = defaultdict(list)
    
    def add_event(self, 
                  stage: ProcessingStage, 
                  event_type: str, 
                  duration: Optional[float] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add timeline event."""
        event = {
            "timestamp": datetime.now(),
            "stage": stage,
            "event_type": event_type,
            "duration": duration,
            "metadata": metadata or {}
        }
        self.events.append(event)
        
        if duration is not None:
            self.stage_durations[stage].append(duration)
    
    def get_stage_statistics(self) -> Dict[ProcessingStage, Dict[str, float]]:
        """Get processing stage statistics."""
        stats = {}
        
        for stage, durations in self.stage_durations.items():
            if durations:
                stats[stage] = {
                    "average_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "total_count": len(durations)
                }
            else:
                stats[stage] = {
                    "average_duration": 0.0,
                    "min_duration": 0.0,
                    "max_duration": 0.0,
                    "total_count": 0
                }
        
        return stats
    
    def get_timeline_visualization_data(self, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get timeline data for visualization."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_events = [
            event for event in self.events 
            if event["timestamp"] >= cutoff_time
        ]
        return recent_events


class GenerationVisualizer:
    """
    Advanced visualization for generation processes.
    
    Features:
    - Multi-stage processing visualization
    - Quality progression charts
    - Memory usage heat maps
    - Processing timeline displays
    - Performance trend analysis
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize generation visualizer.
        
        Args:
            console: Rich console for output (created if None)
        """
        self.console = console or Console()
        self.chart_renderer = ChartRenderer(self.console)
        self.memory_tracker = MemoryTracker()
        self.timeline_manager = TimelineManager()
        
        # Visualization state
        self.quality_history: List[QualityMetric] = []
        self.performance_history: List[Dict[str, Any]] = []
        self.max_history = 1000
        
        # Visualization settings
        self.update_interval = 0.5  # seconds
        self.chart_width = 60
        self.chart_height = 20
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
    
    def render_processing_pipeline(self, pipeline_state: PipelineState) -> Panel:
        """
        Render visual representation of processing pipeline.
        
        Args:
            pipeline_state: Current pipeline state
            
        Returns:
            Rich Panel with pipeline visualization
        """
        pipeline_tree = Tree("🔄 Processing Pipeline")
        
        stage_icons = {
            ProcessingStage.INPUT: "📥",
            ProcessingStage.TOKENIZATION: "🔤",
            ProcessingStage.EMBEDDING: "🧠",
            ProcessingStage.ATTENTION: "👁️",
            ProcessingStage.GENERATION: "⚡",
            ProcessingStage.POST_PROCESSING: "🔧",
            ProcessingStage.OUTPUT: "📤"
        }
        
        for stage in ProcessingStage:
            progress = pipeline_state.stage_progress.get(stage, 0.0)
            metrics = pipeline_state.stage_metrics.get(stage, {})
            
            # Create progress bar
            bar_length = 20
            filled = int(progress * bar_length / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            # Determine status and color
            if stage == pipeline_state.current_stage:
                status = "🟢 Active"
                color = "green"
            elif progress >= 100:
                status = "✅ Complete"
                color = "bright_green"
            elif progress > 0:
                status = "🟡 In Progress"
                color = "yellow"
            else:
                status = "⭕ Pending"
                color = "dim"
            
            # Check for bottlenecks
            bottleneck_info = ""
            for bottleneck_stage, reason in pipeline_state.bottlenecks:
                if bottleneck_stage == stage:
                    bottleneck_info = f" ⚠️ {reason}"
                    color = "red"
            
            # Stage information
            stage_info = f"{stage_icons.get(stage, '🔹')} {stage.value.title()}"
            progress_info = f"[{bar}] {progress:.1f}%"
            
            # Add metrics if available
            metrics_info = ""
            if metrics:
                if "duration" in metrics:
                    metrics_info += f" ({metrics['duration']:.2f}s)"
                if "memory_mb" in metrics:
                    metrics_info += f" {metrics['memory_mb']:.0f}MB"
            
            stage_node = pipeline_tree.add(
                f"[{color}]{stage_info} - {status}[/{color}]"
            )
            stage_node.add(f"[{color}]{progress_info}{metrics_info}{bottleneck_info}[/{color}]")
        
        # Add overall progress
        overall_progress = f"Overall Progress: {pipeline_state.total_progress:.1f}%"
        if pipeline_state.estimated_completion:
            eta = pipeline_state.estimated_completion.strftime("%H:%M:%S")
            overall_progress += f" (ETA: {eta})"
        
        pipeline_tree.add(f"[bold cyan]{overall_progress}[/bold cyan]")
        
        return Panel(pipeline_tree, title="Processing Pipeline", box=ROUNDED, style="blue")
    
    def create_quality_chart(self, quality_data: List[QualityMetric]) -> Panel:
        """
        Generate quality progression visualization.
        
        Args:
            quality_data: List of quality metrics over time
            
        Returns:
            Rich Panel with quality chart
        """
        if not quality_data:
            return Panel("No quality data available", title="Quality Progression")
        
        # Group data by resolution level
        data_series = defaultdict(list)
        
        for metric in quality_data[-100:]:  # Last 100 points
            timestamp_float = metric.timestamp.timestamp()
            data_series[metric.resolution_level].append(
                (timestamp_float, metric.quality_score)
            )
        
        # Create line graph
        return self.chart_renderer.render_line_graph(
            data_series,
            title="Quality Progression Over Time",
            width=self.chart_width,
            height=self.chart_height
        )
    
    def generate_memory_heatmap(self, memory_data: MemoryData) -> Panel:
        """
        Create memory usage heat map.
        
        Args:
            memory_data: Current memory usage data
            
        Returns:
            Rich Panel with memory heatmap
        """
        # Get heatmap data from memory tracker
        data_matrix, x_labels, y_labels = self.memory_tracker.get_memory_heatmap_data()
        
        return self.chart_renderer.render_heatmap(
            data_matrix,
            x_labels,
            y_labels,
            title=f"Memory Usage Heatmap ({memory_data.timestamp.strftime('%H:%M:%S')})"
        )
    
    def create_performance_dashboard(self, 
                                   pipeline_state: PipelineState,
                                   quality_metrics: List[QualityMetric],
                                   memory_data: MemoryData) -> Layout:
        """
        Create comprehensive performance visualization dashboard.
        
        Args:
            pipeline_state: Current pipeline state
            quality_metrics: Quality metrics history
            memory_data: Memory usage data
            
        Returns:
            Rich Layout with comprehensive dashboard
        """
        layout = Layout()
        
        layout.split_column(
            Layout(name="top", ratio=2),
            Layout(name="bottom", ratio=1)
        )
        
        layout["top"].split_row(
            Layout(name="pipeline"),
            Layout(name="quality")
        )
        
        layout["bottom"].split_row(
            Layout(name="memory"),
            Layout(name="performance")
        )
        
        # Update panels
        layout["pipeline"].update(self.render_processing_pipeline(pipeline_state))
        layout["quality"].update(self.create_quality_chart(quality_metrics))
        layout["memory"].update(self.generate_memory_heatmap(memory_data))
        
        # Performance statistics
        stage_stats = self.timeline_manager.get_stage_statistics()
        performance_data = {
            stage.value: stats["average_duration"]
            for stage, stats in stage_stats.items()
        }
        
        layout["performance"].update(
            self.chart_renderer.render_bar_chart(
                performance_data,
                title="Average Stage Duration (s)"
            )
        )
        
        return layout
    
    def record_quality_metric(self, quality_metric: QualityMetric) -> None:
        """Record quality metric for visualization."""
        self.quality_history.append(quality_metric)
        
        # Limit history size
        if len(self.quality_history) > self.max_history:
            self.quality_history = self.quality_history[-self.max_history:]
    
    def record_memory_data(self, memory_data: MemoryData) -> None:
        """Record memory data for visualization."""
        self.memory_tracker.record_memory_usage(memory_data)
    
    def record_timeline_event(self, 
                            stage: ProcessingStage,
                            event_type: str,
                            duration: Optional[float] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record timeline event for visualization."""
        self.timeline_manager.add_event(stage, event_type, duration, metadata)
    
    def export_visualization_data(self, filename: Optional[str] = None) -> str:
        """
        Export visualization data for analysis.
        
        Args:
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"visualization_data_{timestamp}.json"
        
        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "quality_metrics_count": len(self.quality_history),
                "memory_records_count": len(self.memory_tracker.memory_history),
                "timeline_events_count": len(self.timeline_manager.events)
            },
            "quality_metrics": [
                {
                    "timestamp": qm.timestamp.isoformat(),
                    "quality_score": qm.quality_score,
                    "resolution_level": qm.resolution_level,
                    "processing_time": qm.processing_time,
                    "memory_usage": qm.memory_usage,
                    "stage": qm.stage.value,
                    "user_satisfaction": qm.user_satisfaction
                }
                for qm in self.quality_history
            ],
            "stage_statistics": {
                stage.value: stats
                for stage, stats in self.timeline_manager.get_stage_statistics().items()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename
    
    def update_pipeline_state(self, pipeline_state: Optional[PipelineState]) -> None:
        """
        Update the visualization with new pipeline state.
        
        Args:
            pipeline_state: New pipeline state (can be None for error handling)
        """
        if pipeline_state is None:
            self.logger.warning("Received None pipeline state - skipping update")
            return
            
        try:
            # Render the pipeline visualization
            visualization = self.render_processing_pipeline(pipeline_state)
            self.console.print(visualization)
            
            # Record timeline event
            self.record_timeline_event(
                f"Pipeline stage: {pipeline_state.current_stage.value}",
                "pipeline_update"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to update pipeline state: {e}")


# Example usage and testing
if __name__ == "__main__":
    def demo_visualizer():
        """Demonstrate the generation visualizer."""
        import random
        
        visualizer = GenerationVisualizer()
        
        # Create sample data
        pipeline_state = PipelineState()
        pipeline_state.current_stage = ProcessingStage.ATTENTION
        pipeline_state.stage_progress = {
            ProcessingStage.INPUT: 100.0,
            ProcessingStage.TOKENIZATION: 100.0,
            ProcessingStage.EMBEDDING: 100.0,
            ProcessingStage.ATTENTION: 75.0,
            ProcessingStage.GENERATION: 0.0,
            ProcessingStage.POST_PROCESSING: 0.0,
            ProcessingStage.OUTPUT: 0.0
        }
        pipeline_state.total_progress = 60.0
        pipeline_state.bottlenecks = [(ProcessingStage.ATTENTION, "Memory constraint")]
        
        # Create quality metrics
        quality_metrics = []
        base_time = datetime.now() - timedelta(minutes=5)
        for i in range(50):
            quality_metrics.append(QualityMetric(
                timestamp=base_time + timedelta(seconds=i*6),
                quality_score=random.uniform(0.7, 0.95),
                resolution_level=random.choice(["high", "balanced", "fast"]),
                processing_time=random.uniform(0.5, 2.0),
                memory_usage=random.uniform(2000, 3500),
                stage=random.choice(list(ProcessingStage))
            ))
        
        # Create memory data
        memory_data = MemoryData(
            timestamp=datetime.now(),
            gpu_memory={
                "model_weights": 1500.0,
                "activations": 800.0,
                "cache": 400.0,
                "other": 200.0
            },
            cpu_memory={
                "buffers": 2000.0,
                "preprocessing": 500.0,
                "other": 300.0
            },
            memory_pools={},
            fragmentation_score=0.15,
            allocation_efficiency=0.85
        )
        
        # Record data
        for qm in quality_metrics:
            visualizer.record_quality_metric(qm)
        
        visualizer.record_memory_data(memory_data)
        
        # Create dashboard
        dashboard = visualizer.create_performance_dashboard(
            pipeline_state, quality_metrics, memory_data
        )
        
        # Display
        console = Console()
        console.print(dashboard)
        
        # Export data
        export_file = visualizer.export_visualization_data()
        console.print(f"\n[green]Visualization data exported to: {export_file}[/green]")
    
    # Run demo
    demo_visualizer()
