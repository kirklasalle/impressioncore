"""
BrainSim-Enhanced Model Training Pipeline
Created: October 11, 2025

This training script implements the 4-phase training strategy for creating
truly intelligent AI through brain-inspired cognitive enhancement.

TRAINING PHILOSOPHY:
Option B taught us that relevance alone isn't intelligence. The model learned
"what" to talk about (9.12/10 relevance) but not "how" to think. This training
pipeline adds the missing cognitive layers that enable actual reasoning, memory,
attention, and personality.

4-PHASE TRAINING STRATEGY:
Phase 1: Cognitive Bootstrap (1 epoch)
  - Initialize working memory, reasoning, attention, personality
  - Keep instruction head frozen (preserve 9.12/10 relevance)
  - Focus: Get cognitive components working individually

Phase 2: Cognitive Integration (2 epochs)
  - Unfreeze instruction head, train all components together
  - Focus: Integrate cognition with answer generation
  - Develop natural conversation flow

Phase 3: Quality Refinement (1 epoch)
  - Fine-tune all components for naturalness
  - Focus: Polish grammar, strengthen personality, enhance reasoning

Phase 4: Final Validation
  - Comprehensive intelligence testing
  - Compare with Phase 1 and Option B baselines
  - Deploy if targets met

QUALITY METRICS:
- Grammar: Fluency, naturalness, coherence (target >8.5)
- Relevance: Answer accuracy and topical fit (target >9.0, maintain Option B)
- Intelligence: Reasoning + Memory + Personality (target >9.0, NEW)
- Combined: Weighted average (target >9.0)

INTELLIGENCE EVALUATION:
- Reasoning: Can explain cause-effect, solve multi-step problems
- Memory: Remembers context, maintains topic continuity
- Personality: Consistent style, natural expression, appropriate tone
- Coherence: Logical flow, no repetition, thoughtful responses
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import GPT2Tokenizer
import json
import os
from typing import Dict, List, Tuple
import time
from datetime import datetime

from brain_instruction_model import BrainEnhancedGPT2


class InstructionDataset(Dataset):
    """Dataset for instruction-tuning with Q&A pairs."""

    def __init__(self, data_path: str, tokenizer: GPT2Tokenizer, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Load data
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        # Parse text field (format: "Question: ... Answer: ...")
        text_content = item['text']
        if 'Answer:' in text_content:
            parts = text_content.split('Answer:', 1)
            question = parts[0].replace('Question:', '').strip()
            answer = parts[1].strip()
        else:
            question = text_content
            answer = ""

        # Format with plain text markers (no special tokens)
        text = f"Question: {question}\n\nAnswer: {answer}"

        # Tokenize
        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].squeeze()
        attention_mask = encoding['attention_mask'].squeeze()

        # Create labels - mask padding tokens with -100 (ignore index)
        labels = input_ids.clone()
        labels[attention_mask == 0] = -100

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }


def score_grammar(text: str) -> float:
    """Score text grammar and fluency (0-10)."""
    score = 10.0

    # Check for repetition
    words = text.split()
    if len(words) > 5:
        # Count repeated words
        word_counts = {}
        for word in words:
            word_lower = word.lower()
            if len(word_lower) > 3:  # Only count substantial words
                word_counts[word_lower] = word_counts.get(word_lower, 0) + 1

        # Penalize excessive repetition
        max_repetitions = max(word_counts.values()) if word_counts else 1
        if max_repetitions > 3:
            score -= min(4.0, (max_repetitions - 3) * 1.0)

    # Check for completeness
    if len(text.strip()) < 10:
        score -= 3.0

    # Check for nonsense patterns (repeated characters)
    if any(char * 5 in text for char in 'abcdefghijklmnopqrstuvwxyz'):
        score -= 3.0

    # Check for proper sentence structure
    if not any(text.strip().endswith(p) for p in ['.', '!', '?', ':', ';']):
        score -= 1.0

    return max(0.0, min(10.0, score))


def score_relevance(query: str, response: str) -> float:
    """Score answer relevance to query (0-10)."""
    score = 10.0

    # Extract key terms from query
    query_words = set(query.lower().split())
    response_words = set(response.lower().split())

    # Check if response echoes query
    if query.lower() in response.lower():
        # Good: response addresses the query
        pass
    else:
        # Check for keyword overlap
        common_words = query_words & response_words
        if len(common_words) < len(query_words) * 0.3:
            score -= 2.0

    # Check if response is too short
    if len(response.split()) < 5:
        score -= 2.0

    # Check if response is just repeating query
    if response.strip().startswith(query.strip()):
        if len(response.split()) < len(query.split()) + 3:
            score -= 1.0

    return max(0.0, min(10.0, score))


def score_intelligence(query: str, response: str) -> Dict[str, float]:
    """
    Score intelligence dimensions (0-10 each).

    Returns:
        reasoning: Multi-step thinking, cause-effect, logical flow
        memory: Context awareness, topic continuity
        personality: Consistent style, natural expression
        coherence: Logical structure, no repetition, thoughtfulness
        overall: Average of all dimensions
    """
    scores = {}

    # REASONING: Does it explain or just state?
    reasoning_score = 5.0  # Baseline
    if any(word in response.lower() for word in ['because', 'therefore', 'thus', 'since', 'as a result']):
        reasoning_score += 2.0  # Shows causal thinking
    if any(word in response.lower() for word in ['first', 'second', 'then', 'next', 'finally']):
        reasoning_score += 1.5  # Shows sequential thinking
    if any(word in response.lower() for word in ['for example', 'such as', 'like', 'including']):
        reasoning_score += 1.5  # Shows elaboration
    if len(response.split('.')) > 2:
        reasoning_score += 1.0  # Multi-sentence (more complex)
    scores['reasoning'] = min(10.0, reasoning_score)

    # MEMORY: Does it stay on topic?
    memory_score = 8.0  # Baseline (assume good unless problems)
    query_words = set(query.lower().split())
    response_words = set(response.lower().split())
    topic_overlap = len(query_words & response_words) / max(len(query_words), 1)
    if topic_overlap < 0.2:
        memory_score -= 3.0  # Lost the topic
    scores['memory'] = max(0.0, memory_score)

    # PERSONALITY: Natural and consistent?
    personality_score = 7.0  # Baseline
    if any(word in response.lower() for word in ['i think', 'i believe', 'in my opinion', 'i would say']):
        personality_score += 1.5  # Shows personality
    if any(word in response.lower() for word in ['interesting', 'important', 'fascinating', 'wonderful']):
        personality_score += 1.0  # Shows engagement
    if response.count('?') > 0:
        personality_score += 0.5  # Asks questions (interactive)
    scores['personality'] = min(10.0, personality_score)

    # COHERENCE: Logical and well-structured?
    coherence_score = 8.0  # Baseline
    words = response.split()
    if len(words) > 5:
        # Check for excessive repetition (hurts coherence)
        word_counts = {}
        for word in words:
            word_lower = word.lower()
            if len(word_lower) > 3:
                word_counts[word_lower] = word_counts.get(word_lower, 0) + 1
        max_reps = max(word_counts.values()) if word_counts else 1
        if max_reps > 3:
            coherence_score -= min(5.0, (max_reps - 3) * 1.5)

    # Check for logical flow (conjunctions)
    if any(word in response.lower() for word in ['and', 'but', 'however', 'although', 'while']):
        coherence_score += 1.0

    scores['coherence'] = max(0.0, min(10.0, coherence_score))

    # OVERALL: Average of all dimensions
    scores['overall'] = sum(scores.values()) / len(scores)

    return scores


def test_comprehensive_quality(
    model: BrainEnhancedGPT2,
    tokenizer: GPT2Tokenizer,
    device: torch.device,
    phase_name: str = "BASELINE"
) -> Dict[str, float]:
    """
    Comprehensive quality testing with intelligence evaluation.

    Returns averages across all test queries.
    """
    model.eval()

    # Diverse test queries covering different cognitive demands
    test_queries = [
        # Simple greeting (tests personality)
        "Hello! How are you today?",

        # Factual question (tests knowledge retrieval)
        "What is artificial intelligence?",

        # Explanation request (tests reasoning)
        "Explain machine learning to me",

        # Open-ended question (tests creativity)
        "What can you help me with?",

        # Self-reflection (tests personality + memory)
        "Tell me about yourself",

        # Complex reasoning (tests multi-step thinking)
        "How does the weather affect mood?",

        # Personal preference (tests personality)
        "What's your favorite book?",

        # Creative task (tests generation + personality)
        "Can you write a short poem?"
    ]

    print("\n" + "="*70)
    print(f"🧪 COMPREHENSIVE QUALITY TEST - {phase_name}")
    print("="*70 + "\n")

    all_scores = {
        'grammar': [],
        'relevance': [],
        'reasoning': [],
        'memory': [],
        'personality': [],
        'coherence': [],
        'intelligence_overall': [],
        'combined': []
    }

    for i, query in enumerate(test_queries, 1):
        # Generate response using plain text format
        input_text = f"Question: {query}\n\nAnswer:"
        input_ids = tokenizer.encode(input_text, return_tensors='pt', truncation=True, max_length=50).to(device)

        # Ensure input doesn't exceed safe limits
        if input_ids.size(1) > 100:
            input_ids = input_ids[:, :100]

        with torch.no_grad():
            output_ids = model.generate(
                input_ids,
                max_length=200,  # Total length including input
                temperature=0.8,
                top_p=0.9,
                do_sample=True
            )

        full_response = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        # Extract answer after "Answer:"
        if "Answer:" in full_response:
            response = full_response.split("Answer:")[-1].strip()
        else:
            response = full_response.strip()

        # Score grammar and relevance
        grammar = score_grammar(response)
        relevance = score_relevance(query, response)

        # Score intelligence dimensions
        intelligence = score_intelligence(query, response)

        # Combined score (weighted: 30% grammar, 40% relevance, 30% intelligence)
        combined = (grammar * 0.3) + (relevance * 0.4) + (intelligence['overall'] * 0.3)

        # Store scores
        all_scores['grammar'].append(grammar)
        all_scores['relevance'].append(relevance)
        all_scores['reasoning'].append(intelligence['reasoning'])
        all_scores['memory'].append(intelligence['memory'])
        all_scores['personality'].append(intelligence['personality'])
        all_scores['coherence'].append(intelligence['coherence'])
        all_scores['intelligence_overall'].append(intelligence['overall'])
        all_scores['combined'].append(combined)

        # Display result
        print(f"Test {i}/{len(test_queries)}:")
        print(f"Query:      {query}")
        print(f"Response:   {response[:100]}{'...' if len(response) > 100 else ''}")
        print(f"Grammar:    {grammar:.1f}/10.0")
        print(f"Relevance:  {relevance:.1f}/10.0")
        print(f"Intelligence: {intelligence['overall']:.1f}/10.0")
        print(f"  - Reasoning:    {intelligence['reasoning']:.1f}/10.0")
        print(f"  - Memory:       {intelligence['memory']:.1f}/10.0")
        print(f"  - Personality:  {intelligence['personality']:.1f}/10.0")
        print(f"  - Coherence:    {intelligence['coherence']:.1f}/10.0")
        print(f"Combined:   {combined:.1f}/10.0\n")

    # Calculate averages
    averages = {key: sum(values) / len(values) for key, values in all_scores.items()}

    # Display summary
    print("="*70)
    print("📊 AVERAGE SCORES:")
    print(f"   Grammar:      {averages['grammar']:.2f}/10.0")
    print(f"   Relevance:    {averages['relevance']:.2f}/10.0")
    print(f"   Intelligence: {averages['intelligence_overall']:.2f}/10.0")
    print(f"     - Reasoning:    {averages['reasoning']:.2f}/10.0")
    print(f"     - Memory:       {averages['memory']:.2f}/10.0")
    print(f"     - Personality:  {averages['personality']:.2f}/10.0")
    print(f"     - Coherence:    {averages['coherence']:.2f}/10.0")
    print(f"   Combined:     {averages['combined']:.2f}/10.0")
    print("   (30% grammar + 40% relevance + 30% intelligence)")
    print("="*70 + "\n")

    return averages


def train_brain_enhanced():
    """Main training function for BrainSim-enhanced model."""

    # Enable CUDA error debugging
    import os
    os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

    print("\n" + "="*70)
    print("OPTION C-1: FULL BRAINSIM-ENHANCED TRAINING")
    print("="*70 + "\n")

    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}\n")

    # Load tokenizer
    print("📥 Loading tokenizer...")
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    tokenizer.pad_token = tokenizer.eos_token
    print("   ✅ Tokenizer loaded\n")

    # Load datasets
    train_path = "F:/data/qa_datasets/mixed/mixed_train_formatted.json"
    val_path = "F:/data/qa_datasets/mixed/mixed_val_formatted.json"

    print(f"📥 Loading training data: {train_path}")
    train_dataset = InstructionDataset(train_path, tokenizer)
    print(f"   ✅ Loaded {len(train_dataset)} training pairs\n")

    print(f"📥 Loading validation data: {val_path}")
    val_dataset = InstructionDataset(val_path, tokenizer)
    print(f"   ✅ Loaded {len(val_dataset)} validation pairs\n")

    train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=2, shuffle=False)

    print(f"📊 Dataset sizes:")
    print(f"   Training: {len(train_dataset)} pairs")
    print(f"   Validation: {len(val_dataset)} pairs")
    print(f"   Batches per epoch: {len(train_loader)}\n")

    # Create model
    checkpoint_path = "F:/models/checkpoints/b3/hybrid/best_epoch3_q9.2.pth"
    print("📥 Creating BrainSim-enhanced model...")
    model = BrainEnhancedGPT2(checkpoint_path, freeze_base=True).to(device)

    # Display parameter breakdown
    params = model.count_parameters()
    print("\n" + "="*70)
    print("BRAINSIM-ENHANCED GPT-2 MODEL PARAMETERS")
    print("="*70)
    print(f"Total Parameters: {params['total']:,}")
    print(f"  Frozen (GPT-2 Base): {params['frozen']:,}")
    print(f"  Trainable (BrainSim + Instruction): {params['trainable']:,}")
    print(f"  Training: {params['trainable_pct']:.1f}% of model")
    print("="*70 + "\n")

    # Training configuration
    num_epochs = 4  # Phase 1 (1) + Phase 2 (2) + Phase 3 (1)
    learning_rate = 5e-5  # Lower than Option B for stability

    print("⚙️ Training Configuration:")
    print(f"   Epochs: {num_epochs} (1 bootstrap + 2 integration + 1 refinement)")
    print(f"   Batch size: 2")
    print(f"   Learning rate: {learning_rate}")
    print(f"   Max length: 512")
    print(f"   Optimizer: AdamW\n")

    # Baseline test BEFORE training
    print("🧪 Testing BEFORE training...")
    baseline_scores = test_comprehensive_quality(model, tokenizer, device, "BEFORE TRAINING")

    # 4-PHASE TRAINING
    best_combined_score = baseline_scores['combined']
    best_checkpoint = None

    # Phase 1: Cognitive Bootstrap
    print("\n" + "="*70)
    print("🚀 PHASE 1: COGNITIVE BOOTSTRAP (1 epoch)")
    print("   Goal: Initialize cognitive components")
    print("   Training: BrainSim layer only (instruction head frozen)")
    print("="*70 + "\n")

    # Freeze instruction head for Phase 1
    for param in model.instruction_head.parameters():
        param.requires_grad = False

    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=learning_rate
    )

    # Train Phase 1
    train_phase(model, train_loader, val_loader, optimizer, device, 1, "Phase 1")
    phase1_scores = test_comprehensive_quality(model, tokenizer, device, "PHASE 1 COMPLETE")

    if phase1_scores['combined'] > best_combined_score:
        best_combined_score = phase1_scores['combined']
        best_checkpoint = {
            'phase': 1,
            'model_state_dict': model.state_dict(),
            'scores': phase1_scores
        }

    # Phase 2: Cognitive Integration
    print("\n" + "="*70)
    print("🚀 PHASE 2: COGNITIVE INTEGRATION (2 epochs)")
    print("   Goal: Integrate all cognitive components")
    print("   Training: BrainSim + Instruction head (all trainable)")
    print("="*70 + "\n")

    # Unfreeze instruction head
    for param in model.instruction_head.parameters():
        param.requires_grad = True

    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=learning_rate
    )

    # Train Phase 2 (2 epochs)
    for epoch in range(2):
        train_phase(model, train_loader, val_loader, optimizer, device, epoch + 1, f"Phase 2 Epoch {epoch+1}")
        phase2_scores = test_comprehensive_quality(model, tokenizer, device, f"PHASE 2 EPOCH {epoch+1} COMPLETE")

        if phase2_scores['combined'] > best_combined_score:
            best_combined_score = phase2_scores['combined']
            best_checkpoint = {
                'phase': 2,
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'scores': phase2_scores
            }

    # Phase 3: Quality Refinement
    print("\n" + "="*70)
    print("🚀 PHASE 3: QUALITY REFINEMENT (1 epoch)")
    print("   Goal: Polish conversation quality")
    print("   Training: All components with fine-tuning focus")
    print("="*70 + "\n")

    # Lower learning rate for refinement
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=learning_rate * 0.5
    )

    train_phase(model, train_loader, val_loader, optimizer, device, 1, "Phase 3")
    phase3_scores = test_comprehensive_quality(model, tokenizer, device, "PHASE 3 COMPLETE")

    if phase3_scores['combined'] > best_combined_score:
        best_combined_score = phase3_scores['combined']
        best_checkpoint = {
            'phase': 3,
            'model_state_dict': model.state_dict(),
            'scores': phase3_scores
        }

    # Final Summary
    print("\n" + "="*70)
    print("✅ TRAINING COMPLETE - FINAL SUMMARY")
    print("="*70 + "\n")

    print("SCORE PROGRESSION:")
    print(f"Baseline:  Combined {baseline_scores['combined']:.2f} (Grammar {baseline_scores['grammar']:.2f}, Relevance {baseline_scores['relevance']:.2f}, Intelligence {baseline_scores['intelligence_overall']:.2f})")
    print(f"Phase 1:   Combined {phase1_scores['combined']:.2f} (Grammar {phase1_scores['grammar']:.2f}, Relevance {phase1_scores['relevance']:.2f}, Intelligence {phase1_scores['intelligence_overall']:.2f})")
    print(f"Phase 2:   Combined {phase2_scores['combined']:.2f} (Grammar {phase2_scores['grammar']:.2f}, Relevance {phase2_scores['relevance']:.2f}, Intelligence {phase2_scores['intelligence_overall']:.2f})")
    print(f"Phase 3:   Combined {phase3_scores['combined']:.2f} (Grammar {phase3_scores['grammar']:.2f}, Relevance {phase3_scores['relevance']:.2f}, Intelligence {phase3_scores['intelligence_overall']:.2f})\n")

    print(f"BEST CHECKPOINT: Phase {best_checkpoint['phase']}")
    best_scores = best_checkpoint['scores']
    print(f"   Combined: {best_scores['combined']:.2f}/10.0")
    print(f"   Grammar: {best_scores['grammar']:.2f}/10.0")
    print(f"   Relevance: {best_scores['relevance']:.2f}/10.0")
    print(f"   Intelligence: {best_scores['intelligence_overall']:.2f}/10.0\n")

    # Save best checkpoint
    if best_checkpoint:
        save_path = "F:/models/checkpoints/b3/brain_enhanced/best_brainsim.pth"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        torch.save(best_checkpoint, save_path)
        print(f"💾 Saved best checkpoint to: {save_path}\n")

    # Target evaluation
    targets_met = (
        best_scores['grammar'] >= 8.5 and
        best_scores['relevance'] >= 9.0 and
        best_scores['intelligence_overall'] >= 9.0 and
        best_scores['combined'] >= 9.0
    )

    if targets_met:
        print("🎉 ALL TARGETS MET! Model ready for deployment.")
    else:
        print("⚠️  Some targets not met. Consider additional training or adjustments.")
        if best_scores['grammar'] < 8.5:
            print(f"   - Grammar: {best_scores['grammar']:.2f}/10.0 (target 8.5)")
        if best_scores['relevance'] < 9.0:
            print(f"   - Relevance: {best_scores['relevance']:.2f}/10.0 (target 9.0)")
        if best_scores['intelligence_overall'] < 9.0:
            print(f"   - Intelligence: {best_scores['intelligence_overall']:.2f}/10.0 (target 9.0)")
        if best_scores['combined'] < 9.0:
            print(f"   - Combined: {best_scores['combined']:.2f}/10.0 (target 9.0)")

    print("\n" + "="*70)


def train_phase(
    model: BrainEnhancedGPT2,
    train_loader: DataLoader,
    val_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    num_epochs: int,
    phase_name: str
):
    """Train for one or more epochs."""
    model.train()

    for epoch in range(num_epochs):
        epoch_loss = 0
        batch_count = 0

        print(f"🔄 {phase_name} - Epoch {epoch+1}/{num_epochs}")

        for batch_idx, batch in enumerate(train_loader):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            # Debug: Check for invalid labels on first batch
            if batch_idx == 0:
                vocab_size = 50257  # GPT-2 vocab size
                invalid_labels = labels[(labels >= vocab_size) & (labels != -100)]
                if len(invalid_labels) > 0:
                    print(f"⚠️ WARNING: Found {len(invalid_labels)} invalid labels >= {vocab_size}")
                    print(f"   Invalid values: {invalid_labels[:10].tolist()}")
                    # Clamp invalid labels to -100
                    labels = torch.where((labels >= vocab_size) | (labels < -100),
                                        torch.tensor(-100, device=device), labels)

            optimizer.zero_grad()

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )

            loss = outputs['loss']
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            batch_count += 1

            if (batch_idx + 1) % 1000 == 0:
                avg_loss = epoch_loss / batch_count
                print(f"  Batch {batch_idx+1}/{len(train_loader)} | Avg Loss: {avg_loss:.4f}")

        avg_train_loss = epoch_loss / batch_count

        # Validation
        model.eval()
        val_loss = 0
        val_count = 0

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

                val_loss += outputs['loss'].item()
                val_count += 1

        avg_val_loss = val_loss / val_count
        model.train()

        print(f"   ✅ Training Loss: {avg_train_loss:.4f}")
        print(f"   ✅ Validation Loss: {avg_val_loss:.4f}\n")


if __name__ == "__main__":
    train_brain_enhanced()
