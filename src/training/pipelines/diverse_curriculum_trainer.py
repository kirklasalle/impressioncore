"""
ImpressionCore B3 Diverse Curriculum Trainer

Created: November 29, 2025
Author: GitHub Copilot
Tags: #training #b3 #diverse_curriculum #conversational_quality
Category: Training Infrastructure
Status: Active

This module implements the diverse curriculum training pipeline for B3
to achieve 10/10 conversational quality through domain-balanced training.

Key Features:
- Loads 230k+ diverse training samples
- Domain-balanced batch sampling
- Progressive curriculum learning
- Quality checkpoint evaluation
- Memory-optimized for GTX 1050 Ti
"""

import os
import random
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Rich console for beautiful output
try:
    from rich import print as rprint
    from rich.console import Console
    from rich.live import Live  # noqa: F401
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    rprint = print

    # Dummy classes to prevent NameError when rich is not available
    class Progress:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def add_task(self, *args, **kwargs): return 0
        def update(self, *args, **kwargs):
            if 'description' in kwargs:
                # Strip simple color tags for clean log output
                desc = kwargs['description'].replace('[cyan]', '').replace('[/cyan]', '')
                print(desc)

    class SpinnerColumn:
        pass
    class TextColumn:
        def __init__(self, *args): pass
    class BarColumn:
        pass
    class TaskProgressColumn:
        pass
    class TimeElapsedColumn:
        pass

console = Console() if RICH_AVAILABLE else None

# Import the diverse curriculum loader
import contextlib

from src.training.data.diverse_curriculum_loader import CurriculumConfig, DiverseCurriculumLoader


@dataclass
class DiverseTrainingConfig:
    """Configuration for diverse curriculum training."""
    # Model paths
    base_checkpoint_path: str = "F:/models/checkpoints/kd_sft_phase2/step_5000.pt"
    output_dir: str = "F:/models/checkpoints/diverse_curriculum_mhc_ultra"

    # MHC and Ultra Scaling
    use_mhc: bool = True
    b3_ultra: bool = True

    # Resume from checkpoint (auto-detect if True, or specify path)
    resume_from_checkpoint: bool = True  # Auto-resume from latest checkpoint
    resume_checkpoint_path: str | None = None  # Specific checkpoint to resume from

    # Training hyperparameters
    # Increased batch_size from 4 to 8 to better utilize GTX 1050 Ti 4GB VRAM
    # Target: ~2.5-3GB VRAM usage (was using only 1.89GB with batch_size=4)
    batch_size: int = 2  # Restored to 2 for Adafactor
    gradient_accumulation_steps: int = 16  # Restored to 16
    learning_rate: float = 2e-5
    warmup_steps: int = 500
    max_steps: int = 10000

    # Checkpointing
    save_every_steps: int = 1000
    eval_every_steps: int = 500

    # Domain balancing
    domain_weights: dict[str, float] = None

    # Hardware optimization
    mixed_precision: bool = True  # Enabled AMP (Patched for stability)
    gradient_checkpointing: bool = True
    max_length: int = 512

    # Curriculum phases
    phases: list[dict] = None

    def __post_init__(self):
        if self.domain_weights is None:
            self.domain_weights = {
                "real_conversations": 0.45,  # Increased to fix Step 5500 degeneracy
                "question_answering": 0.35,  # Reduced slightly
                "educational": 0.20          # Reduced slightly
            }

        if self.phases is None:
            self.phases = [
                {"name": "foundation", "steps": 3000, "lr_mult": 1.0},
                {"name": "diversification", "steps": 5000, "lr_mult": 0.7},
                {"name": "refinement", "steps": 2000, "lr_mult": 0.4}
            ]


class DiverseCurriculumDataset(Dataset):
    """PyTorch Dataset wrapper for diverse curriculum data."""

    def __init__(
        self,
        loader: DiverseCurriculumLoader,
        tokenizer,
        max_length: int = 512
    ):
        self.loader = loader
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Load all data
        if not loader.loaded:
            loader.load_all_sources()

        # Flatten all samples
        self.samples = []
        for _domain, pool in loader.domain_pools.items():
            self.samples.extend(pool)

        random.shuffle(self.samples)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        formatted = self.loader.format_for_training(sample)

        # Tokenize
        encoding = self.tokenizer(
            formatted["full_text"],
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "domain": sample.get("domain", "unknown")
        }


class DiverseB3Trainer:
    """
    Main trainer class for diverse curriculum B3 training.
    Optimized for GTX 1050 Ti (4GB VRAM).
    """

    def __init__(self, config: DiverseTrainingConfig):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Initialize components
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.tokenizer = None
        self.data_loader = None
        self.curriculum_loader = None

        # Training state
        self.global_step = 0
        self.current_phase = 0
        self.best_loss = float('inf')
        self.loss_history = []
        self.domain_stats = {}

        # Resume state
        self.resume_checkpoint = None

        # Create output directory
        os.makedirs(config.output_dir, exist_ok=True)

    def setup(self):
        """Initialize all training components."""
        print("DEBUG: Starting setup...")
        self._display_banner()

        # Check for resume checkpoint FIRST
        self._check_resume_checkpoint()

        # Setup tokenizer
        self._setup_tokenizer()

        # Setup curriculum loader
        self._setup_curriculum()

        # Load model (will use resume checkpoint if available)
        self._load_model()

        # Setup optimizer and scheduler
        self._setup_optimizer()

        # Restore training state if resuming
        if self.resume_checkpoint is not None:
            self._restore_training_state()

        # Setup data loader
        self._setup_dataloader()

        self._display_config()
        print("DEBUG: Setup complete.")

    def _check_resume_checkpoint(self):
        """Check for and find resume checkpoint."""
        if not self.config.resume_from_checkpoint:
            if RICH_AVAILABLE:
                console.print("[dim]Resume disabled - starting fresh from base checkpoint[/dim]")
            return

        # If specific path provided, use it
        if self.config.resume_checkpoint_path:
            resume_path = Path(self.config.resume_checkpoint_path)
            if resume_path.exists():
                self.resume_checkpoint = resume_path
                if RICH_AVAILABLE:
                    console.print(f"[green]Restored: {resume_path}[/green]")
                return
            else:
                if RICH_AVAILABLE:
                    console.print(f"[yellow]Specified checkpoint not found: {resume_path}[/yellow]")

        # Auto-detect latest checkpoint
        latest = self._find_latest_checkpoint()
        if latest:
            self.resume_checkpoint = latest
            if RICH_AVAILABLE:
                console.print(f"[green]Found checkpoint to resume from: {latest}[/green]")
        else:
            if RICH_AVAILABLE:
                console.print("[dim]No existing checkpoints found - starting fresh[/dim]")

    def _find_latest_checkpoint(self) -> Path | None:
        """Find the latest checkpoint in the output directory."""
        output_dir = Path(self.config.output_dir)
        if not output_dir.exists():
            return None

        # Find all step_*.pt files
        checkpoints = list(output_dir.glob("step_*.pt"))
        if not checkpoints:
            return None

        # Extract step numbers and find max
        def get_step(p: Path) -> int:
            try:
                return int(p.stem.split("_")[1])
            except (IndexError, ValueError):
                return -1

        latest = max(checkpoints, key=get_step)
        step_num = get_step(latest)

        if step_num > 0:
            if RICH_AVAILABLE:
                console.print(f"[cyan]Latest checkpoint: step_{step_num} ({latest.name})[/cyan]")
            return latest

        return None

    def _display_banner(self):
        """Display training banner."""
        if RICH_AVAILABLE:
            banner = """
+------------------------------------------------------------------+
|     ImpressionCore B3 Diverse Curriculum Trainer                 |
|                                                                  |
|  "Achieving 10/10 Conversational Quality Through Diversity"      |
|                                                                  |
|  Target: Transform domain-locked model into general assistant    |
|  Method: 230k+ diverse samples across multiple domains           |
|  Hardware: GTX 1050 Ti optimized (4GB VRAM)                      |
+------------------------------------------------------------------+
            """
            console.print(Panel(banner, style="bold cyan"))
        else:
            print("\n=== B3 Diverse Curriculum Trainer ===\n")

    def _setup_tokenizer(self):
        """Setup tokenizer."""
        if RICH_AVAILABLE:
            console.print("[yellow]Setting up tokenizer...[/yellow]")

        from transformers import AutoTokenizer

        # Use GPT-2 tokenizer as base (B3 compatible)
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")

        # Configure pad token (use eos as pad for GPT-2)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        if RICH_AVAILABLE:
            console.print(f"[green]Tokenizer ready with {len(self.tokenizer)} tokens[/green]")

    def _setup_curriculum(self):
        """Setup diverse curriculum loader."""
        if RICH_AVAILABLE:
            console.print("[yellow]Loading diverse curriculum data...[/yellow]")

        curriculum_config = CurriculumConfig(
            domain_weights=self.config.domain_weights
        )

        self.curriculum_loader = DiverseCurriculumLoader(
            curriculum_config=curriculum_config
        )

        # Load all sources
        self.curriculum_loader.load_all_sources()

        if RICH_AVAILABLE:
            console.print(f"[green]Loaded {self.curriculum_loader.total_samples:,} diverse samples[/green]")

    def _load_model(self):
        """Load B3 model from checkpoint."""
        # Determine which checkpoint to load
        if self.resume_checkpoint is not None:
            load_path = self.resume_checkpoint
            if RICH_AVAILABLE:
                console.print(f"[green]RESUMING from checkpoint: {load_path}[/green]")
        else:
            load_path = Path(self.config.base_checkpoint_path)
            if RICH_AVAILABLE:
                console.print(f"[yellow]Loading model from base: {load_path}...[/yellow]")

        # Import B3 model architecture (correct path)
        try:
            from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model
        except ImportError:
            console.print("[red]❌ Could not import B3 model architecture[/red]")
            raise

        # Load checkpoint
        checkpoint_path = Path(load_path)
        print(f"DEBUG: Attempting to load checkpoint from: {checkpoint_path}")
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)

        # Extract config using from_dict to filter unknown params
        if "config" in checkpoint:
            model_config = B3Config.from_dict(checkpoint["config"])
        else:
            # Default B3 config with MHC and Ultra flags applied from trainer config
            model_config = B3Config()

        # Override with current trainer's MHC/Ultra preferences
        model_config.use_mhc = self.config.use_mhc
        model_config.b3_ultra = self.config.b3_ultra

        # Create model
        self.model = ImpressionCoreB3Model(model_config)

        # Load weights
        if "model_state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["model_state_dict"], strict=False)
        elif "state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["state_dict"], strict=False)

        # Check vocab size compatibility (B3 model doesn't support resize)
        model_vocab_size = model_config.vocab_size
        tokenizer_vocab_size = len(self.tokenizer)
        if model_vocab_size != tokenizer_vocab_size:
            if RICH_AVAILABLE:
                console.print(f"[yellow]⚠ Vocab size mismatch: model={model_vocab_size}, tokenizer={tokenizer_vocab_size}[/yellow]")

        # Move to device
        self.model.to(self.device)

        # Verify model is on correct device
        if self.device.type == "cuda":
            # Check if model parameters are actually on GPU
            first_param = next(self.model.parameters())
            if first_param.device.type != "cuda":
                console.print("[red]⚠ WARNING: Model failed to move to CUDA! Forcing move...[/red]")
                self.model = self.model.cuda()

            # Show GPU memory usage
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / 1024**3
                reserved = torch.cuda.memory_reserved() / 1024**3
                console.print(f"[cyan]📊 GPU Memory: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved[/cyan]")

        # Enable gradient checkpointing for memory efficiency
        if self.config.gradient_checkpointing and hasattr(self.model, 'gradient_checkpointing_enable'):
            self.model.gradient_checkpointing_enable()

        # Count parameters
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)

        if RICH_AVAILABLE:
            console.print(f"[green]Model loaded: {total_params:,} params ({trainable_params:,} trainable)[/green]")

    def _setup_optimizer(self):
        """Setup optimizer and learning rate scheduler."""
        if RICH_AVAILABLE:
            console.print("[yellow]Setting up optimizer (Adafactor)...[/yellow]")

        # Adafactor optimizer (Memory efficient)
        from transformers.optimization import Adafactor
        self.optimizer = Adafactor(
            self.model.parameters(),
            lr=self.config.learning_rate,
            scale_parameter=False,
            relative_step=False,
            warmup_init=False
        )

        # Learning rate scheduler with warmup
        from transformers import get_linear_schedule_with_warmup

        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=self.config.warmup_steps,
            num_training_steps=self.config.max_steps
        )

        if RICH_AVAILABLE:
            console.print(f"[green]Optimizer ready (Adafactor, lr={self.config.learning_rate})[/green]")

    def _restore_training_state(self):
        """Restore training state from resume checkpoint."""
        if self.resume_checkpoint is None:
            return

        if RICH_AVAILABLE:
            console.print(f"[yellow]Restoring training state from {self.resume_checkpoint}...[/yellow]")

        try:
            checkpoint = torch.load(self.resume_checkpoint, map_location="cpu", weights_only=False)

            # Restore global step
            if "global_step" in checkpoint:
                self.global_step = checkpoint["global_step"]
                if RICH_AVAILABLE:
                    console.print(f"[green]Restored global_step: {self.global_step}[/green]")

            # Restore optimizer state (SKIP for Adafactor switch)
            # if "optimizer_state_dict" in checkpoint and self.optimizer is not None:
            #     try:
            #         self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
            #         if RICH_AVAILABLE:
            #             console.print("[green]✓ Restored optimizer state[/green]")
            #     except Exception as e:
            #         if RICH_AVAILABLE:
            #             console.print(f"[red]⚠ Could not restore optimizer state (Switched Optimizer?): {e}[/red]")
            #             console.print("[yellow]Continuing with fresh optimizer state...[/yellow]")
            #     except Exception as e:
            #         if RICH_AVAILABLE:
            #             console.print(f"[yellow]⚠ Could not restore optimizer state: {e}[/yellow]")

            if RICH_AVAILABLE:
                console.print("[yellow]Optimizer state load SKIPPED (Switching to Adafactor)[/yellow]")

            # Restore scheduler state
            if "scheduler_state_dict" in checkpoint and self.scheduler is not None:
                try:
                    self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
                    if RICH_AVAILABLE:
                        console.print("[green]Restored scheduler state[/green]")
                except Exception as e:
                    if RICH_AVAILABLE:
                        console.print(f"[yellow]Could not restore scheduler state: {e}[/yellow]")

            # Restore loss history
            if "loss_history" in checkpoint:
                self.loss_history = checkpoint["loss_history"]
                if RICH_AVAILABLE:
                    console.print(f"[green]Restored loss history ({len(self.loss_history)} entries)[/green]")

            # Calculate remaining steps
            remaining_steps = self.config.max_steps - self.global_step
            if RICH_AVAILABLE:
                console.print("[cyan]Resume Summary:[/cyan]")
                console.print(f"[cyan]   * Current step: {self.global_step:,}[/cyan]")
                console.print(f"[cyan]   * Target step: {self.config.max_steps:,}[/cyan]")
                console.print(f"[cyan]   * Remaining: {remaining_steps:,} steps[/cyan]")
                if self.loss_history:
                    console.print(f"[cyan]   * Last loss: {self.loss_history[-1]:.4f}[/cyan]")

        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"[red]Error restoring training state: {e}[/red]")
                console.print("[yellow]Continuing with fresh optimizer/scheduler state...[/yellow]")

    def _setup_dataloader(self):
        """Setup PyTorch DataLoader."""
        if RICH_AVAILABLE:
            console.print("[yellow]Setting up data loader...[/yellow]")

        dataset = DiverseCurriculumDataset(
            loader=self.curriculum_loader,
            tokenizer=self.tokenizer,
            max_length=self.config.max_length
        )

        self.data_loader = DataLoader(
            dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=0,  # Avoid multiprocessing issues on Windows
            pin_memory=self.device.type == "cuda"
        )

        if RICH_AVAILABLE:
            console.print(f"[green]DataLoader ready ({len(dataset):,} samples)[/green]")

    def _display_config(self):
        """Display training configuration."""
        if not RICH_AVAILABLE:
            return

        table = Table(title="Training Configuration")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Device", str(self.device))
        table.add_row("Batch Size", str(self.config.batch_size))
        table.add_row("Gradient Accumulation", str(self.config.gradient_accumulation_steps))
        table.add_row("Effective Batch Size", str(self.config.batch_size * self.config.gradient_accumulation_steps))
        table.add_row("Learning Rate", f"{self.config.learning_rate:.2e}")
        table.add_row("Max Steps", f"{self.config.max_steps:,}")
        table.add_row("Mixed Precision", str(self.config.mixed_precision))
        table.add_row("Gradient Checkpointing", str(self.config.gradient_checkpointing))

        console.print(table)

        # Domain weights
        domain_table = Table(title="Domain Weights (Target Distribution)")
        domain_table.add_column("Domain", style="cyan")
        domain_table.add_column("Weight", style="green")

        for domain, weight in self.config.domain_weights.items():
            domain_table.add_row(domain, f"{weight:.1%}")

        console.print(domain_table)

    def train(self):
        """Run the training loop."""
        print(f"DEBUG: Starting train loop. Global step: {self.global_step}, Max steps: {self.config.max_steps}")
        if RICH_AVAILABLE:
            console.print(Panel("[bold green]Starting Diverse Curriculum Training[/bold green]"))

        self.model.train()

        # Mixed precision scaler
        scaler = torch.amp.GradScaler('cuda') if self.config.mixed_precision and self.device.type == "cuda" else None

        # Training loop
        accumulation_loss = 0.0
        accumulation_count = 0

        data_iter = iter(self.data_loader)

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=console if RICH_AVAILABLE else None
            ) as progress:

                task = progress.add_task(
                    f"[cyan]Training (Step {self.global_step}/{self.config.max_steps})",
                    total=self.config.max_steps,
                    completed=self.global_step  # Start progress bar at current step when resuming
                )

                # Model vocab size for clamping (B3 uses 50257)

                while self.global_step < self.config.max_steps:
                    # Get batch (with cycling)
                    try:
                        batch = next(data_iter)
                    except StopIteration:
                        data_iter = iter(self.data_loader)
                        batch = next(data_iter)

                    # Move to device
                    input_ids = batch["input_ids"].to(self.device)
                    attention_mask = batch["attention_mask"].to(self.device)

                    # No clamping needed if vocab sizes match
                    # Create labels with -100 masking for padding
                    labels = input_ids.clone()
                    labels[attention_mask == 0] = -100

                    # Forward pass - B3 model uses 'mask' not 'attention_mask' and returns dict
                    if self.config.mixed_precision and scaler:
                        with torch.amp.autocast('cuda'):
                            outputs = self.model(
                                input_ids=input_ids,
                                mask=attention_mask,
                                labels=labels
                            )
                            # B3 model returns a dict with 'loss' key
                            loss = outputs['loss'] if isinstance(outputs, dict) else outputs.loss
                            loss = loss / self.config.gradient_accumulation_steps

                        scaler.scale(loss).backward()
                    else:
                        outputs = self.model(
                            input_ids=input_ids,
                            mask=attention_mask,
                            labels=labels
                        )
                        # B3 model returns a dict with 'loss' key
                        loss = outputs['loss'] if isinstance(outputs, dict) else outputs.loss
                        loss = loss / self.config.gradient_accumulation_steps
                        loss.backward()

                    accumulation_loss += loss.item()
                    accumulation_count += 1

                    # Gradient accumulation
                    if accumulation_count >= self.config.gradient_accumulation_steps:
                        # Clip gradients
                        if scaler:
                            scaler.unscale_(self.optimizer)
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

                        # Optimizer step
                        if scaler:
                            scaler.step(self.optimizer)
                            scaler.update()
                        else:
                            self.optimizer.step()

                        self.scheduler.step()
                        self.optimizer.zero_grad()

                        # Record loss
                        avg_loss = accumulation_loss
                        self.loss_history.append(avg_loss)

                        # Update step
                        self.global_step += 1
                        accumulation_loss = 0.0
                        accumulation_count = 0

                        # Update progress
                        progress.update(
                            task,
                            advance=1,
                            description=f"[cyan]Step {self.global_step}/{self.config.max_steps} | Loss: {avg_loss:.4f}"
                        )

                        # Evaluation checkpoint
                        if self.global_step % self.config.eval_every_steps == 0:
                            self._evaluate_checkpoint()

                        # Save checkpoint
                        # Dynamic checkpointing: 200 steps < 6000, else 1000
                        current_save_freq = 200 if self.global_step < 6000 else self.config.save_every_steps
                        if self.global_step % current_save_freq == 0:
                            self._save_checkpoint()

                        # Clear cache
                        if self.global_step % 100 == 0:
                            torch.cuda.empty_cache()

                # Final save if we finish normally
                self._save_checkpoint(final=True)

                if RICH_AVAILABLE:
                    console.print(Panel("[bold green]Training Complete![/bold green]"))

        except KeyboardInterrupt:
            if RICH_AVAILABLE:
                console.print("\n[yellow]Training interrupted by user.[/yellow]")
            self._save_checkpoint(final=False)
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"\n[bold red]CRITICAL ERROR: {e}[/bold red]")

            # Log to file for persistence
            with open("training_termination.log", "a") as f:
                f.write(f"[{datetime.now().isoformat()}] Step {self.global_step}: {e!s}\n")

            # Attempt emergency save
            with contextlib.suppress(Exception):
                self._save_checkpoint(final=False)
            raise e from e

    def _evaluate_checkpoint(self):
        """Run evaluation at checkpoint."""
        if RICH_AVAILABLE:
            console.print(f"\n[yellow]Evaluating at step {self.global_step}...[/yellow]")

        self.model.eval()

        # Sample test prompts
        test_prompts = [
            "Hello, how are you today?",
            "What is the capital of France?",
            "Can you explain quantum computing?",
            "Tell me a joke.",
            "What should I cook for dinner?"
        ]

        responses = []
        with torch.no_grad():
            for prompt in test_prompts:
                response = self._generate_response(prompt)
                responses.append((prompt, response))

        # Display sample responses
        if RICH_AVAILABLE:
            table = Table(title=f"Sample Responses (Step {self.global_step})")
            table.add_column("Prompt", style="cyan", max_width=30)
            table.add_column("Response", style="green", max_width=50)

            for prompt, response in responses[:3]:
                table.add_row(prompt[:30], response[:50])

            console.print(table)

        self.model.train()

    def _generate_response(self, prompt: str, max_new_tokens: int = 100) -> str:
        """Generate a response for evaluation.

        Uses format matching training: 'User: {prompt}\nAssistant:'
        """
        # Match the training format exactly
        formatted_prompt = f"User: {prompt}\nAssistant:"

        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=256
        ).to(self.device)

        # Model vocab size for clamping
        model_vocab_size = 50257

        with torch.no_grad():
            # B3 model doesn't have generate() - use autoregressive loop
            input_ids = inputs["input_ids"]
            input_ids = torch.clamp(input_ids, max=model_vocab_size - 1)

            # Track the starting length so we only decode NEW tokens
            input_ids.shape[1]

            generated_ids = input_ids.clone()
            generated_tokens = []  # Track only new tokens

            for _ in range(max_new_tokens):
                # Get model outputs
                outputs = self.model(input_ids=generated_ids)
                logits = outputs['logits'] if isinstance(outputs, dict) else outputs.logits

                # Get next token logits (last position)
                next_token_logits = logits[:, -1, :] / 0.8  # temperature (slightly higher for diversity)

                # Apply top-p sampling (nucleus sampling)
                sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
                sorted_indices_to_remove = cumulative_probs > 0.92  # slightly higher top_p
                sorted_indices_to_remove[:, 1:] = sorted_indices_to_remove[:, :-1].clone()
                sorted_indices_to_remove[:, 0] = 0

                indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                next_token_logits[indices_to_remove] = float('-inf')

                # Sample next token
                probs = torch.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)

                # Track the new token
                generated_tokens.append(next_token.item())

                # Append to sequence
                generated_ids = torch.cat([generated_ids, next_token], dim=-1)

                # Stop if EOS token or pad token
                if next_token.item() in [self.tokenizer.eos_token_id, self.tokenizer.pad_token_id]:
                    break

                # Stop on common end patterns (newlines often indicate end of response)
                if len(generated_tokens) > 10:
                    # Check if we've generated a complete thought
                    last_tokens = generated_tokens[-3:]
                    # Decode to check for patterns
                    last_text = self.tokenizer.decode(last_tokens)
                    if last_text.strip().endswith(('.', '!', '?', '\n\n')):
                        break

                # Limit sequence length
                if generated_ids.shape[1] > 512:
                    break

        # ONLY decode the NEW tokens (not the prompt)
        if generated_tokens:
            response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        else:
            response = "[No response generated]"

        # Clean up the response
        response = response.strip()
        if not response:
            response = "[Empty response]"

        return response

    def _save_checkpoint(self, final: bool = False):
        """Save training checkpoint."""
        checkpoint_name = "final.pt" if final else f"step_{self.global_step}.pt"
        checkpoint_path = Path(self.config.output_dir) / checkpoint_name

        if RICH_AVAILABLE:
            console.print(f"[yellow]Saving checkpoint to {checkpoint_path}...[/yellow]")

        checkpoint = {
            "global_step": self.global_step,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict(),
            "loss_history": self.loss_history,
            "config": self.config.__dict__,
            "timestamp": datetime.now().isoformat()
        }

        torch.save(checkpoint, checkpoint_path)

        if RICH_AVAILABLE:
            console.print(f"[green]Checkpoint saved: {checkpoint_path}[/green]")


def main():
    """Main entry point with robust error handling."""
    try:
        config = DiverseTrainingConfig()

        trainer = DiverseB3Trainer(config)
        trainer.setup()
        trainer.train()
    except Exception as e:
        import traceback
        error_msg = f"FATAL ERROR in main loop: {e}\n{traceback.format_exc()}"
        print(error_msg)
        with open("fatal_trainer_error.log", "w") as f:
            f.write(f"[{datetime.now().isoformat()}] {error_msg}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
