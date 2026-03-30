"""
Advanced User Controls - Phase 7B Component 3/3
ImpressionCore User Experience Features

This module provides granular user controls for quality vs speed trade-offs,
custom processing pipelines, advanced memory management, and session comparison tools.

Created: 2025-05-30
Component: Priority 7 Phase 7B - Advanced Progressive Generation UI
Status: Implementation Complete
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from enum import Enum
import asyncio
import json
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.layout import Layout
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.columns import Columns

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


class ControlType(Enum):
    """Types of user controls available."""
    QUALITY_SPEED = "quality_speed"
    MEMORY_MANAGEMENT = "memory_management"
    PIPELINE_CUSTOM = "pipeline_custom"
    SESSION_MANAGEMENT = "session_management"
    ADVANCED_TUNING = "advanced_tuning"


class ProcessingMode(Enum):
    """Available processing modes."""
    SPEED_OPTIMIZED = "speed_optimized"
    BALANCED = "balanced"
    QUALITY_OPTIMIZED = "quality_optimized"
    MEMORY_EFFICIENT = "memory_efficient"
    CUSTOM = "custom"


class PipelineStage(Enum):
    """Customizable pipeline stages."""
    PREPROCESSING = "preprocessing"
    TOKENIZATION = "tokenization"
    ENCODING = "encoding"
    GENERATION = "generation"
    POST_PROCESSING = "post_processing"
    VALIDATION = "validation"


@dataclass
class QualitySpeedProfile:
    """Configuration profile for quality vs speed trade-offs."""
    name: str
    description: str
    speed_weight: float  # 0.0-1.0
    quality_weight: float  # 0.0-1.0
    memory_efficiency: float  # 0.0-1.0
    batch_size: int
    precision: str  # "fp16", "fp32", "int8"
    attention_layers: int
    max_sequence_length: int
    beam_width: int
    temperature: float
    top_p: float
    repetition_penalty: float


@dataclass
class MemoryProfile:
    """Memory management configuration."""
    name: str
    max_vram_usage: int  # MB
    max_ram_usage: int  # MB
    gradient_checkpointing: bool
    mixed_precision: bool
    cpu_offloading: bool
    model_sharding: bool
    cache_size: int  # MB
    swap_threshold: float  # 0.0-1.0


@dataclass
class CustomPipeline:
    """Custom processing pipeline configuration."""
    name: str
    description: str
    stages: List[PipelineStage]
    stage_configs: Dict[PipelineStage, Dict[str, Any]]
    parallel_stages: List[Tuple[PipelineStage, PipelineStage]]
    conditional_stages: Dict[str, PipelineStage]
    error_handling: Dict[PipelineStage, str]


@dataclass
class SessionData:
    """Session data for comparison and analysis."""
    session_id: str
    timestamp: float
    configuration: Dict[str, Any]
    performance_metrics: Dict[str, float]
    quality_metrics: Dict[str, float]
    user_feedback: Optional[Dict[str, Any]] = None
    notes: str = ""


@dataclass
class ControlState:
    """Current state of advanced controls."""
    active_profile: Optional[QualitySpeedProfile] = None
    memory_profile: Optional[MemoryProfile] = None
    custom_pipeline: Optional[CustomPipeline] = None
    session_history: List[SessionData] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    is_learning_enabled: bool = True


class AdvancedControls:
    """
    Advanced user control interface for granular system configuration.
    
    Provides comprehensive controls for:
    - Quality vs speed trade-offs
    - Memory management optimization
    - Custom pipeline configuration
    - Session comparison and analysis
    - Advanced parameter tuning
    """
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize advanced controls."""
        self.console = console or Console()
        self.logger = RichLogger("AdvancedControls")
        self.enhancements = RichEnhancements()
        self.animation = RichStatusAnimation(self.console)
        
        # Initialize state
        self.state = ControlState()
        self.callbacks: Dict[str, List[Callable]] = {}
        
        # Load default profiles
        self._load_default_profiles()
        
        # Session management
        self.current_session: Optional[SessionData] = None
        self.session_start_time: Optional[float] = None
        
        self.logger.info("Advanced Controls initialized")
    
    def _load_default_profiles(self):
        """Load default quality/speed and memory profiles."""
        self.quality_profiles = {
            "ultra_fast": QualitySpeedProfile(
                name="Ultra Fast",
                description="Maximum speed, minimal quality",
                speed_weight=1.0,
                quality_weight=0.1,
                memory_efficiency=0.9,
                batch_size=1,
                precision="fp16",
                attention_layers=6,
                max_sequence_length=512,
                beam_width=1,
                temperature=0.8,
                top_p=0.9,
                repetition_penalty=1.0
            ),
            "fast": QualitySpeedProfile(
                name="Fast",
                description="High speed, good quality",
                speed_weight=0.8,
                quality_weight=0.4,
                memory_efficiency=0.7,
                batch_size=2,
                precision="fp16",
                attention_layers=8,
                max_sequence_length=1024,
                beam_width=2,
                temperature=0.7,
                top_p=0.85,
                repetition_penalty=1.05
            ),
            "balanced": QualitySpeedProfile(
                name="Balanced",
                description="Optimal balance of speed and quality",
                speed_weight=0.5,
                quality_weight=0.5,
                memory_efficiency=0.5,
                batch_size=4,
                precision="fp16",
                attention_layers=12,
                max_sequence_length=2048,
                beam_width=3,
                temperature=0.6,
                top_p=0.8,
                repetition_penalty=1.1
            ),
            "quality": QualitySpeedProfile(
                name="High Quality",
                description="High quality, moderate speed",
                speed_weight=0.3,
                quality_weight=0.8,
                memory_efficiency=0.3,
                batch_size=8,
                precision="fp32",
                attention_layers=16,
                max_sequence_length=4096,
                beam_width=5,
                temperature=0.5,
                top_p=0.75,
                repetition_penalty=1.15
            ),
            "ultra_quality": QualitySpeedProfile(
                name="Ultra Quality",
                description="Maximum quality, slower processing",
                speed_weight=0.1,
                quality_weight=1.0,
                memory_efficiency=0.1,
                batch_size=16,
                precision="fp32",
                attention_layers=24,
                max_sequence_length=8192,
                beam_width=8,
                temperature=0.4,
                top_p=0.7,
                repetition_penalty=1.2
            )
        }
        
        self.memory_profiles = {
            "minimal": MemoryProfile(
                name="Minimal VRAM",
                max_vram_usage=2048,  # 2GB
                max_ram_usage=8192,   # 8GB
                gradient_checkpointing=True,
                mixed_precision=True,
                cpu_offloading=True,
                model_sharding=True,
                cache_size=256,
                swap_threshold=0.9
            ),
            "standard": MemoryProfile(
                name="Standard (4GB VRAM)",
                max_vram_usage=3584,  # 3.5GB (leaving 512MB buffer)
                max_ram_usage=16384,  # 16GB
                gradient_checkpointing=True,
                mixed_precision=True,
                cpu_offloading=False,
                model_sharding=False,
                cache_size=512,
                swap_threshold=0.8
            ),
            "high_memory": MemoryProfile(
                name="High Memory",
                max_vram_usage=8192,  # 8GB
                max_ram_usage=32768,  # 32GB
                gradient_checkpointing=False,
                mixed_precision=False,
                cpu_offloading=False,
                model_sharding=False,
                cache_size=1024,
                swap_threshold=0.7
            )
        }
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for control events."""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    def _trigger_callbacks(self, event: str, data: Any = None):
        """Trigger registered callbacks for an event."""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Callback error for {event}: {e}")
    
    def create_quality_profile(self, profile_data: Dict[str, Any]) -> QualitySpeedProfile:
        """Create a new quality profile from provided data."""
        profile = QualitySpeedProfile(
            name=profile_data.get("name", "Custom Profile"),
            resolution_scale=profile_data.get("resolution_scale", 1.0),
            quality_preset=profile_data.get("quality_preset", "balanced"),
            max_sequence_length=profile_data.get("max_sequence_length", 512),
            beam_width=profile_data.get("beam_width", 1),
            temperature=profile_data.get("temperature", 0.7),
            top_p=profile_data.get("top_p", 0.9),
            repetition_penalty=profile_data.get("repetition_penalty", 1.1)
        )
        
        # Add to available profiles
        self.quality_profiles[profile.name] = profile
        return profile
    
    def set_active_profile(self, profile: Union[str, QualitySpeedProfile]) -> bool:
        """Set the active quality profile."""
        try:
            if isinstance(profile, str):
                if profile in self.quality_profiles:
                    self.state.active_profile = self.quality_profiles[profile]
                else:
                    return False
            else:
                self.state.active_profile = profile
            
            self._trigger_callbacks("profile_changed", self.state.active_profile)
            return True
        except Exception as e:
            self.logger.error(f"Error setting active profile: {e}")
            return False
    
    def show_quality_speed_controls(self) -> Optional[QualitySpeedProfile]:
        """Display and handle quality vs speed controls."""
        self.console.print(Panel(
            self.enhancements.create_gradient_text(
                "Quality vs Speed Trade-offs",
                ["bright_blue", "bright_cyan"]
            ),
            expand=False
        ))
        
        # Display current profile
        if self.state.active_profile:
            self.console.print(f"[green]Current Profile:[/] {self.state.active_profile.name}")
        
        # Create profile selection table
        table = Table(title="Available Profiles")
        table.add_column("Profile", style="cyan")
        table.add_column("Speed", style="green")
        table.add_column("Quality", style="yellow")
        table.add_column("Memory Eff.", style="blue")
        table.add_column("Description", style="white")
        
        for key, profile in self.quality_profiles.items():
            speed_bar = "█" * int(profile.speed_weight * 10) + "░" * (10 - int(profile.speed_weight * 10))
            quality_bar = "█" * int(profile.quality_weight * 10) + "░" * (10 - int(profile.quality_weight * 10))
            memory_bar = "█" * int(profile.memory_efficiency * 10) + "░" * (10 - int(profile.memory_efficiency * 10))
            
            table.add_row(
                f"{key} ({profile.name})",
                speed_bar,
                quality_bar,
                memory_bar,
                profile.description
            )
        
        self.console.print(table)
        
        # Profile selection
        choices = list(self.quality_profiles.keys()) + ["custom", "cancel"]
        choice = Prompt.ask(
            "Select profile",
            choices=choices,
            default="balanced"
        )
        
        if choice == "cancel":
            return None
        elif choice == "custom":
            return self._create_custom_quality_profile()
        else:
            profile = self.quality_profiles[choice]
            self.state.active_profile = profile
            self._trigger_callbacks("profile_changed", profile)
            self.console.print(f"[green]✓[/] Profile '{profile.name}' activated")
            return profile
    
    def _create_custom_quality_profile(self) -> Optional[QualitySpeedProfile]:
        """Create a custom quality/speed profile."""
        self.console.print("[yellow]Creating Custom Profile[/]")
        
        try:
            name = Prompt.ask("Profile name", default="Custom Profile")
            description = Prompt.ask("Description", default="User-defined profile")
            
            # Get weights
            speed_weight = float(Prompt.ask("Speed weight (0.0-1.0)", default="0.5"))
            quality_weight = float(Prompt.ask("Quality weight (0.0-1.0)", default="0.5"))
            memory_efficiency = float(Prompt.ask("Memory efficiency (0.0-1.0)", default="0.5"))
            
            # Get technical parameters
            batch_size = int(Prompt.ask("Batch size", default="4"))
            precision = Prompt.ask("Precision", choices=["fp16", "fp32", "int8"], default="fp16")
            attention_layers = int(Prompt.ask("Attention layers", default="12"))
            max_seq_len = int(Prompt.ask("Max sequence length", default="2048"))
            beam_width = int(Prompt.ask("Beam width", default="3"))
            temperature = float(Prompt.ask("Temperature", default="0.6"))
            top_p = float(Prompt.ask("Top-p", default="0.8"))
            rep_penalty = float(Prompt.ask("Repetition penalty", default="1.1"))
            
            profile = QualitySpeedProfile(
                name=name,
                description=description,
                speed_weight=speed_weight,
                quality_weight=quality_weight,
                memory_efficiency=memory_efficiency,
                batch_size=batch_size,
                precision=precision,
                attention_layers=attention_layers,
                max_sequence_length=max_seq_len,
                beam_width=beam_width,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=rep_penalty
            )
            
            # Save custom profile
            self.quality_profiles[f"custom_{int(time.time())}"] = profile
            self.state.active_profile = profile
            self._trigger_callbacks("profile_changed", profile)
            
            self.console.print(f"[green]✓[/] Custom profile '{name}' created and activated")
            return profile
            
        except (ValueError, KeyboardInterrupt) as e:
            self.console.print(f"[red]Error creating profile: {e}[/]")
            return None
    
    def show_memory_controls(self) -> Optional[MemoryProfile]:
        """Display and handle memory management controls."""
        self.console.print(Panel(
            self.enhancements.create_gradient_text(
                "Memory Management Controls",
                ["bright_magenta", "bright_red"]
            ),
            expand=False
        ))
        
        # Display current memory profile
        if self.state.memory_profile:
            self.console.print(f"[green]Current Memory Profile:[/] {self.state.memory_profile.name}")
        
        # Create memory profile table
        table = Table(title="Memory Profiles")
        table.add_column("Profile", style="cyan")
        table.add_column("VRAM (MB)", style="red")
        table.add_column("RAM (MB)", style="green")
        table.add_column("Features", style="yellow")
        
        for key, profile in self.memory_profiles.items():
            features = []
            if profile.gradient_checkpointing:
                features.append("GC")
            if profile.mixed_precision:
                features.append("MP")
            if profile.cpu_offloading:
                features.append("CPU")
            if profile.model_sharding:
                features.append("Shard")
            
            table.add_row(
                f"{key} ({profile.name})",
                str(profile.max_vram_usage),
                str(profile.max_ram_usage),
                ", ".join(features)
            )
        
        self.console.print(table)
        
        # Profile selection
        choices = list(self.memory_profiles.keys()) + ["custom", "cancel"]
        choice = Prompt.ask(
            "Select memory profile",
            choices=choices,
            default="standard"
        )
        
        if choice == "cancel":
            return None
        elif choice == "custom":
            return self._create_custom_memory_profile()
        else:
            profile = self.memory_profiles[choice]
            self.state.memory_profile = profile
            self._trigger_callbacks("memory_profile_changed", profile)
            self.console.print(f"[green]✓[/] Memory profile '{profile.name}' activated")
            return profile
    
    def _create_custom_memory_profile(self) -> Optional[MemoryProfile]:
        """Create a custom memory management profile."""
        self.console.print("[yellow]Creating Custom Memory Profile[/]")
        
        try:
            name = Prompt.ask("Memory profile name", default="Custom Memory")
            
            max_vram = int(Prompt.ask("Max VRAM usage (MB)", default="3584"))
            max_ram = int(Prompt.ask("Max RAM usage (MB)", default="16384"))
            
            gradient_checkpointing = Confirm.ask("Enable gradient checkpointing?", default=True)
            mixed_precision = Confirm.ask("Enable mixed precision?", default=True)
            cpu_offloading = Confirm.ask("Enable CPU offloading?", default=False)
            model_sharding = Confirm.ask("Enable model sharding?", default=False)
            
            cache_size = int(Prompt.ask("Cache size (MB)", default="512"))
            swap_threshold = float(Prompt.ask("Swap threshold (0.0-1.0)", default="0.8"))
            
            profile = MemoryProfile(
                name=name,
                max_vram_usage=max_vram,
                max_ram_usage=max_ram,
                gradient_checkpointing=gradient_checkpointing,
                mixed_precision=mixed_precision,
                cpu_offloading=cpu_offloading,
                model_sharding=model_sharding,
                cache_size=cache_size,
                swap_threshold=swap_threshold
            )
            
            # Save custom profile
            self.memory_profiles[f"custom_{int(time.time())}"] = profile
            self.state.memory_profile = profile
            self._trigger_callbacks("memory_profile_changed", profile)
            
            self.console.print(f"[green]✓[/] Custom memory profile '{name}' created and activated")
            return profile
            
        except (ValueError, KeyboardInterrupt) as e:
            self.console.print(f"[red]Error creating memory profile: {e}[/]")
            return None
    
    def show_pipeline_controls(self) -> Optional[CustomPipeline]:
        """Display and handle custom pipeline controls."""
        self.console.print(Panel(
            self.enhancements.create_gradient_text(
                "Custom Pipeline Configuration",
                ["bright_green", "bright_yellow"]
            ),
            expand=False
        ))
        
        # Show current pipeline
        if self.state.custom_pipeline:
            self.console.print(f"[green]Current Pipeline:[/] {self.state.custom_pipeline.name}")
            self._display_pipeline_stages(self.state.custom_pipeline)
        
        choice = Prompt.ask(
            "Pipeline action",
            choices=["create", "edit", "view", "reset", "cancel"],
            default="create"
        )
        
        if choice == "cancel":
            return None
        elif choice == "create":
            return self._create_custom_pipeline()
        elif choice == "edit" and self.state.custom_pipeline:
            return self._edit_custom_pipeline(self.state.custom_pipeline)
        elif choice == "view" and self.state.custom_pipeline:
            self._display_pipeline_details(self.state.custom_pipeline)
            return self.state.custom_pipeline
        elif choice == "reset":
            self.state.custom_pipeline = None
            self._trigger_callbacks("pipeline_changed", None)
            self.console.print("[green]✓[/] Pipeline reset to default")
            return None
        else:
            self.console.print("[yellow]No action taken[/]")
            return self.state.custom_pipeline
    
    def _create_custom_pipeline(self) -> Optional[CustomPipeline]:
        """Create a custom processing pipeline."""
        self.console.print("[yellow]Creating Custom Pipeline[/]")
        
        try:
            name = Prompt.ask("Pipeline name", default="Custom Pipeline")
            description = Prompt.ask("Description", default="User-defined pipeline")
            
            # Select stages
            available_stages = list(PipelineStage)
            selected_stages = []
            
            self.console.print("\n[cyan]Select pipeline stages:[/]")
            for i, stage in enumerate(available_stages):
                include = Confirm.ask(f"Include {stage.value}?", default=True)
                if include:
                    selected_stages.append(stage)
            
            if not selected_stages:
                self.console.print("[red]No stages selected![/]")
                return None
            
            # Configure stages
            stage_configs = {}
            for stage in selected_stages:
                self.console.print(f"\n[yellow]Configuring {stage.value}:[/]")
                config = self._configure_pipeline_stage(stage)
                stage_configs[stage] = config
            
            pipeline = CustomPipeline(
                name=name,
                description=description,
                stages=selected_stages,
                stage_configs=stage_configs,
                parallel_stages=[],
                conditional_stages={},
                error_handling={}
            )
            
            self.state.custom_pipeline = pipeline
            self._trigger_callbacks("pipeline_changed", pipeline)
            
            self.console.print(f"[green]✓[/] Custom pipeline '{name}' created and activated")
            return pipeline
            
        except (ValueError, KeyboardInterrupt) as e:
            self.console.print(f"[red]Error creating pipeline: {e}[/]")
            return None
    
    def _configure_pipeline_stage(self, stage: PipelineStage) -> Dict[str, Any]:
        """Configure a specific pipeline stage."""
        config = {}
        
        if stage == PipelineStage.PREPROCESSING:
            config["normalization"] = Confirm.ask("Enable text normalization?", default=True)
            config["filtering"] = Confirm.ask("Enable content filtering?", default=True)
            config["augmentation"] = Confirm.ask("Enable data augmentation?", default=False)
        
        elif stage == PipelineStage.TOKENIZATION:
            config["method"] = Prompt.ask(
                "Tokenization method",
                choices=["bpe", "wordpiece"],
                default="bpe"
            )
            config["vocab_size"] = int(Prompt.ask("Vocabulary size", default="32000"))
        
        elif stage == PipelineStage.ENCODING:
            config["layers"] = int(Prompt.ask("Encoder layers", default="12"))
            config["heads"] = int(Prompt.ask("Attention heads", default="12"))
            config["dropout"] = float(Prompt.ask("Dropout rate", default="0.1"))
        
        elif stage == PipelineStage.GENERATION:
            config["strategy"] = Prompt.ask(
                "Generation strategy",
                choices=["greedy", "beam", "sampling"],
                default="beam"
            )
            config["max_length"] = int(Prompt.ask("Max generation length", default="512"))
        
        elif stage == PipelineStage.POST_PROCESSING:
            config["cleanup"] = Confirm.ask("Enable output cleanup?", default=True)
            config["formatting"] = Confirm.ask("Enable output formatting?", default=True)
        
        elif stage == PipelineStage.VALIDATION:
            config["quality_check"] = Confirm.ask("Enable quality checking?", default=True)
            config["safety_check"] = Confirm.ask("Enable safety checking?", default=True)
        
        return config
    
    def _display_pipeline_stages(self, pipeline: CustomPipeline):
        """Display pipeline stages in a visual format."""
        stages_text = " → ".join([stage.value for stage in pipeline.stages])
        self.console.print(f"[cyan]Stages:[/] {stages_text}")
    
    def _display_pipeline_details(self, pipeline: CustomPipeline):
        """Display detailed pipeline information."""
        table = Table(title=f"Pipeline: {pipeline.name}")
        table.add_column("Stage", style="cyan")
        table.add_column("Configuration", style="white")
        
        for stage in pipeline.stages:
            config = pipeline.stage_configs.get(stage, {})
            config_str = ", ".join([f"{k}={v}" for k, v in config.items()])
            table.add_row(stage.value, config_str or "Default")
        
        self.console.print(table)
    
    def _edit_custom_pipeline(self, pipeline: CustomPipeline) -> Optional[CustomPipeline]:
        """Edit an existing custom pipeline."""
        # Implementation would allow editing of existing pipeline
        # For now, redirect to creation
        self.console.print("[yellow]Pipeline editing not yet implemented. Creating new pipeline...[/]")
        return self._create_custom_pipeline()
    
    def show_session_management(self):
        """Display and handle session management controls."""
        self.console.print(Panel(
            self.enhancements.create_gradient_text(
                "Session Management",
                ["bright_cyan", "bright_white"]
            ),
            expand=False
        ))
        
        if not self.state.session_history:
            self.console.print("[yellow]No sessions recorded yet[/]")
            return
        
        # Display session history
        table = Table(title="Session History")
        table.add_column("Session ID", style="cyan")
        table.add_column("Timestamp", style="green")
        table.add_column("Profile", style="yellow")
        table.add_column("Performance", style="blue")
        table.add_column("Quality", style="magenta")
        
        for session in self.state.session_history[-10:]:  # Show last 10 sessions
            timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(session.timestamp))
            profile_name = session.configuration.get("profile_name", "Unknown")
            
            # Performance summary
            perf_metrics = session.performance_metrics
            perf_summary = f"Speed: {perf_metrics.get('speed', 0):.1f}ms"
            
            # Quality summary
            qual_metrics = session.quality_metrics
            qual_summary = f"Score: {qual_metrics.get('overall_score', 0):.2f}"
            
            table.add_row(
                session.session_id[:8] + "...",
                timestamp,
                profile_name,
                perf_summary,
                qual_summary
            )
        
        self.console.print(table)
        
        # Session management actions
        choice = Prompt.ask(
            "Session action",
            choices=["compare", "export", "clear", "view_details", "cancel"],
            default="cancel"
        )
        
        if choice == "compare":
            self._compare_sessions()
        elif choice == "export":
            self._export_session_data()
        elif choice == "clear":
            if Confirm.ask("Clear all session history?"):
                self.state.session_history.clear()
                self.console.print("[green]✓[/] Session history cleared")
        elif choice == "view_details":
            self._view_session_details()
    
    def _compare_sessions(self):
        """Compare multiple sessions."""
        if len(self.state.session_history) < 2:
            self.console.print("[yellow]Need at least 2 sessions to compare[/]")
            return
        
        # Select sessions to compare
        session_choices = [f"{s.session_id[:8]}... ({time.strftime('%Y-%m-%d %H:%M', time.localtime(s.timestamp))})" 
                          for s in self.state.session_history]
        
        self.console.print("[cyan]Select first session:[/]")
        for i, choice in enumerate(session_choices):
            self.console.print(f"{i}: {choice}")
        
        try:
            idx1 = int(Prompt.ask("First session index"))
            idx2 = int(Prompt.ask("Second session index"))
            
            if 0 <= idx1 < len(self.state.session_history) and 0 <= idx2 < len(self.state.session_history):
                session1 = self.state.session_history[idx1]
                session2 = self.state.session_history[idx2]
                self._display_session_comparison(session1, session2)
            else:
                self.console.print("[red]Invalid session indices[/]")
        except (ValueError, IndexError):
            self.console.print("[red]Invalid input[/]")
    
    def _display_session_comparison(self, session1: SessionData, session2: SessionData):
        """Display detailed comparison between two sessions."""
        comparison_table = Table(title="Session Comparison")
        comparison_table.add_column("Metric", style="cyan")
        comparison_table.add_column(f"Session 1 ({session1.session_id[:8]}...)", style="green")
        comparison_table.add_column(f"Session 2 ({session2.session_id[:8]}...)", style="yellow")
        comparison_table.add_column("Difference", style="red")
        
        # Compare performance metrics
        for metric in ["speed", "memory_usage", "throughput"]:
            val1 = session1.performance_metrics.get(metric, 0)
            val2 = session2.performance_metrics.get(metric, 0)
            diff = val2 - val1
            diff_str = f"{diff:+.2f}" if diff != 0 else "0"
            
            comparison_table.add_row(
                f"Performance: {metric}",
                f"{val1:.2f}",
                f"{val2:.2f}",
                diff_str
            )
        
        # Compare quality metrics
        for metric in ["overall_score", "coherence", "relevance"]:
            val1 = session1.quality_metrics.get(metric, 0)
            val2 = session2.quality_metrics.get(metric, 0)
            diff = val2 - val1
            diff_str = f"{diff:+.2f}" if diff != 0 else "0"
            
            comparison_table.add_row(
                f"Quality: {metric}",
                f"{val1:.2f}",
                f"{val2:.2f}",
                diff_str
            )
        
        self.console.print(comparison_table)
    
    def _export_session_data(self):
        """Export session data to file."""
        if not self.state.session_history:
            self.console.print("[yellow]No session data to export[/]")
            return
        
        export_data = {
            "export_timestamp": time.time(),
            "sessions": [
                {
                    "session_id": s.session_id,
                    "timestamp": s.timestamp,
                    "configuration": s.configuration,
                    "performance_metrics": s.performance_metrics,
                    "quality_metrics": s.quality_metrics,
                    "user_feedback": s.user_feedback,
                    "notes": s.notes
                }
                for s in self.state.session_history
            ]
        }
        
        filename = f"session_data_export_{int(time.time())}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            self.console.print(f"[green]✓[/] Session data exported to {filename}")
        except Exception as e:
            self.console.print(f"[red]Export failed: {e}[/]")
    
    def _view_session_details(self):
        """View detailed information for a specific session."""
        session_choices = [f"{s.session_id[:8]}... ({time.strftime('%Y-%m-%d %H:%M', time.localtime(s.timestamp))})" 
                          for s in self.state.session_history]
        
        self.console.print("[cyan]Select session to view:[/]")
        for i, choice in enumerate(session_choices):
            self.console.print(f"{i}: {choice}")
        
        try:
            idx = int(Prompt.ask("Session index"))
            if 0 <= idx < len(self.state.session_history):
                session = self.state.session_history[idx]
                self._display_detailed_session(session)
            else:
                self.console.print("[red]Invalid session index[/]")
        except (ValueError, IndexError):
            self.console.print("[red]Invalid input[/]")
    
    def _display_detailed_session(self, session: SessionData):
        """Display detailed information for a single session."""
        self.console.print(Panel(f"Session Details: {session.session_id}"))
        
        # Basic info
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(session.timestamp))
        self.console.print(f"[cyan]Timestamp:[/] {timestamp}")
        self.console.print(f"[cyan]Notes:[/] {session.notes or 'None'}")
        
        # Configuration
        config_table = Table(title="Configuration")
        config_table.add_column("Parameter", style="cyan")
        config_table.add_column("Value", style="white")
        
        for key, value in session.configuration.items():
            config_table.add_row(key, str(value))
        
        self.console.print(config_table)
        
        # Performance metrics
        perf_table = Table(title="Performance Metrics")
        perf_table.add_column("Metric", style="green")
        perf_table.add_column("Value", style="white")
        
        for key, value in session.performance_metrics.items():
            perf_table.add_row(key, f"{value:.3f}")
        
        self.console.print(perf_table)
        
        # Quality metrics
        qual_table = Table(title="Quality Metrics")
        qual_table.add_column("Metric", style="yellow")
        qual_table.add_column("Value", style="white")
        
        for key, value in session.quality_metrics.items():
            qual_table.add_row(key, f"{value:.3f}")
        
        self.console.print(qual_table)
    
    def start_session(self, session_id: Optional[str] = None) -> str:
        """Start a new session for tracking."""
        if not session_id:
            session_id = f"session_{int(time.time())}_{len(self.state.session_history)}"
        
        self.current_session = SessionData(
            session_id=session_id,
            timestamp=time.time(),
            configuration={},
            performance_metrics={},
            quality_metrics={}
        )
        self.session_start_time = time.time()
        
        self.logger.info(f"Session started: {session_id}")
        return session_id
    
    def end_session(self, performance_metrics: Dict[str, float], 
                   quality_metrics: Dict[str, float], 
                   user_feedback: Optional[Dict[str, Any]] = None,
                   notes: str = ""):
        """End current session and save data."""
        if not self.current_session:
            self.logger.warning("No active session to end")
            return
        
        self.current_session.performance_metrics = performance_metrics
        self.current_session.quality_metrics = quality_metrics
        self.current_session.user_feedback = user_feedback
        self.current_session.notes = notes
        
        # Capture current configuration
        config = {}
        if self.state.active_profile:
            config["profile_name"] = self.state.active_profile.name
            config["profile_config"] = self.state.active_profile.__dict__
        if self.state.memory_profile:
            config["memory_profile"] = self.state.memory_profile.__dict__
        if self.state.custom_pipeline:
            config["custom_pipeline"] = self.state.custom_pipeline.__dict__
        
        self.current_session.configuration = config
        
        # Add to history
        self.state.session_history.append(self.current_session)
        
        # Trigger callbacks
        self._trigger_callbacks("session_ended", self.current_session)
        
        self.logger.info(f"Session ended: {self.current_session.session_id}")
        self.current_session = None
        self.session_start_time = None
    
    def show_main_controls(self):
        """Display main controls interface."""
        layout = Layout()
        layout.split_column(
            Layout(Panel(
                self.enhancements.create_gradient_text(
                    "ImpressionCore Advanced Controls",
                    ["bright_blue", "bright_cyan", "bright_white"]
                ),
                expand=False
            ), name="header"),
            Layout(name="body")
        )
        
        # Create control panels
        controls = [
            "[1] Quality vs Speed Trade-offs",
            "[2] Memory Management",
            "[3] Custom Pipeline Configuration",
            "[4] Session Management",
            "[5] View Current Settings",
            "[6] Export Configuration",
            "[7] Reset All Settings",
            "[0] Exit"
        ]
        
        control_text = "\n".join(controls)
        layout["body"].update(Panel(control_text, title="Available Controls"))
        
        self.console.print(layout)
        
        choice = Prompt.ask("Select control", choices=["1", "2", "3", "4", "5", "6", "7", "0"])
        
        if choice == "1":
            self.show_quality_speed_controls()
        elif choice == "2":
            self.show_memory_controls()
        elif choice == "3":
            self.show_pipeline_controls()
        elif choice == "4":
            self.show_session_management()
        elif choice == "5":
            self._show_current_settings()
        elif choice == "6":
            self._export_configuration()
        elif choice == "7":
            self._reset_all_settings()
        elif choice == "0":
            return False
        
        return True
    
    def _show_current_settings(self):
        """Display current configuration settings."""
        settings_table = Table(title="Current Settings")
        settings_table.add_column("Category", style="cyan")
        settings_table.add_column("Setting", style="white")
        
        # Quality profile
        if self.state.active_profile:
            settings_table.add_row("Quality Profile", self.state.active_profile.name)
        else:
            settings_table.add_row("Quality Profile", "Default")
        
        # Memory profile
        if self.state.memory_profile:
            settings_table.add_row("Memory Profile", self.state.memory_profile.name)
        else:
            settings_table.add_row("Memory Profile", "Default")
        
        # Custom pipeline
        if self.state.custom_pipeline:
            settings_table.add_row("Custom Pipeline", self.state.custom_pipeline.name)
        else:
            settings_table.add_row("Custom Pipeline", "Default")
        
        # Session info
        if self.current_session:
            settings_table.add_row("Active Session", self.current_session.session_id)
        else:
            settings_table.add_row("Active Session", "None")
        
        settings_table.add_row("Session History", f"{len(self.state.session_history)} sessions")
        
        self.console.print(settings_table)
    
    def _export_configuration(self):
        """Export current configuration to file."""
        config_data = {
            "export_timestamp": time.time(),
            "active_profile": self.state.active_profile.__dict__ if self.state.active_profile else None,
            "memory_profile": self.state.memory_profile.__dict__ if self.state.memory_profile else None,
            "custom_pipeline": self.state.custom_pipeline.__dict__ if self.state.custom_pipeline else None,
            "user_preferences": self.state.user_preferences
        }
        
        filename = f"advanced_controls_config_{int(time.time())}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(config_data, f, indent=2)
            self.console.print(f"[green]✓[/] Configuration exported to {filename}")
        except Exception as e:
            self.console.print(f"[red]Export failed: {e}[/]")
    
    def _reset_all_settings(self):
        """Reset all settings to defaults."""
        if Confirm.ask("Reset all settings to defaults? This cannot be undone."):
            self.state = ControlState()
            self._trigger_callbacks("settings_reset", None)
            self.console.print("[green]✓[/] All settings reset to defaults")
    
    def get_current_configuration(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        return {
            "active_profile": self.state.active_profile.__dict__ if self.state.active_profile else None,
            "memory_profile": self.state.memory_profile.__dict__ if self.state.memory_profile else None,
            "custom_pipeline": self.state.custom_pipeline.__dict__ if self.state.custom_pipeline else None,
            "user_preferences": self.state.user_preferences,
            "learning_enabled": self.state.is_learning_enabled
        }
    
    async def run_interactive_mode(self):
        """Run interactive control mode."""
        self.console.print(Panel(
            self.enhancements.create_gradient_text(
                "Advanced Controls - Interactive Mode",
                ["bright_green", "bright_blue"]
            ),
            expand=False
        ))
        
        try:
            while True:
                if not self.show_main_controls():
                    break
                
                # Small delay for better UX
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Interactive mode interrupted[/]")
        finally:
            self.console.print("[green]Advanced Controls session ended[/]")


# Example usage and testing
if __name__ == "__main__":
    async def main():
        console = Console()
        controls = AdvancedControls(console)
        
        # Register example callbacks
        controls.register_callback("profile_changed", 
                                  lambda p: console.print(f"[green]Profile changed to: {p.name}[/]"))
        controls.register_callback("memory_profile_changed", 
                                  lambda p: console.print(f"[blue]Memory profile changed to: {p.name}[/]"))
        
        # Run interactive mode
        await controls.run_interactive_mode()
    
    # Run the example
    asyncio.run(main())
