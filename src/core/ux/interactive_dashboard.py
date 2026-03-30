"""
Interactive Control Dashboard - Phase 7B Priority 7 Implementation
Advanced Progressive Generation UI - Real-time User Interface

This module provides an interactive dashboard for real-time control and monitoring
of ImpressionCore's generation processes, featuring live metrics, visual controls,
and comprehensive user interaction capabilities.

Author: ImpressionCore Development Team
Created: 2025-05-30
Hardware Target: GTX 1050 Ti (4GB VRAM)
Phase: Priority 7 Phase 7B - Advanced Progressive Generation UI
Dependencies: Phase 7A (Enhanced Dynamic Configuration System)
"""

import asyncio
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import logging

# Rich library for enhanced console interfaces
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.tree import Tree
# Removed rich.gauge - not available in Rich 14.0.0, will use progress bars instead
from rich.prompt import Prompt, Confirm
from rich.box import ROUNDED, HEAVY

# Core ImpressionCore imports with fallback handling
try:
    from ..memory_manager.memory_optimizer import MemoryOptimizer
except ImportError:
    MemoryOptimizer = None

try:
    from ..monitoring.performance_monitor import PerformanceMonitor
except ImportError:
    PerformanceMonitor = None

try:
    from .hardware_detector import HardwareDetector, HardwareInfo
except ImportError:
    HardwareDetector = None
    HardwareInfo = None

try:
    from .user_profiles import UserProfileManager, UserProfile
except ImportError:
    UserProfileManager = None
    UserProfile = None

try:
    from .config_optimizer import ConfigurationOptimizer, OptimizationResult
except ImportError:
    ConfigurationOptimizer = None
    OptimizationResult = None

try:
    from .user_experience_features import ProgressiveGenerator, ResolutionLevel
except ImportError:
    # Fallback for testing or standalone usage
    MemoryOptimizer = None
    PerformanceMonitor = None
    HardwareDetector = None
    HardwareInfo = None
    UserProfileManager = None
    UserProfile = None
    ConfigurationOptimizer = None
    OptimizationResult = None
    ProgressiveGenerator = None
    ResolutionLevel = None
    ConfigurationOptimizer = None
    ProgressiveGenerator = None


class DashboardMode(Enum):
    """Dashboard display modes."""
    COMPACT = "compact"
    DETAILED = "detailed"
    ADVANCED = "advanced"
    MONITORING = "monitoring"


class MetricType(Enum):
    """Types of metrics to display."""
    PERFORMANCE = "performance"
    MEMORY = "memory" 
    QUALITY = "quality"
    HARDWARE = "hardware"
    USER = "user"


@dataclass
class DashboardMetrics:
    """Real-time dashboard metrics data."""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Performance Metrics
    fps: float = 0.0
    tokens_per_second: float = 0.0
    latency_ms: float = 0.0
    queue_size: int = 0
    
    # Memory Metrics
    gpu_memory_used_mb: float = 0.0
    gpu_memory_total_mb: float = 4096.0  # GTX 1050 Ti default
    cpu_memory_used_mb: float = 0.0
    cpu_memory_total_mb: float = 16384.0
    
    # Quality Metrics
    quality_score: float = 0.0
    resolution_level: str = "balanced"
    generation_progress: float = 0.0
    
    # Hardware Metrics
    gpu_temperature: float = 0.0
    gpu_utilization: float = 0.0
    cpu_utilization: float = 0.0
    
    # User Interaction
    active_sessions: int = 0
    user_satisfaction: float = 0.0
    
    # Error and Status
    error_count: int = 0
    warning_count: int = 0
    status_message: str = "Ready"


@dataclass
class ControlEvent:
    """User control event data."""
    event_type: str
    component: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None


class InteractiveDashboard:
    """
    Main interactive dashboard for real-time user interaction and monitoring.
    
    Features:
    - Real-time performance metrics visualization
    - Interactive control panels with live updates
    - Drag-and-drop configuration interface
    - Live performance metrics display
    - Resource utilization monitoring
    - Error and warning notifications
    """
    
    def __init__(self, 
                 mode: DashboardMode = DashboardMode.DETAILED,
                 update_interval: float = 0.1,
                 hardware_info: Optional[Any] = None):
        """
        Initialize the interactive dashboard.
        
        Args:
            mode: Dashboard display mode
            update_interval: Update frequency in seconds (default 100ms)
            hardware_info: Hardware information for optimization
        """
        self.mode = mode
        self.update_interval = update_interval
        self.hardware_info = hardware_info
        
        # Rich console components
        self.console = Console()
        self.live_display: Optional[Live] = None
        self.layout = Layout()
        
        # Core managers and monitors (lazy initialization for memory optimization)
        self.metrics = DashboardMetrics()
        self.metrics_history: List[DashboardMetrics] = []
        self.max_history = 100  # Reduced from 1000 for memory optimization on GTX 1050 Ti
        
        # Component managers (lazy initialization)
        self._hardware_detector = None
        self._performance_monitor = None
        self._memory_optimizer = None
        
        # Dashboard state
        self.is_running = False
        self.is_paused = False
        self.last_update = datetime.now()
        self.update_thread: Optional[threading.Thread] = None
        
        # Event handling (smaller initial capacity)
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.control_events: List[ControlEvent] = []
        
        # Progress tracking (lazy initialization)
        self.progress_bars: Dict[str, Progress] = {}
        self.active_tasks: Dict[str, Any] = {}
        
        # User configuration
        self.show_advanced_metrics = False
        self.color_theme = "default"
        self.refresh_rate = 10  # Hz
        
        # Initialize layout
        self._setup_layout()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
    def _setup_layout(self) -> None:
        """Set up the dashboard layout structure."""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        self.layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        self.layout["left"].split_column(
            Layout(name="metrics", ratio=2),
            Layout(name="controls", ratio=1)
        )
        
        self.layout["right"].split_column(
            Layout(name="status"),
            Layout(name="logs")
        )
    
    def _create_header(self) -> Panel:
        """Create dashboard header panel."""
        title = Text("ImpressionCore Interactive Dashboard", style="bold cyan")
        subtitle = f"Mode: {self.mode.value.title()} | " \
                  f"Hardware: {self.hardware_info.gpu_name if self.hardware_info else 'Unknown'} | " \
                  f"Status: {'Running' if self.is_running else 'Stopped'}"
        
        header_text = Text.assemble(
            title, "\n",
            (subtitle, "dim")
        )
        
        return Panel(
            Align.center(header_text),
            box=ROUNDED,
            style="cyan"
        )
    
    def _create_metrics_panel(self) -> Panel:
        """Create real-time metrics visualization panel."""
        table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Current", style="green", width=15)
        table.add_column("Average", style="yellow", width=15)
        table.add_column("Trend", style="blue", width=10)
        
        # Calculate averages from history
        avg_fps = sum(m.fps for m in self.metrics_history[-60:]) / max(len(self.metrics_history[-60:]), 1)
        avg_latency = sum(m.latency_ms for m in self.metrics_history[-60:]) / max(len(self.metrics_history[-60:]), 1)
        avg_gpu_util = sum(m.gpu_utilization for m in self.metrics_history[-60:]) / max(len(self.metrics_history[-60:]), 1)
        
        # Performance metrics
        table.add_row("FPS", f"{self.metrics.fps:.1f}", f"{avg_fps:.1f}", self._get_trend_arrow(self.metrics.fps, avg_fps))
        table.add_row("Latency (ms)", f"{self.metrics.latency_ms:.1f}", f"{avg_latency:.1f}", self._get_trend_arrow(avg_latency, self.metrics.latency_ms))
        table.add_row("Tokens/sec", f"{self.metrics.tokens_per_second:.1f}", "-", "→")
        
        # Memory metrics
        gpu_usage_pct = (self.metrics.gpu_memory_used_mb / self.metrics.gpu_memory_total_mb) * 100
        cpu_usage_pct = (self.metrics.cpu_memory_used_mb / self.metrics.cpu_memory_total_mb) * 100
        
        table.add_row("GPU Memory", f"{gpu_usage_pct:.1f}%", "-", "→")
        table.add_row("CPU Memory", f"{cpu_usage_pct:.1f}%", "-", "→")
        table.add_row("GPU Utilization", f"{self.metrics.gpu_utilization:.1f}%", f"{avg_gpu_util:.1f}%", self._get_trend_arrow(self.metrics.gpu_utilization, avg_gpu_util))
        
        # Quality metrics
        table.add_row("Quality Score", f"{self.metrics.quality_score:.2f}", "-", "→")
        table.add_row("Resolution", self.metrics.resolution_level, "-", "→")
        
        return Panel(table, title="Real-time Metrics", box=ROUNDED, style="green")
    
    def _create_controls_panel(self) -> Panel:
        """Create interactive controls panel."""
        controls_text = Text()
        controls_text.append("Interactive Controls\n\n", style="bold white")
        
        # Quality controls
        controls_text.append("Quality Controls:\n", style="bold cyan")
        controls_text.append("  [1] Ultra High  [2] High  [3] Balanced  [4] Fast  [5] Ultra Fast\n\n")
        
        # Memory controls
        controls_text.append("Memory Controls:\n", style="bold yellow")
        controls_text.append("  [M] Optimize Memory  [G] Garbage Collect  [C] Clear Cache\n\n")
        
        # Session controls
        controls_text.append("Session Controls:\n", style="bold green")
        controls_text.append("  [S] Save Session  [L] Load Session  [R] Reset\n\n")
        
        # Dashboard controls
        controls_text.append("Dashboard Controls:\n", style="bold magenta")
        controls_text.append("  [P] Pause/Resume  [A] Advanced Mode  [Q] Quit\n")
        
        return Panel(controls_text, title="Controls", box=ROUNDED, style="blue")
    
    def _create_status_panel(self) -> Panel:
        """Create system status panel."""
        status_text = Text()
        
        # System status
        status_text.append("System Status\n\n", style="bold white")
        status_text.append(f"Status: {self.metrics.status_message}\n", style="green")
        status_text.append(f"Active Sessions: {self.metrics.active_sessions}\n")
        status_text.append(f"Queue Size: {self.metrics.queue_size}\n")
        status_text.append(f"Errors: {self.metrics.error_count}\n", style="red" if self.metrics.error_count > 0 else "green")
        status_text.append(f"Warnings: {self.metrics.warning_count}\n", style="yellow" if self.metrics.warning_count > 0 else "green")
        
        # Hardware status
        if self.hardware_info:
            status_text.append(f"\nHardware Status\n", style="bold cyan")
            status_text.append(f"GPU: {self.hardware_info.gpu_name}\n")
            status_text.append(f"Temperature: {self.metrics.gpu_temperature:.1f}°C\n")
            status_text.append(f"CPU Usage: {self.metrics.cpu_utilization:.1f}%\n")
        
        # Generation progress
        if self.metrics.generation_progress > 0:
            status_text.append(f"\nGeneration Progress\n", style="bold yellow")
            progress_bar = "█" * int(self.metrics.generation_progress * 20 / 100)
            progress_bar += "░" * (20 - int(self.metrics.generation_progress * 20 / 100))
            status_text.append(f"[{progress_bar}] {self.metrics.generation_progress:.1f}%\n")
        
        return Panel(status_text, title="Status", box=ROUNDED, style="yellow")
    
    def _create_logs_panel(self) -> Panel:
        """Create logs and events panel."""
        logs_text = Text()
        logs_text.append("Recent Events\n\n", style="bold white")
        
        # Show recent control events
        recent_events = self.control_events[-10:]  # Last 10 events
        for event in recent_events:
            timestamp = event.timestamp.strftime("%H:%M:%S")
            logs_text.append(f"[{timestamp}] {event.event_type}: {event.component} = {event.value}\n")
        
        if not recent_events:
            logs_text.append("No recent events", style="dim")
        
        return Panel(logs_text, title="Event Log", box=ROUNDED, style="white")
    
    def _get_trend_arrow(self, current: float, average: float) -> str:
        """Get trend arrow based on current vs average."""
        if current > average * 1.1:
            return "↗"
        elif current < average * 0.9:
            return "↘"
        else:
            return "→"
    
    def update_metrics(self, new_metrics: DashboardMetrics) -> None:
        """
        Update dashboard metrics with new data.
        
        Args:
            new_metrics: New metrics data to display
        """
        self.metrics = new_metrics
        self.metrics_history.append(new_metrics)
        
        # Limit history size for memory efficiency
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]
        
        self.last_update = datetime.now()
    
    def handle_user_input(self, key: str) -> bool:
        """
        Handle user input and update configuration.
        
        Args:
            key: Input key pressed by user
            
        Returns:
            bool: False if should quit, True to continue
        """
        event = ControlEvent(
            event_type="user_input",
            component="dashboard",
            value=key
        )
        self.control_events.append(event)
        
        # Quality controls
        if key in "12345":
            quality_levels = {
                "1": "ultra_high",
                "2": "high", 
                "3": "balanced",
                "4": "fast",
                "5": "ultra_fast"
            }
            self.metrics.resolution_level = quality_levels[key]
            self._emit_event("quality_changed", quality_levels[key])
        
        # Memory controls
        elif key.lower() == "m":
            self._emit_event("optimize_memory", True)
        elif key.lower() == "g":
            self._emit_event("garbage_collect", True)
        elif key.lower() == "c":
            self._emit_event("clear_cache", True)
        
        # Session controls
        elif key.lower() == "s":
            self._emit_event("save_session", True)
        elif key.lower() == "l":
            self._emit_event("load_session", True)
        elif key.lower() == "r":
            self._emit_event("reset_session", True)
        
        # Dashboard controls
        elif key.lower() == "p":
            self.is_paused = not self.is_paused
            self._emit_event("pause_toggled", self.is_paused)
        elif key.lower() == "a":
            self.show_advanced_metrics = not self.show_advanced_metrics
            self._emit_event("advanced_mode_toggled", self.show_advanced_metrics)
        elif key.lower() == "q":
            return False
        
        return True
    
    def _emit_event(self, event_type: str, value: Any) -> None:
        """Emit an event to registered handlers."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(value)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event_type}: {e}")
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """Register an event handler for specific events."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for specific events (alias for register_event_handler)."""
        self.register_event_handler(event_type, callback)
    
    def _update_layout(self) -> None:
        """Update the dashboard layout with current data."""
        self.layout["header"].update(self._create_header())
        self.layout["metrics"].update(self._create_metrics_panel())
        self.layout["controls"].update(self._create_controls_panel())
        self.layout["status"].update(self._create_status_panel())
        self.layout["logs"].update(self._create_logs_panel())
    
    async def start_dashboard(self) -> None:
        """
        Start the interactive dashboard with live updates.
        
        This method starts the main dashboard loop with real-time updates
        and user input handling.
        """
        self.is_running = True
        
        with Live(self.layout, console=self.console, refresh_per_second=self.refresh_rate) as live:
            self.live_display = live
            
            self.console.print("[bold green]🚀 ImpressionCore Interactive Dashboard Started[/bold green]")
            self.console.print("[dim]Press 'Q' to quit, 'P' to pause, 'A' for advanced mode[/dim]\n")
            
            try:
                while self.is_running:
                    if not self.is_paused:
                        # Update layout with current data
                        self._update_layout()
                    
                    # Sleep for update interval
                    await asyncio.sleep(self.update_interval)
                    
                    # Check for user input (non-blocking)
                    # Note: This would need to be implemented with proper async input handling
                    # For now, we'll rely on external input handling
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Dashboard interrupted by user[/yellow]")
            except Exception as e:
                self.console.print(f"\n[red]Dashboard error: {e}[/red]")
                self.logger.error(f"Dashboard error: {e}")
            finally:
                self.is_running = False
                self.console.print("[dim]Dashboard stopped[/dim]")
    
    def stop_dashboard(self) -> None:
        """Stop the interactive dashboard."""
        self.is_running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
    
    def get_current_metrics(self) -> DashboardMetrics:
        """Get current dashboard metrics."""
        return self.metrics
    
    def get_metrics_history(self, 
                          seconds: Optional[int] = None) -> List[DashboardMetrics]:
        """
        Get metrics history for specified time period.
        
        Args:
            seconds: Number of seconds of history to return (None for all)
            
        Returns:
            List of historical metrics
        """
        if seconds is None:
            return self.metrics_history.copy()
        
        cutoff_time = datetime.now() - timedelta(seconds=seconds)
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
    
    def export_session_data(self, filename: Optional[str] = None) -> str:
        """
        Export current session data to JSON file.
        
        Args:
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dashboard_session_{timestamp}.json"
        
        session_data = {
            "session_info": {
                "start_time": self.metrics_history[0].timestamp.isoformat() if self.metrics_history else None,
                "end_time": datetime.now().isoformat(),
                "mode": self.mode.value,
                "hardware_info": self.hardware_info.__dict__ if self.hardware_info else None
            },
            "metrics_history": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "fps": m.fps,
                    "tokens_per_second": m.tokens_per_second,
                    "latency_ms": m.latency_ms,
                    "gpu_memory_used_mb": m.gpu_memory_used_mb,
                    "cpu_memory_used_mb": m.cpu_memory_used_mb,
                    "quality_score": m.quality_score,
                    "resolution_level": m.resolution_level,
                    "gpu_utilization": m.gpu_utilization,
                    "cpu_utilization": m.cpu_utilization
                }
                for m in self.metrics_history
            ],
            "control_events": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "event_type": e.event_type,
                    "component": e.component,
                    "value": str(e.value)
                }
                for e in self.control_events
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return filename
    
    @property
    def hardware_detector(self):
        """Lazy-loaded hardware detector for memory optimization."""
        if self._hardware_detector is None and HardwareDetector:
            self._hardware_detector = HardwareDetector()
        return self._hardware_detector
    
    @property
    def performance_monitor(self):
        """Lazy-loaded performance monitor for memory optimization."""
        if self._performance_monitor is None and PerformanceMonitor:
            self._performance_monitor = PerformanceMonitor()
        return self._performance_monitor
    
    @property
    def memory_optimizer(self):
        """Lazy-loaded memory optimizer for memory optimization."""
        if self._memory_optimizer is None and MemoryOptimizer:
            self._memory_optimizer = MemoryOptimizer()
        return self._memory_optimizer


# Example usage and testing
if __name__ == "__main__":
    async def demo_dashboard():
        """Demonstrate the interactive dashboard."""
        import random
        
        # Create dashboard
        dashboard = InteractiveDashboard(mode=DashboardMode.DETAILED)
        
        # Register event handlers
        def handle_quality_change(level):
            print(f"Quality changed to: {level}")
        
        def handle_memory_optimize(value):
            print("Memory optimization triggered")
        
        dashboard.register_event_handler("quality_changed", handle_quality_change)
        dashboard.register_event_handler("optimize_memory", handle_memory_optimize)
        
        # Start dashboard in background
        dashboard_task = asyncio.create_task(dashboard.start_dashboard())
        
        # Simulate metric updates
        for i in range(100):
            metrics = DashboardMetrics(
                fps=random.uniform(30, 60),
                tokens_per_second=random.uniform(50, 100),
                latency_ms=random.uniform(100, 300),
                gpu_memory_used_mb=random.uniform(2000, 3800),
                cpu_memory_used_mb=random.uniform(4000, 8000),
                quality_score=random.uniform(0.7, 0.95),
                gpu_utilization=random.uniform(70, 95),
                cpu_utilization=random.uniform(20, 60),
                active_sessions=random.randint(1, 5),
                generation_progress=random.uniform(0, 100)
            )
            
            dashboard.update_metrics(metrics)
            await asyncio.sleep(0.1)
        
        dashboard.stop_dashboard()
    
    # Run demo
    try:
        asyncio.run(demo_dashboard())
    except KeyboardInterrupt:
        print("Demo interrupted")
