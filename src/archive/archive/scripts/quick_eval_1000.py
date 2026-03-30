import sys
import time
import torch
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from inference.b3_rag_inference import B3RAGInference
from rich.console import Console

console = Console()

def main():
    path = "F:/models/checkpoints/diverse_curriculum/step_1000.pt"
    console.print(f"\n[bold purple]Evaluating Checkpoint: Resumed (Step 1000)[/bold purple]")

    if not Path(path).exists():
        console.print(f"[red]❌ Checkpoint not found: {path}[/red]")
        return

    try:
        console.print(f"[cyan]Loading model...[/cyan]")
        inferencer = B3RAGInference(
            model_path=path,
            f_data_root="F:/data",
            device="cuda" if torch.cuda.is_available() else "cpu",
        )
        console.print("[green]✅ Model Loaded![/green]")

        queries = [
            "Hello! How are you today?",
            "Describe a beautiful sunset over the ocean with vibrant colors",
            "Can you help me understand how you work?",
        ]

        for i, query in enumerate(queries, 1):
            console.print(f"\n[bold cyan]Query {i}:[/bold cyan] {query}")

            start_time = time.time()
            result = inferencer.generate_smart_hybrid(
                query,
                max_length=128,
                temperature=0.7
            )
            elapsed = time.time() - start_time

            response = result.get('response', '')
            strategy = result.get('strategy', 'N/A')
            confidence = result.get('confidence', 0.0)

            console.print(f"[green]Response ({elapsed:.2f}s):[/green] {response}")
            console.print(f"[dim]Strategy: {strategy} | Confidence: {confidence:.2f}[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()
