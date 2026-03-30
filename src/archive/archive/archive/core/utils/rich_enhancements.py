
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #deployment #memory_management #multimodal #performance #python #source_code #src/core/utils/rich_enhancements.py #testing
**Category:** Core Implementation
**Status:** Active
"""



import os
import sys
import time
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from rich import box

# Setup basic logging first before attempting rich imports
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Try importing rich library with error handling
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import (
        Progress, SpinnerColumn, BarColumn,
        TextColumn, TimeElapsedColumn, TaskProgressColumn
    )
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.layout import Layout
    from rich.tree import Tree
    from rich.text import Text
    from rich.columns import Columns
    from rich.logging import RichHandler
    from rich.traceback import install as install_rich_traceback

    # Install rich traceback handler
    install_rich_traceback(show_locals=False, width=100, word_wrap=True)    # Configure rich console with memory-efficient settings
    # Memory optimization: Memory-critical operation
    console = Console(
        width=100,
        color_system="auto",
        soft_wrap=True,
        highlight=True,
        markup=True,
        record=False,  # Set to True only when needed to avoid memory overhead
        force_terminal=True,
        legacy_windows=False  # Use modern Windows console features
        # Memory optimization: Memory-critical operation
    )

    HAS_RICH = True
except ImportError as e:
    logger.warning(f"Rich library not available: {e}")
    logger.warning("Falling back to standard text output.")
    HAS_RICH = False
    console = None

# Optional visualization imports with error handling
try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt

    HAS_VISUALIZATION = True
except ImportError:
    logger.warning("Matplotlib visualization libraries not available.")
    HAS_VISUALIZATION = False


class FallbackConsole:
    """Fallback console for environments without Rich."""

    def __init__(self):
        """

    __init__ function for processing.

    Args:
        self: Function parameters

    Returns:
        Processed result

    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints

        """
        self.width = 80

    def print(self, *args, **kwargs):
        """Print text to console."""
        # Extract text from Rich objects if present
        text = ""
        for arg in args:
            if hasattr(arg, "plain"):  # Rich Text object
                text += arg.plain
            elif isinstance(arg, dict):  # Rich renderable converted to dict
                if "text" in arg:
                    text += str(arg["text"])
                else:
                    text += str(arg)
            else:
                text += str(arg)
        print(text)

    def rule(self, title=None, **kwargs):
        """Print a horizontal rule with optional title."""
        width = self.width
        if title:
            padding = max(0, (width - len(title) - 4) // 2)
            print(f"{'-' * padding} {title} {'-' * padding}")
        else:
            print("-" * width)


# Create fallback console if Rich is not available
if not HAS_RICH:
    console = FallbackConsole()


def create_header(title: str, subtitle: Optional[str] = None, style: str = "bold cyan") -> None:
    """
    Create a standardized header for scripts, tests, and demos.

    Args:
        title: The main title to display
        subtitle: Optional subtitle text
        style: Style to apply to the title (only with Rich)

    Returns:
        None
    """
    if HAS_RICH:
        try:
            title_text = Text(title, style=style, justify="center")
            if subtitle:
                title_panel = Panel(
                    title_text,
                    subtitle=subtitle,
                    border_style="cyan",
                    width=console.width
                )
            else:
                title_panel = Panel(title_text, border_style="cyan", width=console.width)
            console.print(title_panel)
        except Exception as e:
            logger.warning(f"Error displaying rich header: {e}")
            print(f"\n===== {title} =====")
            if subtitle:
                print(f"{subtitle}\n")
    else:
        print(f"\n===== {title} =====")
        if subtitle:
            print(f"{subtitle}\n")


def create_table(title: Optional[str] = None,
                columns: List[str] = None,
                show_header: bool = True,
                header_style: str = "bold magenta",
                box_style=box.ROUNDED) -> Union[Table, Dict]:
    """
    Create a standardized table for displaying data.

    Args:
        title: Optional table title
        columns: List of column names
        show_header: Whether to show the header row
        header_style: Style to apply to the header row
        box: Box style for the table borders

    Returns:
        A Rich Table object or a dictionary for fallback mode
    """
    if HAS_RICH:
        try:
            table = Table(
                title=title,
                show_header=show_header,
                header_style=header_style,
                box=box_style,
                expand=True
            )
            # Add columns if provided
            if columns:
                for column in columns:
                    table.add_column(column)
            return table
        except Exception as e:
            logger.warning(f"Error creating rich table: {e}")
            return {"type": "table", "title": title, "columns": columns or [], "rows": []}
    else:
        return {"type": "table", "title": title, "columns": columns or [], "rows": []}


def add_table_row(table: Union[Table, Dict], *values, style: Optional[str] = None) -> None:
    """
    Add a row to a table with optional styling.

    Args:
        table: The table to add a row to
        values: Values to add to the row
        style: Optional style to apply to the row

    Returns:
        None
    """
    if HAS_RICH and isinstance(table, Table):
        try:
            table.add_row(*values, style=style)
        except Exception as e:
            logger.warning(f"Error adding row to rich table: {e}")
            if isinstance(table, dict) and "rows" in table:
                table["rows"].append(list(values))
    elif isinstance(table, dict) and "rows" in table:
        table["rows"].append(list(values))


def display_table(table: Union[Table, Dict]) -> None:
    """
    Display a table with proper fallback.

    Args:
        table: The table to display

    Returns:
        None
    """
    if HAS_RICH and isinstance(table, Table):
        try:
            console.print(table)
        except Exception as e:
            logger.warning(f"Error displaying rich table: {e}")
            _display_fallback_table(table)
    else:
        _display_fallback_table(table)


def _display_fallback_table(table: Dict) -> None:
    """Display a table in fallback mode without Rich."""
    if not isinstance(table, dict):
        print("Cannot display table: invalid format")
        return

    if table.get("title"):
        print(f"\n{table['title']}:")

    columns = table.get("columns", [])
    rows = table.get("rows", [])

    if not columns and not rows:
        print("(Empty table)")
        return

    # Calculate column widths
    col_widths = [len(col) for col in columns]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
            else:
                col_widths.append(len(str(cell)))

    # Print header
    if columns:
        header = " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(columns))
        print(header)
        print("-" * len(header))

    # Print rows
    for row in rows:
        row_str = " | ".join(str(cell).ljust(col_widths[i])
                         for i, cell in enumerate(row) if i < len(col_widths))
        print(row_str)


def create_progress(transient: bool = True,
                    refresh_per_second: float = 10.0,
                    auto_refresh: bool = True) -> Union[Progress, Dict]:
    """
    Create a standardized progress display.

    Args:
        transient: Whether to remove the progress display when complete
        refresh_per_second: How often to refresh the display per second
        auto_refresh: Whether to automatically refresh

    Returns:
        A Rich Progress object or a dictionary for fallback mode
    """
    if HAS_RICH:
        try:
            return Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                transient=transient,
                refresh_per_second=refresh_per_second,
                console=console
            )
        except Exception as e:
            logger.warning(f"Error creating rich progress: {e}")
            return {"type": "progress", "tasks": {}}
    else:
        return {"type": "progress", "tasks": {}}


def update_progress(progress: Union[Progress, Dict],
                   task_id: Any,
                   completed: float,
                   description: Optional[str] = None,
                   total: Optional[float] = None) -> None:
    """
    Update a progress bar with optional new description.

    Args:
        progress: The progress object to update
        task_id: The ID of the task to update
        completed: The new completed value
        description: Optional new description for the task
        total: Optional new total for the task

    Returns:
        None
    """
    if HAS_RICH and isinstance(progress, Progress):
        try:
            update_kwargs = {"completed": completed}
            if description is not None:
                update_kwargs["description"] = description
            if total is not None:
                update_kwargs["total"] = total

            progress.update(task_id, **update_kwargs)
        except Exception as e:
            logger.warning(f"Error updating rich progress: {e}")
            if isinstance(progress, dict) and task_id in progress.get("tasks", {}):
                _update_fallback_progress(progress, task_id, completed)
    elif isinstance(progress, dict) and task_id in progress.get("tasks", {}):
        _update_fallback_progress(progress, task_id, completed)


def _update_fallback_progress(progress: Dict, task_id: Any, completed: float) -> None:
    """Update a progress bar in fallback mode without Rich."""
    task = progress["tasks"][task_id]
    old_percent = int(task["completed"] / task["total"] * 100)
    task["completed"] = completed
    new_percent = int(completed / task["total"] * 100)

    # Only print update if percentage changed significantly
    if new_percent - old_percent >= 5:
        print(f"{task['description']}: {new_percent}% complete")


def print_info(message: str) -> None:
    """
    Print an information message with consistent styling.

    Args:
        message: The message to print

    Returns:
        None
    """
    # Remove problematic Unicode characters for Windows compatibility
    clean_message = message.encode('ascii', errors='replace').decode('ascii')

    if HAS_RICH:
        try:
            console.print(f"[cyan]INFO:[/cyan] {clean_message}")
        except Exception:
            print(f"INFO: {clean_message}")
    else:
        print(f"INFO: {clean_message}")


def print_success(message: str) -> None:
    """
    Print a success message with consistent styling.

    Args:
        message: The message to print

    Returns:
        None
    """
    # Remove problematic Unicode characters for Windows compatibility
    clean_message = message.encode('ascii', errors='replace').decode('ascii')

    if HAS_RICH:
        try:
            console.print(f"[green]SUCCESS:[/green] {clean_message}")
        except Exception:
            print(f"SUCCESS: {clean_message}")
    else:
        print(f"SUCCESS: {clean_message}")


def print_warning(message: str) -> None:
    """
    Print a warning message with consistent styling.

    Args:
        message: The message to print

    Returns:
        None
    """
    # Remove problematic Unicode characters for Windows compatibility
    clean_message = message.encode('ascii', errors='replace').decode('ascii')

    if HAS_RICH:
        try:
            console.print(f"[yellow]WARNING:[/yellow] {clean_message}")
        except Exception:
            print(f"WARNING: {clean_message}")
    else:
        print(f"WARNING: {clean_message}")


def print_error(message: str, exception: Optional[Exception] = None) -> None:
    """
    Print an error message with consistent styling and optional exception details.

    Args:
        message: The error message to print
        exception: Optional exception object to include details from

    Returns:
        None
    """
    # Remove problematic Unicode characters for Windows compatibility
    clean_message = message.encode('ascii', errors='replace').decode('ascii')

    if HAS_RICH:
        try:
            console.print(f"[bold red]ERROR:[/bold red] {clean_message}")
            if exception:
                console.print_exception(show_locals=False, width=console.width, word_wrap=True)
        except Exception:
            print(f"ERROR: {clean_message}")
            if exception:
                traceback.print_exc()
    else:
        print(f"ERROR: {clean_message}")
        if exception:
            traceback.print_exc()


def show_tree(label: str, data: Dict, style: str = "bold blue") -> None:
    """
    Display hierarchical data using a tree structure.

    Args:
        label: The root label for the tree
        data: Hierarchical data to display
        style: Style to apply to the root label

    Returns:
        None
    """
    if HAS_RICH:
        try:
            tree = Tree(f"[{style}]{label}[/{style}]")
            _build_tree(tree, data)
            console.print(tree)
        except Exception as e:
            logger.warning(f"Error displaying rich tree: {e}")
            _display_fallback_tree(label, data)
    else:
        _display_fallback_tree(label, data)


def _build_tree(tree: Tree, data: Any, indent: int = 0) -> None:
    """Helper function to recursively build a tree from nested data."""
    if isinstance(data, dict):
        for key, value in data.items():
            branch = tree.add(key)
            _build_tree(branch, value, indent + 1)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                branch = tree.add("Item")
                _build_tree(branch, item, indent + 1)
            else:
                tree.add(str(item))
    else:
        if data is not None:
            tree.add(str(data))


def _display_fallback_tree(label: str, data: Any, indent: int = 0) -> None:
    """Display a tree in fallback mode without Rich."""
    prefix = "  " * indent
    if indent == 0:
        print(f"\n{label}")

    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{prefix}├── {key}")
            _display_fallback_tree("", value, indent + 1)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                _display_fallback_tree("", item, indent + 1)
            else:
                print(f"{prefix}├── {item}")
    elif data is not None:
        print(f"{prefix}└── {data}")


def create_markdown(text: str) -> Union[Markdown, str]:
    """
    Create a markdown renderable for rich text display.

    Args:
        text: The markdown text to render

    Returns:
        A Rich Markdown object or the original string for fallback mode
    """
    if HAS_RICH:
        try:
            return Markdown(text)
        except Exception as e:
            logger.warning(f"Error creating rich markdown: {e}")
            return text
    else:
        return text


def display_memory_metrics(metrics: Dict[str, float], title: str = "Memory Usage") -> None:
# Memory optimization: Memory-critical operation
    """
    Display memory usage metrics in a consistent format.
    # Memory optimization: Memory-critical operation

    Args:
        metrics: Dictionary of memory metrics (name -> value in MB)
        # Memory optimization: Memory-critical operation
        title: Title for the metrics display

    Returns:
        None
    """
    if HAS_RICH:
        try:
            table = Table(title=title, show_header=True, header_style="bold magenta")
            table.add_column("Metric")
            table.add_column("Usage (MB)")

            for name, value in metrics.items():
                # Add color-coding based on memory usage
                # Memory optimization: Memory-critical operation
                if value < 100:
                    color = "green"
                elif value < 500:
                    color = "yellow"
                else:
                    color = "red"

                table.add_row(name, f"[{color}]{value:.2f}[/{color}]")

            console.print(table)
        except Exception as e:
            logger.warning(f"Error displaying rich memory metrics: {e}")
            # Memory optimization: Memory-critical operation
            print(f"\n{title}:")
            for name, value in metrics.items():
                print(f"- {name}: {value:.2f} MB")
    else:
        print(f"\n{title}:")
        for name, value in metrics.items():
            print(f"- {name}: {value:.2f} MB")


def show_dashboard(components: List[Union[Table, Panel, Tree, Dict]],
                 title: Optional[str] = None,
                 equal_height: bool = False) -> None:
    """
    Display multiple components in a dashboard layout.

    Args:
        components: List of Rich renderables to display
        title: Optional title for the dashboard
        equal_height: Whether to make all components the same height

    Returns:
        None
    """
    if not components:
        print("No dashboard components to display.")
        return

    if HAS_RICH:
        try:
            if title:
                console.print(f"[bold]{title}[/bold]")

            if len(components) <= 2:
                # Display components in columns if there are just 1 or 2
                console.print(Columns(components, equal=equal_height))
            else:
                # Use grid layout for 3+ components
                layout = Layout()

                if len(components) == 3:
                    # 2x2 grid with first component spanning full width
                    layout.split(
                        Layout(components[0], name="top"),
                        Layout(name="bottom")
                    )
                    layout["bottom"].split_row(
                        Layout(components[1], name="bottom-left"),
                        Layout(components[2], name="bottom-right")
                    )
                else:
                    # Create a grid with rows and columns
                    rows = []
                    for i in range(0, len(components), 2):
                        row_components = components[i:i+2]
                        if len(row_components) == 2:
                            row = Layout(name=f"row_{i//2}")
                            row.split_row(
                                Layout(row_components[0], name=f"cell_{i}"),
                                Layout(row_components[1], name=f"cell_{i+1}")
                            )
                        else:
                            row = Layout(row_components[0], name=f"row_{i//2}")
                        rows.append(row)

                    layout = Layout()
                    layout.split(*rows)

                console.print(layout)
        except Exception as e:
            logger.warning(f"Error displaying rich dashboard: {e}")
            if title:
                print(f"\n{title}")

            for i, component in enumerate(components):
                print(f"\n--- Component {i+1} ---")
                if isinstance(component, dict) and "type" in component:
                    if component["type"] == "table":
                        _display_fallback_table(component)
    else:
        if title:
            print(f"\n{title}")

        for i, component in enumerate(components):
            print(f"\n--- Component {i+1} ---")
            if isinstance(component, dict) and "type" in component:
                if component["type"] == "table":
                    _display_fallback_table(component)


def create_panel(content: Any,
                title: Optional[str] = None,
                border_style: str = "blue") -> Union[Panel, Dict]:
    """
    Create a panel to display content with a border.

    Args:
        content: The content to display in the panel
        title: Optional title for the panel
        border_style: Style to apply to the border

    Returns:
        A Rich Panel object or a dictionary for fallback mode
    """
    if HAS_RICH:
        try:
            return Panel(
                content,
                title=title,
                border_style=border_style,
                expand=True
            )
        except Exception as e:
            logger.warning(f"Error creating rich panel: {e}")
            return {
                "type": "panel",
                "title": title,
                "content": str(content) if not isinstance(content, dict) else content
            }
    else:
        return {
            "type": "panel",
            "title": title,
            "content": str(content) if not isinstance(content, dict) else content
        }


def setup_rich_logging() -> None:
    """
    Configure Rich for logging with a standardized format.

    Returns:
        None
    """
    if HAS_RICH:
        try:
            logging.basicConfig(
                level=logging.INFO,
                format="%(message)s",
                datefmt="[%X]",
                handlers=[
                    RichHandler(
                        rich_tracebacks=True,
                        markup=True,
                        show_time=True,
                        show_path=False
                    )
                ]
            )
            logger.info("Rich logging configured.")
        except Exception as e:
            logger.warning(f"Failed to configure rich logging: {e}")
    else:
        logger.warning("Rich library not available, using standard logging.")


def visualize_data(data: Union[List, np.ndarray],
                  title: str = "Data Visualization",
                  kind: str = "line",
                  xlabel: str = "",
                  ylabel: str = "",
                  save_path: Optional[str] = None,
                  width: int = 8,
                  height: int = 5) -> None:
    """
    Visualize data using matplotlib with memory-efficient settings.
    # Memory optimization: Memory-critical operation
    Falls back to text representation if visualization is not available.

    Args:
        data: Data to visualize
        title: Title for the visualization
        kind: Kind of plot (line, bar, scatter, hist)
        xlabel: Label for x-axis
        ylabel: Label for y-axis
        save_path: Optional path to save the visualization
        width: Figure width in inches
        height: Figure height in inches

    Returns:
        None
    """
    if not HAS_VISUALIZATION:
        print_warning("Visualization libraries not available. Showing data summary instead.")
        print(f"\n{title}:")
        if isinstance(data, (list, np.ndarray)):
            if len(data) > 10:
                print(f"Data points: {len(data)} (showing first 5 and last 5)")
                print(f"Start: {data[:5]}")
                print(f"End: {data[-5:]}")
                if isinstance(data, np.ndarray):
                    print(f"Min: {data.min()}, Max: {data.max()}, Mean: {data.mean()}")
                else:
                    print(f"Min: {min(data)}, Max: {max(data)}, Mean: {sum(data)/len(data)}")
            else:
                print(f"Data: {data}")
        else:
            print(f"Data: {data}")
        return

    try:
        # Create a new figure with memory-efficient settings
        # Memory optimization: Memory-critical operation
        plt.figure(figsize=(width, height), dpi=80, facecolor='white')

        # Plot based on kind
        if kind == "line":
            plt.plot(data)
        elif kind == "bar":
            plt.bar(range(len(data)), data)
        elif kind == "scatter":
            if isinstance(data, list):
                data = np.array(data)
            x = np.arange(len(data))
            plt.scatter(x, data)
        elif kind == "hist":
            plt.hist(data, bins=min(20, len(data)//5) if len(data) > 20 else 10)
        else:
            plt.plot(data)

        # Add labels and title
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()

        # Save if requested
        if save_path:
            plt.savefig(save_path, dpi=100)
            print_info(f"Visualization saved to {save_path}")

        # Close the figure to free memory
        # Memory optimization: Memory-critical operation
        plt.close()

    except Exception as e:
        print_error(f"Error creating visualization: {e}")


def timeit(func: Callable) -> Callable:
    """
    Decorator to time function execution with rich output.

    Args:
        func: The function to time

    Returns:
        Wrapped function that prints execution time
    """
    def wrapper(*args, **kwargs):
        """

    wrapper function for processing.

    Args:
        No arguments: Function parameters

    Returns:
        Processed result

    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints

        """
        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()
        elapsed = end_time - start_time

        if HAS_RICH:
            try:
                console.print(
                    f"[dim]Function [bold]{func.__name__}[/bold] completed in "
                    f"[bold cyan]{elapsed:.4f}[/bold cyan] seconds[/dim]"
                )
            except Exception:
                print(f"Function {func.__name__} completed in {elapsed:.4f} seconds")
        else:
            print(f"Function {func.__name__} completed in {elapsed:.4f} seconds")

        return result

    return wrapper


def init_rich_environment() -> None:
    """
    Initialize the rich environment with optimal settings.
    Call this at the beginning of scripts to set up rich enhancements.

    Returns:
        None
    """
    if HAS_RICH:
        # Configure console with memory-efficient settings
        # Memory optimization: Memory-critical operation
        try:
            # Set console width based on terminal size
            terminal_width = console.width
            if terminal_width > 120:
                # For wide terminals, limit width to prevent excessive memory usage
                # Memory optimization: Memory-critical operation
                console.width = 120

            # Install rich exception handling
            install_rich_traceback(show_locals=False, width=console.width, word_wrap=True)

            # Setup rich logging
            setup_rich_logging()

            print_info("Rich environment initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize rich environment: {e}")
    else:
        pass
        logger.warning("Rich library not available, using standard environment.")


def create_progress_bar(total: Optional[int] = None, description: str = "Processing", transient: bool = False):
    """
    Create a progress bar with consistent styling across ImpressionCore.

    Args:
        total: Total number of items to process (if known)
        description: Description to display
        transient: Whether the progress bar should disappear when complete
          Returns:
        Progress bar instance or fallback
    """
    try:
        if HAS_RICH:
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=console,
                transient=transient
            )
            if total is not None:
                task_id = progress.add_task(description, total=total)
                return progress, task_id
            else:
                return progress
        else:
            # Fallback implementation
            return FallbackProgress(total, description)
    except Exception as e:
        logger.warning(f"Failed to create progress bar: {e}")
        return FallbackProgress(total, description)


def create_spinner(text: str = "Loading...", spinner: str = "dots"):
    """
    Create a spinner with consistent styling.

    Args:
        text: Text to display with spinner
        spinner: Spinner style
          Returns:
        Spinner context manager or fallback
    """
    try:
        if HAS_RICH:
            from rich.spinner import Spinner
            return console.status(text, spinner=spinner)
        else:
            return FallbackSpinner(text)
    except Exception as e:
        logger.warning(f"Failed to create spinner: {e}")
        return FallbackSpinner(text)


class FallbackProgress:
    """Fallback progress bar when rich is not available."""

    def __init__(self, total: Optional[int], description: str):
        self.total = total
        self.description = description
        self.current = 0

    def update(self, task_id=None, advance=1):
        """Update progress."""
        self.current += advance
        if self.total:
            percent = (self.current / self.total) * 100
            print(f"{self.description}: {self.current}/{self.total} ({percent:.1f}%)")
        else:
            print(f"{self.description}: {self.current}")

    def add_task(self, description: str, total: Optional[int] = None):
        """Add a task (fallback implementation)."""
        return 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class FallbackSpinner:
    """Fallback spinner when rich is not available."""

    def __init__(self, text: str):
        self.text = text

    def __enter__(self):
        print(f"{self.text}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class RichStatusManager:
    """Rich status manager for deployment operations with fallback support."""

    def __init__(self):
        """Initialize the status manager."""
        self.console = FallbackConsole()
        self._current_status = None

    def start_status(self, message: str):
        """Start a status display.

        Args:
            message: Status message to display
        """
        try:
            from rich.status import Status
            self._current_status = Status(message, console=self.console)
            self._current_status.start()
        except ImportError:
            print(f"[STATUS] {message}")

    def update_status(self, message: str):
        """Update the current status message.

        Args:
            message: New status message
        """
        if self._current_status:
            try:
                self._current_status.update(message)
            except Exception:
                print(f"[STATUS] {message}")
        else:
            print(f"[STATUS] {message}")

    def stop_status(self):
        """Stop the current status display."""
        if self._current_status:
            try:
                self._current_status.stop()
            except Exception:
                pass
            finally:
                self._current_status = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_status()


class RichEnhancer:
    """
    Rich enhancement utilities wrapper for ImpressionCore.

    Provides a simplified interface to rich formatting capabilities
    with fallback support for environments without rich.
    """

    def __init__(self):
        """Initialize the RichEnhancer."""
        self.console = console

    def create_header(self, title: str, subtitle: Optional[str] = None, style: str = "bold cyan"):
        """Create a formatted header."""
        return create_header(title, subtitle, style)

    def create_table(self, title: Optional[str] = None, **kwargs):
        """Create a formatted table."""
        return create_table(title, **kwargs)

    def create_panel(self, content: Any, title: Optional[str] = None, **kwargs):
        """Create a formatted panel."""
        return create_panel(content, title, **kwargs)

    def print_info(self, message: str):
        """Print an info message."""
        return print_info(message)

    def print_success(self, message: str):
        """Print a success message."""
        return print_success(message)

    def print_warning(self, message: str):
        """Print a warning message."""
        return print_warning(message)

    def print_error(self, message: str, exception: Optional[Exception] = None):
        """Print an error message."""
        return print_error(message, exception)

    def create_progress(self, **kwargs):
        """Create a progress bar."""
        return create_progress(**kwargs)

    def display_memory_metrics(self, metrics: Dict[str, float], title: str = "Memory Usage"):
        """Display memory metrics."""
        return display_memory_metrics(metrics, title)


def setup_rich_console():
    """
    Set up and return a rich console instance.

    Returns:
        Console: Rich console instance or fallback console
    """
    return console

def create_rich_console():
    """
    Create and return a rich console instance.

    Returns:
        Console: Rich console instance or fallback console
    """
    try:
        from rich.console import Console
        return Console()
    except ImportError:
        return FallbackConsole()

def create_rich_progress():
    """
    Create and return a rich progress instance.

    Returns:
        Progress: Rich progress instance or fallback progress
    """
    try:
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeRemainingColumn(),
        )
    except ImportError:
        return FallbackProgress()
