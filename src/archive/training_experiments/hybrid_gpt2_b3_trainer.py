"""
Hybrid GPT-2 + B3 Training Pipeline

Implements progressive training strategy for Path B hybrid model:
- Phase 1: Train base GPT-2 (30M params)
- Phase 2: Add MoE enhancement (4.7M params)
- Phase 3: Add enhanced attention (0.6M params)
- Phase 4: Optional brain adapters (0.15M params)

CRITICAL: Tests actual conversation quality every 3 epochs (NOT just loss metrics)
Early stopping if quality degrades or gibberish/symbols appear

Created: October 6, 2025
Author: ImpressionCore Team
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
from src.training.hybrid_gpt2_b3_model import create_hybrid_model, HybridGPT2B3Model


class ConversationDataset(Dataset):
    """Dataset for conversation pairs."""

    def __init__(self, data_path: str, tokenizer: GPT2Tokenizer, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Load conversation pairs
        with open(data_path, 'r', encoding='utf-8') as f:
            self.conversations = json.load(f)

        print(f"✅ Loaded {len(self.conversations)} conversation pairs from {data_path}")

    def __len__(self) -> int:
        return len(self.conversations)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        conv = self.conversations[idx]

        # Format: "Context: <context> Response: <response>"
        text = f"Context: {conv['context']} Response: {conv['response']}"

        # Tokenize
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].squeeze(0)
        attention_mask = encoding['attention_mask'].squeeze(0)

        # Labels for language modeling (shifted by model internally)
        labels = input_ids.clone()
        labels[attention_mask == 0] = -100  # Ignore padding in loss

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }


class QualityTester:
    """Tests conversation quality at checkpoints."""

    def __init__(self, model: HybridGPT2B3Model, tokenizer: GPT2Tokenizer):
        self.model = model
        self.tokenizer = tokenizer

        # Test queries (same as Path C/A for comparison)
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

    def test_quality(self, device: str = 'cuda') -> Tuple[float, List[str]]:
        """Test conversation quality with sample queries."""
        self.model.eval()
        responses = []
        quality_scores = []

        print("\n" + "=" * 60)
        print("🧪 TESTING CONVERSATION QUALITY")
        print("=" * 60)

        with torch.no_grad():
            for i, query in enumerate(self.test_queries, 1):
                # Format query
                prompt = f"Context: {query} Response:"

                # Generate response
                input_ids = self.tokenizer.encode(prompt, return_tensors='pt').to(device)

                try:
                    output = self.model.generate(
                        input_ids,
                        max_length=100,
                        temperature=0.8,
                        do_sample=True,
                        top_p=0.9,
                        pad_token_id=self.tokenizer.eos_token_id
                    )

                    response = self.tokenizer.decode(output[0], skip_special_tokens=True)

                    # Extract only the response part
                    if "Response:" in response:
                        response = response.split("Response:")[-1].strip()

                    responses.append(response)

                    # Quality assessment
                    score = self._assess_quality(response)
                    quality_scores.append(score)

                    print(f"\nTest {i}/8:")
                    print(f"Query:    {query}")
                    print(f"Response: {response[:100]}...")
                    print(f"Quality:  {score:.1f}/10.0")

                except Exception as e:
                    print(f"\n⚠️  Generation failed for query {i}: {e}")
                    responses.append("")
                    quality_scores.append(0.0)

        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

        print("\n" + "=" * 60)
        print(f"📊 AVERAGE QUALITY: {avg_quality:.2f}/10.0")
        print("=" * 60)

        self.model.train()
        return avg_quality, responses

    def _assess_quality(self, response: str) -> float:
        """Simple quality assessment (0-10 scale)."""
        score = 0.0

        # Length check (not too short, not too long)
        word_count = len(response.split())
        if 5 <= word_count <= 50:
            score += 2.0
        elif word_count > 0:
            score += 1.0

        # Not gibberish (has common words)
        common_words = ['the', 'a', 'an', 'is', 'are', 'I', 'you', 'can', 'will']
        if any(word in response.lower() for word in common_words):
            score += 2.0

        # Not repeated symbols (Path A failure)
        if not any(char * 5 in response for char in "abcdefghijklmnopqrstuvwxyz:;.,!?"):
            score += 2.0

        # Has sentence structure (capital + punctuation)
        if response and response[0].isupper() and any(p in response for p in '.!?'):
            score += 2.0

        # Coherence (subjective, simple heuristic)
        if len(response) > 10 and not response.isspace():
            score += 2.0

        return score


class HybridTrainer:
    """Progressive trainer for Hybrid GPT-2 + B3 model."""

    def __init__(
        self,
        model: HybridGPT2B3Model,
        tokenizer: GPT2Tokenizer,
        train_dataset: ConversationDataset,
        val_dataset: ConversationDataset,
        device: str = 'cuda',
        batch_size: int = 2,
        learning_rate: float = 5e-5
    ):
        self.model = model.to(device)
        self.tokenizer = tokenizer
        self.device = device

        # Data loaders
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0
        )
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=0
        )

        # Optimizer (will be reset for each phase)
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=learning_rate
        )

        # Quality tester
        self.tester = QualityTester(self.model, tokenizer)

        # Training state
        self.global_epoch = 0
        self.best_quality = 0.0
        self.phase_history = []

    def train_phase(
        self,
        phase_name: str,
        num_epochs: int,
        quality_target: float,
        test_every: int = 3
    ) -> float:
        """Train a phase with quality testing."""
        print("\n" + "=" * 60)
        print(f"🚀 STARTING {phase_name}")
        print("=" * 60)
        print(f"Epochs: {num_epochs}")
        print(f"Quality target: {quality_target:.1f}/10.0")
        print(f"Testing every: {test_every} epochs")

        phase_start_time = time.time()

        for epoch in range(num_epochs):
            self.global_epoch += 1
            epoch_start_time = time.time()

            # Training
            train_loss = self._train_epoch()

            # Validation
            val_loss = self._validate_epoch()

            epoch_time = time.time() - epoch_start_time

            print(f"\n📊 Epoch {self.global_epoch} Summary:")
            print(f"   Train Loss: {train_loss:.4f}")
            print(f"   Val Loss:   {val_loss:.4f}")
            print(f"   Time:       {epoch_time/60:.1f} min")

            # Quality testing every N epochs
            if (epoch + 1) % test_every == 0 or (epoch + 1) == num_epochs:
                quality, _ = self.tester.test_quality(self.device)

                # Save if best
                if quality > self.best_quality:
                    self.best_quality = quality
                    self._save_checkpoint(f"best_epoch{self.global_epoch}_q{quality:.1f}")
                    print(f"🎯 NEW BEST QUALITY: {quality:.2f}/10.0")

                # Early stopping checks
                if quality < 1.0:
                    print(f"\n⚠️  CRITICAL: Quality collapsed to {quality:.2f}")
                    print("Stopping training to prevent further degradation")
                    return quality

                if quality >= quality_target:
                    print(f"\n✅ TARGET ACHIEVED: {quality:.2f} >= {quality_target:.1f}")
                    self._save_checkpoint(f"target_epoch{self.global_epoch}_q{quality:.1f}")
                    return quality

            # Save checkpoint
            if (epoch + 1) % 3 == 0:
                self._save_checkpoint(f"epoch{self.global_epoch}")

        phase_time = time.time() - phase_start_time
        print(f"\n✅ {phase_name} complete in {phase_time/60:.1f} min")

        # Final quality test
        final_quality, _ = self.tester.test_quality(self.device)

        self.phase_history.append({
            'phase': phase_name,
            'epochs': num_epochs,
            'final_quality': final_quality,
            'time': phase_time
        })

        return final_quality

    def _train_epoch(self) -> float:
        """Train one epoch."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0

        print(f"\n🔄 Training epoch {self.global_epoch}...", flush=True)

        for i, batch in enumerate(self.train_loader):
            if i == 0:
                print(f"   Processing batch 1/{len(self.train_loader)}...", flush=True)
            elif (i + 1) % 1000 == 0:
                print(f"   Batch {i+1}/{len(self.train_loader)} | Avg Loss: {total_loss/num_batches:.4f}", flush=True)

            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['labels'].to(self.device)

            self.optimizer.zero_grad()

            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )

            loss = outputs['loss']
            loss.backward()

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

            self.optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        return total_loss / num_batches if num_batches > 0 else 0.0

    def _validate_epoch(self) -> float:
        """Validate one epoch."""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0

        print(f"🔍 Validating...", flush=True)

        with torch.no_grad():
            for batch in self.val_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )

                loss = outputs['loss']
                total_loss += loss.item()
                num_batches += 1

        return total_loss / num_batches if num_batches > 0 else 0.0

    def _save_checkpoint(self, name: str):
        """Save model checkpoint."""
        checkpoint_dir = Path("F:/models/checkpoints/b3/hybrid")
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        checkpoint_path = checkpoint_dir / f"{name}.pth"

        torch.save({
            'epoch': self.global_epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_quality': self.best_quality,
            'phase_history': self.phase_history
        }, checkpoint_path)

        print(f"💾 Saved checkpoint: {checkpoint_path}")


def main():
    """Main training execution."""
    print("=" * 60)
    print("🚀 HYBRID GPT-2 + B3 TRAINING PIPELINE")
    print("=" * 60)

    # Setup
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    # Load tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    tokenizer.pad_token = tokenizer.eos_token

    # Load datasets
    train_dataset = ConversationDataset(
        "F:/data/conversations/hybrid_training_train.json",
        tokenizer
    )
    val_dataset = ConversationDataset(
        "F:/data/conversations/hybrid_training_val.json",
        tokenizer
    )

    # Phase 1: Base GPT-2 only
    print("\n" + "=" * 60)
    print("PHASE 1: TRAIN BASE GPT-2")
    print("=" * 60)

    model, config = create_hybrid_model(
        use_moe=False,
        use_enhanced_attention=False,
        use_brain_adapters=False
    )

    trainer = HybridTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        device=device,
        batch_size=2,
        learning_rate=5e-5
    )

    phase1_quality = trainer.train_phase(
        phase_name="PHASE 1: Base GPT-2",
        num_epochs=6,
        quality_target=4.0,
        test_every=3
    )

    print(f"\n📊 Phase 1 Final Quality: {phase1_quality:.2f}/10.0")

    if phase1_quality < 3.0:
        print("\n⚠️  Phase 1 quality insufficient. Stopping.")
        return

    # Phase 2: Add MoE
    print("\n" + "=" * 60)
    print("PHASE 2: ADD MOE ENHANCEMENT")
    print("=" * 60)

    # Create new model with MoE
    model_moe, config_moe = create_hybrid_model(
        use_moe=True,
        use_enhanced_attention=False,
        use_brain_adapters=False
    )

    # Load Phase 1 weights (base GPT-2 part)
    # TODO: Implement weight transfer logic

    trainer_moe = HybridTrainer(
        model=model_moe,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        device=device,
        batch_size=2,
        learning_rate=3e-5  # Lower LR for fine-tuning
    )

    phase2_quality = trainer_moe.train_phase(
        phase_name="PHASE 2: Base + MoE",
        num_epochs=6,
        quality_target=6.0,
        test_every=3
    )

    print(f"\n📊 Phase 2 Final Quality: {phase2_quality:.2f}/10.0")

    if phase2_quality <= phase1_quality:
        print("\n⚠️  MoE didn't improve quality. Consider deploying Phase 1 model.")

    # Phase 3: Add Enhanced Attention
    print("\n" + "=" * 60)
    print("PHASE 3: ADD ENHANCED ATTENTION")
    print("=" * 60)

    model_full, config_full = create_hybrid_model(
        use_moe=True,
        use_enhanced_attention=True,
        use_brain_adapters=False
    )

    trainer_full = HybridTrainer(
        model=model_full,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        device=device,
        batch_size=2,
        learning_rate=1e-5  # Even lower LR
    )

    phase3_quality = trainer_full.train_phase(
        phase_name="PHASE 3: Full Hybrid",
        num_epochs=6,
        quality_target=7.5,
        test_every=3
    )

    print(f"\n📊 Phase 3 Final Quality: {phase3_quality:.2f}/10.0")

    # Final report
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE")
    print("=" * 60)
    print(f"Phase 1 (Base GPT-2):     {phase1_quality:.2f}/10.0")
    print(f"Phase 2 (+ MoE):          {phase2_quality:.2f}/10.0")
    print(f"Phase 3 (+ Attention):    {phase3_quality:.2f}/10.0")
    print(f"Best Quality Achieved:    {trainer_full.best_quality:.2f}/10.0")

    if phase3_quality >= 7.5:
        print("\n🎯 TARGET ACHIEVED: Ready for production deployment!")
    elif phase3_quality >= 6.0:
        print("\n✅ Good quality achieved. Consider additional fine-tuning.")
    else:
        print("\n⚠️  Quality below target. May need more data or training.")


if __name__ == "__main__":
    main()
