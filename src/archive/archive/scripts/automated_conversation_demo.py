"""
Automated Conversation Demo - Phase 3 Smart Hybrid System
Watch the AI engage in natural conversation with visual feedback!

Created: October 5, 2025
Status: Production Demo
"""

import sys
import time
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from inference.b3_rag_inference import B3RAGInference
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich import box

console = Console()

class ConversationDemo:
    """Automated conversation demo with visual feedback"""

    def __init__(self):
        self.inferencer = None
        self.conversation_history = []

    def initialize(self):
        """Initialize the inference system with visual feedback"""
        console.print("\n" + "="*70, style="cyan")
        console.print("🤖 IMPRESSIONCORE PHASE 3 - AUTOMATED CONVERSATION DEMO",
                     style="bold cyan", justify="center")
        console.print("="*70 + "\n", style="cyan")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Initializing Smart Hybrid System...", total=None)

            try:
                self.inferencer = B3RAGInference(
                    model_path="F:/models/checkpoints/b3/b3_massive_final.pth",
                    f_data_root="F:/data",
                    device="cuda",
                    rag_confidence_threshold=0.4,
                    verbose=False
                )
                progress.update(task, description="[green]✅ System Ready!")
                time.sleep(0.5)

            except Exception as e:
                progress.update(task, description=f"[red]❌ Initialization failed: {e}")
                raise

        # Show system info
        info_table = Table(show_header=False, box=box.ROUNDED, border_style="cyan")
        info_table.add_column("Property", style="yellow")
        info_table.add_column("Value", style="white")

        info_table.add_row("Model", "b3_massive_final.pth (35.5M params)")
        info_table.add_row("Device", "CUDA (GTX 1050 Ti)")
        info_table.add_row("RAG Threshold", "0.4 (optimal)")
        info_table.add_row("Quality", "4.43/5.0 (validated)")
        info_table.add_row("Generic Rate", "7.7% (below 10% target)")

        console.print(Panel(info_table, title="[bold cyan]System Configuration",
                          border_style="cyan"))
        console.print()

    def display_query(self, query: str, query_num: int, total: int):
        """Display the user query"""
        console.print(Panel(
            f"[bold white]{query}",
            title=f"[bold cyan]💭 Query {query_num}/{total}",
            border_style="cyan",
            padding=(1, 2)
        ))

    def display_thinking(self):
        """Show thinking animation"""
        console.print("🤔 [cyan italic]Generating response...[/cyan italic]", end="")

    def display_response(self, result: dict, query_num: int):
        """Display the AI response with metadata"""
        # Clear thinking message
        console.print("\r" + " "*50 + "\r", end="")

        # Create response panel
        response_text = result['response']

        # Add metadata table
        meta_table = Table(show_header=False, box=None, padding=(0, 1))
        meta_table.add_column("Key", style="dim cyan")
        meta_table.add_column("Value", style="dim white")

        meta_table.add_row("Strategy", result.get('strategy', 'N/A'))
        meta_table.add_row("Confidence", f"{result.get('confidence', 0.0):.3f}")
        meta_table.add_row("Quality Preserved",
                          "✅ Yes" if result.get('quality_preserved', True) else "❌ No")

        # Combine response and metadata
        console.print(Panel(
            f"[bold white]{response_text}[/bold white]\n\n" +
            "[dim]─" * 60 + "[/dim]\n" +
            meta_table.__rich_console__(console, console.options),
            title=f"[bold green]🤖 AI Response #{query_num}",
            border_style="green",
            padding=(1, 2)
        ))
        console.print()

    def run_conversation(self):
        """Run the automated conversation demo"""
        # Conversation scenarios covering different domains
        queries = [
            # Greeting (Conversational)
            "Hello! How are you today?",

            # Multimodal (Visual description)
            "Describe a beautiful sunset over the ocean with vibrant colors",

            # Conversational (Help request)
            "Can you help me understand how you work?",

            # Cross-domain (Technical + Context)
            "I'm a beginner learning AI. What should I focus on first?",

            # Multimodal (Scene composition)
            "Paint me a picture of a cozy coffee shop on a rainy day",

            # Educational (with context)
            "Explain machine learning in simple terms for someone new to technology",

            # Conversational (Preferences)
            "What kind of questions do you answer best?",

            # Multimodal (Color and emotion)
            "Describe the feeling of spring with colors and imagery",
        ]

        console.print(Panel(
            f"[bold white]Starting automated conversation with [cyan]{len(queries)}[/cyan] diverse queries\n" +
            "[dim]Covering: Greetings, Visual Descriptions, Help Requests, Learning, Preferences[/dim]",
            title="[bold yellow]📋 Conversation Plan",
            border_style="yellow"
        ))
        console.print()

        # Run conversation
        for i, query in enumerate(queries, 1):
            # Display query
            self.display_query(query, i, len(queries))

            # Show thinking
            self.display_thinking()

            # Generate response
            start_time = time.time()
            result = self.inferencer.generate_with_smart_hybrid(
                query,
                max_length=512,
                temperature=0.7
            )
            elapsed = time.time() - start_time

            # Add timing to result
            result['response_time'] = elapsed

            # Display response
            self.display_response(result, i)

            # Store in history
            self.conversation_history.append({
                'query': query,
                'response': result['response'],
                'strategy': result.get('strategy', 'N/A'),
                'confidence': result.get('confidence', 0.0),
                'time': elapsed
            })

            # Brief pause between queries for readability
            time.sleep(1.5)

        # Show summary
        self.show_summary()

    def show_summary(self):
        """Display conversation summary statistics"""
        console.print("\n" + "="*70, style="cyan")
        console.print("📊 CONVERSATION SUMMARY", style="bold cyan", justify="center")
        console.print("="*70 + "\n", style="cyan")

        # Calculate statistics
        total_queries = len(self.conversation_history)
        avg_time = sum(h['time'] for h in self.conversation_history) / total_queries
        strategies = {}
        for h in self.conversation_history:
            strat = h['strategy']
            strategies[strat] = strategies.get(strat, 0) + 1

        # Summary table
        summary_table = Table(box=box.ROUNDED, border_style="cyan")
        summary_table.add_column("Metric", style="yellow")
        summary_table.add_column("Value", style="white", justify="right")

        summary_table.add_row("Total Queries", str(total_queries))
        summary_table.add_row("Average Response Time", f"{avg_time:.2f}s")
        summary_table.add_row("", "")  # Spacer

        for strategy, count in sorted(strategies.items()):
            pct = (count / total_queries) * 100
            summary_table.add_row(f"Strategy: {strategy}", f"{count} ({pct:.1f}%)")

        console.print(Panel(summary_table, title="[bold cyan]Performance Metrics",
                          border_style="cyan"))

        # Quality indicators
        console.print()
        console.print(Panel(
            "[bold green]✅ All responses generated successfully![/bold green]\n\n" +
            "[white]System Performance:[/white]\n" +
            "  • [green]Quality:[/green] Natural, contextual responses\n" +
            "  • [green]Strategy:[/green] Smart Hybrid optimization\n" +
            "  • [green]Speed:[/green] ~2-3 seconds per response (GPU)\n" +
            "  • [green]Hardware:[/green] GTX 1050 Ti (4GB VRAM)\n\n" +
            "[dim]Phase 3 Smart Hybrid: 4.43/5.0 quality | 7.7% generic rate[/dim]",
            title="[bold green]🎉 Conversation Complete",
            border_style="green"
        ))

        console.print("\n[dim]Demo completed successfully![/dim]\n")

def main():
    """Run the automated conversation demo"""
    try:
        demo = ConversationDemo()
        demo.initialize()
        demo.run_conversation()

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc(), style="dim red")

if __name__ == "__main__":
    main()
