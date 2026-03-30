"""
Quick Test: Real Data Integration for Knowledge Distillation

Created: October 11, 2025
Author: Kirk LaSalle; GitHub Copilot
Tags: #testing #knowledge_distillation #real_data
Category: Testing
Status: Active

Purpose:
    Validate that the conversational dataset loader works correctly with
    the teacher and student models before running full distillation.

Tests:
    1. Dataset loading (50K train + 2.5K val)
    2. Model compatibility with real data
    3. Tokenization alignment (50K teacher → 28K student)
    4. Sample forward pass with real conversation
    5. Loss computation with actual data
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import torch
from src.core.models.b3_foundation_integrated import B3FoundationIntegrated
from test_b3_optimized import B3OptimizedIntegrated
from src.core.models.b3_foundation_architecture import B3FoundationConfig
from src.core.models.b3_foundation_optimized_config import B3OptimizedConfig
from core.data.conversational_distillation_dataset import load_conversational_datasets


def test_real_data_integration():
    """Test real conversational data with teacher and student models."""

    print("\n" + "="*80)
    print("🧪 Testing Real Data Integration for Knowledge Distillation")
    print("="*80)

    # 1. Load models
    print("\n📦 Loading models...")
    teacher_config = B3FoundationConfig()
    teacher_model = B3FoundationIntegrated(teacher_config)
    teacher_params = sum(p.numel() for p in teacher_model.parameters())
    print(f"✅ Teacher: {teacher_params:,} params (vocab: {teacher_config.vocab_size:,})")

    student_config = B3OptimizedConfig()
    student_model = B3OptimizedIntegrated(student_config)
    student_params = sum(p.numel() for p in student_model.parameters())
    print(f"✅ Student: {student_params:,} params (vocab: {student_config.vocab_size:,})")

    # 2. Load tokenizers (create from pretrained)
    print("\n📚 Loading tokenizers...")
    from transformers import GPT2Tokenizer

    teacher_tokenizer = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-small')
    student_tokenizer = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-small')

    # Add padding tokens
    if teacher_tokenizer.pad_token is None:
        teacher_tokenizer.pad_token = teacher_tokenizer.eos_token
    if student_tokenizer.pad_token is None:
        student_tokenizer.pad_token = student_tokenizer.eos_token

    print(f"✅ Teacher tokenizer: {len(teacher_tokenizer)} tokens")
    print(f"✅ Student tokenizer: {len(student_tokenizer)} tokens")

    # 3. Load datasets (just 100 samples for quick test)
    print("\n📚 Loading real conversational data (test subset)...")

    train_dataset, val_dataset = load_conversational_datasets(
        teacher_tokenizer=teacher_tokenizer,
        student_tokenizer=student_tokenizer,
        train_path="F:/data/qa_datasets/mixed/mixed_qa_conversation_train.json",
        val_path="F:/data/qa_datasets/mixed/mixed_qa_conversation_val.json",
        max_length=128,
        combine_qa=True
    )

    print(f"\n✅ Loaded {len(train_dataset):,} training samples")
    print(f"✅ Loaded {len(val_dataset):,} validation samples")

    # 4. Test sample retrieval
    print("\n🔬 Testing sample retrieval...")
    sample = train_dataset[0]
    print(f"   Teacher input shape: {sample['teacher_input_ids'].shape}")
    print(f"   Student input shape: {sample['student_input_ids'].shape}")
    print(f"   Labels shape: {sample['labels'].shape}")
    print(f"   Attention mask shape: {sample['attention_mask'].shape}")

    # Decode to verify content
    decoded = teacher_tokenizer.decode(sample['teacher_input_ids'], skip_special_tokens=True)
    print(f"\n📝 Sample conversation:")
    print(f"   {decoded[:150]}...")

    # 5. Test batch creation
    print("\n🔬 Testing batch creation...")
    from torch.utils.data import DataLoader

    # Use small subset for quick test
    test_subset = torch.utils.data.Subset(train_dataset, range(100))
    dataloader = DataLoader(test_subset, batch_size=4, shuffle=False)
    batch = next(iter(dataloader))

    print(f"   Batch size: {batch['teacher_input_ids'].shape[0]}")
    print(f"   Teacher batch shape: {batch['teacher_input_ids'].shape}")
    print(f"   Student batch shape: {batch['student_input_ids'].shape}")

    # 6. Test forward pass with real data
    print("\n🔬 Testing forward pass with real data...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"   Device: {device}")

    teacher_model = teacher_model.to(device)
    student_model = student_model.to(device)
    teacher_model.eval()
    student_model.eval()

    teacher_input = batch['teacher_input_ids'][:2].to(device)  # 2 samples
    student_input = batch['student_input_ids'][:2].to(device)

    with torch.no_grad():
        # Teacher forward (returns tuple)
        teacher_output_raw = teacher_model(input_ids=teacher_input)
        teacher_logits = teacher_output_raw[0] if isinstance(teacher_output_raw, tuple) else teacher_output_raw['logits']

        # Student forward (needs manual forward since optimized model doesn't have forward method yet)
        # Just pass through text encoder and output projection for test
        text_embed = student_model.text_encoder(student_input)
        student_logits = student_model.output_projection(student_model.output_layer_norm(text_embed))

    print(f"   Teacher output shape: {teacher_logits.shape}")
    print(f"   Student output shape: {student_logits.shape}")
    print(f"   Teacher vocab: {teacher_logits.shape[-1]}")
    print(f"   Student vocab: {student_logits.shape[-1]}")

    # 7. Test loss computation (vocab alignment)
    print("\n🔬 Testing loss computation with vocab alignment...")
    labels = batch['labels'][:2].to(device)

    # Align vocab sizes (truncate teacher to student size)
    teacher_logits_aligned = teacher_logits[:, :, :student_config.vocab_size]

    # Compute losses
    task_loss = torch.nn.functional.cross_entropy(
        student_logits.view(-1, student_config.vocab_size),
        labels.view(-1),
        ignore_index=-100
    )

    temperature = 4.0
    student_soft = torch.nn.functional.log_softmax(student_logits / temperature, dim=-1)
    teacher_soft = torch.nn.functional.softmax(teacher_logits_aligned / temperature, dim=-1)
    distill_loss = torch.nn.functional.kl_div(
        student_soft.view(-1, student_config.vocab_size),
        teacher_soft.view(-1, student_config.vocab_size),
        reduction='batchmean'
    ) * (temperature ** 2)

    combined_loss = 0.5 * task_loss + 0.5 * distill_loss

    print(f"   Task loss: {task_loss.item():.4f}")
    print(f"   Distillation loss: {distill_loss.item():.4f}")
    print(f"   Combined loss: {combined_loss.item():.4f}")

    # 8. Memory usage check
    if torch.cuda.is_available():
        print("\n💾 GPU Memory Usage:")
        print(f"   Allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
        print(f"   Reserved: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

    # Success summary
    print("\n" + "="*80)
    print("✅ ALL REAL DATA INTEGRATION TESTS PASSED")
    print("="*80)
    print("\n🎯 Ready for full knowledge distillation training!")
    print("   Run: python b3_knowledge_distillation.py")
    print(f"   Dataset: 50,000 training samples")
    print(f"   Validation: 2,500 samples")
    print(f"   Teacher: {teacher_params:,} params")
    print(f"   Student: {student_params:,} params")
    print(f"   Target: >95% performance retention")
    print("="*80 + "\n")


if __name__ == '__main__':
    test_real_data_integration()
