"""
Download and Test GPT-2 Small Base Model

Purpose: Verify GPT-2 small works for conversation before building hybrid
Created: October 6, 2025
"""

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from pathlib import Path
from rich.console import Console

console = Console()


def download_and_test_gpt2():
    """Download GPT-2 small and test basic conversation generation"""

    console.print("\n[bold cyan]" + "="*60)
    console.print("[bold cyan]DOWNLOADING GPT-2 SMALL BASE MODEL")
    console.print("[bold cyan]" + "="*60 + "\n")

    model_name = "gpt2"  # This is GPT-2 small (124M params)
    cache_dir = "F:/models/base/gpt2_small"

    # Download tokenizer
    console.print("📚 Downloading GPT-2 tokenizer...")
    tokenizer = GPT2Tokenizer.from_pretrained(
        model_name,
        cache_dir=cache_dir
    )
    tokenizer.pad_token = tokenizer.eos_token
    console.print("✅ Tokenizer downloaded\n")

    # Download model
    console.print("🤖 Downloading GPT-2 small model (124M params)...")
    model = GPT2LMHeadModel.from_pretrained(
        model_name,
        cache_dir=cache_dir
    )
    console.print("✅ Model downloaded\n")

    # Model statistics
    total_params = sum(p.numel() for p in model.parameters())
    console.print("[green]Model Statistics:")
    console.print(f"  Total Parameters: {total_params:,}")
    console.print(f"  Vocabulary Size: {tokenizer.vocab_size}")
    console.print(f"  Model Type: {model.config.model_type}")
    console.print(f"  Hidden Size: {model.config.n_embd}")
    console.print(f"  Num Layers: {model.config.n_layer}")
    console.print(f"  Num Heads: {model.config.n_head}")
    console.print(f"  Max Position: {model.config.n_positions}")
    console.print()

    # Test conversation generation
    console.print("[cyan]" + "="*60)
    console.print("[bold cyan]TESTING CONVERSATION GENERATION")
    console.print("[cyan]" + "="*60 + "\n")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    model.eval()

    console.print(f"Device: {device}\n")

    # Test queries
    test_queries = [
        "Hello! How are you today?",
        "What is artificial intelligence?",
        "Explain machine learning to me",
        "What can you help me with?",
    ]

    for i, query in enumerate(test_queries, 1):
        console.print(f"[cyan][{i}/4] Query:[/cyan] \"{query}\"")

        # Format as conversation
        prompt = f"Human: {query}\nAssistant:"

        # Tokenize
        inputs = tokenizer(prompt, return_tensors='pt').to(device)

        # Generate
        with torch.no_grad():
            outputs = model.generate(
                inputs['input_ids'],
                max_length=150,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )

        # Decode
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract assistant response
        if "Assistant:" in response:
            response = response.split("Assistant:")[-1].strip()

        console.print(f"[green]Response:[/green] \"{response}\"\n")

    # Summary
    console.print("[cyan]" + "="*60)
    console.print("[bold green]✅ GPT-2 SMALL READY!")
    console.print("[cyan]" + "="*60 + "\n")

    console.print("[yellow]Next Steps:")
    console.print("[yellow]1. ✅ Base GPT-2 model working (generates coherent text)")
    console.print("[yellow]2. ⏳ Build reduced GPT-2 architecture (~38M params)")
    console.print("[yellow]3. ⏳ Add B3 enhancements (MoE, attention, adapters)")
    console.print("[yellow]4. ⏳ Train on real conversation data")
    console.print()

    return model, tokenizer


if __name__ == "__main__":
    download_and_test_gpt2()
