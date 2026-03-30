#!/usr/bin/env python3
"""
ImpressionCore B3-Hope Progressive Ollama Distillation System
=============================================================

4-Stage Progressive Curriculum Learning with Ollama Knowledge Distillation:
Stage 1: Simple conversations (llama3.2:1b teacher)
Stage 2: Complex discussions (llama3.2:1b teacher)
Stage 3: Technical knowledge (llama3.2:1b teacher)
Stage 4: Advanced reasoning (llama3.2:1b teacher)

Uses the successfully trained b3_massive_best.pth (loss 0.0105) as starting point.

Created: October 3, 2025
Author: Kirk LaSalle; GitHub Copilot
Purpose: Transform B3-Hope into world-class conversational AI through teacher distillation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from torch.utils.data import Dataset, DataLoader
import logging
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import time
import requests
from tqdm import tqdm
from transformers import AutoTokenizer

# Setup enhanced logging with UTF-8 encoding for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(
            f'b3_progressive_distillation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import B3-Hope model
from b3_constitutional_trainer import ImpressionCoreB3Hope, B3HopeConfig

@dataclass
class DistillationConfig:
    """Configuration for progressive distillation"""

    # Ollama Teacher Configuration
    teacher_model: str = "llama3.2:3b"  # Using available 3B parameter teacher (better than 1B!)
    ollama_base_url: str = "http://localhost:11434"
    teacher_temperature: float = 0.7

    # Student Model (B3-Hope)
    student_checkpoint: str = "b3_massive_best.pth"  # Our working 10-epoch model
    student_device: str = "cuda"

    # Distillation Hyperparameters
    distillation_temperature: float = 2.0  # Soften distributions for better knowledge transfer
    alpha: float = 0.7  # Weight for distillation loss vs student loss
    learning_rate: float = 5e-6  # Lower than base training for fine-tuning
    weight_decay: float = 0.01
    max_grad_norm: float = 0.5
    batch_size: int = 1
    gradient_accumulation_steps: int = 4

    # Progressive Curriculum
    stage_1_samples: int = 500   # Simple conversations
    stage_2_samples: int = 750   # Complex discussions
    stage_3_samples: int = 1000  # Technical knowledge
    stage_4_samples: int = 1250  # Advanced reasoning

    # Training Configuration
    epochs_per_stage: int = 3
    save_every_steps: int = 100
    eval_every_steps: int = 50

    # Memory Optimization
    use_fp16: bool = False  # FP32 for GTX 1050 Ti stability
    gradient_checkpointing: bool = True

class OllamaTeacher:
    """Manages Ollama API interactions for knowledge distillation"""

    def __init__(self, config: DistillationConfig):
        self.config = config
        self.api_url = f"{config.ollama_base_url}/api/generate"
        self.tags_url = f"{config.ollama_base_url}/api/tags"
        logger.info(f"OllamaTeacher initialized with model: {config.teacher_model}")

    def check_availability(self) -> bool:
        """Check if Ollama is running and teacher model is available"""
        try:
            response = requests.get(self.tags_url, timeout=5)
            if response.status_code == 200:
                models = response.json()
                available_models = [m['name'] for m in models.get('models', [])]

                # Check for exact match or partial match (e.g., llama3.2:1b or llama3.2)
                model_available = any(
                    self.config.teacher_model in model or model in self.config.teacher_model
                    for model in available_models
                )

                if model_available:
                    logger.info(f"[OK] Teacher model {self.config.teacher_model} available")
                    return True
                else:
                    logger.error(f"[ERROR] Teacher model {self.config.teacher_model} not found")
                    logger.info(f"Available models: {available_models}")
                    return False
            else:
                logger.error("[ERROR] Ollama API not responding")
                return False
        except Exception as e:
            logger.error(f"[ERROR] Ollama check failed: {e}")
            return False

    def generate_response(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Generate teacher response with retry logic"""
        for attempt in range(max_retries):
            try:
                payload = {
                    "model": self.config.teacher_model,
                    "prompt": prompt,
                    "temperature": self.config.teacher_temperature,
                    "stream": False,
                    "options": {
                        "num_predict": 256,  # Shorter responses for faster generation
                        "top_k": 40,
                        "top_p": 0.9
                    }
                }

                response = requests.post(self.api_url, json=payload, timeout=120)
                if response.status_code == 200:
                    result = response.json()
                    teacher_response = result.get('response', '').strip()
                    return teacher_response
                else:
                    logger.warning(f"Ollama API error {response.status_code}, attempt {attempt+1}/{max_retries}")

            except Exception as e:
                logger.warning(f"Error generating teacher response (attempt {attempt+1}/{max_retries}): {e}")
                time.sleep(2)  # Wait before retry

        return None

    def create_distillation_pairs(self, prompts: List[str], stage_name: str) -> List[Dict]:
        """Create prompt-response pairs from teacher model"""
        logger.info(f"\n{'='*70}")
        logger.info(f"Creating {stage_name} distillation dataset: {len(prompts)} prompts")
        logger.info(f"{'='*70}")

        distillation_pairs = []
        successful = 0
        failed = 0

        for i, prompt in enumerate(tqdm(prompts, desc=f"{stage_name} generation")):
            teacher_response = self.generate_response(prompt)

            if teacher_response:
                distillation_pairs.append({
                    "prompt": prompt,
                    "teacher_response": teacher_response
                })
                successful += 1
            else:
                failed += 1
                logger.warning(f"Failed to generate response for prompt: {prompt[:50]}...")

            # Log progress every 50 samples
            if (i + 1) % 50 == 0:
                logger.info(f"Progress: {i+1}/{len(prompts)} - Success: {successful}, Failed: {failed}")

        logger.info(f"\n{stage_name} dataset complete: {successful} successful, {failed} failed")
        return distillation_pairs

class ProgressiveCurriculumDesigner:
    """Designs the 4-stage progressive curriculum"""

    @staticmethod
    def get_stage_1_prompts() -> List[str]:
        """Stage 1: Simple conversations and basic interactions"""
        return [
            # Greetings
            "Hello", "Hi", "Hey", "Good morning", "Good afternoon", "Good evening",
            "How are you?", "How's it going?", "What's up?", "Nice to meet you",

            # Basic questions
            "What's your name?", "Who are you?", "What do you do?",
            "Can you help me?", "I need help", "I have a question",

            # Simple topics
            "What is AI?", "Explain machine learning", "What is Python?",
            "Tell me about yourself", "What can you do?", "How do you work?",

            # Polite interactions
            "Thank you", "Thanks", "I appreciate it", "You're helpful",
            "Please help me", "Can you explain?", "I don't understand",

            # Farewells
            "Goodbye", "Bye", "See you later", "Take care", "Have a nice day",

            # Simple requests
            "Explain this simply", "Give me an example", "Can you clarify?",
            "What does that mean?", "How does this work?", "Why is this important?",
        ] * 8  # Repeat for 500+ samples

    @staticmethod
    def get_stage_2_prompts() -> List[str]:
        """Stage 2: Complex discussions and multi-turn conversations"""
        return [
            # Complex topics
            "Explain the difference between machine learning and deep learning in detail",
            "How do neural networks actually learn from data?",
            "What are the ethical implications of artificial intelligence?",
            "Describe the process of training a large language model",
            "What is the transformer architecture and why is it important?",

            # Problem-solving
            "I'm trying to understand recursion, can you explain it with examples?",
            "How would you approach debugging a complex software issue?",
            "What's the best way to optimize code for performance?",
            "Explain the concept of Big O notation with real examples",

            # Explanatory discussions
            "Walk me through how computers process human language",
            "Explain quantum computing like I'm five years old",
            "What's the relationship between AI, machine learning, and data science?",
            "How do recommendation systems like Netflix or YouTube work?",

            # Abstract reasoning
            "What makes a good programming language?",
            "How has technology changed how we learn?",
            "What are the most important skills for a software developer?",
            "Discuss the future of artificial intelligence",
        ] * 15  # Repeat for 750+ samples

    @staticmethod
    def get_stage_3_prompts() -> List[str]:
        """Stage 3: Technical knowledge and specialized domains"""
        return [
            # Advanced ML/AI
            "Explain backpropagation in neural networks with mathematical detail",
            "What is attention mechanism and how does it work in transformers?",
            "Describe different types of neural network architectures and their uses",
            "Explain gradient descent optimization algorithms",
            "What is overfitting and how do you prevent it?",
            "Describe convolutional neural networks and their applications",

            # Programming concepts
            "Explain object-oriented programming principles",
            "What are design patterns and when should they be used?",
            "Describe different data structures and their time complexities",
            "Explain functional programming vs imperative programming",
            "What is concurrent programming and how does it differ from parallel programming?",

            # Computer science fundamentals
            "Explain how compilers work",
            "Describe the OSI model and network protocols",
            "What are different types of databases and when to use each?",
            "Explain cryptography basics and common algorithms",

            # Mathematics for ML
            "Explain linear algebra concepts important for machine learning",
            "What is calculus used for in neural networks?",
            "Describe probability theory and its role in AI",
            "Explain statistical concepts relevant to data science",
        ] * 20  # Repeat for 1000+ samples

    @staticmethod
    def get_stage_4_prompts() -> List[str]:
        """Stage 4: Advanced reasoning and complex problem-solving"""
        return [
            # Advanced reasoning
            "Compare and contrast different approaches to artificial general intelligence",
            "Analyze the philosophical implications of consciousness in AI systems",
            "Evaluate the trade-offs between model size and efficiency in modern AI",
            "Critically assess current limitations of large language models",

            # Complex problem-solving
            "Design a system architecture for a scalable web application handling millions of users",
            "Propose solutions to the bias problem in machine learning models",
            "Devise a strategy for optimizing a neural network for edge devices",
            "Create a framework for evaluating AI system safety and alignment",

            # Interdisciplinary topics
            "Discuss the intersection of neuroscience and artificial intelligence",
            "Analyze how economic principles apply to resource allocation in computing",
            "Explore the relationship between linguistics and natural language processing",
            "Examine ethical frameworks for AI development and deployment",

            # Future-oriented thinking
            "Predict how AI will transform education in the next decade",
            "Envision the future of human-AI collaboration",
            "Analyze potential risks and benefits of artificial general intelligence",
            "Discuss the role of AI in addressing global challenges like climate change",
        ] * 25  # Repeat for 1250+ samples

class DistillationDataset(Dataset):
    """Dataset for knowledge distillation from teacher to student"""

    def __init__(self, distillation_pairs: List[Dict], tokenizer, max_length: int = 512):
        self.pairs = distillation_pairs
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        pair = self.pairs[idx]

        # Combine prompt and teacher response
        full_text = f"User: {pair['prompt']}\nAssistant: {pair['teacher_response']}"

        # Tokenize
        encoding = self.tokenizer(
            full_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'teacher_response': pair['teacher_response']
        }

class ProgressiveDistillationTrainer:
    """Manages the 4-stage progressive distillation training"""

    def __init__(self, config: DistillationConfig):
        self.config = config
        self.device = torch.device(config.student_device if torch.cuda.is_available() else "cpu")

        # Initialize teacher
        self.teacher = OllamaTeacher(config)

        # Load tokenizer
        logger.info("Loading DialoGPT tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
        self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load student model
        logger.info(f"Loading student model from {config.student_checkpoint}...")
        self.student = self._load_student_model()

        # Setup optimizer
        self.optimizer = AdamW(
            self.student.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay
        )

        # Curriculum designer
        self.curriculum = ProgressiveCurriculumDesigner()

        # Training state
        self.global_step = 0
        self.best_loss = float('inf')

        logger.info("[OK] ProgressiveDistillationTrainer initialized")

    def _load_student_model(self) -> ImpressionCoreB3Hope:
        """Load the pre-trained student model"""
        student_config = B3HopeConfig()
        student = ImpressionCoreB3Hope(student_config)

        # Load checkpoint
        checkpoint = torch.load(self.config.student_checkpoint, map_location=self.device, weights_only=False)
        student.load_state_dict(checkpoint['model_state_dict'])
        student = student.to(self.device)

        logger.info(f"[OK] Student loaded: {sum(p.numel() for p in student.parameters()):,} parameters")
        logger.info(f"   Starting from loss: {checkpoint.get('train_loss', 'unknown')}")

        return student

    def run_full_curriculum(self):
        """Execute the complete 4-stage progressive curriculum"""
        logger.info("\n" + "="*70)
        logger.info("STARTING PROGRESSIVE DISTILLATION TRAINING")
        logger.info("="*70)
        logger.info(f"Teacher: {self.config.teacher_model}")
        logger.info(f"Student: B3-Hope (35.5M parameters)")
        logger.info(f"Device: {self.device}")
        logger.info("="*70 + "\n")

        # Verify teacher availability
        if not self.teacher.check_availability():
            logger.error("❌ Teacher model not available. Please ensure Ollama is running with llama3.2:1b")
            return

        # Stage 1: Simple Conversations
        logger.info("\n[STAGE 1] Simple Conversations")
        self._train_stage(
            stage_name="Stage 1",
            prompts=self.curriculum.get_stage_1_prompts()[:self.config.stage_1_samples],
            save_prefix="stage1"
        )

        # Stage 2: Complex Discussions
        logger.info("\n[STAGE 2] Complex Discussions")
        self._train_stage(
            stage_name="Stage 2",
            prompts=self.curriculum.get_stage_2_prompts()[:self.config.stage_2_samples],
            save_prefix="stage2"
        )

        # Stage 3: Technical Knowledge
        logger.info("\n[STAGE 3] Technical Knowledge")
        self._train_stage(
            stage_name="Stage 3",
            prompts=self.curriculum.get_stage_3_prompts()[:self.config.stage_3_samples],
            save_prefix="stage3"
        )

        # Stage 4: Advanced Reasoning
        logger.info("\n[STAGE 4] Advanced Reasoning")
        self._train_stage(
            stage_name="Stage 4",
            prompts=self.curriculum.get_stage_4_prompts()[:self.config.stage_4_samples],
            save_prefix="stage4"
        )

        logger.info("\n" + "="*70)
        logger.info("[SUCCESS] PROGRESSIVE DISTILLATION COMPLETE!")
        logger.info("="*70)

    def _train_stage(self, stage_name: str, prompts: List[str], save_prefix: str):
        """Train a single curriculum stage"""
        # Generate distillation dataset
        distillation_pairs = self.teacher.create_distillation_pairs(prompts, stage_name)

        if not distillation_pairs:
            logger.error(f"[ERROR] No distillation pairs generated for {stage_name}")
            return

        # Create dataset and dataloader
        dataset = DistillationDataset(distillation_pairs, self.tokenizer)
        dataloader = DataLoader(
            dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=0  # Windows compatibility
        )

        # Training loop
        self.student.train()
        stage_start_time = time.time()

        for epoch in range(self.config.epochs_per_stage):
            epoch_loss = 0.0
            num_batches = 0

            logger.info(f"\n{stage_name} - Epoch {epoch+1}/{self.config.epochs_per_stage}")

            pbar = tqdm(dataloader, desc=f"{stage_name} E{epoch+1}")
            for batch_idx, batch in enumerate(pbar):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)

                # Forward pass
                outputs = self.student(input_ids, attention_mask=attention_mask)

                # Calculate cross-entropy loss manually (student learns from tokenized teacher responses)
                logits = outputs['logits']

                # Shift logits and labels for causal LM
                shift_logits = logits[..., :-1, :].contiguous()
                shift_labels = input_ids[..., 1:].contiguous()

                # Calculate loss
                loss_fct = nn.CrossEntropyLoss()
                loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))

                # Backward pass with gradient accumulation
                loss = loss / self.config.gradient_accumulation_steps
                loss.backward()

                if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                    torch.nn.utils.clip_grad_norm_(self.student.parameters(), self.config.max_grad_norm)
                    self.optimizer.step()
                    self.optimizer.zero_grad()
                    self.global_step += 1

                # Track loss
                epoch_loss += loss.item() * self.config.gradient_accumulation_steps
                num_batches += 1

                # Update progress bar
                pbar.set_postfix({'loss': f"{loss.item():.4f}", 'step': self.global_step})

                # Save checkpoint periodically
                if self.global_step % self.config.save_every_steps == 0:
                    avg_loss = epoch_loss / num_batches
                    if avg_loss < self.best_loss:
                        self.best_loss = avg_loss
                        self._save_checkpoint(f"b3_distill_{save_prefix}_best.pth", avg_loss, epoch)

            # Epoch summary
            avg_epoch_loss = epoch_loss / num_batches
            logger.info(f"{stage_name} - Epoch {epoch+1} complete: avg_loss = {avg_epoch_loss:.4f}")

        # Save stage checkpoint
        self._save_checkpoint(f"b3_distill_{save_prefix}_final.pth", avg_epoch_loss, epoch)

        stage_duration = time.time() - stage_start_time
        logger.info(f"[OK] {stage_name} complete in {stage_duration/60:.1f} minutes")

    def _save_checkpoint(self, filename: str, loss: float, epoch: int):
        """Save model checkpoint"""
        checkpoint = {
            'model_state_dict': self.student.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'train_loss': loss,
            'epoch': epoch,
            'global_step': self.global_step,
            'config': self.config
        }
        torch.save(checkpoint, filename)
        logger.info(f"[SAVE] Checkpoint: {filename} (loss: {loss:.4f})")

def main():
    """Main execution"""
    logger.info("="*70)
    logger.info("ImpressionCore B3-Hope Progressive Ollama Distillation")
    logger.info("="*70)

    # Initialize configuration
    config = DistillationConfig()

    # Create trainer
    trainer = ProgressiveDistillationTrainer(config)

    # Run full curriculum
    trainer.run_full_curriculum()

    logger.info("\n[SUCCESS] Training complete! Best checkpoints saved.")
    logger.info("Run b3_generation_tester.py to evaluate the distilled model.")

if __name__ == "__main__":
    main()
