"""Final loss computation test with fixed remapping"""
import sys, os
sys.path.insert(0, 'src')

import torch
import torch.nn.functional as F
from transformers import GPT2Tokenizer
from core.data.conversational_distillation_dataset import load_conversational_datasets
from torch.utils.data import DataLoader

print("\n" + "="*80)
print("FINAL Loss Computation Test")
print("="*80)

# Load tokenizers
print("\nLoading tokenizers...")
teacher_tok = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-small')
student_tok = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-small')
teacher_tok.pad_token = teacher_tok.eos_token
student_tok.pad_token = student_tok.eos_token

# Load datasets with vocab remapping
print("\nLoading datasets with student_vocab_size=28000...")
train_ds, _ = load_conversational_datasets(
    teacher_tok, student_tok,
    "F:/data/qa_datasets/mixed/mixed_qa_conversation_train.json",
    "F:/data/qa_datasets/mixed/mixed_qa_conversation_val.json",
    128, True, 28000
)

# Create batch
print("\nCreating batch...")
loader = DataLoader(torch.utils.data.Subset(train_ds, range(8)), batch_size=4)
batch = next(iter(loader))

print(f"Student input max: {batch['student_input_ids'].max().item()}")
print(f"Labels max (excluding -100): {batch['labels'][batch['labels'] != -100].max().item()}")

# Create mock logits
print("\nCreating mock logits...")
student_logits = torch.randn(4, 128, 28000)
labels = batch['labels']

# Test loss
print("\nComputing task loss...")
try:
    loss = F.cross_entropy(
        student_logits.view(-1, 28000),
        labels.view(-1),
        ignore_index=-100
    )
    print(f"✅ SUCCESS: Task loss = {loss.item():.4f}")
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - Loss computation working correctly!")
    print("="*80)
except Exception as e:
    print(f"❌ FAILED: {e}")
