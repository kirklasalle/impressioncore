#!/usr/bin/env python3
"""
B3-Hope Distillation Training - Simplified and Robust
====================================================

Streamlined distillation with:
- Shorter responses (faster generation)
- Progress saving and resume capability
- Better error handling
- ASCII output (no emoji encoding issues)

Created: October 3, 2025
"""

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import Dataset, DataLoader
import logging
import json
import os
import time
import requests
from tqdm import tqdm
from transformers import AutoTokenizer
from datetime import datetime

# Setup logging - ASCII only, UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(
            f'b3_distillation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from b3_constitutional_trainer import ImpressionCoreB3Hope, B3HopeConfig

class SimpleOllamaTeacher:
    """Simplified Ollama teacher with robust error handling"""

    def __init__(self, model_name="llama3.2:3b"):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/generate"
        logger.info(f"Teacher: {model_name}")

    def generate(self, prompt: str, max_tokens=150) -> str:
        """Generate response with timeout and retry"""
        for attempt in range(3):
            try:
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.7
                    }
                }

                response = requests.post(self.api_url, json=payload, timeout=120)
                if response.status_code == 200:
                    return response.json().get('response', '').strip()

            except Exception as e:
                logger.warning(f"Attempt {attempt+1}/3 failed: {e}")
                time.sleep(2)

        return None

class SimpleDistillationDataset(Dataset):
    """Simple dataset for distillation"""

    def __init__(self, pairs, tokenizer, max_length=512):
        self.pairs = pairs
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        pair = self.pairs[idx]
        text = f"User: {pair['prompt']}\nAssistant: {pair['response']}"

        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0)
        }

def create_dataset(prompts, teacher, stage_name, progress_file):
    """Create or resume distillation dataset"""

    # Check for existing progress
    if os.path.exists(progress_file):
        logger.info(f"[RESUME] Loading existing {stage_name} dataset")
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    logger.info(f"[CREATE] Generating {stage_name} dataset: {len(prompts)} prompts")

    pairs = []
    for i, prompt in enumerate(tqdm(prompts, desc=stage_name)):
        response = teacher.generate(prompt)

        if response:
            pairs.append({"prompt": prompt, "response": response})

        # Save progress every 50 samples
        if (i + 1) % 50 == 0:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(pairs, f, indent=2, ensure_ascii=False)
            logger.info(f"[SAVE] Progress: {len(pairs)}/{len(prompts)}")

    # Final save
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(pairs, f, indent=2, ensure_ascii=False)

    logger.info(f"[OK] {stage_name} complete: {len(pairs)} pairs")
    return pairs

def train_stage(model, pairs, tokenizer, stage_name, device):
    """Train one stage"""

    logger.info(f"\n[TRAIN] {stage_name}: {len(pairs)} samples")

    dataset = SimpleDistillationDataset(pairs, tokenizer)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=True, num_workers=0)

    optimizer = AdamW(model.parameters(), lr=5e-6, weight_decay=0.01)

    model.train()
    best_loss = float('inf')

    for epoch in range(3):
        epoch_loss = 0.0
        num_batches = 0

        logger.info(f"{stage_name} - Epoch {epoch+1}/3")

        pbar = tqdm(dataloader, desc=f"E{epoch+1}")
        for batch in pbar:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)

            outputs = model(input_ids, attention_mask=attention_mask)
            loss = outputs['loss']

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
            optimizer.step()
            optimizer.zero_grad()

            epoch_loss += loss.item()
            num_batches += 1

            pbar.set_postfix({'loss': f"{loss.item():.4f}"})

        avg_loss = epoch_loss / num_batches
        logger.info(f"{stage_name} - Epoch {epoch+1}: loss = {avg_loss:.4f}")

        if avg_loss < best_loss:
            best_loss = avg_loss
            checkpoint = {
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_loss': avg_loss,
                'epoch': epoch,
                'stage': stage_name
            }
            filename = f"b3_distill_{stage_name.lower().replace(' ', '_')}_best.pth"
            torch.save(checkpoint, filename)
            logger.info(f"[SAVE] {filename} (loss: {avg_loss:.4f})")

    return best_loss

def main():
    """Main execution"""

    logger.info("="*70)
    logger.info("B3-Hope Distillation Training - Simplified and Robust")
    logger.info("="*70)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Device: {device}")

    # Load teacher
    teacher = SimpleOllamaTeacher("llama3.2:3b")

    # Load student
    logger.info("Loading student model...")
    config = B3HopeConfig()
    student = ImpressionCoreB3Hope(config)

    checkpoint = torch.load('b3_massive_best.pth', map_location=device, weights_only=False)
    student.load_state_dict(checkpoint['model_state_dict'])
    student = student.to(device)

    logger.info(f"Student loaded: {sum(p.numel() for p in student.parameters()):,} parameters")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
    tokenizer.pad_token = tokenizer.eos_token

    # Simple prompts for quick testing
    stage1_prompts = [
        "Hello", "Hi", "How are you?", "Good morning",
        "What is AI?", "Explain machine learning", "What is Python?",
        "Can you help me?", "I need assistance", "Thank you",
        "What can you do?", "Who are you?", "Tell me about yourself",
        "Goodbye", "See you later", "How does AI work?",
        "What is deep learning?", "Explain neural networks", "What is data science?",
        "How do computers learn?", "What is an algorithm?", "Explain programming"
    ] * 20  # 440 samples

    # Stage 1: Simple conversations
    logger.info("\n[STAGE 1] Simple Conversations")
    pairs1 = create_dataset(stage1_prompts, teacher, "Stage1", "stage1_dataset.json")
    loss1 = train_stage(student, pairs1, tokenizer, "Stage1", device)

    logger.info("\n" + "="*70)
    logger.info(f"[SUCCESS] Distillation complete!")
    logger.info(f"Final loss: {loss1:.4f}")
    logger.info("="*70)

if __name__ == "__main__":
    main()
