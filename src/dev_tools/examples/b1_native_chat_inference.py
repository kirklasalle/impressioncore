#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #gpu_optimization #inference #memory_management #multimodal #python #source_code #src/dev_tools/examples\b1_native_chat_inference.py #tokenization #training #transformer
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #cuda #gpu_optimization #inference #memory_management #multimodal #python #source_code #src\\dev_tools\\examples\\b1_native_chat_inference.py #tokenization #training #transformer
# Category:** Development Tools
# Status:** Active

"""
ImpressionCore B1 Distilled Model - Native Architecture Chat Inference

Uses the actual project model classes for proper inference.

File: b1_native_chat_inference.py
Created: 2025-06-29
Version: 1.0.0
"""

import sys
import time
from pathlib import Path

import torch
import torch.nn.functional as F
from rich.console import Console
from rich.panel import Panel

# Add project to path for imports
sys.path.append('.')

console = Console()

def load_native_model():
    """Load model using the actual project architecture"""
    try:
        console.print("[bold cyan]🤖 Loading B1 Model with Native Architecture...[/bold cyan]")

        # Import the actual model classes

        # Load the original model checkpoint (not the production one)
        original_model_path = Path("F:/impressioncore-b1-distillation-training/distilled_model_epoch_4_quality_12.30/model.pt")

        if not original_model_path.exists():
            console.print(f"[red]❌ Original model not found: {original_model_path}[/red]")
            return None, None

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        console.print(f"[blue]📱 Device: {device}[/blue]")

        # Load the checkpoint
        checkpoint = torch.load(original_model_path, map_location=device, weights_only=False)
        console.print(f"[green]✅ Checkpoint loaded ({len(checkpoint)} keys)[/green]")

        # Get the model from checkpoint
        if 'model' in checkpoint:
            model = checkpoint['model']
            console.print("[green]✅ Model extracted from checkpoint[/green]")
        else:
            console.print("[red]❌ No 'model' key in checkpoint[/red]")
            return None, None

        # Set to evaluation mode
        model.eval()
        model = model.to(device)

        # Load tokenizer
        try:
            from transformers import AutoTokenizer
            tokenizer_path = "src/models/production/impressioncore_b1_distilled_v12.30"
            tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
            console.print("[green]✅ Tokenizer loaded[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️ Tokenizer warning: {e}[/yellow]")
            tokenizer = None

        # Display model info
        if 'conversation_quality' in checkpoint:
            quality = checkpoint['conversation_quality']
            console.print(f"[yellow]⭐ Quality: {quality}/10.0[/yellow]")

        if 'teacher_model' in checkpoint:
            teacher = checkpoint['teacher_model']
            console.print(f"[blue]🎓 Teacher: {teacher}[/blue]")

        # Memory info
        if device.type == "cuda":
            memory_mb = torch.cuda.memory_allocated() / (1024 * 1024)
            console.print(f"[magenta]💾 GPU Memory: {memory_mb:.1f}MB[/magenta]")

        return model, tokenizer

    except Exception as e:
        console.print(f"[red]❌ Failed to load native model: {e}[/red]")
        return None, None

def simple_generate(model, tokenizer, prompt, max_length=50, temperature=0.8):
    """Simple text generation"""
    device = next(model.parameters()).device

    try:
        if tokenizer:
            # Use proper tokenizer
            inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=128)
            input_ids = inputs["input_ids"].to(device)
        else:
            # Fallback: simple encoding
            tokens = [ord(c) % 50257 for c in prompt[:50]]
            input_ids = torch.tensor([tokens], device=device)

        with torch.no_grad():
            # Get model output
            if hasattr(model, 'generate'):
                # Use built-in generate method if available
                output = model.generate(
                    input_ids,
                    max_length=input_ids.size(1) + max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id if tokenizer else 0
                )
                response_ids = output[0, input_ids.size(1):]
            else:
                # Manual generation
                generated = input_ids.clone()
                for _ in range(max_length):
                    outputs = model(generated)

                    # Handle different output formats
                    if isinstance(outputs, dict):
                        logits = outputs.get('logits', outputs.get('conversation_logits'))
                    elif isinstance(outputs, tuple):
                        logits = outputs[0]  # Assume first element is logits
                    else:
                        logits = outputs

                    if logits is None:
                        break

                    # Get next token
                    next_token_logits = logits[:, -1, :] / temperature
                    probs = F.softmax(next_token_logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)

                    generated = torch.cat([generated, next_token], dim=-1)

                    # Stop on EOS
                    if next_token.item() == (tokenizer.eos_token_id if tokenizer else 0):
                        break

                response_ids = generated[0, input_ids.size(1):]

        # Decode response
        if tokenizer:
            response = tokenizer.decode(response_ids, skip_special_tokens=True)
        else:
            # Simple decode
            response = ''.join([chr(min(max(32, tid % 127), 126)) for tid in response_ids.cpu().tolist()[:20]])

        return response.strip()

    except Exception as e:
        return f"Generation error: {e!s}"

def main():
    """Main chat interface"""
    try:
        # Load model
        model, tokenizer = load_native_model()

        if model is None:
            console.print("[red]❌ Failed to load model[/red]")
            return 1

        # Chat header
        header = Panel.fit(
            "[bold cyan]🤖 ImpressionCore B1 - Native Architecture Chat[/bold cyan]\n"
            "[green]Quality: 12.30/10.0 | Direct Model Access[/green]\n"
            f"[blue]Device: {next(model.parameters()).device}[/blue]\n"
            "[yellow]Type 'quit' to exit[/yellow]",
            style="bright_blue",
            border_style="bright_cyan"
        )
        console.print("\n")
        console.print(header)

        # Chat loop
        while True:
            try:
                user_input = console.input("\n[bold green]You:[/bold green] ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    break

                if not user_input:
                    continue

                console.print("[blue]B1 (generating...)⠋[/blue]", end="")

                start_time = time.time()
                response = simple_generate(model, tokenizer, user_input, max_length=30, temperature=0.7)
                generation_time = time.time() - start_time

                console.print(f"\r[blue]B1:[/blue] {response}")
                console.print(f"[dim]({generation_time:.2f}s)[/dim]")

            except KeyboardInterrupt:
                console.print("\n[yellow]Chat interrupted[/yellow]")
                break
            except Exception as e:
                console.print(f"\n[red]Chat error: {e}[/red]")
                continue

        console.print("\n[bold cyan]👋 Goodbye![/bold cyan]")
        return 0

    except Exception as e:
        console.print(f"\n[bold red]❌ Chat failed: {e}[/bold red]")
        return 1

if __name__ == "__main__":
    exit(main())
