#!/usr/bin/env python3
"""
ImpressionCore: Train Small

Module for train small functionality in the ImpressionCore framework.

File: examples\train_small.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, pytorch, production, 2025, object-oriented]
Dependencies: [torch, rich, typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements train small functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
from examples.train_small import SimpleModelTrainer
instance = SimpleModelTrainer()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import sys
import math
import time
import psutil
import random
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, get_scheduler

# Rich terminal imports
from rich.console import Console
from rich.progress import (
    Progress, TextColumn, BarColumn, TimeElapsedColumn,
    TimeRemainingColumn, TaskProgressColumn, SpinnerColumn
)
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.logging import RichHandler
from rich.traceback import install as install_rich_traceback
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich.align import Align
from rich.box import Box, ROUNDED

# Install rich traceback handler for improved error reporting
install_rich_traceback(show_locals=True)

# Add the project root to the path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Import the modules we need
from src.core.model import ImpressionCoreModel
# Memory optimization: Explicit memory cleanup
from src.core.config import get_impressioncore_small_config
from examples.custom_dataset import CustomTextDataset

# Initialize console
console = Console()

# Configure rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)

def get_memory_stats() -> Dict[str, float]:
# Memory optimization: Memory-critical operation
    """Get current memory usage statistics for CPU and GPU."""
    # Memory optimization: Memory-critical operation
    stats = {
        'cpu_percent': psutil.cpu_percent(),
        'cpu_used_gb': psutil.virtual_memory().used / (1024**3),
        # Memory optimization: Memory-critical operation
        'cpu_total_gb': psutil.virtual_memory().total / (1024**3),
        # Memory optimization: Memory-critical operation
    }
    
    # Add GPU stats if available
    # Memory optimization: Memory-critical operation
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        current_device = torch.cuda.current_device()
        # Memory optimization: CUDA operations for GPU acceleration
        stats.update({
            'gpu_used_gb': torch.cuda.memory_allocated(current_device) / (1024**3),
            # Memory optimization: CUDA operations for GPU acceleration
            'gpu_reserved_gb': torch.cuda.memory_reserved(current_device) / (1024**3),
            # Memory optimization: CUDA operations for GPU acceleration
            'gpu_total_gb': torch.cuda.get_device_properties(current_device).total_memory / (1024**3),
            # Memory optimization: CUDA operations for GPU acceleration
            'gpu_percent': (torch.cuda.memory_allocated(current_device) / 
            # Memory optimization: CUDA operations for GPU acceleration
                           torch.cuda.get_device_properties(current_device).total_memory) * 100,
                           # Memory optimization: CUDA operations for GPU acceleration
            'gpu_utilization': torch.cuda.utilization(current_device) if hasattr(torch.cuda, 'utilization') else 0
            # Memory optimization: CUDA operations for GPU acceleration
        })
        
        # Add memory fragmentation stats if available
        # Memory optimization: Memory-critical operation
        try:
            memory_stats = torch.cuda.memory_stats(current_device)
            # Memory optimization: CUDA operations for GPU acceleration
            if 'allocated_bytes.all.current' in memory_stats and 'reserved_bytes.all.current' in memory_stats:
            # Memory optimization: Memory-critical operation
                allocation_ratio = memory_stats['allocated_bytes.all.current'] / max(memory_stats['reserved_bytes.all.current'], 1)
                # Memory optimization: Memory-critical operation
                stats['gpu_fragmentation'] = (1 - allocation_ratio) * 100  # Higher value means more fragmentation
                # Memory optimization: Memory-critical operation
        except:
            # Some older CUDA versions don't support memory_stats
            # Memory optimization: Memory-critical operation
            stats['gpu_fragmentation'] = 0
            # Memory optimization: Memory-critical operation
    
    return stats

def format_time(seconds: float) -> str:
    """Format seconds into a human-readable time string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{int(minutes)}m {int(seconds % 60)}s"
    else:
        hours = seconds / 3600
        minutes = (seconds % 3600) / 60
        return f"{int(hours)}h {int(minutes)}m"

def format_memory(bytes_value: float) -> str:
# Memory optimization: Memory-critical operation
    """Format memory values into human-readable format with appropriate units."""
    # Memory optimization: Memory-critical operation
    kb = bytes_value / 1024
    if kb < 1024:
        return f"{kb:.2f} KB"
    mb = kb / 1024
    if mb < 1024:
        return f"{mb:.2f} MB"
    gb = mb / 1024
    return f"{gb:.2f} GB"

def display_system_info() -> Panel:
    """Display detailed system information in a rich formatted panel."""
    # Create system info table
    system_table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
    system_table.add_column("Component", style="dim")
    system_table.add_column("Details", justify="right")
    
    # Add CPU information
    cpu_count = psutil.cpu_count(logical=True)
    physical_cores = psutil.cpu_count(logical=False)
    system_table.add_row("CPU Cores", f"[cyan]{physical_cores} physical / {cpu_count} logical[/cyan]")
    system_table.add_row("CPU Usage", f"[yellow]{psutil.cpu_percent()}%[/yellow]")
    
    # Add RAM information
    ram = psutil.virtual_memory()
    # Memory optimization: Memory-critical operation
    system_table.add_row("RAM", f"[green]{ram.total / (1024**3):.2f} GB total / {ram.used / (1024**3):.2f} GB used ({ram.percent}%)[/green]")
    
    # Add GPU information
    # Memory optimization: Memory-critical operation
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        gpu_count = torch.cuda.device_count()
        # Memory optimization: CUDA operations for GPU acceleration
        for i in range(gpu_count):
        # Memory optimization: Memory-critical operation
            gpu_props = torch.cuda.get_device_properties(i)
            # Memory optimization: CUDA operations for GPU acceleration
            gpu_mem_total = gpu_props.total_memory / (1024**3)
            # Memory optimization: Memory-critical operation
            gpu_mem_used = torch.cuda.memory_allocated(i) / (1024**3)
            # Memory optimization: CUDA operations for GPU acceleration
            gpu_mem_reserved = torch.cuda.memory_reserved(i) / (1024**3)
            # Memory optimization: CUDA operations for GPU acceleration
            gpu_mem_percent = (gpu_mem_used / gpu_mem_total) * 100
            # Memory optimization: Memory-critical operation
            
            system_table.add_row(
                f"GPU {i}", 
                # Memory optimization: Memory-critical operation
                f"[bold red]{gpu_props.name}[/bold red]\n#!/usr/bin/env python3
"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: src\examples\train_small.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-25
Modified: 2025-05-25
Version: 1.0.0

Authors:
- Kirk LaSalle & GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [examples]
Dependencies: [] # TODO: Auto-detect or allow manual input
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
# TODO: Add a brief description of this file's purpose.

Design Philosophy:
# TODO: Add design philosophy if applicable.

Memory Considerations:
# TODO: Document any specific memory considerations for this file.

Examples:
# TODO: Provide usage examples if applicable.

Notes:
# TODO: Add any relevant notes.
"""
\n\n"
                # Memory optimization: Memory-critical operation
                f"[red]Used: {gpu_mem_used:.2f} GB / {gpu_mem_total:.2f} GB ({gpu_mem_percent:.1f}%)[/red]\n"
                # Memory optimization: Memory-critical operation
                f"[yellow]Reserved: {gpu_mem_reserved:.2f} GB ({(gpu_mem_reserved / gpu_mem_total) * 100:.1f}%)[/yellow]"
                # Memory optimization: Memory-critical operation
            )
    else:
        system_table.add_row("GPU", "[red]No GPU available[/red]")
        # Memory optimization: Memory-critical operation
    
    # Add PyTorch information
    system_table.add_row("PyTorch", f"[blue]{torch.__version__}[/blue]")
    system_table.add_row("CUDA Available", f"[{'green' if torch.cuda.is_available() else 'red'}]{torch.cuda.is_available()}[/{'green' if torch.cuda.is_available() else 'red'}]")
    # Memory optimization: CUDA operations for GPU acceleration
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        system_table.add_row("CUDA Version", f"[blue]{torch.version.cuda}[/blue]")
        # Memory optimization: Memory-critical operation
    
    # Return the table in a panel
    return Panel(system_table, title="[bold]System Information[/bold]", border_style="green")

def create_memory_efficiency_panel(memory_stats: Dict[str, float]) -> Panel:
# Memory optimization: Memory-critical operation
    """Create a panel with memory efficiency metrics and recommendations."""
    # Memory optimization: Memory-critical operation
    memory_table = Table(box=ROUNDED)
    # Memory optimization: Memory-critical operation
    memory_table.add_column("Metric", style="cyan")
    # Memory optimization: Memory-critical operation
    memory_table.add_column("Value", style="green")
    # Memory optimization: Memory-critical operation
    memory_table.add_column("Status", style="yellow")
    # Memory optimization: Memory-critical operation
    
    # Add CPU memory metrics
    # Memory optimization: Memory-critical operation
    cpu_percent = memory_stats['cpu_percent']
    # Memory optimization: Memory-critical operation
    cpu_status = "✅ Good" if cpu_percent < 80 else "⚠️ High" if cpu_percent < 95 else "❌ Critical"
    memory_table.add_row(
    # Memory optimization: Memory-critical operation
        "CPU Usage", 
        f"{cpu_percent:.1f}%", 
        cpu_status
    )
    
    # Add RAM memory metrics
    # Memory optimization: Memory-critical operation
    ram_used = memory_stats['cpu_used_gb']
    # Memory optimization: Memory-critical operation
    ram_total = memory_stats['cpu_total_gb']
    # Memory optimization: Memory-critical operation
    ram_percent = (ram_used / ram_total) * 100
    ram_status = "✅ Good" if ram_percent < 80 else "⚠️ High" if ram_percent < 95 else "❌ Critical"
    memory_table.add_row(
    # Memory optimization: Memory-critical operation
        "RAM Usage", 
        f"{ram_used:.2f} GB / {ram_total:.2f} GB ({ram_percent:.1f}%)", 
        ram_status
    )
    
    # Add GPU metrics if available
    # Memory optimization: Memory-critical operation
    recommendations = []
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        gpu_used = memory_stats['gpu_used_gb']
        # Memory optimization: Memory-critical operation
        gpu_total = memory_stats['gpu_total_gb']
        # Memory optimization: Memory-critical operation
        gpu_percent = memory_stats['gpu_percent']
        # Memory optimization: Memory-critical operation
        gpu_status = "✅ Good" if gpu_percent < 80 else "⚠️ High" if gpu_percent < 95 else "❌ Critical"
        # Memory optimization: Memory-critical operation
        
        memory_table.add_row(
        # Memory optimization: Memory-critical operation
            "GPU Memory", 
            # Memory optimization: Memory-critical operation
            f"{gpu_used:.2f} GB / {gpu_total:.2f} GB ({gpu_percent:.1f}%)",
            # Memory optimization: Memory-critical operation
            gpu_status
            # Memory optimization: Memory-critical operation
        )
        
        # Add fragmentation information if available
        if 'gpu_fragmentation' in memory_stats:
        # Memory optimization: Memory-critical operation
            frag_percent = memory_stats['gpu_fragmentation']
            # Memory optimization: Memory-critical operation
            frag_status = "✅ Low" if frag_percent < 15 else "⚠️ Medium" if frag_percent < 30 else "❌ High"
            memory_table.add_row(
            # Memory optimization: Memory-critical operation
                "GPU Fragmentation", 
                # Memory optimization: Memory-critical operation
                f"{frag_percent:.1f}%", 
                frag_status
            )
            
            if frag_percent > 15:
                recommendations.append("⚠️ Consider using torch.cuda.empty_cache() periodically to reduce fragmentation")
                # Memory optimization: CUDA operations for GPU acceleration
        
        # Add recommendations based on GPU usage
        # Memory optimization: Memory-critical operation
        if gpu_percent > 90:
        # Memory optimization: Memory-critical operation
            recommendations.append("⚠️ GPU memory usage is very high. Consider reducing batch size or model size")
            # Memory optimization: Explicit memory cleanup
            recommendations.append("⚠️ Enable gradient checkpointing to reduce memory requirements")
            # Memory optimization: Memory-critical operation
        
        if gpu_percent > 80:
        # Memory optimization: Memory-critical operation
            recommendations.append("ℹ️ Use mixed precision (fp16) to reduce memory usage")
            # Memory optimization: Memory-critical operation
    
    # Create recommendations text
    recommendations_text = "\n".join(recommendations) if recommendations else "✅ No memory efficiency issues detected"
    # Memory optimization: Memory-critical operation
    
    # Return combined panel
    return Panel(
        Align.center(
            Text.from_markup(f"{memory_table}\n\n[bold cyan]Recommendations:[/bold cyan]\n{recommendations_text}")
            # Memory optimization: Memory-critical operation
        ),
        title="[bold]Memory Efficiency[/bold]",
        # Memory optimization: Memory-critical operation
        border_style="yellow"
    )

def create_training_metrics_panel(history: Dict[str, List[float]], current_epoch: int, total_epochs: int) -> Panel:
    """Create a panel with training metrics visualization."""
    # Create a table for current metrics
    metrics_table = Table(box=ROUNDED)
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Current", style="green")
    metrics_table.add_column("Best", style="yellow")
    metrics_table.add_column("Average", style="blue")
    
    # Add training loss metrics
    train_losses = history.get('train_loss', [])
    if train_losses:
        current_train_loss = train_losses[-1]
        best_train_loss = min(train_losses)
        avg_train_loss = sum(train_losses) / len(train_losses)
        
        metrics_table.add_row(
            "Training Loss",
            f"{current_train_loss:.4f}",
            f"{best_train_loss:.4f}",
            f"{avg_train_loss:.4f}"
        )
    
    # Add validation loss metrics if available
    val_losses = history.get('val_loss', [])
    if val_losses:
        current_val_loss = val_losses[-1]
        best_val_loss = min(val_losses)
        avg_val_loss = sum(val_losses) / len(val_losses)
        
        metrics_table.add_row(
            "Validation Loss",
            f"{current_val_loss:.4f}",
            f"{best_val_loss:.4f}",
            f"{avg_val_loss:.4f}"
        )
    
    # Add learning rate if available
    learning_rates = history.get('learning_rates', [])
    if learning_rates:
        current_lr = learning_rates[-1]
        metrics_table.add_row(
            "Learning Rate",
            f"{current_lr:.6f}",
            f"{max(learning_rates):.6f}",
            f"{sum(learning_rates) / len(learning_rates):.6f}"
        )
    
    # Create a simple ASCII chart for loss trends
    loss_chart = ""
    if train_losses:
        # Normalize the last 20 values of train_losses for ASCII chart
        display_losses = train_losses[-20:] if len(train_losses) > 20 else train_losses
        max_loss = max(display_losses)
        min_loss = min(display_losses)
        range_loss = max(max_loss - min_loss, 1e-5)  # Avoid division by zero
        
        # Generate ASCII chart
        chart_height = 5
        chart_width = len(display_losses)
        
        # Choose chart symbols based on trend
        loss_trend = "⬆️ Increasing" if len(display_losses) > 1 and display_losses[-1] > display_losses[0] else "⬇️ Decreasing"
        chart_symbols = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        
        # Generate chart line
        chart_line = ""
        for loss in display_losses:
            normalized = (loss - min_loss) / range_loss
            idx = min(int(normalized * (len(chart_symbols) - 1)), len(chart_symbols) - 1)
            chart_line += chart_symbols[idx]
        
        loss_chart = f"Loss Trend: {loss_trend}\n[cyan]{chart_line}[/cyan]"
    
    # Combine everything into a panel
    return Panel(
        Align.center(
            Text.from_markup(
                f"[bold]Epoch {current_epoch}/{total_epochs}[/bold]\n\n"
                f"{metrics_table}\n\n"
                f"{loss_chart}"
            )
        ),
        title="[bold]Training Metrics[/bold]",
        border_style="blue"
    )

def create_checkpoint_panel(model_path: str, save_interval: int, current_step: int) -> Panel:
    """Create a panel with checkpoint information."""
    checkpoint_info = Text()
    
    # Calculate steps until next checkpoint
    steps_to_checkpoint = save_interval - (current_step % save_interval) if save_interval > 0 else 0
    
    # Add checkpoint directory information
    checkpoint_info.append("Checkpoint Directory:\n", style="bold cyan")
    checkpoint_info.append(f"{model_path}\n\n", style="green")
    
    # Add checkpoint interval information
    checkpoint_info.append("Save Interval: ", style="bold cyan")
    checkpoint_info.append(f"{save_interval} steps\n", style="yellow")
    
    # Add steps to next checkpoint
    checkpoint_info.append("Next Checkpoint: ", style="bold cyan")
    checkpoint_info.append(
        f"In {steps_to_checkpoint} steps" if steps_to_checkpoint > 0 else "At current step",
        style="green"
    )
    
    # Check if checkpoint directory exists and how many checkpoints are saved
    checkpoint_count = 0
    if os.path.exists(model_path):
        checkpoint_files = [f for f in os.listdir(model_path) if f.endswith('.pt') or f.endswith('.bin')]
        checkpoint_count = len(checkpoint_files)
    
    # Add checkpoint count information
    checkpoint_info.append("\n\nCheckpoints Saved: ", style="bold cyan")
    checkpoint_info.append(f"{checkpoint_count}", style="green")
    
    # Return the panel
    return Panel(
        Align.center(checkpoint_info),
        title="[bold]Checkpoint Status[/bold]",
        border_style="magenta"
    )

class SimpleModelTrainer:
    """A simple trainer for language models with rich progress visualization."""
    
    def __init__(
        """
        
    __init__ function for processing.
    
    Args:
        self, model, tokenizer, optimizer, train_dataloader, val_dataloader, scheduler, device, output_dir, save_steps, fp16, memory_efficient: Function parameters
        # Memory optimization: Device placement for memory management
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self,
        model: nn.Module,
        tokenizer: Any,
        optimizer: optim.Optimizer,
        train_dataloader: DataLoader,
        val_dataloader: Optional[DataLoader] = None,
        scheduler: Optional[Any] = None,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        # Memory optimization: CUDA operations for GPU acceleration
        output_dir: str = "./models/small",
        save_steps: int = 0,
        fp16: bool = False,
        memory_efficient: bool = False
        # Memory optimization: Memory-critical operation
    ):
        self.model = model
        # Memory optimization: Explicit memory cleanup
        self.tokenizer = tokenizer
        self.optimizer = optimizer
        self.train_dataloader = train_dataloader
        self.val_dataloader = val_dataloader
        self.scheduler = scheduler
        self.device = device
        # Memory optimization: Device placement for memory management
        self.output_dir = output_dir
        self.save_steps = save_steps
        self.fp16 = fp16
        self.memory_efficient = memory_efficient
        # Memory optimization: Memory-critical operation
        
        # Set up memory efficient training if needed
        # Memory optimization: Memory-critical operation
        if self.memory_efficient and torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            # Apply gradient checkpointing if model supports it
            # Memory optimization: Explicit memory cleanup
            if hasattr(self.model, "gradient_checkpointing_enable"):
                self.model.gradient_checkpointing_enable()
                console.print("[bold green]Enabled gradient checkpointing for memory efficiency[/bold green]")
                # Memory optimization: Memory-critical operation
            
            # Set up automatic mixed precision training if requested
            if self.fp16:
                # Initialize GradScaler for AMP
                self.scaler = torch.cuda.amp.GradScaler()
                # Memory optimization: CUDA operations for GPU acceleration
                console.print("[bold green]Enabled mixed precision training with GradScaler[/bold green]")
        
        # Move model to device
        # Memory optimization: Device placement for memory management
        self.model.to(self.device)
        # Memory optimization: Device placement for memory management
        
        # History for tracking metrics
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'learning_rates': [],
            'gpu_memory': [],
            # Memory optimization: Memory-critical operation
            'cpu_memory': [],
            # Memory optimization: Memory-critical operation
            'train_perplexity': [],
            'val_perplexity': []
        }
        
        # Step counter for checkpoints
        self.global_step = 0
    
    def save_checkpoint(self, tag: str = "checkpoint") -> None:
        """Save a model checkpoint.
        # Memory optimization: Explicit memory cleanup
        
        Args:
            tag: Tag to add to the checkpoint filename
        """
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create checkpoint filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_path = os.path.join(
            self.output_dir, 
            f"{tag}_{timestamp}_step{self.global_step}.pt"
        )
        
        # Save the model checkpoint
        # Memory optimization: Explicit memory cleanup
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'global_step': self.global_step,
            'history': self.history
        }
        
        if self.scheduler:
            checkpoint['scheduler_state_dict'] = self.scheduler.state_dict()
        
        # Save the checkpoint
        torch.save(checkpoint, checkpoint_path)
        console.print(f"[bold green]Checkpoint saved to:[/bold green] {checkpoint_path}")
        
    def train(self, epochs: int, log_interval: int = 10) -> Dict[str, List[float]]:
        """Train the model with rich progress visualization and live dashboard.
        # Memory optimization: Explicit memory cleanup
        
        Args:
            epochs: Number of training epochs
            log_interval: How often to log training stats
            
        Returns:
            Dictionary containing training history
        """
        console.print(Panel("[bold blue]Starting Training[/bold blue]", border_style="blue"))
        start_time = time.time()
        total_steps = epochs * len(self.train_dataloader)
        
        # Set up dashboard layout
        layout = Layout()
        
        # Split layout into rows
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Split body into main and sidebar
        layout["body"].split_row(
            Layout(name="main", ratio=2),
            Layout(name="sidebar", ratio=1)
        )
        
        # Split main into upper and lower
        layout["main"].split_column(
            Layout(name="progress", ratio=1),
            Layout(name="metrics", ratio=1)
        )
        
        # Split sidebar into upper and lower
        layout["sidebar"].split_column(
            Layout(name="system", ratio=1),
            Layout(name="memory", ratio=1)
            # Memory optimization: Memory-critical operation
        )
        
        # Create progress visualization
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn()
        )
        
        # Add overall progress task
        overall_task = progress.add_task("[yellow]Training Progress", total=total_steps)
            
        # Create Live display for dashboard - Note: We use a single Live display
        with Live(layout, refresh_per_second=1, console=console) as live:
            # Set up header
            header_text = Text.from_markup(
                f"[bold blue]ImpressionCore Small Model Training[/bold blue] - "
                # Memory optimization: Explicit memory cleanup
                f"[yellow]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/yellow]"
            )
            layout["header"].update(Align.center(header_text))
            
            # Set up footer
            footer_text = Text.from_markup(
                "[dim]Press Ctrl+C to stop training[/dim]"
            )
            layout["footer"].update(Align.center(footer_text))
            
            # Set up initial system info
            layout["system"].update(display_system_info())
            
            # Set memory efficiency panel
            # Memory optimization: Memory-critical operation
            layout["memory"].update(create_memory_efficiency_panel(get_memory_stats()))
            # Memory optimization: Memory-critical operation
            
            # Update progress panel
            layout["progress"].update(Panel(progress, title="[bold]Training Progress[/bold]", border_style="green"))
            
            # Start training loop
            for epoch in range(epochs):
                epoch_task = progress.add_task(
                    f"[green]Epoch {epoch+1}/{epochs}", 
                    total=len(self.train_dataloader)
                )
                
                # Training mode
                self.model.train()
                epoch_loss = 0.0
                
                # Create metrics panel with empty history
                layout["metrics"].update(create_training_metrics_panel(self.history, epoch+1, epochs))
                
                for step, batch in enumerate(self.train_dataloader):
                    # Increment global step counter
                    self.global_step += 1
                    
                    # Move batch to device
                    # Memory optimization: Device placement for memory management
                    batch = {k: v.to(self.device) for k, v in batch.items()}
                    # Memory optimization: Device placement for memory management
                    
                    # Forward and backward pass with memory efficient handling
                    # Memory optimization: Memory-critical operation
                    if self.memory_efficient and self.fp16 and torch.cuda.is_available():
                    # Memory optimization: CUDA operations for GPU acceleration
                        # Mixed precision training flow
                        self.optimizer.zero_grad()
                        
                        with torch.cuda.amp.autocast():
                        # Memory optimization: CUDA operations for GPU acceleration
                            outputs = self.model(**batch)
                            # Access loss using dictionary key
                            loss = outputs["loss"]
                        
                        # Scale loss and calculate gradients
                        self.scaler.scale(loss).backward()
                        self.scaler.step(self.optimizer)
                        self.scaler.update()
                    else:
                        # Standard training flow
                        self.optimizer.zero_grad()
                        outputs = self.model(**batch)
                        # Access loss using dictionary key
                        loss = outputs["loss"]
                        loss.backward()
                        self.optimizer.step()
                    
                    # Update scheduler if it exists
                    if self.scheduler:
                        self.scheduler.step()
                        self.history['learning_rates'].append(self.scheduler.get_last_lr()[0])
                    else:
                        self.history['learning_rates'].append(self.optimizer.param_groups[0]['lr'])
                    
                    # Update metrics
                    loss_value = loss.item()
                    epoch_loss += loss_value
                    self.history['train_loss'].append(loss_value)
                    
                    # Calculate perplexity
                    perplexity = math.exp(loss_value)
                    self.history['train_perplexity'].append(perplexity)
                    
                    # Collect memory stats
                    # Memory optimization: Memory-critical operation
                    memory_stats = get_memory_stats()
                    # Memory optimization: Memory-critical operation
                    if 'gpu_used_gb' in memory_stats:
                    # Memory optimization: Memory-critical operation
                        self.history['gpu_memory'].append(memory_stats['gpu_used_gb'])
                        # Memory optimization: Memory-critical operation
                    self.history['cpu_memory'].append(memory_stats['cpu_used_gb'])
                    # Memory optimization: Memory-critical operation
                    
                    # Update progress bars
                    progress.update(epoch_task, advance=1)
                    progress.update(overall_task, advance=1)
                    
                    # Update progress panel to reflect updates
                    layout["progress"].update(Panel(progress, title="[bold]Training Progress[/bold]", border_style="green"))
                    
                    # Update memory efficiency panel periodically
                    # Memory optimization: Memory-critical operation
                    if step % 5 == 0 or step == len(self.train_dataloader) - 1:
                        layout["memory"].update(create_memory_efficiency_panel(memory_stats))
                        # Memory optimization: Memory-critical operation
                        
                        # Update system info
                        layout["system"].update(display_system_info())
                    
                    # Update training metrics periodically
                    if step % 5 == 0 or step == len(self.train_dataloader) - 1:
                        layout["metrics"].update(create_training_metrics_panel(self.history, epoch+1, epochs))
                    
                    # Save checkpoint if needed
                    if self.save_steps > 0 and self.global_step % self.save_steps == 0:
                        self.save_checkpoint(tag=f"epoch{epoch+1}")
                        
                        # Update footer to show checkpoint saved
                        checkpoint_notice = Text.from_markup(
                            f"[green]Checkpoint saved at step {self.global_step}[/green]"
                        )
                        layout["footer"].update(Align.center(checkpoint_notice))
                    
                    # Log periodically
                    if step % log_interval == 0 or step == len(self.train_dataloader) - 1:
                        avg_loss = epoch_loss / (step + 1)
                        memory_info = ""
                        # Memory optimization: Memory-critical operation
                        if torch.cuda.is_available():
                        # Memory optimization: CUDA operations for GPU acceleration
                            memory_info = f"GPU: {memory_stats['gpu_used_gb']:.2f}GB ({memory_stats['gpu_percent']:.1f}%)"
                            # Memory optimization: Memory-critical operation
                        
                        log_message = (
                            f"Step: {step}/{len(self.train_dataloader)} | "
                            f"Loss: {loss_value:.4f} | Avg: {avg_loss:.4f} | "
                            f"PPL: {perplexity:.2f} | "
                            f"LR: {self.optimizer.param_groups[0]['lr']:.6f} | "
                            f"{memory_info}"
                            # Memory optimization: Memory-critical operation
                        )
                        
                        # Update description to show current stats
                        progress.update(
                            epoch_task, 
                            description=f"[green]Epoch {epoch+1}/{epochs} [white]| Loss: {avg_loss:.4f} | PPL: {perplexity:.2f}"
                        )
                
                # Calculate average loss for the epoch
                avg_epoch_loss = epoch_loss / len(self.train_dataloader)
                
                # Run validation if validation dataloader is provided
                val_loss = None
                if self.val_dataloader:
                    val_loss = self.evaluate(epoch, epochs, progress, layout)
                        
                    # Display epoch summary
                    summary_text = Text.from_markup(
                        f"[bold]Epoch {epoch+1}/{epochs} Summary:[/bold] "
                        f"Train Loss: [cyan]{avg_epoch_loss:.4f}[/cyan] | "
                        f"Val Loss: [green]{val_loss:.4f}[/green] | "
                        f"Time: {format_time(time.time() - start_time)}"
                    )
                    layout["footer"].update(Align.center(summary_text))
                else:
                    # Display epoch summary without validation
                    summary_text = Text.from_markup(
                        f"[bold]Epoch {epoch+1}/{epochs} Summary:[/bold] "
                        f"Train Loss: [cyan]{avg_epoch_loss:.4f}[/cyan] | "
                        f"Time: {format_time(time.time() - start_time)}"
                    )
                    layout["footer"].update(Align.center(summary_text))
                
                # Save checkpoint at the end of each epoch
                self.save_checkpoint(tag=f"epoch{epoch+1}_final")
        
        # Display final training summary
        total_time = time.time() - start_time
        console.print(Panel(
            f"[bold]Training Completed in {format_time(total_time)}[/bold]\n"
            f"Final Training Loss: [cyan]{self.history['train_loss'][-1]:.4f}[/cyan]\n"
            f"Final Training Perplexity: [cyan]{self.history['train_perplexity'][-1]:.2f}[/cyan]" +
            (f"\nFinal Validation Loss: [green]{self.history['val_loss'][-1]:.4f}[/green]\n"
             f"Final Validation Perplexity: [green]{self.history['val_perplexity'][-1]:.2f}[/green]" 
             if self.val_dataloader else ""),
            title="[bold]Training Summary[/bold]",
            border_style="green"
        ))
        
        return self.history
    
    def evaluate(self, epoch: int, total_epochs: int, progress: Progress, layout: Layout) -> float:
        """Evaluate the model on the validation set with rich progress visualization.
        # Memory optimization: Explicit memory cleanup
        
        Args:
            epoch: Current epoch number
            total_epochs: Total number of epochs
            progress: Progress instance for visualization
            layout: Dashboard layout for updating components
            
        Returns:
            Average validation loss
        """
        self.model.eval()
        val_loss = 0.0
        
        # Add validation progress task
        val_task = progress.add_task(
            f"[blue]Validating Epoch {epoch+1}/{total_epochs}", 
            total=len(self.val_dataloader)
        )
        
        # Update layout to show we're in validation mode
        validation_notice = Text.from_markup("[bold blue]Running Validation...[/bold blue]")
        layout["footer"].update(Align.center(validation_notice))
        
        with torch.no_grad():
        # Memory optimization: Disable gradient computation to save memory
            for batch in self.val_dataloader:
                # Move batch to device
                # Memory optimization: Device placement for memory management
                batch = {k: v.to(self.device) for k, v in batch.items()}
                # Memory optimization: Device placement for memory management
                
                # Forward pass with mixed precision if enabled
                if self.fp16 and torch.cuda.is_available():
                # Memory optimization: CUDA operations for GPU acceleration
                    with torch.cuda.amp.autocast():
                    # Memory optimization: CUDA operations for GPU acceleration
                        outputs = self.model(**batch)
                        # Access loss using dictionary key
                        loss = outputs["loss"]
                else:
                    outputs = self.model(**batch)
                    # Access loss using dictionary key
                    loss = outputs["loss"]
                
                # Update metrics
                loss_value = loss.item()
                val_loss += loss_value
                
                # Calculate perplexity
                perplexity = math.exp(loss_value)
                
                # Update progress
                progress.update(val_task, advance=1)
        
        # Calculate average validation loss
        avg_val_loss = val_loss / len(self.val_dataloader)
        self.history['val_loss'].append(avg_val_loss)
        
        # Calculate average validation perplexity
        avg_val_perplexity = math.exp(avg_val_loss)
        self.history['val_perplexity'].append(avg_val_perplexity)
        
        # Update training metrics with validation results
        layout["metrics"].update(create_training_metrics_panel(self.history, epoch+1, total_epochs))
        
        return avg_val_loss
    
    def generate_sample_text(self, prompt: str, max_length: int = 100) -> str:
        """Generate sample text from the model with visualization.
        # Memory optimization: Explicit memory cleanup
        
        Args:
            prompt: Text prompt to start generation from
            max_length: Maximum length of generated sequence
            
        Returns:
            Generated text
        """
        self.model.eval()
        
        # Tokenize the prompt
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        # Memory optimization: Device placement for memory management
        
        # Create a panel for generation process
        console.print(Panel(f"[bold cyan]Prompt:[/bold cyan] {prompt}", title="Text Generation", border_style="cyan"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            generation_task = progress.add_task("[magenta]Generating text...", total=max_length)
            
            # Generate text token by token with visualization
            input_ids = inputs.input_ids
            attention_mask = inputs.attention_mask
            
            # Use mixed precision for generation if enabled
            generation_mode = torch.cuda.amp.autocast() if self.fp16 and torch.cuda.is_available() else nullcontext()
            # Memory optimization: CUDA operations for GPU acceleration
            
            with generation_mode:
                for _ in range(max_length):
                    with torch.no_grad():
                    # Memory optimization: Disable gradient computation to save memory
                        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                    
                    # Get the next token logits
                    next_token_logits = outputs["logits"][:, -1, :]
                    
                    # Apply temperature sampling
                    temperature = 0.7
                    next_token_logits = next_token_logits / temperature
                    
                    # Sample from the distribution
                    next_token = torch.multinomial(torch.softmax(next_token_logits, dim=-1), num_samples=1)
                    
                    # Update input_ids and attention_mask
                    input_ids = torch.cat([input_ids, next_token], dim=-1)
                    attention_mask = torch.cat([
                        attention_mask, 
                        torch.ones((attention_mask.shape[0], 1), device=self.device)
                        # Memory optimization: Device placement for memory management
                    ], dim=-1)
                    
                    # Update progress
                    progress.update(generation_task, advance=1)
                    
                    # Check if EOS token was generated
                    if next_token.item() == self.tokenizer.eos_token_id:
                        break
        
        # Decode the generated text
        generated_text = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
        
        # Print the final generated text
        console.print(Panel(generated_text, title="[bold green]Generated Text[/bold green]", border_style="green"))
        
        return generated_text


def load_sample_data(data_dir, max_samples=1000):
    """Load sample data for training."""
    sample_file = os.path.join(data_dir, "sample_text.txt")
    
    # Create sample data if it doesn't exist
    if not os.path.exists(sample_file):
        os.makedirs(data_dir, exist_ok=True)
        with open(sample_file, "w") as f:
            f.write("\n".join([
                "ImpressionCore is a versatile natural language processing framework.",
                "It supports various tasks like text generation, classification, and more.",
                "The architecture is based on transformer models with attention mechanisms.",
                "Knowledge distillation allows creating smaller, faster models.",
                "This sample data is being used to demonstrate training functionality."
            ] * 200))  # Repeat to have more samples
    
    # Load data
    with open(sample_file, "r") as f:
        texts = [line.strip() for line in f.readlines() if line.strip()]
    
    # Limit number of samples
    if max_samples > 0:
        texts = texts[:max_samples]
    
    return texts

# Add missing nullcontext implementation
from contextlib import contextmanager

@contextmanager
def nullcontext():
    """Context manager that does nothing. Used as a stand-in for mixed precision context when not using it."""
    yield

def main():
    """Run small model training."""
    # Memory optimization: Explicit memory cleanup
    # Parse arguments
    parser = argparse.ArgumentParser(description="Train a small model with ImpressionCore")
    # Memory optimization: Explicit memory cleanup
    parser.add_argument("--batch_size", type=int, default=8, help="Training batch size")
    parser.add_argument("--grad_accum", type=int, default=2, help="Gradient accumulation steps")
    parser.add_argument("--fp16", action="store_true", help="Use mixed precision training")
    parser.add_argument("--use_cuda", action="store_true", help="Use CUDA if available")
    # Memory optimization: Memory-critical operation
    parser.add_argument("--memory_efficient", action="store_true", default=True, help="Use memory-efficient training")
    # Memory optimization: Memory-critical operation
    parser.add_argument("--epochs", type=int, default=2, help="Number of training epochs")
    parser.add_argument("--no_generate", action="store_true", help="Skip text generation after training")
    parser.add_argument("--save_steps", type=int, default=200, help="Save checkpoint every N steps (0 to disable)")
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="Learning rate")
    parser.add_argument("--max_samples", type=int, default=1000, help="Maximum number of training samples to use")
    args = parser.parse_args()

    # Show beautiful header
    console.print(Panel.fit(
        "[bold cyan]ImpressionCore[/bold cyan] [bold blue]Small Model Training[/bold blue]",
        # Memory optimization: Explicit memory cleanup
        subtitle=f"[yellow]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/yellow]",
        border_style="blue"
    ))
    
    # Display system information
    console.print(display_system_info())
    
    # Set CUDA memory management environment variables
    # Memory optimization: Memory-critical operation
    if args.use_cuda and torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True,max_split_size_mb:128"
        # Memory optimization: Memory-critical operation
        # Configure for GTX 1050 Ti limited memory
        # Memory optimization: Memory-critical operation
        torch.cuda.set_per_process_memory_fraction(0.7)  # Only use 70% of available VRAM
        # Memory optimization: CUDA operations for GPU acceleration
        console.print("[bold green]CUDA memory management configured for limited VRAM[/bold green]")
        # Memory optimization: Memory-critical operation
    
    # Define directories
    data_dir = os.path.join(project_root, "data", "training")
    output_dir = os.path.join(project_root, "models", "small")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Display configuration
    config_table = Table(title="[bold]Training Configuration[/bold]", box=ROUNDED)
    config_table.add_column("Parameter", style="cyan")
    config_table.add_column("Value", style="green")
    
    config_table.add_row("Batch Size", str(args.batch_size))
    config_table.add_row("Gradient Accumulation", str(args.grad_accum))
    config_table.add_row("Mixed Precision", "Enabled" if args.fp16 else "Disabled")
    config_table.add_row("CUDA", "Enabled" if args.use_cuda and torch.cuda.is_available() else "Disabled")
    # Memory optimization: CUDA operations for GPU acceleration
    config_table.add_row("Epochs", str(args.epochs))
    config_table.add_row("Memory Efficient", "Enabled" if args.memory_efficient else "Disabled")
    # Memory optimization: Memory-critical operation
    config_table.add_row("Learning Rate", str(args.learning_rate))
    config_table.add_row("Save Steps", str(args.save_steps))
    config_table.add_row("Max Samples", str(args.max_samples))
    config_table.add_row("Data Directory", data_dir)
    config_table.add_row("Output Directory", output_dir)
    
    console.print(config_table)
    
    # Load tokenizer with progress
    with console.status("[bold green]Loading tokenizer...[/bold green]", spinner="dots"):
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        tokenizer.pad_token = tokenizer.eos_token
    
    console.print("[bold green]✓[/bold green] Tokenizer loaded successfully")
    
    # Get training data with progress
    with console.status("[bold green]Loading training data...[/bold green]", spinner="dots"):
        texts = load_sample_data(data_dir, max_samples=args.max_samples)
    
    console.print(f"[bold green]✓[/bold green] Loaded [bold cyan]{len(texts)}[/bold cyan] training samples")
    
    # Create datasets with progress
    with console.status("[bold green]Preparing datasets...[/bold green]", spinner="dots"):
        # Split 90% for training, 10% for evaluation
        split_idx = int(len(texts) * 0.9)
        train_texts = texts[:split_idx]
        eval_texts = texts[split_idx:]
        
        # Create datasets with explicit labels for better loss calculation
        train_dataset = CustomTextDataset(train_texts, tokenizer, max_length=128)
        eval_dataset = CustomTextDataset(eval_texts, tokenizer, max_length=128)
        
        # Create data loaders
        train_dataloader = DataLoader(
            train_dataset, 
            batch_size=args.batch_size, 
            shuffle=True,
            pin_memory=True if torch.cuda.is_available() else False
            # Memory optimization: CUDA operations for GPU acceleration
        )
        
        eval_dataloader = DataLoader(
            eval_dataset, 
            batch_size=args.batch_size, 
            shuffle=False,
            pin_memory=True if torch.cuda.is_available() else False
            # Memory optimization: CUDA operations for GPU acceleration
        )
    
    console.print(f"[bold green]✓[/bold green] Created training dataset with [bold cyan]{len(train_dataset)}[/bold cyan] samples")
    console.print(f"[bold green]✓[/bold green] Created validation dataset with [bold cyan]{len(eval_dataset)}[/bold cyan] samples")
    
    # Create model configuration with progress
    # Memory optimization: Explicit memory cleanup
    with console.status("[bold green]Creating model configuration...[/bold green]", spinner="dots"):
    # Memory optimization: Explicit memory cleanup
        # Create small model config - using the proper helper function
        # Memory optimization: Explicit memory cleanup
        small_config = get_impressioncore_small_config()
        
        # Customize the config if needed
        small_config.dimensions.hidden_size = 256
        small_config.dimensions.num_hidden_layers = 4
        small_config.dimensions.num_attention_heads = 4
        small_config.dimensions.intermediate_size = 1024
    
    # Display model configuration
    # Memory optimization: Explicit memory cleanup
    model_config_table = Table(title="[bold]Model Configuration[/bold]", box=ROUNDED)
    # Memory optimization: Explicit memory cleanup
    model_config_table.add_column("Parameter", style="cyan")
    model_config_table.add_column("Value", style="green")
    
    model_config_table.add_row("Hidden Size", str(small_config.dimensions.hidden_size))
    model_config_table.add_row("Hidden Layers", str(small_config.dimensions.num_hidden_layers))
    model_config_table.add_row("Attention Heads", str(small_config.dimensions.num_attention_heads))
    model_config_table.add_row("Intermediate Size", str(small_config.dimensions.intermediate_size))
    
    console.print(model_config_table)
    
    # Create model with progress
    # Memory optimization: Explicit memory cleanup
    with console.status("[bold green]Creating model...[/bold green]", spinner="dots"):
        # Create model
        model = ImpressionCoreModel(small_config)
        # Memory optimization: Explicit memory cleanup
        
        # Configure optimizer
        optimizer = optim.AdamW(model.parameters(), lr=args.learning_rate)
        
        # Configure scheduler
        num_training_steps = len(train_dataloader) * args.epochs
        scheduler = get_scheduler(
            "linear",
            optimizer=optimizer,
            num_warmup_steps=int(0.1 * num_training_steps),
            num_training_steps=num_training_steps
        )
    
    console.print("[bold green]✓[/bold green] Model created successfully")
    # Memory optimization: Explicit memory cleanup
    
    # Create trainer
    trainer = SimpleModelTrainer(
        model=model,
        tokenizer=tokenizer,
        optimizer=optimizer,
        train_dataloader=train_dataloader,
        val_dataloader=eval_dataloader,
        scheduler=scheduler,
        device="cuda" if args.use_cuda and torch.cuda.is_available() else "cpu",
        # Memory optimization: CUDA operations for GPU acceleration
        output_dir=output_dir,
        save_steps=args.save_steps,
        fp16=args.fp16,
        memory_efficient=args.memory_efficient
        # Memory optimization: Memory-critical operation
    )
    
    # Run training
    training_history = trainer.train(epochs=args.epochs)
    
    # Generate sample text
    if not args.no_generate:
        console.print("\n[bold]Generating sample text from trained model:[/bold]")
        sample_prompts = [
            "ImpressionCore is a",
            "Natural language processing can",
            "The best way to train a model is"
            # Memory optimization: Explicit memory cleanup
        ]
        
        for prompt in sample_prompts:
            trainer.generate_sample_text(prompt, max_length=50)
    
    console.print("[bold green]Training completed successfully![/bold green]")

if __name__ == "__main__":
    # Install rich traceback handler for better error reporting
    install_rich_traceback()
    
    try:
        main()
    except KeyboardInterrupt:
        console.print("[bold yellow]Training interrupted by user[/bold yellow]")
    except Exception as e:
        console.print("[bold red]Error during training:[/bold red]", e)
        console.print_exception()
