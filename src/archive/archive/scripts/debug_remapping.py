import sys, os
sys.path.insert(0, 'src')
from transformers import GPT2Tokenizer
from core.data.conversational_distillation_dataset import ConversationalDistillationDataset

t = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-small')
t.pad_token = t.eos_token

ds = ConversationalDistillationDataset(
    'F:/data/qa_datasets/mixed/mixed_qa_conversation_train.json',
    t, t, 128, True, 28000
)

# Get 5 samples
for i in range(5):
    sample = ds[i]
    student_max = sample['student_input_ids'].max().item()
    label_max_valid = sample['labels'][sample['labels'] != -100].max().item() if (sample['labels'] != -100).any() else -1
    print(f"Sample {i}: student_max={student_max}, label_max={label_max_valid}")
    if student_max >= 28000:
        print(f"  ERROR: Student token {student_max} >= 28000!")
    if label_max_valid >= 28000:
        print(f"  ERROR: Label {label_max_valid} >= 28000!")
