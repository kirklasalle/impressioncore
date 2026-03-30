#!/usr/bin/env python3
"""
ImpressionCore B3: Triad Dialogue Monitor
=========================================
Visualizes the Triple-Response flow (Left, Right, Colossus) in real-time.
"""

import os
import sys
from pathlib import Path

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

# Setup path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.orchestrator.unified_triad import load_unified_triad

console = Console()

class TriadDialogueMonitor:
    def __init__(self, config_path: str):
        self.triad = load_unified_triad(config_path)
        self.history = []
        self.current_responses = {"left": "", "right": "", "colossus": ""}
        self.current_logs = []
        self.hardware_status = {}

    def create_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=10),
        )
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right"),
            Layout(name="colossus"),
        )
        return layout

    def update_layout(self, layout: Layout):
        # Header: Hardware Status
        vram = self.hardware_status.get("vram_allocated", 0.0)
        mode = "SIMULTANEOUS" if self.triad.simultaneous_load else "SEQUENTIAL"
        status_text = Text(f"VRAM: {vram:.2f}GB | Mode: {mode} | Cameras: Active | Triad: ONLINE", style="bold green")
        layout["header"].update(Panel(status_text, title="🛰️ ImpressionCore B3 Status", border_style="cyan"))

        # Left Panel: Isolated Analytical Path
        left_text = Text(self.current_responses.get("left", "..."), style="cyan")
        layout["left"].update(Panel(left_text, title="🧠 Left Hemisphere (Isolated)", border_style="blue"))

        # Right Panel: Isolated Creative Path
        right_text = Text(self.current_responses.get("right", "..."), style="magenta")
        layout["right"].update(Panel(right_text, title="🎨 Right Hemisphere (Isolated)", border_style="magenta"))

        # Colossus Panel: Integrated
        colossus_text = Text(self.current_responses.get("colossus", "..."), style="bold yellow")
        layout["colossus"].update(Panel(colossus_text, title="🛰️ Colossus (Integrated)", border_style="yellow"))

        # Footer: Logs
        logs = "\n".join(self.current_logs[-8:])
        layout["footer"].update(Panel(logs, title="📜 Nexus Reasoning Logs", border_style="dim"))

    def run_interaction(self, prompt: str):
        self.current_logs.append(f"Broadcasting prompt: {prompt}")
        result = self.triad.generate(prompt)

        # Hemispheric States (Internal Monitoring)
        self.current_responses["left"] = result["internal_monitors"]["left_hemisphere"]
        self.current_responses["right"] = result["internal_monitors"]["right_hemisphere"]

        # Colossus: The Aggregator and Sole Output
        self.current_responses["colossus"] = result["response"]

        self.current_logs.extend(result["nexus_logs"])
        self.hardware_status = self.triad.get_hardware_status()

    def start(self):
        console.clear()
        console.print("[bold cyan]ImpressionCore B3: Triad Dialogue Monitor Initialized[/bold cyan]")

        layout = self.create_layout()
        self.hardware_status = self.triad.get_hardware_status()

        with Live(layout, refresh_per_second=4, screen=True) as live:
            while True:
                self.update_layout(layout)
                # Live doesn't easily support 'input' inside the loop without complex handling
                # So we'll break the live view slightly or use a thread.
                # For simplicity in this dev tool, we'll use a standard prompt.
                live.stop()
                user_input = console.input("[green]User > [/green]")
                if user_input.lower() in ["exit", "quit"]:
                    break

                live.start()
                self.run_interaction(user_input)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Triad Dialogue Monitor")
    parser.add_argument("--config", type=str, default="d:/Projects/impressioncore/src/core/src/core/config/nano_triad_config.json", help="Path to Triad config")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"Error: Config not found at {args.config}")
        sys.exit(1)

    monitor = TriadDialogueMonitor(args.config)
    monitor.start()
