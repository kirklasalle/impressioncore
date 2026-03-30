#!/usr/bin/env python3
"""
Phase 4: Ollama Knowledge Distillation Trainer
==============================================

Implements Sequence-Level Knowledge Distillation (SFT on Teacher Outputs)
using a local Ollama instance as the teacher.

Objective:
- Use high-quality teacher (e.g., Llama3, Mistral) to generate responses.
- Train B3-Hope (Student) to mimic these high-quality responses.
- Maintain strict 39M parameter and GTX 1050 Ti constraints.

Created: October 2025
Author: ImpressionCore Team
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
import ollama
import json
import os
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
import logging
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.training.b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(f'phase4_distillation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
console = Console()

class OllamaTeacher:
    """Interface for the Ollama Teacher Model"""
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        self.console = Console()

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response from teacher"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = ollama.chat(model=self.model_name, messages=messages)
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return None

class DistillationDataset(Dataset):
    """Dataset that generates/caches teacher responses on the fly or pre-loads them"""
    def __init__(self, source_file: str, tokenizer, teacher: OllamaTeacher, max_length=512, cache_file=None):
        self.tokenizer = tokenizer
        self.teacher = teacher
        self.max_length = max_length
        self.data = []
        self.cache_file = cache_file

        # Load source prompts
        self.prompts = []
        with open(source_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line)
                    # Support DPO format (prompt, chosen, rejected) or simple format
                    if 'prompt' in item:
                        self.prompts.append(item['prompt'])
                    elif 'instruction' in item and 'input' in item:
                        self.prompts.append(f"{item['instruction']}\n{item['input']}")
                except Exception:
                    continue

        # Load cache if exists
        if cache_file and os.path.exists(cache_file):
            console.print(f"[green]Loading cached teacher responses from {cache_file}[/green]")
            with open(cache_file, 'r', encoding='utf-8') as f:
                for line in f:
                    self.data.append(json.loads(line))
        else:
            console.print(f"[yellow]No cache found. Teacher will generate responses during initialization...[/yellow]")
            self._generate_dataset()

    def _generate_dataset(self):
        """Generate responses for all prompts"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.percentage:>3.0f}%"),
            TimeElapsedColumn()
        ) as progress:
            task = progress.add_task("[cyan]Generating Teacher Responses...", total=len(self.prompts))

            for prompt in self.prompts:
                # Skip if we already have enough data (optional limit)
                # if len(self.data) >= 1000: break

                response = self.teacher.generate(
                    prompt,
                    system_prompt="You are a helpful, empathetic, and wise AI assistant. Answer concisely."
                )

                if response:
                    entry = {"prompt": prompt, "response": response}
                    self.data.append(entry)

                    # Append to cache file immediately
                    if self.cache_file:
                        with open(self.cache_file, 'a', encoding='utf-8') as f:
                            f.write(json.dumps(entry) + "\n")

                progress.advance(task)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text = f"Human: {item['prompt']}\nAssistant: {item['response']}"

        enc = self.tokenizer(
            text,
            max_length=self.max_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )

        input_ids = enc['input_ids'].squeeze(0)
        labels = input_ids.clone()

        # Mask user part for loss calculation (optional, but good for chat)
        # Simple heuristic: mask until "Assistant:"
        # For now, we train on full sequence for stability in small models

        return {
            'input_ids': input_ids,
            'attention_mask': enc['attention_mask'].squeeze(0),
            'labels': labels
        }

def train_phase4():
    console.print(Panel.fit("[bold green]Phase 4: Ollama Distillation Training[/bold green]", border_style="green"))

    # Configuration
    config = B3HopeConfig()
    # Match checkpoint config
    config.d_model = 768
    config.n_heads = 12
    config.n_layers = 8
    config.num_experts = 8
    config.expert_dim = 2048
    config.active_experts = 2

    config.batch_size = 1 # Strict 1050 Ti constraint
    config.gradient_accumulation_steps = 8
    config.learning_rate = 5e-6 # Lower LR for fine-tuning
    config.num_epochs = 1 # 1 epoch of high quality distillation is usually enough

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    console.print(f"Device: [bold yellow]{device}[/bold yellow]")

    # Initialize Tokenizer
    tokenizer = AutoTokenizer.from_pretrained("gpt2") # B3 uses GPT2 tokenizer
    tokenizer.pad_token = tokenizer.eos_token

    # Initialize Teacher
    teacher = OllamaTeacher(model_name="llama3.2:3b") # Use available model

    # Prepare Dataset (Generate/Load BEFORE loading student model to save VRAM)
    console.print("[yellow]Preparing dataset first to optimize VRAM usage...[/yellow]")
    source_file = "src/training/data/datasets/dpo_phase3_dataset_with_logprobs.jsonl"
    cache_file = "src/training/data/datasets/phase4_distillation_cache.jsonl"

    dataset = DistillationDataset(source_file, tokenizer, teacher, cache_file=cache_file)
    dataloader = DataLoader(dataset, batch_size=config.batch_size, shuffle=True)

    # Load Student Model (Phase 3 Production) - Load AFTER dataset generation
    model_path = "F:/models/production/b3_hope_v1/impressioncore_b3_hope.pt"
    if not os.path.exists(model_path):
        console.print(f"[red]Model not found at {model_path}[/red]")
        return

    console.print(f"Loading student model from: {model_path}")
    checkpoint = torch.load(model_path, map_location=device)

    # Initialize model structure
    model = ImpressionCoreB3Hope(config).to(device)

    # Load weights
    # Handle state dict key mismatch if necessary (e.g. "module." prefix)
    state_dict = checkpoint['model_state_dict'] if 'model_state_dict' in checkpoint else checkpoint
    model.load_state_dict(state_dict, strict=False)
    console.print("[green]Student model loaded successfully[/green]")

    # Optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)

    # Training Loop
    model.train()
    total_steps = len(dataloader) * config.num_epochs

    console.print(f"Starting training: {len(dataset)} samples, {config.num_epochs} epochs")

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn()
    )

    with progress:
        task = progress.add_task("[cyan]Training...", total=total_steps)

        for epoch in range(config.num_epochs):
            for step, batch in enumerate(dataloader):
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)

                outputs = model(input_ids, attention_mask=attention_mask)

                # Calculate Loss (Standard Causal LM Loss)
                # Shift logits and labels
                shift_logits = outputs[:, :-1, :].contiguous()
                shift_labels = labels[:, 1:].contiguous()

                loss_fct = nn.CrossEntropyLoss()
                loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))

                loss = loss / config.gradient_accumulation_steps
                loss.backward()

                if (step + 1) % config.gradient_accumulation_steps == 0:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), config.max_grad_norm)
                    optimizer.step()
                    optimizer.zero_grad()
                    progress.advance(task)
                    progress.update(task, description=f"[cyan]Training... Loss: {loss.item() * config.gradient_accumulation_steps:.4f}")

            # Save Checkpoint per epoch
            save_path = f"F:/models/checkpoints/phase4_distillation/epoch_{epoch+1}.pt"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': loss.item(),
            }, save_path)
            console.print(f"[green]Saved checkpoint to {save_path}[/green]")

    console.print("[bold green]Phase 4 Training Complete![/bold green]")

if __name__ == "__main__":
    train_phase4()
