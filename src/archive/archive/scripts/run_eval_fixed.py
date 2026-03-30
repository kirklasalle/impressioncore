import sys
import time
import torch
import gc
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from inference.b3_rag_inference import B3RAGInference
from training.b3_intelligent_inference import B3IntelligentInference
from training.b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope
from transformers import AutoTokenizer

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class CustomB3IntelligentInference(B3IntelligentInference):
    """
    Subclass that allows overriding the config/model initialization
    to handle 768-dim models instead of the default 256-dim.
    """
    def __init__(self, checkpoint_path: str, hidden_size: int = 256):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Override initialization logic
        # 1. Create Config with correct size
        self.config = B3HopeConfig()
        self.config.d_model = hidden_size
        self.config.embed_dim = hidden_size
        self.config.hidden_size = hidden_size
        self.config.n_embd = hidden_size

        # 2. Create Model with this config
        self.model = ImpressionCoreB3Hope(self.config)

        # 3. Load Checkpoint
        self._load_checkpoint(checkpoint_path)

        # 4. Setup Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
        self.tokenizer.pad_token = self.tokenizer.eos_token

        # 5. Initialize other attributes
        self.fallback_messages = {
             'greeting': ["Hello! How can I assist you today?"],
             'help': ["I'd be happy to help! Could you tell me more about what you need?"],
             'question': ["That's an interesting question! Could you provide more context?"],
             'technical': ["That's a technical topic I'd like to explain. What specific aspect interests you?"],
             'general': ["I'd be happy to help! Could you tell me more?"]
        }
        self.intent_patterns = {
            'greeting': [r'\b(hello|hi|hey|greetings)\b'],
            'help': [r'\b(help|assist|need|support)\b'],
            'question': [r'\b(what|how|why|when|where|who|explain)\b'],
            'technical': [r'\b(ai|machine learning|code|data)\b'],
        }

    def _load_checkpoint(self, checkpoint_path):
        load_kwargs = {"map_location": self.device}
        checkpoint = None
        last_error = None
        for weights_only in (True, False):
            try:
                checkpoint = torch.load(
                    checkpoint_path,
                    weights_only=weights_only,
                    **load_kwargs,
                )
                break
            except (TypeError, AttributeError, RuntimeError) as exc:
                last_error = exc
                if weights_only:
                    continue
                raise

        if checkpoint is None:
             raise RuntimeError(f"Unable to load checkpoint: {checkpoint_path}")

        if isinstance(checkpoint, dict):
            state_dict = None
            for key in ("model_state_dict", "model", "state_dict"):
                candidate = checkpoint.get(key)
                if isinstance(candidate, dict):
                    state_dict = candidate
                    break

            if state_dict is None:
                 state_dict = {k: v for k, v in checkpoint.items() if hasattr(v, "shape")}

            self.model.load_state_dict(state_dict, strict=False)
        else:
             raise ValueError("Unsupported checkpoint format")

        self.model = self.model.to(self.device)
        self.model.eval()


class CustomB3RAGInference(B3RAGInference):
    """
    Subclass that uses CustomB3IntelligentInference instead of the standard one.
    """
    def __init__(self, model_path: str, hidden_size: int = 256, **kwargs):
        # We need to skip the super().__init__ because it initializes the wrong Phase 1 system
        # So we basically copy the needed parts of __init__

        self.device = kwargs.get("device", "cuda" if torch.cuda.is_available() else "cpu")
        self.f_data_root = Path(kwargs.get("f_data_root", "F:/data"))

        # Initialize CUSTOM Phase 1 inference system
        self.phase1_system = CustomB3IntelligentInference(
            checkpoint_path=model_path,
            hidden_size=hidden_size
        )

        # Initialize standard searcher logic (copied/adapted from base class)
        # Assuming RAG infrastructure is importable and works the same
        from inference.b3_rag_infrastructure import B3EmbeddingSearcher
        from sentence_transformers import SentenceTransformer

        self.searcher = B3EmbeddingSearcher(
            f_data_root=str(self.f_data_root),
            use_faiss=True,
            topk=5,
            score_threshold=0.01,
            use_sentence_transformers=True
        )

        # Load necessary components for RAG (simplified for eval speed if possible,
        # but full loading is safer to match existing logic)
        self.searcher.load_multimodal_embeddings()
        self.searcher.load_b3_embeddings(category="educational")
        self.searcher.load_b3_embeddings(category="conversational")

        self.multimodal_encoder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
        self.query_encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


class CheckpointEvaluator:
    def __init__(self):
        self.results = {}

    def evaluate_checkpoint(self, name: str, path: str, hidden_size: int):
        console.print(f"\n[bold purple]Evaluating Checkpoint: {name}[/bold purple]")
        console.print(f"Path: {path}")
        console.print(f"Config: hidden_size={hidden_size}")

        if not Path(path).exists():
            console.print(f"[red]❌ Checkpoint not found: {path}[/red]")
            return

        # Clear GPU
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

                # Use Custom Intelligent Inference DIRECTLY (Skip RAG overhead for quick check)
                inferencer = CustomB3IntelligentInference(
                    checkpoint_path=path,
                    hidden_size=hidden_size
                )
                progress.update(task, description="[green]✅ Model Loaded!")
                time.sleep(0.5)

            # Test Queries
            queries = [
                "Hello! How are you today?",
                "Describe a beautiful sunset over the ocean with vibrant colors",
                "Can you help me understand how you work?",
                "I'm a beginner learning AI. What should I focus on first?",
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
                    # Direct generation call
                    result = inferencer.generate_with_fallback(
                        query,
                        max_tokens=64,
                        temperature=0.7,
                        verbose=False
                    )
                    elapsed = time.time() - start_time
                    checkpoint_stats['total_time'] += elapsed

                    response = result.get('response', '')
                    strategy = "Direct (No RAG)"
                    confidence = result.get('confidence', 0.0)
                    used_fallback = result.get('used_fallback', False)

                    if used_fallback:
                        console.print(f"[yellow]Fallback Response ({elapsed:.2f}s):[/yellow] {response}")
                        console.print(f"[dim]Reason: {result.get('reason')} | Confidence: {confidence:.2f}[/dim]")
                    else:
                        console.print(f"[green]Response ({elapsed:.2f}s):[/green] {response}")
                        console.print(f"[dim]Confidence: {confidence:.2f}[/dim]")

                    checkpoint_stats['responses'].append({
                        'query': query,
                        'response': response,
                        'confidence': confidence,
                        'time': elapsed
                    })

                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")

            # Calculate metrics
            avg_time = checkpoint_stats['total_time'] / len(queries)
            checkpoint_stats['avg_time'] = avg_time
            self.results[name] = checkpoint_stats

            console.print(f"\n[bold green]✅ Evaluation of {name} Complete![/bold green]")

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

    # Both checkpoints are 768-dim models (Standard B3 size)
    # The "Hope" config default of 256 was for a smaller distilled version
    checkpoints = [
        ("Resumed (Step 1000)", "F:/models/checkpoints/diverse_curriculum/step_1000.pt", 768),
        ("Base (Step 5000)", "F:/models/checkpoints/kd_sft_phase2/step_5000.pt", 768),
    ]

    for name, path, hidden_size in checkpoints:
        evaluator.evaluate_checkpoint(name, path, hidden_size)

    evaluator.print_summary()

if __name__ == "__main__":
    main()
