import sys, os
sys.path.insert(0, 'src')
from transformers import GPT2Tokenizer
from core.data.conversational_distillation_dataset import ConversationalDistillationDataset

t = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-small')
t.pad_token = t.eos_token
print(f"Tokenizer vocab size: {len(t)}")
print(f"UNK token ID: {t.unk_token_id}")
print(f"EOS token ID: {t.eos_token_id}")
print(f"PAD token ID: {t.pad_token_id}")

ds = ConversationalDistillationDataset(
    'F:/data/qa_datasets/mixed/mixed_qa_conversation_train.json',
    t, t, 128, True, 28000
)

sample = ds[0]
print(f"\nStudent input max: {sample['student_input_ids'].max().item()}")
print(f"Student input min: {sample['student_input_ids'].min().item()}")
print(f"Labels max (excluding -100): {sample['labels'][sample['labels'] != -100].max().item()}")
print(f"Labels min: {sample['labels'][sample['labels'] != -100].min().item()}")
