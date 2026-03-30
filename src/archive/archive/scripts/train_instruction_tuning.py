"""
Instruction-Tuning Head Training Script
Created: October 10, 2025

Train only the instruction-tuning head while keeping GPT-2 base frozen.
This addresses the root cause of previous failures (training objective misalignment).

Previous Attempts:
- Attempt #1: Fine-tuned full model with synthetic explanatory data
  - Result: Relevance 3.5→2.2 (-1.3 points) ❌
- Attempt #2: Fine-tuned full model with real MS MARCO data
  - Result: Relevance 5.3→2.9 (-2.4 points) ❌❌
- Root Cause: Cross-entropy loss optimizes next token prediction, not answer relevance

New Approach (Option B):
- Freeze GPT-2 base completely (preserves grammar 9.0+)
- Train only instruction-tuning head (learns Q&A relationships)
- Explicit architecture for query understanding and answer relevance
- Expected: Grammar maintained, Relevance improved to 7.5-8.5

Target Quality:
- Grammar: >8.5/10.0 (maintained from frozen base)
- Relevance: >7.5/10.0 (improved via instruction head)
- Combined: >8.0/10.0 (40% grammar + 60% relevance)
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import GPT2Tokenizer
import json
import time
from pathlib import Path
from tqdm import tqdm
import os

from instruction_tuning_model import InstructionTunedGPT2, count_parameters


class InstructionDataset(Dataset):
    """Dataset for instruction-tuning with query-answer pairs"""

    def __init__(self, data_path: str, tokenizer: GPT2Tokenizer, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Load Q&A pairs
        print(f"📥 Loading dataset from {data_path}...")
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        print(f"✅ Loaded {len(self.data)} pairs")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        # Parse the text field which has format: "Question: ... Answer: ..."
        text_content = item['text']

        # Split on "Answer:" to separate question and answer
        if 'Answer:' in text_content:
            parts = text_content.split('Answer:', 1)
            question = parts[0].replace('Question:', '').strip()
            answer = parts[1].strip()
        else:
            # Fallback: use the whole text as question
            question = text_content
            answer = ""

        # Format as instruction-response pair
        # [INSTRUCTION] marks the query, [RESPONSE] marks the answer
        text = f"[INSTRUCTION] {question} [RESPONSE] {answer}"

        # Tokenize
        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].squeeze(0)
        attention_mask = encoding['attention_mask'].squeeze(0)

        # Create query mask (1 for question tokens, 0 for answer tokens)
        # This helps the model understand which part is query vs answer
        response_token = self.tokenizer.encode("[RESPONSE]", add_special_tokens=False)[0]
        query_mask = torch.ones_like(input_ids)

        # Find [RESPONSE] token position
        response_positions = (input_ids == response_token).nonzero(as_tuple=True)[0]
        if len(response_positions) > 0:
            response_pos = response_positions[0].item()
            query_mask[response_pos:] = 0  # Answer tokens marked as 0

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': input_ids.clone(),
            'query_mask': query_mask
        }


def test_quality(model, tokenizer, device):
    """
    Test model quality: grammar + relevance
    Same test queries as previous attempts for consistency
    """
    model.eval()

    test_queries = [
        "Hello! How are you today?",
        "What is artificial intelligence?",
        "Explain machine learning to me",
        "What can you help me with?",
        "Tell me about yourself",
        "How does the weather affect mood?",
        "What's your favorite book?",
        "Can you write a short poem?"
    ]

    print("\n" + "="*70)
    print("🧪 TESTING QUALITY (Grammar + Relevance)")
    print("="*70)

    grammar_scores = []
    relevance_scores = []

    with torch.no_grad():
        for i, query in enumerate(test_queries, 1):
            # Format as instruction
            input_text = f"[INSTRUCTION] {query} [RESPONSE]"
            input_ids = tokenizer.encode(input_text, return_tensors='pt').to(device)

            # Generate response
            output_ids = model.generate(
                input_ids=input_ids,
                max_length=100,
                temperature=0.8,
                top_p=0.9,
                do_sample=True
            )

            # Decode response
            output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

            # Extract only the response part (after [RESPONSE])
            if "[RESPONSE]" in output_text:
                response = output_text.split("[RESPONSE]")[1].strip()
            else:
                response = output_text

            # Truncate for display
            response_display = response[:100] + "..." if len(response) > 100 else response

            # Simple quality scoring (same as previous attempts)
            # Grammar: Check for basic sentence structure
            grammar = 9.0 if len(response.split()) > 3 and response[0].isupper() else 6.0

            # Relevance: Check if response relates to query keywords
            query_words = set(query.lower().split())
            response_words = set(response.lower().split())
            overlap = len(query_words & response_words)
            relevance = min(10.0, 2.0 + overlap * 1.5)

            grammar_scores.append(grammar)
            relevance_scores.append(relevance)

            combined = 0.4 * grammar + 0.6 * relevance

            print(f"\nTest {i}/{len(test_queries)}:")
            print(f"Query:     {query}")
            print(f"Response:  {response_display}")
            print(f"Grammar:   {grammar:.1f}/10.0")
            print(f"Relevance: {relevance:.1f}/10.0")
            print(f"Combined:  {combined:.1f}/10.0")

    avg_grammar = sum(grammar_scores) / len(grammar_scores)
    avg_relevance = sum(relevance_scores) / len(relevance_scores)
    avg_combined = 0.4 * avg_grammar + 0.6 * avg_relevance

    print("\n" + "="*70)
    print("📊 AVERAGE SCORES:")
    print(f"   Grammar:   {avg_grammar:.2f}/10.0")
    print(f"   Relevance: {avg_relevance:.2f}/10.0")
    print(f"   Combined:  {avg_combined:.2f}/10.0 (40% grammar + 60% relevance)")
    print("="*70)

    model.train()
    return avg_grammar, avg_relevance, avg_combined


def train_instruction_head():
    """
    Train instruction-tuning head on frozen GPT-2 base
    """
    print("\n" + "="*70)
    print("OPTION B - INSTRUCTION-TUNING HEAD TRAINING")
    print("="*70)
    print()

    # Configuration
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Paths
    base_checkpoint = "F:/models/checkpoints/b3/hybrid/best_epoch3_q9.2.pth"
    train_data = "F:/data/qa_datasets/mixed/mixed_train_formatted.json"
    val_data = "F:/data/qa_datasets/mixed/mixed_val_formatted.json"
    output_dir = Path("F:/models/checkpoints/b3/instruction_tuning")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Hyperparameters
    batch_size = 2  # Same as previous attempts
    learning_rate = 5e-4  # Higher LR since only training head
    num_epochs = 3
    max_length = 512

    # Load tokenizer
    print("📥 Loading tokenizer...")
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token
    print("   ✅ Tokenizer loaded")

    # Add special tokens for instruction format
    special_tokens = {"additional_special_tokens": ["[INSTRUCTION]", "[RESPONSE]"]}
    tokenizer.add_special_tokens(special_tokens)
    print("   ✅ Added instruction format tokens")

    # Load datasets
    train_dataset = InstructionDataset(train_data, tokenizer, max_length)
    val_dataset = InstructionDataset(val_data, tokenizer, max_length)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )

    print(f"\n📊 Dataset sizes:")
    print(f"   Training: {len(train_dataset)} pairs")
    print(f"   Validation: {len(val_dataset)} pairs")
    print(f"   Batches per epoch: {len(train_loader)}")

    # Create model with frozen base
    print(f"\n📥 Creating model with frozen GPT-2 base...")
    model = InstructionTunedGPT2(
        base_model_path=base_checkpoint,
        device=device,
        freeze_base=True  # Critical: freeze base to preserve grammar
    )

    # Resize embeddings for new tokens
    model.base_model.resize_token_embeddings(len(tokenizer))

    # Verify parameter counts
    param_info = count_parameters(model)
    print(f"\n📊 Parameter Summary:")
    print(f"   Total: {param_info['total']:,}")
    print(f"   Trainable: {param_info['trainable']:,} ({param_info['trainable_percent']:.1f}%)")
    print(f"   Frozen: {param_info['frozen']:,}")

    # Optimizer (only for trainable parameters)
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable_params, lr=learning_rate)

    print(f"\n⚙️ Training Configuration:")
    print(f"   Epochs: {num_epochs}")
    print(f"   Batch size: {batch_size}")
    print(f"   Learning rate: {learning_rate}")
    print(f"   Max length: {max_length}")
    print(f"   Optimizer: AdamW (trainable params only)")

    # Test BEFORE training
    print("\n🧪 Testing BEFORE training...")
    initial_grammar, initial_relevance, initial_combined = test_quality(
        model, tokenizer, device
    )

    # Training loop
    print("\n" + "="*70)
    print("🚀 STARTING TRAINING")
    print("="*70)

    best_relevance = initial_relevance
    best_combined = initial_combined

    for epoch in range(num_epochs):
        print(f"\n🔄 Epoch {epoch + 1}/{num_epochs}")
        epoch_start = time.time()

        # Training
        model.train()
        train_loss = 0.0
        train_batches = 0

        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch + 1}")

        for batch_idx, batch in enumerate(progress_bar):
            # Move to device
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            query_mask = batch['query_mask'].to(device)

            # Forward pass
            logits, loss = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels,
                query_mask=query_mask
            )

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            train_batches += 1

            # Update progress bar
            progress_bar.set_postfix({"loss": f"{loss.item():.4f}"})

            # Log every 1000 batches
            if (batch_idx + 1) % 1000 == 0:
                avg_loss = train_loss / train_batches
                print(f"\n  Batch {batch_idx + 1}/{len(train_loader)} | Avg Loss: {avg_loss:.4f}")

        avg_train_loss = train_loss / train_batches

        # Validation
        model.eval()
        val_loss = 0.0
        val_batches = 0

        with torch.no_grad():
            val_progress = tqdm(val_loader, desc="Validating")
            for batch in val_progress:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                query_mask = batch['query_mask'].to(device)

                logits, loss = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels,
                    query_mask=query_mask
                )

                val_loss += loss.item()
                val_batches += 1

        avg_val_loss = val_loss / val_batches

        epoch_time = (time.time() - epoch_start) / 60

        print(f"   ✅ Training Loss: {avg_train_loss:.4f}")
        print(f"   ✅ Validation Loss: {avg_val_loss:.4f}")
        print(f"   ⏱️  Time: {epoch_time:.1f} minutes")

        # Test quality after epoch
        grammar, relevance, combined = test_quality(model, tokenizer, device)

        # Save checkpoint if relevance improved
        if relevance > best_relevance:
            improvement = relevance - initial_relevance
            checkpoint_path = output_dir / f"best_instruction_head_r{relevance:.1f}.pth"
            model.save_checkpoint(
                path=str(checkpoint_path),
                epoch=epoch + 1,
                grammar_score=grammar,
                relevance_score=relevance
            )
            print(f"   ✅ NEW BEST! Relevance: {initial_relevance:.2f}→{relevance:.2f} (+{improvement:.2f})")
            best_relevance = relevance
            best_combined = combined

    # Final summary
    print("\n" + "="*70)
    print("✅ TRAINING COMPLETE")
    print("="*70)
    print(f"Before: Grammar {initial_grammar:.1f}, Relevance {initial_relevance:.1f}")
    print(f"After:  Grammar {grammar:.1f}, Relevance {relevance:.1f}")
    print(f"Improvement: Relevance {relevance - initial_relevance:+.1f} points")

    if relevance > 7.5 and grammar > 8.5:
        print("\n🎉 SUCCESS! Target quality achieved:")
        print(f"   ✅ Grammar: {grammar:.1f}/10.0 (target: >8.5)")
        print(f"   ✅ Relevance: {relevance:.1f}/10.0 (target: >7.5)")
        print(f"   ✅ Combined: {combined:.1f}/10.0 (target: >8.0)")
    elif relevance > initial_relevance:
        print("\n✅ IMPROVED! Relevance increased:")
        print(f"   Relevance: {initial_relevance:.1f}→{relevance:.1f} (+{relevance - initial_relevance:.1f})")
        print(f"   Note: Target was >7.5, consider additional training")
    else:
        print("\n⚠️ NO IMPROVEMENT: Relevance did not increase")
        print(f"   This suggests instruction-tuning head approach also has limitations")

    print("="*70)


if __name__ == "__main__":
    train_instruction_head()
