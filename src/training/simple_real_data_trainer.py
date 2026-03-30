#!/usr/bin/env python3
"""
🎓 SIMPLE REAL DATA TRAINER - STEP 2 SUCCESS!
Direct training with our real Wikipedia educational data
"""

import json
import logging
import torch
import time
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from torch.utils.data import Dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleEducationalDataset(Dataset):
    def __init__(self, qa_pairs, tokenizer):
        self.data = []
        for qa in qa_pairs:
            text = f"Question: {qa['question']}\nAnswer: {qa['answer']}"
            encoding = tokenizer(text, truncation=True, padding="max_length", max_length=256, return_tensors="pt")
            self.data.append({
                'input_ids': encoding['input_ids'].squeeze(),
                'attention_mask': encoding['attention_mask'].squeeze(),
                'labels': encoding['input_ids'].squeeze()
            })
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx]

def main():
    logger.info("🎓 STEP 2: Training with REAL Educational Data!")
      # Load our real dataset
    with open("real_high_school_math_dataset.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    qa_pairs = data['training_data']
    logger.info(f"✅ Loaded {len(qa_pairs)} real Q&A pairs from Wikipedia")
    
    # Setup model
    model_name = "microsoft/DialoGPT-small"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Create dataset
    dataset = SimpleEducationalDataset(qa_pairs, tokenizer)
    
    # Training arguments for 4GB VRAM
    training_args = TrainingArguments(
        output_dir="./real_math_model",
        num_train_epochs=2,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=3e-5,
        logging_steps=5,
        save_steps=50,
        fp16=True,
        remove_unused_columns=False,
    )
    
    # Train
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )
    
    logger.info("🔥 Starting training with real educational data...")
    start_time = time.time()
    
    trainer.train()
    
    training_time = time.time() - start_time
    logger.info(f"✅ Training completed in {training_time:.1f} seconds")
    
    # Save model
    trainer.save_model("./real_math_model_final")
    tokenizer.save_pretrained("./real_math_model_final")
    
    # Test the model
    logger.info("🧪 Testing trained model...")
    model.eval()
    
    test_questions = [
        "What is linear algebra?",
        "Can you explain calculus?",
        "What is trigonometry?"
    ]
    
    for question in test_questions:
        prompt = f"Question: {question}\nAnswer:"
        inputs = tokenizer(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_length=inputs.input_ids.shape[1] + 80,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        answer = response[len(prompt):].strip()
        
        logger.info(f"❓ {question}")
        logger.info(f"💬 {answer[:100]}...")
        logger.info("---")
    
    # Success log
    success_log = {
        "step": 2,
        "status": "SUCCESS",
        "dataset": "Real Wikipedia Mathematics",
        "qa_pairs": len(qa_pairs),
        "training_time": training_time,
        "timestamp": datetime.now().isoformat()
    }
    
    with open("step2_real_data_success.json", "w") as f:
        json.dump(success_log, f, indent=2)
    
    logger.info("🎉 STEP 2 COMPLETE: Successfully trained on real educational data!")
    return True

if __name__ == "__main__":
    main()
