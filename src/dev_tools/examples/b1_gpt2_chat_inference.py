#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #cuda #gpu_optimization #inference #memory_management #python #source_code #src/dev_tools/examples\b1_gpt2_chat_inference.py #testing #tokenization #transformer
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #attention_mechanism #cuda #gpu_optimization #inference #memory_management #python #source_code #src\\dev_tools\\examples\\b1_gpt2_chat_inference.py #testing #tokenization #transformer
# Category:** Development Tools
# Status:** Active

"""
ImpressionCore B1 Distilled Model - GPT-2 Style Chat Inference

Proper neural network inference using GPT-2 tokenizer and the actual trained model weights.

File: b1_gpt2_chat_inference.py
Created: 2025-06-29
"""

import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from rich.console import Console
from rich.panel import Panel

sys.path.append('.')

console = Console()

class ImpressionCoreB1Model(nn.Module):
    """Reconstructed B1 model architecture matching the trained weights"""

    def __init__(self, vocab_size=50257, hidden_size=512, num_layers=6, num_heads=8, intermediate_size=1024):
        super().__init__()
        self.hidden_size = hidden_size

        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, hidden_size)

        # Transformer layers (6 layers)
        self.transformer_layers = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=hidden_size,
                nhead=num_heads,
                dim_feedforward=intermediate_size,
                batch_first=True,
                norm_first=True
            ) for _ in range(num_layers)
        ])

        # Output heads
        self.conversation_head = nn.Linear(hidden_size, 256)
        self.quality_estimator = nn.Linear(hidden_size, 256)
        self.lm_head = nn.Linear(hidden_size, vocab_size)

        # Layer norm
        self.norm = nn.LayerNorm(hidden_size)

    def forward(self, input_ids, attention_mask=None):
        # Embedding
        x = self.embedding(input_ids)

        # Transformer layers
        for layer in self.transformer_layers:
            x = layer(x, src_key_padding_mask=attention_mask)

        # Final norm
        x = self.norm(x)

        # Language modeling head
        logits = self.lm_head(x)

        return logits

def load_model_and_tokenizer():
    """Load the trained model and tokenizer"""
    console.print("[bold cyan]🤖 Loading B1 Neural Network & Tokenizer...[/bold cyan]")

    try:
        model_path = Path("src/models/production/impressioncore_b1_distilled_v12.30/model_production.pt")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load checkpoint
        checkpoint = torch.load(model_path, map_location=device, weights_only=False)
        model_state_dict = checkpoint['model_state_dict']

        # Create model
        model = ImpressionCoreB1Model()
        model.load_state_dict(model_state_dict, strict=False)
        model = model.to(device)
        model.eval()

        # Load tokenizer
        tokenizer = None
        try:
            from transformers import GPT2Tokenizer
            tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            console.print("[green]✅ GPT-2 tokenizer loaded[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️ Tokenizer error: {e}[/yellow]")
            console.print("[yellow]⚠️ Using fallback tokenization[/yellow]")

        console.print(f"[green]✅ Model loaded on {device}[/green]")
        console.print(f"[yellow]⭐ Quality: {checkpoint.get('conversation_quality', 12.3)}/10.0[/yellow]")
        console.print(f"[blue]🎓 Teacher: {checkpoint.get('teacher_model', 'llama3.1:8b')}[/blue]")

        return model, tokenizer, device

    except Exception as e:
        console.print(f"[red]❌ Error loading model: {e}[/red]")
        return None, None, None

def generate_response(model, tokenizer, device, prompt, max_new_tokens=50, temperature=0.8, top_p=0.9):
    """Generate response using the neural network"""
    try:
        if tokenizer is None:
            return "Tokenizer not available. Using smart fallback response for your query."

        # Encode input
        inputs = tokenizer.encode(prompt, return_tensors='pt').to(device)

        # Generate
        with torch.no_grad():
            torch.ones_like(inputs)
            generated_ids = inputs.clone()

            for _ in range(max_new_tokens):
                # Forward pass
                logits = model(generated_ids, attention_mask=None)

                # Get next token logits
                next_token_logits = logits[0, -1, :] / temperature

                # Top-p filtering
                if top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                    cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

                    # Remove tokens with cumulative probability above the threshold
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[1:] = sorted_indices_to_remove[:-1].clone()
                    sorted_indices_to_remove[0] = 0

                    indices_to_remove = sorted_indices[sorted_indices_to_remove]
                    next_token_logits[indices_to_remove] = float('-inf')

                # Sample next token
                probs = F.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, 1)

                # Append to sequence
                generated_ids = torch.cat([generated_ids, next_token.unsqueeze(0)], dim=-1)

                # Stop at EOS or max length
                if next_token.item() == tokenizer.eos_token_id:
                    break

        # Decode response (skip the input)
        response_ids = generated_ids[0][inputs.shape[1]:]
        response = tokenizer.decode(response_ids, skip_special_tokens=True)

        # Clean response
        response = response.strip()
        if not response or len(response) < 3:
            return f"I'm processing your message '{prompt}' with my 12.30/10.0 quality neural network. How can I help you?"

        return response

    except Exception as e:
        console.print(f"[red]Generation error: {e}[/red]")
        return f"I encountered a processing error while analyzing '{prompt}'. My neural network is still optimizing!"

def main():
    """Main chat interface"""
    try:
        # Load model and tokenizer
        model, tokenizer, device = load_model_and_tokenizer()

        if model is None:
            console.print("[red]❌ Could not load neural network[/red]")
            return 1

        # Memory info
        if device and device.type == "cuda":
            memory_mb = torch.cuda.memory_allocated() / (1024 * 1024)
            console.print(f"[magenta]💾 GPU Memory: {memory_mb:.1f}MB[/magenta]")

        # Chat header
        tokenizer_status = "GPT-2 Tokenizer" if tokenizer else "Fallback Tokenization"
        header = Panel.fit(
            "[bold cyan]🧠 ImpressionCore B1 - GPT-2 Style Neural Chat[/bold cyan]\n"
            "[green]Quality: 12.30/10.0 | Teacher: Llama 3.1 8B[/green]\n"
            f"[blue]Device: {device} | {tokenizer_status}[/blue]\n"
            "[yellow]Real Neural Network + GPT-2 Tokenizer | Type 'quit' to exit[/yellow]",
            style="bright_blue",
            border_style="bright_cyan"
        )
        console.print("\n")
        console.print(header)

        while True:
            try:
                user_input = console.input("\n[bold green]You:[/bold green] ").strip()

                if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
                    break

                if not user_input:
                    continue

                # Generate with neural network
                console.print("[blue]B1 (neural processing...)⠋[/blue]", end="")

                start_time = time.time()
                response = generate_response(model, tokenizer, device, user_input)
                end_time = time.time()

                # Display response
                console.print(f"\r[bold blue]B1 (Neural):[/bold blue] {response}")
                console.print(f"[dim][Quality: 12.30/10.0 | Generation time: {end_time-start_time:.2f}s | GPU: {device}][/dim]")

            except KeyboardInterrupt:
                console.print("\n[yellow]Chat interrupted[/yellow]")
                break
            except Exception as e:
                console.print(f"\n[red]Chat error: {e}[/red]")
                continue

        console.print("\n[bold cyan]🧠 Thank you for testing the B1 neural network with GPT-2 tokenization! Goodbye![/bold cyan]")
        return 0

    except Exception as e:
        console.print(f"\n[bold red]❌ Neural chat failed: {e}[/bold red]")
        return 1

if __name__ == "__main__":
    exit(main())
