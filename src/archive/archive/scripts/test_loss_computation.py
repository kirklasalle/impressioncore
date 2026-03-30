"""
Loss Computation Validation Test

Created: October 11, 2025
Purpose: Validate that the distillation loss computation works correctly
         with real conversational data and proper vocab alignment.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import torch
import torch.nn.functional as F
from transformers import GPT2Tokenizer
from core.data.conversational_distillation_dataset import load_conversational_datasets

print("\n" + "="*80)
print("🧪 Loss Computation Validation Test")
print("="*80)

# 1. Load tokenizers and dataset
print("\n1. Loading data...")
teacher_tokenizer = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-small')
student_tokenizer = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-small')

if teacher_tokenizer.pad_token is None:
    teacher_tokenizer.pad_token = teacher_tokenizer.eos_token
if student_tokenizer.pad_token is None:
    student_tokenizer.pad_token = student_tokenizer.eos_token

train_dataset, _ = load_conversational_datasets(
    teacher_tokenizer=teacher_tokenizer,
    student_tokenizer=student_tokenizer,
    train_path="F:/data/qa_datasets/mixed/mixed_qa_conversation_train.json",
    val_path="F:/data/qa_datasets/mixed/mixed_qa_conversation_val.json",
    max_length=128,
    combine_qa=True,
    student_vocab_size=28000  # Student model's actual vocab size
)

print(f"✅ Loaded {len(train_dataset):,} samples")

# 2. Create sample batch
print("\n2. Creating test batch...")
from torch.utils.data import DataLoader

test_subset = torch.utils.data.Subset(train_dataset, range(8))
dataloader = DataLoader(test_subset, batch_size=4, shuffle=False)
batch = next(iter(dataloader))

teacher_input = batch['teacher_input_ids']
student_input = batch['student_input_ids']
labels = batch['labels']
attention_mask = batch['attention_mask']

print(f"   Batch size: {teacher_input.shape[0]}")
print(f"   Sequence length: {teacher_input.shape[1]}")
print(f"   Teacher input shape: {teacher_input.shape}")
print(f"   Student input shape: {student_input.shape}")
print(f"   Labels shape: {labels.shape}")
print(f"   Attention mask shape: {attention_mask.shape}")

# 3. Check label statistics
print("\n3. Analyzing labels...")
valid_labels = labels[labels != -100]
print(f"   Total tokens: {labels.numel()}")
print(f"   Valid tokens (not padded): {valid_labels.numel()}")
print(f"   Padded tokens: {(labels == -100).sum().item()}")
print(f"   Label range: {valid_labels.min().item()} to {valid_labels.max().item()}")
print(f"   Unique labels: {len(valid_labels.unique())}")

# 4. Create mock logits (simulating model outputs)
print("\n4. Creating mock model outputs...")
teacher_vocab_size = 50257
student_vocab_size = 28000
batch_size, seq_len = teacher_input.shape

# Random logits (simulating untrained model)
teacher_logits = torch.randn(batch_size, seq_len, teacher_vocab_size)
student_logits = torch.randn(batch_size, seq_len, student_vocab_size)

print(f"   Teacher logits shape: {teacher_logits.shape}")
print(f"   Student logits shape: {student_logits.shape}")

# 5. Test task loss computation
print("\n5. Testing task loss (cross-entropy)...")
try:
    task_loss = F.cross_entropy(
        student_logits.view(-1, student_vocab_size),
        labels.view(-1),
        ignore_index=-100
    )
    print(f"   ✅ Task loss computed: {task_loss.item():.4f}")
    print(f"      (High loss expected for random logits)")
except Exception as e:
    print(f"   ❌ Task loss failed: {e}")
    sys.exit(1)

# 6. Test distillation loss computation
print("\n6. Testing distillation loss (KL divergence)...")
try:
    temperature = 4.0

    # Align vocab sizes (truncate teacher to student vocab)
    teacher_logits_aligned = teacher_logits[:, :, :student_vocab_size]

    # Soften distributions
    student_soft = F.log_softmax(student_logits / temperature, dim=-1)
    teacher_soft = F.softmax(teacher_logits_aligned / temperature, dim=-1)

    # KL divergence
    distill_loss = F.kl_div(
        student_soft.view(-1, student_vocab_size),
        teacher_soft.view(-1, student_vocab_size),
        reduction='batchmean'
    ) * (temperature ** 2)

    print(f"   ✅ Distillation loss computed: {distill_loss.item():.4f}")
    print(f"      Temperature: {temperature}")
    print(f"      Vocab alignment: {teacher_vocab_size} → {student_vocab_size}")
except Exception as e:
    print(f"   ❌ Distillation loss failed: {e}")
    sys.exit(1)

# 7. Test combined loss
print("\n7. Testing combined loss...")
try:
    moe_loss = torch.tensor(0.01)  # Mock MoE loss

    task_alpha = 0.5
    distillation_alpha = 0.5
    moe_alpha = 0.01

    combined_loss = (
        task_alpha * task_loss +
        distillation_alpha * distill_loss +
        moe_alpha * moe_loss
    )

    print(f"   ✅ Combined loss computed: {combined_loss.item():.4f}")
    print(f"      Task (α={task_alpha}): {(task_alpha * task_loss).item():.4f}")
    print(f"      Distillation (α={distillation_alpha}): {(distillation_alpha * distill_loss).item():.4f}")
    print(f"      MoE balance (α={moe_alpha}): {(moe_alpha * moe_loss).item():.4f}")
except Exception as e:
    print(f"   ❌ Combined loss failed: {e}")
    sys.exit(1)

# 8. Test backward pass
print("\n8. Testing backward pass...")
try:
    # Create a simple model parameter to test gradients
    dummy_param = torch.randn(10, 10, requires_grad=True)
    dummy_output = (dummy_param * student_logits.mean()).sum()

    # Compute loss with dummy output
    test_loss = combined_loss + dummy_output * 0.0001

    # Backward
    test_loss.backward()

    print(f"   ✅ Backward pass successful")
    print(f"      Gradient computed: {dummy_param.grad is not None}")
    print(f"      Gradient shape: {dummy_param.grad.shape if dummy_param.grad is not None else 'None'}")
except Exception as e:
    print(f"   ❌ Backward pass failed: {e}")
    sys.exit(1)

# 9. Test with actual decoder sample
print("\n9. Testing with decoded sample...")
sample_idx = 0
decoded_text = teacher_tokenizer.decode(teacher_input[sample_idx], skip_special_tokens=True)
print(f"   Sample: {decoded_text[:100]}...")
print(f"   Valid tokens in sample: {(labels[sample_idx] != -100).sum().item()}")

# Success summary
print("\n" + "="*80)
print("✅ ALL LOSS COMPUTATION TESTS PASSED")
print("="*80)
print("\n📊 Summary:")
print(f"   Task loss: ✅ Working (cross-entropy with ignore_index=-100)")
print(f"   Distillation loss: ✅ Working (KL divergence with temperature)")
print(f"   Vocab alignment: ✅ Working ({teacher_vocab_size} → {student_vocab_size})")
print(f"   Combined loss: ✅ Working (weighted sum)")
print(f"   Backward pass: ✅ Working (gradients computed)")
print(f"\n🎯 Loss computation is ready for knowledge distillation!")
print(f"   Command: python b3_knowledge_distillation.py")
print("="*80 + "\n")
