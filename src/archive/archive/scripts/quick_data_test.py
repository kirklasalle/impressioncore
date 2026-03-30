"""
Simple Real Data Validation Test

Created: October 11, 2025
Purpose: Quick validation that real conversational data loads correctly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from transformers import GPT2Tokenizer
from core.data.conversational_distillation_dataset import load_conversational_datasets

print("\n" + "="*80)
print("🧪 Quick Real Data Validation Test")
print("="*80)

# Load tokenizers
print("\n1. Loading tokenizers...")
teacher_tokenizer = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-small')
student_tokenizer = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-small')

if teacher_tokenizer.pad_token is None:
    teacher_tokenizer.pad_token = teacher_tokenizer.eos_token
if student_tokenizer.pad_token is None:
    student_tokenizer.pad_token = student_tokenizer.eos_token

print(f"✅ Teacher tokenizer: {len(teacher_tokenizer)} tokens")
print(f"✅ Student tokenizer: {len(student_tokenizer)} tokens")

# Load datasets
print("\n2. Loading real conversational datasets...")
train_dataset, val_dataset = load_conversational_datasets(
    teacher_tokenizer=teacher_tokenizer,
    student_tokenizer=student_tokenizer,
    train_path="F:/data/qa_datasets/mixed/mixed_qa_conversation_train.json",
    val_path="F:/data/qa_datasets/mixed/mixed_qa_conversation_val.json",
    max_length=128,
    combine_qa=True
)

# Test sampling
print("\n3. Testing sample retrieval...")
sample = train_dataset[0]
print(f"   Teacher input shape: {sample['teacher_input_ids'].shape}")
print(f"   Student input shape: {sample['student_input_ids'].shape}")
print(f"   Labels shape: {sample['labels'].shape}")
print(f"   Attention mask shape: {sample['attention_mask'].shape}")

# Decode sample
decoded = teacher_tokenizer.decode(sample['teacher_input_ids'], skip_special_tokens=True)
print(f"\n4. Sample conversation:")
print(f"   {decoded[:200]}...")

# Batch test
print("\n5. Testing batch creation...")
import torch
from torch.utils.data import DataLoader

test_subset = torch.utils.data.Subset(train_dataset, range(10))
dataloader = DataLoader(test_subset, batch_size=4, shuffle=False)
batch = next(iter(dataloader))

print(f"   Batch size: {batch['teacher_input_ids'].shape[0]}")
print(f"   Teacher batch shape: {batch['teacher_input_ids'].shape}")
print(f"   Student batch shape: {batch['student_input_ids'].shape}")

# Success
print("\n" + "="*80)
print("✅ ALL REAL DATA VALIDATION TESTS PASSED")
print("="*80)
print(f"\n🎯 Ready for knowledge distillation!")
print(f"   Training samples: {len(train_dataset):,}")
print(f"   Validation samples: {len(val_dataset):,}")
print(f"   Teacher→Student: 76.8M → 39.8M parameters")
print(f"   Target retention: >95%")
print(f"\n▶️  Next: Run full distillation")
print(f"   Command: python b3_knowledge_distillation.py")
print("="*80 + "\n")
