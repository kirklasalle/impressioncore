#!/usr/bin/env python3
"""
ImpressionCore B3 Brain-Triad Conversational Quality Tester
============================================================

**Created:** November 28, 2025
**Updated:** November 28, 2025
**Author:** Kirk LaSalle; GitHub Copilot
**Tags:** #testing #b3 #brain_triad #conversational #impressioncore_c
**Category:** Testing
**Status:** Active

Purpose: Comprehensive conversational quality testing for the B3 step_5000.pt checkpoint.
This is a critical milestone in the Brain-Triad Architecture - testing the base model
quality before hemispheric specialization.

VIP Architecture Reference: docs/architecture/IMPRESSIONCORE_C_BRAIN_TRIAD_ARCHITECTURE.md
"""

import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import torch

# Setup path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Rich console for beautiful output
try:
    from rich import box
    from rich.console import Console
    from rich.markdown import Markdown  # noqa: F401
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm, Prompt
    from rich.table import Table
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    class Console:
        def print(self, *args, **kwargs):
            print(*args)
    console = Console()

# Model imports
from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model

# Tokenizer
try:
    from transformers import AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    import tiktoken

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ConversationEvalResult:
    """Result of a single conversation evaluation"""
    prompt: str
    response: str
    quality_score: int | None = None
    category: str = "general"
    notes: str = ""
    generation_time_ms: float = 0.0


@dataclass
class QualityTestSuite:
    """Comprehensive quality test suite for B3 evaluation"""
    name: str = "Brain-Triad Base Model Evaluation"
    test_prompts: dict[str, list[str]] = field(default_factory=dict)

    def __post_init__(self):
        if not self.test_prompts:
            self.test_prompts = {
                "greeting": [
                    "Hello, how are you?",
                    "Good morning! What's your name?",
                    "Hi there! Can we have a conversation?",
                ],
                "self_awareness": [
                    "What are you?",
                    "Tell me about yourself.",
                    "Who created you?",
                    "What can you help me with?",
                ],
                "factual": [
                    "What is artificial intelligence?",
                    "Explain how computers work.",
                    "What is the capital of France?",
                    "How does the internet work?",
                ],
                "reasoning": [
                    "If I have 5 apples and give away 2, how many do I have?",
                    "Why is the sky blue?",
                    "What happens when water freezes?",
                    "How do birds fly?",
                ],
                "creative": [
                    "Write a short poem about the sunset.",
                    "Tell me a creative story about a robot.",
                    "What would happen if animals could talk?",
                    "Describe a perfect day.",
                ],
                "helpful": [
                    "Can you help me with something?",
                    "I need advice about learning to code.",
                    "What's a good way to stay healthy?",
                    "How can I be more productive?",
                ],
                "conversational": [
                    "That's interesting! Tell me more.",
                    "I didn't understand that. Can you explain differently?",
                    "Great! What else should I know?",
                    "Thank you for your help!",
                ],
                "edge_cases": [
                    "",  # Empty prompt
                    "???",  # Ambiguous
                    ".",  # Minimal
                    "Can you repeat that please?",
                ],
            }


class B3ConversationalTester:
    """
    Brain-Triad Architecture Base Model Conversational Tester

    This tester evaluates the B3 step_5000.pt checkpoint for conversational quality
    as part of the ImpressionCore-C Brain-Triad Architecture development.

    The goal: Achieve 10/10 conversation quality before hemispheric specialization.
    """

    CHECKPOINT_PATH = Path("F:/models/checkpoints/kd_sft_phase2/step_5000.pt")

    def __init__(
        self,
        checkpoint_path: Path | None = None,
        device: str | None = None,
        max_new_tokens: int = 100,
        temperature: float = 0.7,
    ):
        self.checkpoint_path = checkpoint_path or self.CHECKPOINT_PATH
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature

        self.model = None
        self.tokenizer = None
        self.config = None

        self.conversation_history: list[ConversationEvalResult] = []
        self.test_suite = QualityTestSuite()

    def display_banner(self):
        """Display the impressive startup banner"""
        if RICH_AVAILABLE:
            banner = """
🧠 [bold cyan]ImpressionCore B3 Brain-Triad Conversational Tester[/bold cyan] 🧠

[yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/yellow]

[bold green]VIP GOVERNING ARCHITECTURE[/bold green]: ImpressionCore-C Brain-Triad
[dim]Left Hemisphere (Analytical) + Right Hemisphere (Creative) + Colossus (Arbiter)[/dim]

[bold]Purpose:[/bold] Test base B3 model quality before hemispheric specialization
[bold]Target:[/bold] Achieve 10/10 conversation quality
[bold]Checkpoint:[/bold] step_5000.pt (506M parameters)

[yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/yellow]
"""
            console.print(Panel(banner, title="🎯 Historic Moment", border_style="cyan"))
        else:
            print("=" * 60)
            print("ImpressionCore B3 Brain-Triad Conversational Tester")
            print("=" * 60)
            print(f"Checkpoint: {self.checkpoint_path}")
            print("=" * 60)

    def load_model(self) -> bool:
        """Load the B3 model from checkpoint"""
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("[cyan]Loading B3 model (506M parameters)...", total=None)
                success = self._load_model_internal()
                progress.update(task, completed=True)
        else:
            print("Loading B3 model...")
            success = self._load_model_internal()

        return success

    def _load_model_internal(self) -> bool:
        """Internal model loading logic"""
        try:
            # Ensure checkpoint_path is a Path object
            if isinstance(self.checkpoint_path, str):
                self.checkpoint_path = Path(self.checkpoint_path)

            # Check checkpoint exists
            if not self.checkpoint_path.exists():
                console.print(f"[red]❌ Checkpoint not found: {self.checkpoint_path}[/red]")
                return False

            # Initialize config and model
            self.config = B3Config()
            self.model = ImpressionCoreB3Model(self.config)

            # Load checkpoint
            checkpoint = torch.load(self.checkpoint_path, map_location=self.device, weights_only=False)

            # Handle different checkpoint formats
            if "model_state_dict" in checkpoint:
                state_dict = checkpoint["model_state_dict"]
                training_info = {
                    "step": checkpoint.get("step", "unknown"),
                    "epoch": checkpoint.get("epoch", "unknown"),
                    "loss": checkpoint.get("loss", "unknown"),
                }
            else:
                state_dict = checkpoint
                training_info = {}

            # Load state dict
            missing, unexpected = self.model.load_state_dict(state_dict, strict=False)

            if missing:
                logger.warning(f"Missing keys: {len(missing)}")
            if unexpected:
                logger.warning(f"Unexpected keys: {len(unexpected)}")

            # Move to device and set eval mode
            self.model = self.model.to(self.device)
            self.model.eval()

            # Load tokenizer
            if TRANSFORMERS_AVAILABLE:
                self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
                self.tokenizer.pad_token = self.tokenizer.eos_token
            else:
                self.tokenizer = tiktoken.get_encoding("gpt2")

            # Display success info
            param_count = sum(p.numel() for p in self.model.parameters())

            if RICH_AVAILABLE:
                info_table = Table(title="Model Loaded Successfully", box=box.ROUNDED)
                info_table.add_column("Property", style="cyan")
                info_table.add_column("Value", style="green")
                info_table.add_row("Parameters", f"{param_count:,}")
                info_table.add_row("Device", self.device)
                info_table.add_row("Checkpoint", str(self.checkpoint_path.name))
                if training_info:
                    info_table.add_row("Training Step", str(training_info.get("step", "N/A")))
                console.print(info_table)
            else:
                print(f"✅ Model loaded: {param_count:,} parameters on {self.device}")

            return True

        except Exception as e:
            console.print(f"[red]❌ Error loading model: {e}[/red]")
            logger.exception("Model loading failed")
            return False

    def generate_response(
        self,
        prompt: str,
        max_new_tokens: int | None = None,
        temperature: float | None = None,
    ) -> tuple[str, float]:
        """Generate a response to a prompt"""
        if self.model is None:
            return "Model not loaded", 0.0

        max_tokens = max_new_tokens or self.max_new_tokens
        temp = temperature or self.temperature

        # Format prompt for conversation
        formatted_prompt = f"Human: {prompt}\nAssistant:"

        start_time = datetime.now()

        try:
            # Tokenize
            if TRANSFORMERS_AVAILABLE:
                inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
                input_ids = inputs["input_ids"].to(self.device)
            else:
                input_ids = torch.tensor([self.tokenizer.encode(formatted_prompt)]).to(self.device)

            # Generate
            with torch.no_grad():
                generated = input_ids.clone()

                for _ in range(max_tokens):
                    outputs = self.model(input_ids=generated)
                    logits = outputs["logits"][:, -1, :] / temp

                    # Sample next token
                    probs = torch.softmax(logits, dim=-1)
                    next_token = torch.multinomial(probs, 1)

                    # Check for end token
                    if TRANSFORMERS_AVAILABLE and next_token.item() == self.tokenizer.eos_token_id:
                        break

                    generated = torch.cat([generated, next_token], dim=1)

                    # Stop at natural breaks
                    if TRANSFORMERS_AVAILABLE:
                        decoded_token = self.tokenizer.decode(next_token[0])
                    else:
                        decoded_token = self.tokenizer.decode([next_token.item()])

                    if decoded_token in ['\n', '\r'] and generated.shape[1] > input_ids.shape[1] + 10:
                        break

            # Decode response
            if TRANSFORMERS_AVAILABLE:
                full_response = self.tokenizer.decode(generated[0], skip_special_tokens=True)
            else:
                full_response = self.tokenizer.decode(generated[0].tolist())

            # Extract assistant response
            response = full_response.split("Assistant:")[-1].strip()
            response = response.split("Human:")[0].strip()
            response = response.split("\n")[0].strip()  # Take first line

            if not response:
                response = "[No response generated]"

        except Exception as e:
            logger.error(f"Generation error: {e}")
            response = f"[Error: {e!s}]"

        generation_time = (datetime.now() - start_time).total_seconds() * 1000

        return response, generation_time

    def run_quick_evaluation(self) -> dict[str, list[ConversationEvalResult]]:
        """Run a quick evaluation across all test categories"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]🧪 Running Quick Evaluation[/bold cyan]\n")
        else:
            print("\n🧪 Running Quick Evaluation\n")

        results = {}

        for category, prompts in self.test_suite.test_prompts.items():
            if RICH_AVAILABLE:
                console.print(f"\n[bold yellow]Category: {category.upper()}[/bold yellow]")
            else:
                print(f"\nCategory: {category.upper()}")

            category_results = []

            for prompt in prompts:
                response, gen_time = self.generate_response(prompt)

                result = ConversationEvalResult(
                    prompt=prompt,
                    response=response,
                    category=category,
                    generation_time_ms=gen_time,
                )
                category_results.append(result)

                if RICH_AVAILABLE:
                    console.print(f"  [green]Human:[/green] {prompt if prompt else '[empty]'}")
                    console.print(f"  [cyan]B3:[/cyan] {response}")
                    console.print(f"  [dim]({gen_time:.0f}ms)[/dim]\n")
                else:
                    print(f"  Human: {prompt if prompt else '[empty]'}")
                    print(f"  B3: {response}")
                    print(f"  ({gen_time:.0f}ms)\n")

            results[category] = category_results
            self.conversation_history.extend(category_results)

        return results

    def interactive_mode(self):
        """Run interactive conversation mode with quality scoring"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]💬 Interactive Conversation Mode[/bold cyan]")
            console.print("[dim]Commands: 'quit', 'eval', 'score', 'save', 'help'[/dim]\n")
        else:
            print("\n💬 Interactive Conversation Mode")
            print("Commands: 'quit', 'eval', 'score', 'save', 'help'\n")

        while True:
            try:
                user_input = Prompt.ask("[green]You[/green]") if RICH_AVAILABLE else input("You: ")

                user_input = user_input.strip()

                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    if RICH_AVAILABLE:
                        console.print("[yellow]👋 Goodbye! Making history together.[/yellow]")
                    else:
                        print("👋 Goodbye!")
                    break

                elif user_input.lower() == 'eval':
                    self.run_quick_evaluation()
                    continue

                elif user_input.lower() == 'score':
                    self.display_quality_summary()
                    continue

                elif user_input.lower() == 'save':
                    self.save_conversation_history()
                    continue

                elif user_input.lower() == 'help':
                    self.display_help()
                    continue

                elif not user_input:
                    continue

                # Generate response
                response, gen_time = self.generate_response(user_input)

                if RICH_AVAILABLE:
                    console.print(f"[cyan]B3:[/cyan] {response}")
                    console.print(f"[dim]({gen_time:.0f}ms)[/dim]")

                    # Ask for quality score
                    score_input = Prompt.ask(
                        "[dim]Rate response (1-10, or Enter to skip)[/dim]",
                        default=""
                    )
                else:
                    print(f"B3: {response}")
                    print(f"({gen_time:.0f}ms)")
                    score_input = input("Rate (1-10, Enter to skip): ")

                # Parse score
                quality_score = None
                if score_input:
                    try:
                        quality_score = int(score_input)
                        if not 1 <= quality_score <= 10:
                            quality_score = None
                    except ValueError:
                        pass

                # Record result
                result = ConversationEvalResult(
                    prompt=user_input,
                    response=response,
                    quality_score=quality_score,
                    category="interactive",
                    generation_time_ms=gen_time,
                )
                self.conversation_history.append(result)

            except KeyboardInterrupt:
                console.print("\n[yellow]👋 Interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

    def display_quality_summary(self):
        """Display summary of quality scores"""
        scored = [r for r in self.conversation_history if r.quality_score is not None]

        if not scored:
            console.print("[yellow]No scored conversations yet.[/yellow]")
            return

        avg_score = sum(r.quality_score for r in scored) / len(scored)

        if RICH_AVAILABLE:
            summary_table = Table(title="Quality Summary", box=box.ROUNDED)
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", style="green")
            summary_table.add_row("Total Conversations", str(len(self.conversation_history)))
            summary_table.add_row("Scored Conversations", str(len(scored)))
            summary_table.add_row("Average Score", f"{avg_score:.1f}/10")
            summary_table.add_row("Target", "10/10")
            summary_table.add_row("Status", "🎯 On Track" if avg_score >= 7 else "📈 Improving")
            console.print(summary_table)
        else:
            print("\nQuality Summary:")
            print(f"  Total: {len(self.conversation_history)}")
            print(f"  Scored: {len(scored)}")
            print(f"  Average: {avg_score:.1f}/10")

    def display_help(self):
        """Display help information"""
        help_text = """
[bold]Commands:[/bold]
  [green]quit/exit/q[/green] - End conversation
  [green]eval[/green]        - Run quick evaluation (all test prompts)
  [green]score[/green]       - Display quality summary
  [green]save[/green]        - Save conversation history to file
  [green]help[/green]        - Show this help

[bold]Quality Scoring:[/bold]
  After each response, rate it 1-10:
  • 1-3: Poor (incoherent, wrong, unhelpful)
  • 4-6: Acceptable (understandable but improvable)
  • 7-9: Good (helpful, accurate, well-formed)
  • 10:  Excellent (perfect response)

[bold]Brain-Triad Architecture:[/bold]
  This tester evaluates the base B3 model quality.
  Target: Achieve 10/10 before hemispheric specialization.
"""
        if RICH_AVAILABLE:
            console.print(Panel(help_text, title="Help", border_style="cyan"))
        else:
            print(help_text)

    def save_conversation_history(self):
        """Save conversation history to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"b3_conversation_eval_{timestamp}.json"

        # Prepare data
        data = {
            "session_info": {
                "timestamp": datetime.now().isoformat(),
                "checkpoint": str(self.checkpoint_path),
                "device": self.device,
                "total_conversations": len(self.conversation_history),
            },
            "conversations": [
                {
                    "prompt": r.prompt,
                    "response": r.response,
                    "quality_score": r.quality_score,
                    "category": r.category,
                    "generation_time_ms": r.generation_time_ms,
                }
                for r in self.conversation_history
            ],
        }

        # Calculate summary stats
        scored = [r for r in self.conversation_history if r.quality_score is not None]
        if scored:
            data["session_info"]["average_score"] = sum(r.quality_score for r in scored) / len(scored)
            data["session_info"]["scored_count"] = len(scored)

        # Save
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        if RICH_AVAILABLE:
            console.print(f"[green]💾 Saved to: {filename}[/green]")
        else:
            print(f"💾 Saved to: {filename}")

    def run(self):
        """Main entry point"""
        self.display_banner()

        # Load model
        if not self.load_model():
            return

        # Menu
        if RICH_AVAILABLE:
            console.print("\n[bold]What would you like to do?[/bold]")
            console.print("  [green]1.[/green] Quick evaluation (standard test prompts)")
            console.print("  [green]2.[/green] Interactive conversation with scoring")
            console.print("  [green]3.[/green] Both (evaluation then interactive)")
            choice = Prompt.ask("\nChoice", choices=["1", "2", "3"], default="3")
        else:
            print("\nWhat would you like to do?")
            print("  1. Quick evaluation")
            print("  2. Interactive conversation")
            print("  3. Both")
            choice = input("\nChoice (1/2/3): ").strip() or "3"

        if choice == "1":
            self.run_quick_evaluation()
            self.display_quality_summary()
        elif choice == "2":
            self.interactive_mode()
        elif choice == "3":
            self.run_quick_evaluation()
            self.display_quality_summary()
            if RICH_AVAILABLE:
                if Confirm.ask("\n[cyan]Continue to interactive mode?[/cyan]", default=True):
                    self.interactive_mode()
            else:
                cont = input("\nContinue to interactive mode? (y/n): ")
                if cont.lower() in ['y', 'yes', '']:
                    self.interactive_mode()

        # Final summary
        self.display_quality_summary()

        # Offer to save
        if self.conversation_history:
            if RICH_AVAILABLE:
                if Confirm.ask("\n[cyan]Save conversation history?[/cyan]", default=True):
                    self.save_conversation_history()
            else:
                save = input("\nSave conversation history? (y/n): ")
                if save.lower() in ['y', 'yes']:
                    self.save_conversation_history()

        if RICH_AVAILABLE:
            console.print("\n[bold green]🎯 Thank you for testing ImpressionCore B3![/bold green]")
            console.print("[dim]Making history together - Brain-Triad Architecture[/dim]\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="B3 Brain-Triad Conversational Tester")
    parser.add_argument("--checkpoint", type=str, help="Path to checkpoint file")
    parser.add_argument("--device", type=str, choices=["cuda", "cpu"], help="Device to use")
    parser.add_argument("--max-tokens", type=int, default=100, help="Max new tokens to generate")
    parser.add_argument("--temperature", type=float, default=0.7, help="Generation temperature")
    parser.add_argument("--prompt", type=str, help="Single prompt to test (non-interactive)")

    args = parser.parse_args()

    # Create tester
    tester = B3ConversationalTester(
        checkpoint_path=Path(args.checkpoint) if args.checkpoint else None,
        device=args.device,
        max_new_tokens=args.max_tokens,
        temperature=args.temperature,
    )

    # Single prompt mode
    if args.prompt:
        tester.display_banner()
        if tester.load_model():
            response, gen_time = tester.generate_response(args.prompt)
            print(f"\nHuman: {args.prompt}")
            print(f"B3: {response}")
            print(f"({gen_time:.0f}ms)")
        return

    # Full interactive mode
    tester.run()


if __name__ == "__main__":
    main()
