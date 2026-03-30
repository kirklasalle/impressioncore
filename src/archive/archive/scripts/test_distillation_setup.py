"""
Test Knowledge Distillation Setup

Quick validation that distillation infrastructure is operational.
"""

import torch
from b3_knowledge_distillation import (
    DistillationConfig,
    DummyConversationalDataset,
    KnowledgeDistillationTrainer
)
from src.core.models.b3_foundation_integrated import B3FoundationIntegrated
from test_b3_optimized import B3OptimizedIntegrated
from src.core.models.b3_foundation_architecture import B3FoundationConfig
from src.core.models.b3_foundation_optimized_config import B3OptimizedConfig

print("=" * 80)
print("Testing Knowledge Distillation Setup")
print("=" * 80)

# Create minimal config for testing
test_config = DistillationConfig(
    teacher_epochs=1,
    student_epochs=1,
    batch_size=2,
    gradient_accumulation_steps=1,
    output_dir="checkpoints/distillation_test",
    logging_steps=5,
    save_steps=50
)

print("\n✅ Configuration created")

# Load models
print("\n🔧 Loading models...")
teacher_config = B3FoundationConfig()
teacher_model = B3FoundationIntegrated(teacher_config)
print(f"   Teacher: {sum(p.numel() for p in teacher_model.parameters()):,} params")

student_config = B3OptimizedConfig()
student_model = B3OptimizedIntegrated(student_config)
print(f"   Student: {sum(p.numel() for p in student_model.parameters()):,} params")

# Create small dataset for testing
print("\n📚 Creating test dataset...")
test_dataset = DummyConversationalDataset(
    teacher_vocab_size=teacher_config.vocab_size,
    student_vocab_size=student_config.vocab_size,
    num_samples=50,  # Small for quick test
    max_length=64
)
print(f"   Dataset: {len(test_dataset)} samples")

# Test dataset sampling
print("\n🧪 Testing dataset...")
sample = test_dataset[0]
print(f"   Teacher input shape: {sample['teacher_input_ids'].shape}")
print(f"   Student input shape: {sample['student_input_ids'].shape}")
print(f"   Labels shape: {sample['labels'].shape}")

# Initialize trainer
print("\n🎓 Initializing trainer...")
try:
    trainer = KnowledgeDistillationTrainer(
        teacher_model=teacher_model,
        student_model=student_model,
        config=test_config,
        train_dataset=test_dataset
    )
    print("✅ Trainer initialized successfully")
except Exception as e:
    print(f"❌ Trainer initialization failed: {e}")
    raise

# Test loss computation
print("\n🧮 Testing loss computation...")
try:
    # Create dummy logits
    batch_size, seq_len = 2, 32
    teacher_logits = torch.randn(batch_size, seq_len, teacher_config.vocab_size)
    student_logits = torch.randn(batch_size, seq_len, student_config.vocab_size)
    labels = torch.randint(0, student_config.vocab_size, (batch_size, seq_len))

    losses = trainer.compute_distillation_loss(
        student_logits,
        teacher_logits,
        labels
    )

    print(f"   Total loss: {losses['total'].item():.4f}")
    print(f"   Task loss: {losses['task'].item():.4f}")
    print(f"   Distillation loss: {losses['distillation'].item():.4f}")
    print(f"   MoE balance: {losses['moe_balance'].item():.4f}")
    print("✅ Loss computation working")
except Exception as e:
    print(f"❌ Loss computation failed: {e}")
    raise

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED - Distillation setup is operational!")
print("=" * 80)
print("\nReady to run full distillation with:")
print("  python b3_knowledge_distillation.py")
