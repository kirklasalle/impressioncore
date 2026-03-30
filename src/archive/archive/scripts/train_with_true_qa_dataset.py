"""
Train Path B model with true Q&A dataset (SQuAD + ELI5 + Conversation).

This script fine-tunes the Phase 1 checkpoint on mixed Q&A data to improve
relevance from 4.5/10 to target 7.5-8.5/10 while maintaining grammar 8.5-9.0/10.

Created: October 8, 2025
Author: Kirk LaSalle; GitHub Copilot
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.training.hybrid_gpt2_b3_model import create_hybrid_model
from transformers import AutoTokenizer

# Default configuration
DEFAULT_CHECKPOINT_PATH = Path("F:/models/checkpoints/b3/hybrid/best_epoch3_q9.2.pth")
DEFAULT_TRAIN_DATA_PATH = Path("F:/data/qa_datasets/mixed/mixed_train_formatted.json")
DEFAULT_VAL_DATA_PATH = Path("F:/data/qa_datasets/mixed/mixed_val_formatted.json")
DEFAULT_OUTPUT_DIR = Path("F:/models/checkpoints/b3/hybrid")

# Default hyperparameters
DEFAULT_BATCH_SIZE = 2  # Same as Phase 1
DEFAULT_LEARNING_RATE = 3e-5  # Same as relevance fix attempt
DEFAULT_EPOCHS = 3
DEFAULT_MAX_LENGTH = 512
DEFAULT_GRADIENT_ACCUMULATION_STEPS = 1


class QADataset(Dataset):
    """Dataset for Q&A pairs with context masking."""

    def __init__(self, data_path: Path, tokenizer, max_length: int = 512):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        example = self.data[idx]
        text = example['text']  # Already formatted as "Question: X\nAnswer: Y"

        # Tokenize
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].squeeze(0)
        attention_mask = encoding['attention_mask'].squeeze(0)

        # Context masking: Only train on answer portion
        # Find "Answer:" token position
        answer_token = "Answer:"
        answer_encoding = self.tokenizer.encode(answer_token, add_special_tokens=False)

        # Create labels (copy of input_ids)
        labels = input_ids.clone()

        # Find answer start position
        input_ids_list = input_ids.tolist()
        try:
            answer_start = -1
            for i in range(len(input_ids_list) - len(answer_encoding)):
                if input_ids_list[i:i+len(answer_encoding)] == answer_encoding:
                    answer_start = i + len(answer_encoding)
                    break

            # Mask everything before answer (don't train on question)
            if answer_start > 0:
                labels[:answer_start] = -100
        except Exception:
            pass  # If can't find answer marker, train on full text

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }


class QualityTester:
    """Test grammar and relevance quality."""

    def __init__(self, model, tokenizer, device):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device

        # Test queries (same as before for comparison)
        self.test_queries = [
            "Hello! How are you today?",
            "What is artificial intelligence?",
            "Explain machine learning to me",
            "What can you help me with?",
            "Tell me about yourself",
            "How does the weather affect mood?",
            "What's your favorite book?",
            "Can you write a short poem?"
        ]

        self.expected_types = [
            'greeting', 'definition', 'explanation', 'capabilities',
            'self-description', 'explanation', 'personal', 'creative'
        ]

    def generate_response(self, query: str, max_length: int = 100) -> str:
        """Generate response to query."""
        self.model.eval()

        prompt = f"Question: {query}\nAnswer:"
        inputs = self.tokenizer(prompt, return_tensors='pt').to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                inputs['input_ids'],
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract answer part
        if "Answer:" in response:
            response = response.split("Answer:")[-1].strip()

        return response

    def assess_grammar(self, text: str) -> float:
        """Assess grammar quality (0-10)."""
        score = 10.0
        words = text.split()

        # Length check
        if len(words) < 5:
            score -= 3
        elif len(words) > 50:
            score -= 1

        # Common words check
        common_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'of', 'in'}
        if not any(word.lower() in common_words for word in words):
            score -= 2

        # Structure check
        if not any(c in text for c in '.!?'):
            score -= 2

        # Repetition check
        if len(words) > 0 and len(set(words)) / len(words) < 0.5:
            score -= 2

        return max(0, min(10, score))

    def assess_relevance(self, query: str, response: str, expected_type: str) -> float:
        """Assess relevance to query (0-10)."""
        score = 0.0
        query_lower = query.lower()
        response_lower = response.lower()

        # Keyword overlap (2 points)
        query_words = set(query_lower.split())
        response_words = set(response_lower.split())
        overlap = len(query_words & response_words) / len(query_words) if query_words else 0
        score += overlap * 2

        # Expected type matching (3 points)
        if expected_type == 'definition' and any(word in response_lower for word in ['is', 'refers', 'means', 'type of']):
            score += 3
        elif expected_type == 'explanation' and any(word in response_lower for word in ['because', 'when', 'how', 'process']):
            score += 3
        elif expected_type == 'greeting' and any(word in response_lower for word in ['hello', 'hi', 'good', 'fine', 'well']):
            score += 3
        elif expected_type == 'capabilities' and any(word in response_lower for word in ['help', 'can', 'assist', 'answer']):
            score += 3

        # Off-topic detection (2 points)
        if not any(word in response_lower for word in ['uh', 'um', 'dunno', 'random', 'unrelated']):
            score += 2

        # Question pattern matching (3 points)
        if query_lower.startswith('what') and ('is' in response_lower or 'are' in response_lower):
            score += 3
        elif query_lower.startswith('explain') and len(response.split()) > 15:
            score += 3
        elif query_lower.startswith('how') and ('by' in response_lower or 'through' in response_lower):
            score += 3

        return min(10, score)

    def test_quality(self) -> Tuple[float, float, float]:
        """Test overall quality. Returns (grammar, relevance, combined)."""
        print("\n" + "=" * 70)
        print("🧪 TESTING QUALITY (Grammar + Relevance)")
        print("=" * 70)

        grammar_scores = []
        relevance_scores = []

        for i, (query, expected_type) in enumerate(zip(self.test_queries, self.expected_types), 1):
            response = self.generate_response(query)

            grammar = self.assess_grammar(response)
            relevance = self.assess_relevance(query, response, expected_type)
            combined = grammar * 0.4 + relevance * 0.6

            grammar_scores.append(grammar)
            relevance_scores.append(relevance)

            print(f"\nTest {i}/{len(self.test_queries)}:")
            print(f"Query:     {query}")
            print(f"Response:  {response[:80]}...")
            print(f"Grammar:   {grammar:.1f}/10.0")
            print(f"Relevance: {relevance:.1f}/10.0")
            print(f"Combined:  {combined:.1f}/10.0")

        avg_grammar = sum(grammar_scores) / len(grammar_scores)
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        avg_combined = avg_grammar * 0.4 + avg_relevance * 0.6

        print("\n" + "=" * 70)
        print("📊 AVERAGE SCORES:")
        print(f"   Grammar:   {avg_grammar:.2f}/10.0")
        print(f"   Relevance: {avg_relevance:.2f}/10.0")
        print(f"   Combined:  {avg_combined:.2f}/10.0 (40% grammar + 60% relevance)")
        print("=" * 70)

        return avg_grammar, avg_relevance, avg_combined


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for training configuration."""
    parser = argparse.ArgumentParser(
        description="Fine-tune the Phase 1 hybrid GPT-2 checkpoint on a mixed Q&A dataset."
    )
    parser.add_argument(
        "--checkpoint-path",
        type=Path,
        default=DEFAULT_CHECKPOINT_PATH,
        help="Path to the Phase 1 checkpoint to load for initialization."
    )
    parser.add_argument(
        "--train-data",
        type=Path,
        default=DEFAULT_TRAIN_DATA_PATH,
        help="Path to the training dataset JSON file."
    )
    parser.add_argument(
        "--val-data",
        type=Path,
        default=DEFAULT_VAL_DATA_PATH,
        help="Path to the validation dataset JSON file."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where improved checkpoints will be stored."
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=DEFAULT_EPOCHS,
        help="Number of training epochs to run (default: 3)."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Batch size for DataLoader (default: 2)."
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=DEFAULT_LEARNING_RATE,
        help="Learning rate for AdamW optimizer (default: 3e-5)."
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=DEFAULT_MAX_LENGTH,
        help="Maximum token length for tokenizer truncation (default: 512)."
    )
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        default=None,
        help="Force computation device. Defaults to CUDA when available."
    )
    parser.add_argument(
        "--gradient-accumulation",
        type=int,
        default=DEFAULT_GRADIENT_ACCUMULATION_STEPS,
        help="Number of gradient accumulation steps before optimizer updates (default: 1)."
    )
    return parser.parse_args()


def train_epoch(
    model,
    dataloader,
    optimizer,
    device,
    epoch: int,
    grad_accum_steps: int = DEFAULT_GRADIENT_ACCUMULATION_STEPS
) -> float:
    """Train one epoch."""
    model.train()
    total_loss = 0
    progress_bar = tqdm(dataloader, desc=f"Epoch {epoch}")

    for batch_idx, batch in enumerate(progress_bar):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )

        loss = outputs['loss']
        loss.backward()

        if (batch_idx + 1) % grad_accum_steps == 0:
            optimizer.step()
            optimizer.zero_grad()

        total_loss += loss.item()

        # Progress update every 1000 batches
        if (batch_idx + 1) % 1000 == 0:
            avg_loss = total_loss / (batch_idx + 1)
            print(f"   Batch {batch_idx + 1}/{len(dataloader)} | Avg Loss: {avg_loss:.4f}")

    # Handle leftover gradients when dataloader size is not divisible by accumulation steps
    if len(dataloader) % grad_accum_steps != 0:
        optimizer.step()
        optimizer.zero_grad()

    return total_loss / len(dataloader)


def validate(model, dataloader, device) -> float:
    """Validate model."""
    model.eval()
    total_loss = 0

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Validating"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )

            total_loss += outputs['loss'].item()

    return total_loss / len(dataloader)


def main():
    """Main training loop."""
    args = parse_args()
    device_str = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    device = torch.device(device_str)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    gradient_accumulation_steps = max(1, args.gradient_accumulation)

    print("=" * 70)
    print("PATH B OPTION A - TRUE Q&A DATASET TRAINING")
    print("=" * 70)

    print(f"\nDevice: {device}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch size: {args.batch_size}")
    print(f"Learning rate: {args.learning_rate}")
    if gradient_accumulation_steps > 1:
        print(f"Gradient accumulation steps: {gradient_accumulation_steps}")
    print(f"Max sequence length: {args.max_length}")
    print(f"Training data: {args.train_data}")
    print(f"Validation data: {args.val_data}")
    print(f"Checkpoint path: {args.checkpoint_path}")
    print(f"Output directory: {output_dir}")

    if not args.train_data.exists():
        raise FileNotFoundError(f"Training dataset not found at {args.train_data}")
    if not args.val_data.exists():
        raise FileNotFoundError(f"Validation dataset not found at {args.val_data}")
    if not args.checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint file not found at {args.checkpoint_path}")

    # Load tokenizer
    print("📥 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
    tokenizer.pad_token = tokenizer.eos_token
    print("   ✅ Tokenizer loaded")

    # Load datasets
    print("📥 Loading mixed Q&A datasets...")
    train_dataset = QADataset(args.train_data, tokenizer, args.max_length)
    val_dataset = QADataset(args.val_data, tokenizer, args.max_length)
    print(f"✅ Loaded {len(train_dataset)} training pairs")
    print(f"✅ Loaded {len(val_dataset)} validation pairs")

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size)

    # Load Phase 1 checkpoint
    print(f"\n📥 Loading Phase 1 checkpoint from {args.checkpoint_path}...")

    model, config = create_hybrid_model(
        use_moe=False,
        use_enhanced_attention=False,
        use_brain_adapters=False
    )

    checkpoint = torch.load(args.checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)

    print(f"   ✅ Loaded checkpoint (original quality: {checkpoint.get('best_quality', 'N/A')})")

    # Optimizer
    optimizer = AdamW(model.parameters(), lr=args.learning_rate)

    # Test before training
    print("\n🧪 Testing BEFORE training with true Q&A data...")
    tester = QualityTester(model, tokenizer, device)
    baseline_grammar, baseline_relevance, baseline_combined = tester.test_quality()

    # Training loop
    print("\n" + "=" * 70)
    print(f"🚀 STARTING TRAINING ({args.epochs} epochs)")
    print("=" * 70)

    best_relevance = baseline_relevance

    for epoch in range(1, args.epochs + 1):
        print(f"\n🔄 Epoch {epoch}/{args.epochs}")
        start_time = time.time()

        # Train
        train_loss = train_epoch(
            model,
            train_loader,
            optimizer,
            device,
            epoch,
            grad_accum_steps=gradient_accumulation_steps
        )

        # Validate
        val_loss = validate(model, val_loader, device)

        epoch_time = time.time() - start_time

        print(f"   ✅ Training Loss: {train_loss:.4f}")
        print(f"   ✅ Validation Loss: {val_loss:.4f}")
        print(f"   ⏱️  Time: {epoch_time/60:.1f} minutes")

        # Test quality
        grammar, relevance, combined = tester.test_quality()

        # Save if relevance improved
        if relevance > best_relevance:
            best_relevance = relevance
            checkpoint_path = output_dir / f"true_qa_epoch{epoch}_r{relevance:.1f}.pth"

            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_loss': train_loss,
                'val_loss': val_loss,
                'grammar': grammar,
                'relevance': relevance,
                'combined': combined,
                'best_relevance': best_relevance
            }, checkpoint_path)

            print(f"💾 Saved improved model: {checkpoint_path.name}")

    final_grammar = locals().get('grammar', baseline_grammar)
    final_relevance = locals().get('relevance', baseline_relevance)

    # Final results
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE")
    print("=" * 70)
    print(f"Before: Grammar {baseline_grammar:.1f}, Relevance {baseline_relevance:.1f}")
    print(f"After:  Grammar {final_grammar:.1f}, Relevance {final_relevance:.1f}")
    print(f"Improvement: Relevance +{final_relevance - baseline_relevance:.1f} points")
    print("=" * 70)


if __name__ == "__main__":
    main()
