import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "Qwen/Qwen2.5-0.5B-Instruct"
cache_dir = "d:/Projects/impressioncore/models/qwen_cache"

print(f"Checking for {model_id}...")

try:
    tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir)
    model = AutoModelForCausalLM.from_pretrained(model_id, cache_dir=cache_dir, torch_dtype=torch.float16)
    model.to("cuda")
    print("SUCCESS: Model loaded on CUDA.")
    print(f"VRAM used: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
except Exception as e:
    print(f"FAILED: {e}")
