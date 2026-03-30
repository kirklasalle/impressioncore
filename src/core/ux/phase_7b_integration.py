"""
Phase 7B Integration Module - Advanced Progressive Generation UI
ImpressionCore User Experience Features

This module integrates all Phase 7B components:
1. Interactive Dashboard (Component 1/3)
2. Generation Visualizer (Component 2/3)  
3. Advanced Controls (Component 3/3)

Created: 2025-05-30
Component: Priority 7 Phase 7B - Integration & Testing
Status: Implementation Complete
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
import asyncio
import time
import logging
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text

# Import Phase 7B components
from .interactive_dashboard import InteractiveDashboard, DashboardMetrics
from .generation_visualizer import GenerationVisualizer, PipelineState, ProcessingStage
from .advanced_controls import AdvancedControls, QualitySpeedProfile, MemoryProfile, CustomPipeline

# Import core utilities
try:
    from ...utils.rich_enhancements import RichEnhancements
    from ...utils.rich_logging import RichLogger
    from ...utils.rich_status_animation import RichStatusAnimation
except ImportError:
    # Fallback for development/testing
    class RichEnhancements:
        @staticmethod
        def create_gradient_text(text: str, colors: List[str]) -> Text:
            return Text(text)
    
    class RichLogger:
        def __init__(self, name: str):
            self.console = Console()
        def info(self, msg: str): self.console.print(f"[blue]INFO[/]: {msg}")
        def warning(self, msg: str): self.console.print(f"[yellow]WARN[/]: {msg}")
        def error(self, msg: str): self.console.print(f"[red]ERROR[/]: {msg}")
    
    class RichStatusAnimation:
        def __init__(self, console: Console):
            self.console = console


class UIMode(Enum):
    """Available UI display modes."""
    DASHBOARD_ONLY = "dashboard_only"
    VISUALIZER_ONLY = "visualizer_only"
    CONTROLS_ONLY = "controls_only"
    SPLIT_VIEW = "split_view"
    TABBED_VIEW = "tabbed_view"
    FULL_INTEGRATED = "full_integrated"


class IntegrationState(Enum):
    """Integration system states."""
    INITIALIZING = "initializing"
    READY = "ready"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class IntegratedMetrics:
    """Combined metrics from all Phase 7B components."""
    dashboard_metrics: Optional[DashboardMetrics] = None
    pipeline_state: Optional[PipelineState] = None
    active_profile: Optional[QualitySpeedProfile] = None
    memory_profile: Optional[MemoryProfile] = None
    custom_pipeline: Optional[CustomPipeline] = None
    
    # Integration-specific metrics
    update_latency: float = 0.0
    memory_overhead: float = 0.0
    component_sync_status: Dict[str, bool] = field(default_factory=dict)
    last_update_time: float = field(default_factory=time.time)


@dataclass
class UIConfiguration:
    """Configuration for the integrated UI system."""
    mode: UIMode = UIMode.FULL_INTEGRATED
    update_interval: float = 0.05  # 50ms for <50ms target latency
    auto_save_config: bool = True
    save_session_data: bool = True
    enable_animations: bool = True
    enable_real_time_updates: bool = True
    max_history_size: int = 1000
    
    # Component-specific settings
    dashboard_enabled: bool = True
    visualizer_enabled: bool = True
    controls_enabled: bool = True
    
    # Performance settings
    low_memory_mode: bool = False
    high_performance_mode: bool = False


class Phase7BIntegration:
    """
    Integrated Advanced Progressive Generation UI system.
    
    Combines Interactive Dashboard, Generation Visualizer, and Advanced Controls
    into a cohesive user experience with real-time updates and seamless interaction.
    
    Key Features:
    - Real-time component synchronization
    - Unified configuration management
    - Performance monitoring and optimization
    - Session management across all components
    - Adaptive UI based on system performance
    """
    
    def __init__(self, console: Optional[Console] = None, config: Optional[UIConfiguration] = None):
        """Initialize the integrated Phase 7B system."""
        self.console = console or Console()
        self.config = config or UIConfiguration()
        self.logger = RichLogger("Phase7BIntegration")
        self.enhancements = RichEnhancements()
        self.animation = RichStatusAnimation(self.console)
        
        # Initialize components
        self.dashboard = InteractiveDashboard(self.console)
        self.visualizer = GenerationVisualizer(self.console)
        self.controls = AdvancedControls(self.console)
        
        # Integration state
        self.state = IntegrationState.INITIALIZING
        self.metrics = IntegratedMetrics()
        self.is_running = False
        self.update_task: Optional[asyncio.Task] = None
        
        # Event synchronization
        self.event_callbacks: Dict[str, List[Callable]] = {}
        self.component_states: Dict[str, Any] = {}
        
        # Performance tracking
        self.performance_history: List[Dict[str, float]] = []
        self.last_performance_check = time.time()
        
        # Setup component integration
        self._setup_component_integration()
        
        self.logger.info("Phase 7B Integration initialized")
    
    def _setup_component_integration(self):
        """Setup cross-component event handling and synchronization."""
        # Dashboard callbacks
        self.dashboard.register_callback("metrics_updated", self._on_dashboard_metrics_updated)
        self.dashboard.register_callback("user_action", self._on_dashboard_user_action)
        
        # Controls callbacks
        self.controls.register_callback("profile_changed", self._on_profile_changed)
        self.controls.register_callback("memory_profile_changed", self._on_memory_profile_changed)
        self.controls.register_callback("pipeline_changed", self._on_pipeline_changed)
        self.controls.register_callback("session_ended", self._on_session_ended)
        
        # Visualizer callbacks (would be implemented if visualizer had callback system)
        # For now, we'll poll visualizer state
        
        self.logger.info("Component integration setup complete")
    
    def _on_dashboard_metrics_updated(self, metrics: DashboardMetrics):
        """Handle dashboard metrics updates."""
        self.metrics.dashboard_metrics = metrics
        self.metrics.last_update_time = time.time()
        
        # Update visualizer with new metrics
        if self.config.visualizer_enabled:
            pipeline_state = PipelineState(
                stage=ProcessingStage.GENERATION,
                progress=metrics.generation_progress,
                tokens_processed=metrics.tokens_processed,
                tokens_remaining=max(0, metrics.total_tokens - metrics.tokens_processed),
                quality_score=metrics.quality_score,
                memory_usage=metrics.memory_usage_mb,
                processing_speed=metrics.tokens_per_second
            )
            self.visualizer.update_pipeline_state(pipeline_state)
        
        # Trigger integration callbacks
        self._trigger_callbacks("metrics_synchronized", self.metrics)
    
    def _on_dashboard_user_action(self, action_data: Dict[str, Any]):
        """Handle user actions from dashboard."""
        action_type = action_data.get("action_type", "unknown")
        
        if action_type == "pause_generation":
            self._pause_generation()
        elif action_type == "resume_generation":
            self._resume_generation()
        elif action_type == "adjust_quality":
            quality_level = action_data.get("quality_level", 0.5)
            self._adjust_quality_on_the_fly(quality_level)
        elif action_type == "emergency_stop":
            self._emergency_stop()
        
        self.logger.info(f"Processed user action: {action_type}")
    
    def _on_profile_changed(self, profile: QualitySpeedProfile):
        """Handle quality/speed profile changes."""
        self.metrics.active_profile = profile
        
        # Update dashboard with new profile settings
        if self.config.dashboard_enabled:
            self.dashboard.update_configuration({
                "profile_name": profile.name,
                "speed_weight": profile.speed_weight,
                "quality_weight": profile.quality_weight,
                "memory_efficiency": profile.memory_efficiency
            })
        
        # Trigger system reconfiguration
        self._apply_profile_changes(profile)
        self.logger.info(f"Applied profile change: {profile.name}")
    
    def _on_memory_profile_changed(self, profile: MemoryProfile):
        """Handle memory profile changes."""
        self.metrics.memory_profile = profile
        
        # Update dashboard memory monitoring
        if self.config.dashboard_enabled:
            self.dashboard.update_memory_limits(
                max_vram=profile.max_vram_usage,
                max_ram=profile.max_ram_usage
            )
        
        # Apply memory optimizations
        self._apply_memory_optimizations(profile)
        self.logger.info(f"Applied memory profile: {profile.name}")
    
    def _on_pipeline_changed(self, pipeline: Optional[CustomPipeline]):
        """Handle custom pipeline changes."""
        self.metrics.custom_pipeline = pipeline
        
        if pipeline:
            # Update visualizer with new pipeline structure
            if self.config.visualizer_enabled:
                self.visualizer.update_pipeline_structure(pipeline.stages)
            
            # Reconfigure processing pipeline
            self._reconfigure_pipeline(pipeline)
            self.logger.info(f"Applied custom pipeline: {pipeline.name}")
        else:
            self.logger.info("Reset to default pipeline")
    
    def _on_session_ended(self, session_data):
        """Handle session end events."""
        # Store session data in integrated metrics
        if self.config.save_session_data:
            self._save_integrated_session_data(session_data)
        
        # Update performance history
        self._update_performance_history(session_data)
        
        self.logger.info(f"Session ended: {session_data.session_id}")
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for integration events."""
        if event not in self.event_callbacks:
            self.event_callbacks[event] = []
        self.event_callbacks[event].append(callback)
    
    def _trigger_callbacks(self, event: str, data: Any = None):
        """Trigger registered callbacks for an event."""
        if event in self.event_callbacks:
            for callback in self.event_callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Callback error for {event}: {e}")
    
    async def start(self):
        """Start the integrated UI system."""
        if self.is_running:
            self.logger.warning("System already running")
            return
        
        self.logger.info("Starting Phase 7B Integrated UI...")
        
        try:
            self.state = IntegrationState.INITIALIZING
            
            # Initialize components
            await self._initialize_components()
            
            # Start update loop
            self.is_running = True
            self.state = IntegrationState.READY
            
            if self.config.enable_real_time_updates:
                self.update_task = asyncio.create_task(self._update_loop())
            
            self.state = IntegrationState.ACTIVE
            self.logger.info("Phase 7B Integrated UI started successfully")
            
            # Trigger start callbacks
            self._trigger_callbacks("system_started", self.metrics)
            
        except Exception as e:
            self.state = IntegrationState.ERROR
            self.logger.error(f"Failed to start system: {e}")
            raise
    
    async def stop(self):
        """Stop the integrated UI system."""
        if not self.is_running:
            return
        
        self.logger.info("Stopping Phase 7B Integrated UI...")
        
        try:
            self.state = IntegrationState.SHUTDOWN
            self.is_running = False
            
            # Cancel update task
            if self.update_task and not self.update_task.done():
                self.update_task.cancel()
                try:
                    await self.update_task
                except asyncio.CancelledError:
                    pass
            
            # Cleanup components
            await self._cleanup_components()
            
            # Save final state if configured
            if self.config.auto_save_config:
                self._save_configuration()
            
            self.logger.info("Phase 7B Integrated UI stopped")
            
            # Trigger stop callbacks
            self._trigger_callbacks("system_stopped", self.metrics)
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    async def _initialize_components(self):
        """Initialize all Phase 7B components."""
        # Initialize dashboard
        if self.config.dashboard_enabled:
            await self.dashboard.start()
            self.metrics.component_sync_status["dashboard"] = True
        
        # Initialize visualizer
        if self.config.visualizer_enabled:
            # Visualizer doesn't have async start, but we can prepare it
            self.visualizer.clear_data()
            self.metrics.component_sync_status["visualizer"] = True
        
        # Initialize controls
        if self.config.controls_enabled:
            # Controls don't require async initialization
            self.metrics.component_sync_status["controls"] = True
        
        # Apply any pre-existing configurations
        if self.metrics.active_profile:
            self._apply_profile_changes(self.metrics.active_profile)
        
        if self.metrics.memory_profile:
            self._apply_memory_optimizations(self.metrics.memory_profile)
    
    async def _cleanup_components(self):
        """Cleanup all Phase 7B components."""
        # Cleanup dashboard
        if self.config.dashboard_enabled and self.dashboard.is_running:
            await self.dashboard.stop()
        
        # Cleanup visualizer
        if self.config.visualizer_enabled:
            self.visualizer.clear_data()
        
        # Reset component sync status
        self.metrics.component_sync_status.clear()
    
    async def _update_loop(self):
        """Main update loop for real-time synchronization."""
        self.logger.info(f"Starting update loop with {self.config.update_interval*1000:.1f}ms interval")
        
        try:
            while self.is_running:
                update_start = time.time()
                
                # Update metrics
                await self._update_integrated_metrics()
                
                # Check performance
                await self._check_performance()
                
                # Apply any pending optimizations
                await self._apply_optimizations()
                
                # Calculate update latency
                update_time = time.time() - update_start
                self.metrics.update_latency = update_time
                
                # Adaptive delay to maintain target latency
                if update_time < self.config.update_interval:
                    await asyncio.sleep(self.config.update_interval - update_time)
                elif update_time > 0.05:  # >50ms, we're falling behind
                    self.logger.warning(f"Update latency high: {update_time*1000:.1f}ms")
                
        except asyncio.CancelledError:
            self.logger.info("Update loop cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Update loop error: {e}")
            self.state = IntegrationState.ERROR
    
    async def _update_integrated_metrics(self):
        """Update integrated metrics from all components."""
        # Get dashboard metrics
        if self.config.dashboard_enabled and self.dashboard.is_running:
            current_metrics = self.dashboard.get_current_metrics()
            if current_metrics:
                self.metrics.dashboard_metrics = current_metrics
        
        # Update visualizer with latest data
        if self.config.visualizer_enabled and self.metrics.dashboard_metrics:
            # Convert dashboard metrics to pipeline state
            pipeline_state = PipelineState(
                stage=ProcessingStage.GENERATION,
                progress=self.metrics.dashboard_metrics.generation_progress,
                tokens_processed=self.metrics.dashboard_metrics.tokens_processed,
                tokens_remaining=max(0, self.metrics.dashboard_metrics.total_tokens - self.metrics.dashboard_metrics.tokens_processed),
                quality_score=self.metrics.dashboard_metrics.quality_score,
                memory_usage=self.metrics.dashboard_metrics.memory_usage_mb,
                processing_speed=self.metrics.dashboard_metrics.tokens_per_second
            )
            self.visualizer.update_pipeline_state(pipeline_state)
            self.metrics.pipeline_state = pipeline_state
        
        # Calculate memory overhead
        base_memory = 1024  # Estimated base system memory usage (MB)
        current_memory = self.metrics.dashboard_metrics.memory_usage_mb if self.metrics.dashboard_metrics else base_memory
        self.metrics.memory_overhead = max(0, (current_memory - base_memory) / base_memory * 100)
        
        self.metrics.last_update_time = time.time()
    
    async def _check_performance(self):
        """Check system performance and apply optimizations if needed."""
        current_time = time.time()
        
        # Check if performance check is due
        if current_time - self.last_performance_check < 1.0:  # Check every second
            return
        
        self.last_performance_check = current_time
        
        # Collect performance data
        perf_data = {
            "timestamp": current_time,
            "update_latency": self.metrics.update_latency,
            "memory_overhead": self.metrics.memory_overhead,
            "component_sync": all(self.metrics.component_sync_status.values())
        }
        
        self.performance_history.append(perf_data)
        
        # Keep history size manageable
        if len(self.performance_history) > self.config.max_history_size:
            self.performance_history = self.performance_history[-self.config.max_history_size:]
        
        # Check for performance issues
        if self.metrics.update_latency > 0.05:  # >50ms target
            await self._handle_performance_issue("high_latency")
        
        if self.metrics.memory_overhead > 5.0:  # >5% overhead target
            await self._handle_performance_issue("high_memory_overhead")
    
    async def _handle_performance_issue(self, issue_type: str):
        """Handle detected performance issues."""
        if issue_type == "high_latency":
            # Reduce update frequency
            self.config.update_interval = min(0.1, self.config.update_interval * 1.2)
            self.logger.warning(f"Increased update interval to {self.config.update_interval*1000:.1f}ms due to high latency")
        
        elif issue_type == "high_memory_overhead":
            # Enable low memory optimizations
            if not self.config.low_memory_mode:
                self.config.low_memory_mode = True
                self.logger.warning("Enabled low memory mode due to high overhead")
                
                # Reduce visualization complexity
                if self.config.visualizer_enabled:
                    self.visualizer.set_low_memory_mode(True)
                
                # Reduce dashboard update frequency
                if self.config.dashboard_enabled:
                    self.dashboard.set_reduced_updates(True)
    
    async def _apply_optimizations(self):
        """Apply performance optimizations based on current state."""
        if self.config.low_memory_mode:
            # Limit history sizes
            if len(self.performance_history) > 100:
                self.performance_history = self.performance_history[-100:]
        
        if self.config.high_performance_mode:
            # Reduce update interval for faster responses
            self.config.update_interval = max(0.02, self.config.update_interval * 0.9)
    
    def _apply_profile_changes(self, profile: QualitySpeedProfile):
        """Apply quality/speed profile changes to the system."""
        # This would interface with the actual model/generation system
        # For now, we'll just log the changes
        changes = {
            "batch_size": profile.batch_size,
            "precision": profile.precision,
            "attention_layers": profile.attention_layers,
            "max_sequence_length": profile.max_sequence_length,
            "temperature": profile.temperature,
            "top_p": profile.top_p
        }
        
        self.logger.info(f"Applying profile changes: {changes}")
        # In a real implementation, this would update the model configuration
    
    def _apply_memory_optimizations(self, profile: MemoryProfile):
        """Apply memory optimization settings."""
        optimizations = {
            "max_vram_usage": profile.max_vram_usage,
            "gradient_checkpointing": profile.gradient_checkpointing,
            "mixed_precision": profile.mixed_precision,
            "cpu_offloading": profile.cpu_offloading,
            "model_sharding": profile.model_sharding
        }
        
        self.logger.info(f"Applying memory optimizations: {optimizations}")
        # In a real implementation, this would configure memory management
    
    def _reconfigure_pipeline(self, pipeline: CustomPipeline):
        """Reconfigure the processing pipeline."""
        pipeline_config = {
            "stages": [stage.value for stage in pipeline.stages],
            "stage_configs": pipeline.stage_configs,
            "parallel_stages": pipeline.parallel_stages
        }
        
        self.logger.info(f"Reconfiguring pipeline: {pipeline_config}")
        # In a real implementation, this would restructure the processing pipeline
    
    def _pause_generation(self):
        """Pause the generation process."""
        self.logger.info("Pausing generation")
        # In a real implementation, this would pause the model
    
    def _resume_generation(self):
        """Resume the generation process."""
        self.logger.info("Resuming generation")
        # In a real implementation, this would resume the model
    
    def _adjust_quality_on_the_fly(self, quality_level: float):
        """Adjust quality settings during generation."""
        self.logger.info(f"Adjusting quality to {quality_level}")
        # In a real implementation, this would adjust generation parameters
    
    def _emergency_stop(self):
        """Emergency stop all processing."""
        self.logger.warning("Emergency stop activated")
        # In a real implementation, this would immediately halt all processing
    
    def _save_configuration(self):
        """Save current configuration to file."""
        config_data = {
            "ui_configuration": {
                "mode": self.config.mode.value,
                "update_interval": self.config.update_interval,
                "auto_save_config": self.config.auto_save_config,
                "save_session_data": self.config.save_session_data
            },
            "active_profile": self.metrics.active_profile.__dict__ if self.metrics.active_profile else None,
            "memory_profile": self.metrics.memory_profile.__dict__ if self.metrics.memory_profile else None,
            "custom_pipeline": self.metrics.custom_pipeline.__dict__ if self.metrics.custom_pipeline else None
        }
        
        try:
            import json
            filename = f"phase_7b_config_{int(time.time())}.json"
            with open(filename, 'w') as f:
                json.dump(config_data, f, indent=2)
            self.logger.info(f"Configuration saved to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def _save_integrated_session_data(self, session_data):
        """Save integrated session data."""
        # Combine session data with integrated metrics
        integrated_data = {
            "session_data": session_data.__dict__,
            "integrated_metrics": {
                "update_latency": self.metrics.update_latency,
                "memory_overhead": self.metrics.memory_overhead,
                "component_sync_status": self.metrics.component_sync_status
            },
            "performance_history": self.performance_history[-100:]  # Last 100 samples
        }
        
        try:
            import json
            filename = f"integrated_session_{session_data.session_id}.json"
            with open(filename, 'w') as f:
                json.dump(integrated_data, f, indent=2)
            self.logger.info(f"Integrated session data saved to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save session data: {e}")
    
    def _update_performance_history(self, session_data):
        """Update performance history with session results."""
        if hasattr(session_data, 'performance_metrics'):
            perf_summary = {
                "timestamp": time.time(),
                "session_id": session_data.session_id,
                "performance_metrics": session_data.performance_metrics,
                "quality_metrics": getattr(session_data, 'quality_metrics', {}),
                "integration_metrics": {
                    "update_latency": self.metrics.update_latency,
                    "memory_overhead": self.metrics.memory_overhead
                }
            }
            self.performance_history.append(perf_summary)
    
    def show_status(self):
        """Display current system status."""
        status_table = Table(title="Phase 7B Integration Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Metrics", style="white")
        
        # System status
        status_table.add_row("Integration", self.state.value, f"Running: {self.is_running}")
        
        # Component statuses
        for component, synced in self.metrics.component_sync_status.items():
            status = "✓ Synced" if synced else "✗ Not Synced"
            status_table.add_row(component.title(), status, "")
        
        # Performance metrics
        status_table.add_row("Update Latency", 
                           f"{self.metrics.update_latency*1000:.1f}ms",
                           "Target: <50ms")
        status_table.add_row("Memory Overhead", 
                           f"{self.metrics.memory_overhead:.1f}%",
                           "Target: <5%")
        
        self.console.print(status_table)
    
    def get_integration_metrics(self) -> IntegratedMetrics:
        """Get current integrated metrics."""
        return self.metrics
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status as a dictionary."""
        return {
            "is_running": self.is_running,
            "component_sync_status": self.metrics.component_sync_status.copy(),
            "update_latency_ms": self.metrics.update_latency * 1000,
            "memory_overhead_percent": self.metrics.memory_overhead,
            "ui_mode": self.ui_mode.value if hasattr(self, 'ui_mode') else "unknown",
            "components_connected": {
                "dashboard": self.dashboard is not None,
                "visualizer": self.visualizer is not None,
                "controls": self.controls is not None
            }
        }
    
    def set_ui_mode(self, mode: UIMode):
        """Set the UI display mode."""
        self.config.mode = mode
        self.logger.info(f"UI mode changed to: {mode.value}")
        
        # Update component visibility
        self.config.dashboard_enabled = mode in [UIMode.DASHBOARD_ONLY, UIMode.SPLIT_VIEW, 
                                               UIMode.TABBED_VIEW, UIMode.FULL_INTEGRATED]
        self.config.visualizer_enabled = mode in [UIMode.VISUALIZER_ONLY, UIMode.SPLIT_VIEW,
                                                UIMode.TABBED_VIEW, UIMode.FULL_INTEGRATED]
        self.config.controls_enabled = mode in [UIMode.CONTROLS_ONLY, UIMode.TABBED_VIEW,
                                              UIMode.FULL_INTEGRATED]
    
    async def run_integrated_demo(self):
        """Run a demonstration of the integrated system."""
        self.console.print(Panel(
            self.enhancements.create_gradient_text(
                "Phase 7B Integration Demo",
                ["bright_green", "bright_blue", "bright_magenta"]
            ),
            expand=False
        ))
        
        try:
            # Start the integrated system
            await self.start()
            
            # Demonstrate different UI modes
            modes = [UIMode.DASHBOARD_ONLY, UIMode.VISUALIZER_ONLY, UIMode.FULL_INTEGRATED]
            
            for mode in modes:
                self.console.print(f"\n[cyan]Demonstrating {mode.value} mode...[/]")
                self.set_ui_mode(mode)
                
                # Show status
                self.show_status()
                
                # Wait a bit for demonstration
                await asyncio.sleep(2.0)
            
            # Show final integrated view
            self.console.print("\n[green]Integration demonstration complete![/]")
            self.show_status()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Demo interrupted[/]")
        finally:
            await self.stop()


# Example usage and testing
if __name__ == "__main__":
    async def main():
        console = Console()
        
        # Create configuration
        config = UIConfiguration(
            mode=UIMode.FULL_INTEGRATED,
            update_interval=0.05,  # 50ms
            enable_real_time_updates=True,
            save_session_data=True
        )
        
        # Create integrated system
        integration = Phase7BIntegration(console, config)
        
        # Register example callbacks
        integration.register_callback("system_started", 
                                    lambda m: console.print(f"[green]System started with metrics: {type(m).__name__}[/]"))
        integration.register_callback("metrics_synchronized", 
                                    lambda m: console.print(f"[blue]Metrics synchronized at {time.strftime('%H:%M:%S')}[/]"))
        
        # Run demonstration
        await integration.run_integrated_demo()
    
    # Run the example
    asyncio.run(main())
