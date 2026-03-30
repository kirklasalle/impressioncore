import sys
import time
import torch
import gc
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from inference.b3_rag_inference import B3RAGInference
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class CheckpointEvaluator:
    def __init__(self):
        self.results = {}

    def evaluate_checkpoint(self, name: str, path: str, hidden_size: int = 256):
        console.print(f"\n[bold purple]Evaluating Checkpoint: {name}[/bold purple]")
        console.print(f"Path: {path}")
        console.print(f"Config: hidden_size={hidden_size}")

        if not Path(path).exists():
            console.print(f"[red]❌ Checkpoint not found: {path}[/red]")
            return

        # Clear GPU integrity
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()

        inferencer = None
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"[cyan]Loading {name}...", total=None)

                # Monkey patch B3HopeConfig across all loaded modules
                if hidden_size != 256:
                    import sys
                    patched_count = 0
                    for module_name, module in list(sys.modules.items()):
                        if "b3_constitutional_trainer" in module_name:
                            if hasattr(module, "B3HopeConfig"):
                                config_class = getattr(module, "B3HopeConfig")
                                config_class.d_model = hidden_size
                                config_class.embed_dim = hidden_size
                                config_class.hidden_size = hidden_size
                                config_class.n_embd = hidden_size
                                patched_count += 1
                                console.print(f"[dim]Patched B3HopeConfig in {module_name}[/dim]")

                    if patched_count == 0:
                        # Force import and patch
                        from src.training.b3_constitutional_trainer import B3HopeConfig
                        B3HopeConfig.d_model = hidden_size
                        B3HopeConfig.embed_dim = hidden_size
                        B3HopeConfig.hidden_size = hidden_size
                        B3HopeConfig.n_embd = hidden_size
                        console.print("[dim]Force-imported and patched src.training.b3_constitutional_trainer[/dim]")
                else:
                    # Restore defaults
                    import sys
                    for module_name, module in list(sys.modules.items()):
                        if "b3_constitutional_trainer" in module_name:
                            if hasattr(module, "B3HopeConfig"):
                                config_class = getattr(module, "B3HopeConfig")
                                config_class.d_model = 256
                                config_class.embed_dim = 256
                                config_class.hidden_size = 256
                                config_class.n_embd = 256

                inferencer = B3RAGInference(
                    model_path=path,
                    f_data_root="F:/data",
                    device="cuda" if torch.cuda.is_available() else "cpu",
                )
                progress.update(task, description="[green]✅ Model Loaded!")
                time.sleep(0.5)

            # Test Queries
            queries = [
                "Hello! How are you today?",
                "Describe a beautiful sunset over the ocean with vibrant colors",
                "Can you help me understand how you work?",
                "I'm a beginner learning AI. What should I focus on first?",
                "Explain machine learning in simple terms for someone new to technology",
            ]

            checkpoint_stats = {
                'total_time': 0,
                'queries': len(queries),
                'responses': []
            }

            for i, query in enumerate(queries, 1):
                console.print(f"\n[bold cyan]Query {i}/{len(queries)}:[/bold cyan] {query}")

                start_time = time.time()
                try:
                    # Use smart hybrid generation
                    result = inferencer.generate_smart_hybrid(
                        query,
                        max_length=128,
                        temperature=0.7
                    )
                    elapsed = time.time() - start_time
                    checkpoint_stats['total_time'] += elapsed

                    response = result.get('response', '')
                    strategy = result.get('strategy', 'N/A')
                    confidence = result.get('confidence', 0.0)

                    console.print(f"[green]Response ({elapsed:.2f}s):[/green] {response}")
                    console.print(f"[dim]Strategy: {strategy} | Confidence: {confidence:.2f}[/dim]")

                    checkpoint_stats['responses'].append({
                        'query': query,
                        'response': response,
                        'time': elapsed,
                        'strategy': strategy,
                        'confidence': confidence
                    })

                except Exception as e:
                    console.print(f"[red]Error generating response: {e}[/red]")

            # Calculate average time
            avg_time = checkpoint_stats['total_time'] / len(queries)
            checkpoint_stats['avg_time'] = avg_time
            self.results[name] = checkpoint_stats

            console.print(f"\n[bold green]✅ Evaluation of {name} Complete![/bold green]")
            console.print(f"Average Response Time: {avg_time:.2f}s")

        except Exception as e:
            console.print(f"[red]❌ Critical Error evaluating {name}: {e}[/red]")
            import traceback
            console.print(traceback.format_exc())
        finally:
            if inferencer:
                del inferencer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gc.collect()

    def print_summary(self):
        console.print("\n" + "="*80)
        console.print("[bold yellow]📊 COMPARATIVE SUMMARY[/bold yellow]", justify="center")
        console.print("="*80 + "\n")

        table = Table(title="Checkpoint Performance Comparison")
        table.add_column("Metric", style="cyan")

        for name in self.results.keys():
            table.add_column(name, style="green")

        # Metrics to compare
        metrics = [
            ("Avg Response Time", lambda s: f"{s['avg_time']:.2f}s"),
            ("Avg Confidence", lambda s: f"{sum(r['confidence'] for r in s['responses'])/s['queries']:.2f}"),
        ]

        for metric_name, extractor in metrics:
            row = [metric_name]
            for name in self.results.keys():
                try:
                    row.append(extractor(self.results[name]))
                except Exception:
                    row.append("N/A")
            table.add_row(*row)

        console.print(table)

def main():
    evaluator = CheckpointEvaluator()

    checkpoints = [
        ("Resumed (Step 1000)", "F:/models/checkpoints/diverse_curriculum/step_1000.pt", 256),
        ("Base (Step 5000)", "F:/models/checkpoints/kd_sft_phase2/step_5000.pt", 768),
    ]

    for name, path, hidden_size in checkpoints:
        evaluator.evaluate_checkpoint(name, path, hidden_size)

    evaluator.print_summary()

if __name__ == "__main__":
    main()
