"""
Fix Path B Relevance - Fine-tune with Q&A Format

Loads the best Phase 1 checkpoint and fine-tunes it with:
1. Reformatted Q&A dataset (Question: / Answer: format)
2. Context masking (only train on answer tokens)
3. Relevance-aware quality testing

This should fix the relevance issue while maintaining grammar quality.

Created: October 7, 2025
Expected: 2-3 epochs, 8-10 hours training time
"""

import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import time
from datetime import datetime

from transformers import GPT2Tokenizer
from src.training.hybrid_gpt2_b3_model import HybridGPT2B3Model


class QADataset(Dataset):
    """Dataset for Q&A pairs with context masking."""

    def __init__(self, data_path: str, tokenizer: GPT2Tokenizer, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Load Q&A pairs
        with open(data_path, 'r', encoding='utf-8') as f:
            self.qa_pairs = json.load(f)

        print(f"✅ Loaded {len(self.qa_pairs)} Q&A pairs from {data_path}")

    def __len__(self) -> int:
        return len(self.qa_pairs)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        qa = self.qa_pairs[idx]

        # Format: "Question: <question>\nAnswer: <answer>"
        # More explicit Q&A structure than "Context: / Response:"
        question_part = f"Question: {qa['question']}\nAnswer:"
        full_text = f"{question_part} {qa['answer']}"

        # Tokenize
        encoding = self.tokenizer(
            full_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].squeeze(0)
        attention_mask = encoding['attention_mask'].squeeze(0)

        # CRITICAL FIX: Mask question tokens in loss
        # Only train on answer tokens to force relevance
        labels = input_ids.clone()
        labels[attention_mask == 0] = -100  # Ignore padding

        # Find where answer starts
        question_encoding = self.tokenizer(
            question_part,
            add_special_tokens=False
        )
        question_length = len(question_encoding['input_ids'])

        # Mask question tokens - don't calculate loss on them
        labels[:question_length] = -100

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }


class RelevanceAwareQualityTester:
    """Tests both grammar AND relevance."""

    def __init__(self, model: HybridGPT2B3Model, tokenizer: GPT2Tokenizer):
        self.model = model
        self.tokenizer = tokenizer

        # Test queries with expected answer types
        self.test_queries = [
            ("Hello! How are you today?", "greeting"),
            ("What is artificial intelligence?", "definition"),
            ("Explain machine learning to me", "explanation"),
            ("What can you help me with?", "capabilities"),
            ("Tell me about yourself", "self-description"),
            ("How does the weather affect mood?", "explanation"),
            ("What's your favorite book?", "preference"),
            ("Can you write a short poem?", "creative")
        ]

    def test_quality(self, device: str = 'cuda') -> Tuple[float, float, List[str]]:
        """Test conversation quality with RELEVANCE checking."""
        self.model.eval()
        responses = []
        grammar_scores = []
        relevance_scores = []

        print("\n" + "=" * 70)
        print("🧪 TESTING QUALITY (Grammar + Relevance)")
        print("=" * 70)

        with torch.no_grad():
            for i, (query, expected_type) in enumerate(self.test_queries, 1):
                # Format with new Q&A style
                prompt = f"Question: {query}\nAnswer:"

                # Generate response
                input_ids = self.tokenizer.encode(prompt, return_tensors='pt').to(device)

                try:
                    output = self.model.generate(
                        input_ids,
                        max_length=150,
                        temperature=0.7,  # Slightly lower for more focused responses
                        do_sample=True,
                        top_p=0.9,
                        pad_token_id=self.tokenizer.eos_token_id
                    )

                    response = self.tokenizer.decode(output[0], skip_special_tokens=True)

                    # Extract only the answer part
                    if "Answer:" in response:
                        response = response.split("Answer:")[-1].strip()

                    responses.append(response)

                    # Quality assessment
                    grammar_score = self._assess_grammar(response)
                    relevance_score = self._assess_relevance(query, response, expected_type)

                    grammar_scores.append(grammar_score)
                    relevance_scores.append(relevance_score)

                    # Combined score (weighted: 40% grammar, 60% relevance)
                    combined = (grammar_score * 0.4) + (relevance_score * 0.6)

                    print(f"\nTest {i}/8:")
                    print(f"Query:     {query}")
                    print(f"Response:  {response[:80]}...")
                    print(f"Grammar:   {grammar_score:.1f}/10.0")
                    print(f"Relevance: {relevance_score:.1f}/10.0")
                    print(f"Combined:  {combined:.1f}/10.0")

                except Exception as e:
                    print(f"\n⚠️  Generation failed for query {i}: {e}")
                    responses.append("")
                    grammar_scores.append(0.0)
                    relevance_scores.append(0.0)

        avg_grammar = sum(grammar_scores) / len(grammar_scores) if grammar_scores else 0.0
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        avg_combined = (avg_grammar * 0.4) + (avg_relevance * 0.6)

        print("\n" + "=" * 70)
        print(f"📊 AVERAGE SCORES:")
        print(f"   Grammar:   {avg_grammar:.2f}/10.0")
        print(f"   Relevance: {avg_relevance:.2f}/10.0")
        print(f"   Combined:  {avg_combined:.2f}/10.0 (40% grammar + 60% relevance)")
        print("=" * 70)

        self.model.train()
        return avg_grammar, avg_relevance, responses

    def _assess_grammar(self, response: str) -> float:
        """Assess grammar quality (same as before)."""
        score = 0.0

        # Length check
        word_count = len(response.split())
        if 5 <= word_count <= 50:
            score += 2.0
        elif word_count > 0:
            score += 1.0

        # Has common words
        common_words = ['the', 'a', 'an', 'is', 'are', 'I', 'you', 'can', 'will']
        if any(word in response.lower() for word in common_words):
            score += 2.0

        # No repeated symbols
        if not any(char * 5 in response for char in "abcdefghijklmnopqrstuvwxyz:;.,!?"):
            score += 2.0

        # Has sentence structure
        if response and response[0].isupper() and any(p in response for p in '.!?'):
            score += 2.0

        # Coherence
        if len(response) > 10 and not response.isspace():
            score += 2.0

        return score

    def _assess_relevance(self, query: str, response: str, expected_type: str) -> float:
        """NEW: Assess if response is relevant to query."""
        score = 0.0
        query_lower = query.lower()
        response_lower = response.lower()

        # 1. Keyword overlap (2 points)
        query_words = set(w for w in query_lower.split() if len(w) > 3)
        response_words = set(w for w in response_lower.split() if len(w) > 3)
        overlap = len(query_words & response_words)
        if overlap > 0:
            score += min(overlap * 0.5, 2.0)

        # 2. Response type matching (3 points)
        if expected_type == "greeting":
            if any(w in response_lower for w in ["hello", "hi", "good", "fine", "well", "great", "thanks"]):
                score += 3.0

        elif expected_type == "definition":
            if any(w in response_lower for w in ["is", "means", "refers", "describes", "intelligence", "ai", "artificial"]):
                score += 3.0

        elif expected_type == "explanation":
            if any(w in response_lower for w in ["learn", "machine", "algorithm", "data", "model", "weather", "mood", "affect"]):
                score += 3.0

        elif expected_type == "capabilities":
            if any(w in response_lower for w in ["help", "assist", "can", "provide", "answer", "support"]):
                score += 3.0

        elif expected_type == "self-description":
            if any(w in response_lower for w in ["i am", "i'm", "my", "me", "assistant", "ai"]):
                score += 3.0

        elif expected_type == "preference":
            if any(w in response_lower for w in ["favorite", "like", "love", "prefer", "book", "enjoy"]):
                score += 3.0

        elif expected_type == "creative":
            if any(w in response_lower for w in ["poem", "rose", "sky", "heart", "love", "write"]):
                score += 3.0

        # 3. Not completely off-topic (2 points)
        # Response shouldn't be about random unrelated topics
        off_topic_indicators = [
            ("apartment" in response_lower and "apartment" not in query_lower),
            ("angry" in response_lower and "angry" not in query_lower and "feel" not in query_lower),
            ("dog" in response_lower and "dog" not in query_lower and "pet" not in query_lower)
        ]
        if not any(off_topic_indicators):
            score += 2.0

        # 4. Question pattern matching (3 points)
        if "what is" in query_lower or "what are" in query_lower:
            # Should have definition-like structure
            if " is " in response_lower or " are " in response_lower:
                score += 1.5

        if "how" in query_lower:
            # Should have explanation
            if any(w in response_lower for w in ["by", "through", "using", "can", "will"]):
                score += 1.5

        if "why" in query_lower:
            # Should have reasoning
            if any(w in response_lower for w in ["because", "since", "due", "reason"]):
                score += 1.5

        return min(score, 10.0)  # Cap at 10


def main():
    """Main fine-tuning pipeline"""

    print("=" * 70)
    print("PATH B RELEVANCE FIX - FINE-TUNING")
    print("=" * 70)
    print()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    # Load tokenizer
    print("📥 Loading tokenizer...")
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    tokenizer.pad_token = tokenizer.eos_token
    print("   ✅ Tokenizer loaded")

    # Load reformatted datasets
    print("📥 Loading reformatted Q&A datasets...")
    train_dataset = QADataset(
        "F:/data/conversations/hybrid_qa_train.json",
        tokenizer
    )
    val_dataset = QADataset(
        "F:/data/conversations/hybrid_qa_val.json",
        tokenizer
    )
    print()

    # Load best Phase 1 checkpoint
    print("📥 Loading Phase 1 checkpoint...")
    checkpoint_path = "F:/models/checkpoints/b3/hybrid/best_epoch3_q9.2.pth"
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)

    # Create model and load state dict (Phase 1 = no enhancements)
    from src.training.hybrid_gpt2_b3_model import create_hybrid_model
    model, config = create_hybrid_model(
        use_moe=False,  # Phase 1 has no MoE
        use_enhanced_attention=False,  # Phase 1 has no enhanced attention
        use_brain_adapters=False  # Phase 1 has no brain adapters
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    print(f"   ✅ Loaded: {checkpoint_path}")
    print(f"   ✅ Original quality: {checkpoint.get('best_quality', 'N/A')}")
    print()

    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=2, shuffle=False)

    # Optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-5)  # Lower LR for fine-tuning

    # Quality tester
    tester = RelevanceAwareQualityTester(model, tokenizer)

    # Test BEFORE fine-tuning
    print("🧪 Testing BEFORE fine-tuning...")
    grammar_before, relevance_before, _ = tester.test_quality(device)
    print()

    # Fine-tune for 2-3 epochs
    num_epochs = 3
    best_relevance = relevance_before

    print("=" * 70)
    print(f"🚀 STARTING FINE-TUNING ({num_epochs} epochs)")
    print("=" * 70)
    print()

    for epoch in range(1, num_epochs + 1):
        print(f"🔄 Epoch {epoch}/{num_epochs}")

        # Training
        model.train()
        total_loss = 0
        num_batches = 0

        for batch_idx, batch in enumerate(train_loader):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            # Forward pass
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )

            loss = outputs['loss']

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

            # Progress
            if (batch_idx + 1) % 1000 == 0:
                avg_loss = total_loss / num_batches
                print(f"   Batch {batch_idx + 1}/{len(train_loader)} | Avg Loss: {avg_loss:.4f}")

        avg_train_loss = total_loss / num_batches
        print(f"   ✅ Training Loss: {avg_train_loss:.4f}")

        # Validation
        model.eval()
        total_val_loss = 0
        num_val_batches = 0

        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)

                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )

                total_val_loss += outputs['loss'].item()
                num_val_batches += 1

        avg_val_loss = total_val_loss / num_val_batches
        print(f"   ✅ Validation Loss: {avg_val_loss:.4f}")
        print()

        # Quality test
        grammar, relevance, _ = tester.test_quality(device)
        combined = (grammar * 0.4) + (relevance * 0.6)

        # Save if relevance improved
        if relevance > best_relevance:
            best_relevance = relevance
            save_path = Path(f"F:/models/checkpoints/b3/hybrid/relevance_fixed_epoch{epoch}_r{relevance:.1f}.pth")
            save_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save({
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'epoch': epoch,
                'grammar': grammar,
                'relevance': relevance,
                'combined': combined,
                'train_loss': avg_train_loss,
                'val_loss': avg_val_loss
            }, save_path)
            print(f"💾 Saved improved model: {save_path.name}")

        print()

    print("=" * 70)
    print("✅ FINE-TUNING COMPLETE")
    print("=" * 70)
    print(f"Before: Grammar {grammar_before:.1f}, Relevance {relevance_before:.1f}")
    print(f"After:  Grammar {grammar:.1f}, Relevance {relevance:.1f}")
    print(f"Improvement: Relevance +{relevance - relevance_before:.1f} points")
    print("=" * 70)


if __name__ == "__main__":
    main()
